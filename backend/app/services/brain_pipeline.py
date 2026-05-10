"""Brain anomaly detection pipeline for DS MRI inference."""

import base64
import io
from dataclasses import dataclass
from typing import Any

from huggingface_hub import hf_hub_download
from PIL import Image
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class SinusoidalPosEmb(nn.Module):
    """Sinusoidal timestep embedding."""

    def __init__(self, dim: int):
        super().__init__()
        self.dim = dim

    def forward(self, time: torch.Tensor) -> torch.Tensor:
        device = time.device
        half_dim = self.dim // 2
        emb = torch.exp(-torch.arange(half_dim, device=device).float() * (np.log(10000) / (half_dim - 1)))
        emb = time[:, None].float() * emb[None, :]
        return torch.cat((emb.sin(), emb.cos()), dim=-1)


class ResBlock(nn.Module):
    """UNet residual block with time embedding."""

    def __init__(self, in_ch: int, out_ch: int, temb_dim: int):
        super().__init__()
        self.norm1 = nn.GroupNorm(8, out_ch)
        self.conv1 = nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1)
        self.norm2 = nn.GroupNorm(8, out_ch)
        self.conv2 = nn.Conv2d(out_ch, out_ch, kernel_size=3, padding=1)
        self.time_proj = nn.Linear(temb_dim, out_ch)
        self.skip = nn.Conv2d(in_ch, out_ch, kernel_size=1) if in_ch != out_ch else nn.Identity()

    def forward(self, x: torch.Tensor, temb: torch.Tensor) -> torch.Tensor:
        h = self.conv1(x)
        h = self.norm1(h)
        h = F.silu(h)
        h = h + self.time_proj(F.silu(temb))[:, :, None, None]
        h = self.norm2(h)
        h = F.silu(h)
        h = self.conv2(h)
        return h + self.skip(x)


