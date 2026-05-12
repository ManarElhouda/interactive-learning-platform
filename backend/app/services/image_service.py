"""
image_service.py
─────────────────
Image generation service with local caching.
Delegates Pollinations API calls to pollinations_service.py
"""

import hashlib
import logging
import os
import time
import base64
from pathlib import Path
from typing import Optional

from app.services.pollinations_service import generate_image as pollinations_generate_image

logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────────────────
DEFAULT_WIDTH = 1024
DEFAULT_HEIGHT = 1024

# Local cache directory
CACHE_DIR = os.getenv("IMAGE_CACHE_DIR", "./cache/images")
Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)


# ── Main Service ───────────────────────────────────────────────────────────
async def generate_image(
    prompt: str,
    negative_prompt: str = "",
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    seed: Optional[int] = None,
    child_id: str = "child_001",
) -> dict:
    """
    Generate image with local caching and Pollinations API integration.

    Args:
        prompt         : Main image prompt
        negative_prompt: Elements to avoid
        width / height : Image dimensions (default 1024x1024)
        seed           : Reproducibility seed (optional)
        child_id       : For cache organization

    Returns:
        dict with:
            - "image_bytes": Raw PNG bytes
            - "image_b64":  Base64 encoded image
            - "image_url":  Pollinations API URL
            - "cached":     Whether served from cache
            - "latency":    Generation time in seconds
    """

    # Enrich prompt with negative elements
    full_prompt = _build_full_prompt(prompt, negative_prompt)

    # Generate deterministic seed if not provided
    if seed is None:
        seed = _prompt_to_seed(full_prompt)

    # Check local cache
    cache_key = f"{hashlib.md5(full_prompt.encode()).hexdigest()}_{width}x{height}_{seed}"
    cache_path = Path(CACHE_DIR) / f"{cache_key}.png"

    if cache_path.exists():
        logger.info(f"✓ Image found in cache: {cache_key}")
        with open(cache_path, "rb") as f:
            image_bytes = f.read()
        return {
            "image_bytes": image_bytes,
            "image_b64": _to_base64(image_bytes),
            "image_url": "",  # No URL for cached images
            "cached": True,
            "latency": 0.0,
        }

    # Generate via Pollinations API (with secure API key)
    logger.info(f"Generating image: {prompt[:60]}...")
    t0 = time.time()

    try:
        result = await pollinations_generate_image(
            prompt=full_prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
        )

        # Download and cache the image
        image_url = result["image_url"]
        image_b64 = result["image_b64"]

        # Decode base64 to bytes and save to cache
        image_bytes = base64.b64decode(image_b64)

        with open(cache_path, "wb") as f:
            f.write(image_bytes)

        latency = round(time.time() - t0, 2)
        logger.info(f"✓ Image generated in {latency}s ({len(image_bytes)/1024:.1f} KB)")

        return {
            "image_bytes": image_bytes,
            "image_b64": image_b64,
            "image_url": image_url,
            "cached": False,
            "latency": latency,
        }

    except Exception as e:
        logger.error(f"Image generation failed: {str(e)}")
        raise


# ── Helpers ────────────────────────────────────────────────────────────────
def _build_full_prompt(prompt: str, negative_prompt: str) -> str:
    """
    Integrate negative prompt into main prompt.
    (Pollinations API now supports negative_prompt natively)

    Args:
        prompt: Main prompt
        negative_prompt: Elements to avoid

    Returns:
        Enhanced full prompt string
    """
    base = prompt.strip().rstrip(",")

    if negative_prompt:
        # Keep only most important negative items (max 5)
        neg_items = [x.strip() for x in negative_prompt.split(",") if x.strip()][:5]
        neg_str = ", ".join(neg_items)
        return f"{base}, avoid: {neg_str}"

    return base


def _prompt_to_seed(prompt: str) -> int:
    """
    Generate deterministic seed from prompt for reproducibility.

    Args:
        prompt: Input prompt

    Returns:
        Reproducible seed integer
    """
    return int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16) % (2**32)


def _to_base64(image_bytes: bytes) -> str:
    """
    Encode image bytes to base64 string.

    Args:
        image_bytes: Raw image bytes

    Returns:
        Base64 encoded string
    """
    return base64.b64encode(image_bytes).decode("utf-8")