class UNet(nn.Module):
    """Small UNet for grayscale diffusion denoising."""

    def __init__(self, in_ch: int = 1, base: int = 32, temb_dim: int = 128):
        super().__init__()
        self.time_emb = nn.Sequential(SinusoidalPosEmb(temb_dim), nn.Linear(temb_dim, temb_dim), nn.SiLU())
        self.init_conv = nn.Conv2d(in_ch, base, kernel_size=3, padding=1)
        self.down1 = ResBlock(base, base * 2, temb_dim)
        self.down2 = ResBlock(base * 2, base * 4, temb_dim)
        self.down3 = ResBlock(base * 4, base * 8, temb_dim)
        self.bot = ResBlock(base * 8, base * 8, temb_dim)
        self.up3 = ResBlock(base * 16, base * 4, temb_dim)
        self.up2 = ResBlock(base * 8, base * 2, temb_dim)
        self.up1 = ResBlock(base * 4, base, temb_dim)
        self.out_conv = nn.Conv2d(base, in_ch, kernel_size=1)
        self.pool = nn.AvgPool2d(2)
        self.upsample = nn.Upsample(scale_factor=2, mode="bilinear", align_corners=False)

    def forward(self, x: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        temb = self.time_emb(t)
        h1 = self.init_conv(x)
        h2 = self.down1(h1, temb)
        h3 = self.down2(self.pool(h2), temb)
        h4 = self.down3(self.pool(h3), temb)
        h5 = self.bot(self.pool(h4), temb)
        u4 = self.up3(torch.cat([self.upsample(h5), h4], dim=1), temb)
        u3 = self.up2(torch.cat([self.upsample(u4), h3], dim=1), temb)
        u2 = self.up1(torch.cat([self.upsample(u3), h2], dim=1), temb)
        return self.out_conv(u2)


class DiffusionClassifier(nn.Module):
    """Classifier for EU vs DS probability guidance."""

    def __init__(self, base: int = 32, temb_dim: int = 128):
        super().__init__()
        self.time_emb = nn.Sequential(SinusoidalPosEmb(temb_dim), nn.Linear(temb_dim, temb_dim), nn.SiLU())
        self.stem = nn.Sequential(
            nn.Conv2d(1, base, kernel_size=3, padding=1),
            nn.GroupNorm(8, base),
            nn.SiLU(),
            nn.AvgPool2d(2),
        )
        self.block1 = ResBlock(base, base * 2, temb_dim)
        self.block2 = ResBlock(base * 2, base * 4, temb_dim)
        self.block3 = ResBlock(base * 4, base * 4, temb_dim)
        self.head = nn.Sequential(nn.AdaptiveAvgPool2d((1, 1)), nn.Flatten(), nn.Linear(base * 4, 2))

    def forward(self, x: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        temb = self.time_emb(t)
        h = self.stem(x)
        h = self.block1(h, temb)
        h = self.block2(self.pool(h), temb)
        h = self.block3(self.pool(h), temb)
        return self.head(h)

    @property
    def pool(self) -> nn.Module:
        return nn.AvgPool2d(2)


class GradCAM_UNet(nn.Module):
    """Deterministic GradCAM-like overlay from the anomaly map."""

    def forward(self, anomaly: torch.Tensor) -> torch.Tensor:
        anomaly = anomaly.squeeze(1)  # [1, 128, 128]
        blurred = self._gaussian_blur(anomaly.unsqueeze(1), kernel_size=21, sigma=5)
        norm = (blurred - blurred.min()) / (blurred.max() - blurred.min() + 1e-8)
        return norm.squeeze(1)

    @staticmethod
    def _gaussian_blur(x: torch.Tensor, kernel_size: int = 11, sigma: float = 3.0) -> torch.Tensor:
        kernel = GradCAM_UNet._make_gaussian_kernel(kernel_size, sigma, x.device)
        padding = kernel_size // 2
        return F.conv2d(x, kernel, padding=padding)

    @staticmethod
    def _make_gaussian_kernel(kernel_size: int, sigma: float, device: torch.device) -> torch.Tensor:
        coords = torch.arange(kernel_size, dtype=torch.float32, device=device) - (kernel_size - 1) / 2
        kernel1d = torch.exp(-(coords**2) / (2 * sigma**2))
        kernel1d = kernel1d / kernel1d.sum()
        kernel2d = kernel1d[:, None] * kernel1d[None, :]
        return kernel2d[None, None, :, :]


class DDPM:
    """Base DDPM noise schedule and helpers."""

    def __init__(self, T: int = 1000):
        self.T = T
        betas = torch.linspace(1e-4, 0.02, T)
        alphas = 1.0 - betas
        alphas_cumprod = torch.cumprod(alphas, dim=0)
        self.register_buffers(alphas, alphas_cumprod)

    def register_buffers(self, alphas: torch.Tensor, alphas_cumprod: torch.Tensor) -> None:
        self.alphas = alphas
        self.alphas_cumprod = alphas_cumprod
        self.sqrt_alphas_cumprod = torch.sqrt(alphas_cumprod)
        self.sqrt_one_minus_alphas_cumprod = torch.sqrt(1.0 - alphas_cumprod)
        self.alphas_cumprod_prev = torch.cat([torch.tensor([1.0]), alphas_cumprod[:-1]])

    def q_sample(self, x_start: torch.Tensor, t: torch.Tensor, noise: torch.Tensor | None = None) -> torch.Tensor:
        if noise is None:
            noise = torch.randn_like(x_start)
        return self.sqrt_alphas_cumprod[t][:, None, None, None] * x_start + self.sqrt_one_minus_alphas_cumprod[t][:, None, None, None] * noise

    def ddim_timesteps(self, L: int) -> torch.Tensor:
        return torch.linspace(0, self.T - 1, steps=L, dtype=torch.long)


def tensor_to_base64_png(tensor: torch.Tensor) -> str:
    pixels = tensor.clamp(-1.0, 1.0).add(1.0).div(2.0).mul(255.0).round().to(torch.uint8).squeeze().cpu().numpy()
    image = Image.fromarray(pixels, mode="L")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"


def load_image_bytes(image_bytes: bytes, device: torch.device) -> torch.Tensor:
    with Image.open(io.BytesIO(image_bytes)) as image:
        image = image.convert("L").resize((128, 128), Image.LANCZOS)
        array = np.array(image, dtype=np.float32) / 255.0
        tensor = torch.from_numpy(array).unsqueeze(0).unsqueeze(0).to(device)
    return tensor * 2.0 - 1.0


def match_histogram(image: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    src = image
    src_mean, src_std = src.mean(), src.std(unbiased=False)
    target_mean, target_std = target.mean(), target.std(unbiased=False)
    scale = target_std / (src_std + 1e-8)
    return ((src - src_mean) * scale + target_mean).clamp(-1.0, 1.0)


def compute_anomaly_map(original: torch.Tensor, reconstruction: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, float]:
    anomaly = torch.abs(original - reconstruction)
    brain_mask = (original > -0.05).float()
    masked = anomaly * brain_mask
    score = masked.sum() / (brain_mask.sum() + 1e-8)
    return masked, brain_mask, score.item()


@dataclass
class PredictionResult:
    score: float
    label: str
    anomaly_map: str
    reconstruction: str
    gradcam: str


class BrainPipeline:
    """Complete inference pipeline for DS brain anomaly detection."""

    def __init__(self) -> None:
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.diffusion = DDPM()
        self.unet = None
        self.classifier = None
        self.gradcam = GradCAM_UNet()

    def _ensure_models_loaded(self) -> None:
        """Lazy load models on first use."""
        if self.unet is None:
            self.unet = self._load_model("zienebo/ds-brain-detection", "unet_diffusion.pth", UNet)
        if self.classifier is None:
            self.classifier = self._load_model("zienebo/ds-brain-detection", "classifier.pth", DiffusionClassifier)

    def _load_model(self, repo_id: str, filename: str, model_cls: type[torch.nn.Module]) -> torch.nn.Module:
        print(f"Loading model {filename} from {repo_id}")
        try:
            model_path = hf_hub_download(repo_id=repo_id, filename=filename)
            print(f"Downloaded to {model_path}")
            model = model_cls().to(self.device)
            state = torch.load(model_path, map_location=self.device)
            model.load_state_dict(state, strict=False)
            model.eval()
            print(f"Model {filename} loaded successfully")
            return model
        except Exception as e:
            print(f"Error loading model {filename}: {e}")
            raise

    def ddim_inversion(self, x0: torch.Tensor, L: int = 200) -> torch.Tensor:
        timesteps = self.diffusion.ddim_timesteps(L)
        noise = torch.randn_like(x0, device=self.device)
        x = x0
        for t in timesteps:
            alpha = self.diffusion.sqrt_alphas_cumprod[t]
            x = alpha * x0 + self.diffusion.sqrt_one_minus_alphas_cumprod[t] * noise
        return x

    def ddim_guided_denoising(self, xT: torch.Tensor, L: int = 200, guidance_scale: float = 3.0) -> torch.Tensor:
        x = xT.detach().clone()
        timesteps = self.diffusion.ddim_timesteps(L)
        for index in reversed(range(len(timesteps))):
            t = timesteps[index].unsqueeze(0).to(self.device)
            x = x.detach().requires_grad_(True)
            eps = self.unet(x, t)
            logits = self.classifier(x, t)
            log_probs = F.log_softmax(logits, dim=-1)
            logp_eu = log_probs[:, 0].sum()
            grad = torch.autograd.grad(logp_eu, x)[0]
            guided_eps = eps - guidance_scale * self.diffusion.sqrt_one_minus_alphas_cumprod[t] * grad
            alpha_t = self.diffusion.sqrt_alphas_cumprod[t]
            x0_pred = (x - self.diffusion.sqrt_one_minus_alphas_cumprod[t] * guided_eps) / (alpha_t + 1e-8)
            prev_alpha = self.diffusion.sqrt_alphas_cumprod[0] if index == 0 else self.diffusion.sqrt_alphas_cumprod[timesteps[index - 1]]
            x = prev_alpha * x0_pred + self.diffusion.sqrt_one_minus_alphas_cumprod[t] * guided_eps
        return x.detach()

    def run_full_pipeline(self, image_bytes: bytes, L: int = 200, guidance_scale: float = 3.0) -> PredictionResult:
        self._ensure_models_loaded()
        x0 = load_image_bytes(image_bytes, self.device)
        xT = self.ddim_inversion(x0, L=L)
        reconstruction = self.ddim_guided_denoising(xT, L=L, guidance_scale=guidance_scale)
        reconstruction = match_histogram(reconstruction, x0)
        anomaly_map, _, score = compute_anomaly_map(x0, reconstruction)
        gradcam_map = self.gradcam(anomaly_map)

        label = "DS Detected" if score > 0.18 else "Normal"

        return PredictionResult(
            score=round(score, 4),
            label=label,
            anomaly_map=tensor_to_base64_png(anomaly_map),
            reconstruction=tensor_to_base64_png(reconstruction),
            gradcam=tensor_to_base64_png(gradcam_map),
        )


brain_pipeline = BrainPipeline()
