"""
pollinations_service.py
─────────────────────────
Secure integration with Pollinations.ai API.
Manages API key, HTTP requests, and error handling.
"""

import os
import httpx
import logging
import time
import urllib.parse
import base64
import asyncio
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────────────────
# Use the direct image API endpoint (proven to work)
POLLINATIONS_BASE_URL = "https://image.pollinations.ai/prompt"

# Request settings
DEFAULT_WIDTH = 1024
DEFAULT_HEIGHT = 1024
DEFAULT_MODEL = "flux"
TIMEOUT_SEC = 180.0  # Increased for slower API responses


# ── Main Service ───────────────────────────────────────────────────────────
async def generate_image(
    prompt: str,
    negative_prompt: str = "",
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    model: str = DEFAULT_MODEL,
    seed: Optional[int] = None,
) -> dict:
    """
    Generate image via Pollinations.ai with retry logic.

    Args:
        prompt         : Main prompt for image generation
        negative_prompt: Elements to avoid (integrated into prompt)
        width / height : Image dimensions (default 1024x1024)
        model          : Model to use (default: flux)
        seed           : Optional seed for reproducibility

    Returns:
        dict with:
            - "image_url": Generated image URL
            - "image_b64": Base64 encoded image
            - "latency": Generation time in seconds
            - "cached": False (never cached from this service)

    Raises:
        RuntimeError: If API call fails after retries
    """

    # Build full prompt with negative elements
    full_prompt = _build_full_prompt(prompt, negative_prompt)

    # Generate deterministic seed if not provided
    if seed is None:
        import hashlib
        seed = int(hashlib.md5(full_prompt.encode()).hexdigest()[:8], 16) % (2**32)

    # Build URL with all parameters
    image_url = _build_url(full_prompt, width, height, seed, model)

    logger.info(
        f"📤 Generating image: model={model}, size={width}x{height}, "
        f"prompt={prompt[:50]}..."
    )
    t0 = time.time()

    # Retry logic for robustness
    max_retries = 5
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            logger.debug(f"Attempt {attempt + 1}/{max_retries}: GET {image_url[:100]}...")
            
            async with httpx.AsyncClient(timeout=TIMEOUT_SEC, follow_redirects=True) as client:
                response = await client.get(image_url)
                response.raise_for_status()

                # Verify it's an image
                content_type = response.headers.get("content-type", "")
                if "image" not in content_type:
                    raise ValueError(
                        f"Invalid content-type: {content_type} (expected image/*)"
                    )

                image_bytes = response.content
                if not image_bytes:
                    raise ValueError("Empty image response")

                latency = round(time.time() - t0, 2)
                image_b64 = base64.b64encode(image_bytes).decode("utf-8")

                logger.info(
                    f"✓ Image generated in {latency}s "
                    f"({len(image_bytes)/1024:.1f} KB)"
                )

                return {
                    "image_url": image_url,
                    "image_b64": image_b64,
                    "latency": latency,
                    "cached": False,
                }

        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            is_rate_limit = status_code == 429
            is_server_error = 500 <= status_code < 600
            is_client_error = 400 <= status_code < 500
            should_retry = is_rate_limit or is_server_error

            if should_retry and attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                error_type = (
                    "rate limit" if is_rate_limit else f"server error"
                )
                logger.warning(
                    f"❌ {error_type} ({status_code}) — "
                    f"retry {attempt + 1}/{max_retries} in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)
                continue
            else:
                error_msg = (
                    f"Pollinations API error [{status_code}]: "
                    f"{e.response.reason_phrase}"
                )
                logger.error(error_msg)
                raise RuntimeError(error_msg)

        except httpx.TimeoutException:
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                logger.warning(
                    f"⏱️  Timeout — retry {attempt + 1}/{max_retries} "
                    f"in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)
                continue
            else:
                error_msg = "Pollinations.ai timeout after all retries"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                logger.warning(
                    f"⚠️  Error ({type(e).__name__}) — "
                    f"retry {attempt + 1}/{max_retries} in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)
                continue
            else:
                error_msg = f"Image generation failed: {str(e)}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

    raise RuntimeError(f"Image generation failed after {max_retries} retries")


# ── Helpers ────────────────────────────────────────────────────────────────
def _build_full_prompt(prompt: str, negative_prompt: str) -> str:
    """Integrate negative prompt into main prompt."""
    base = prompt.strip().rstrip(",")

    if negative_prompt:
        neg_items = [x.strip() for x in negative_prompt.split(",") if x.strip()][:5]
        neg_str = ", ".join(neg_items)
        return f"{base}, avoid: {neg_str}"

    return base


def _build_url(prompt: str, width: int, height: int, seed: int, model: str) -> str:
    """Build direct image URL with all parameters."""
    encoded = urllib.parse.quote(prompt, safe="")
    url = (
        f"{POLLINATIONS_BASE_URL}/{encoded}"
        f"?width={width}"
        f"&height={height}"
        f"&seed={seed}"
        f"&model={model}"
        f"&nologo=true"
    )
    return url


async def _download_image_as_base64(image_url: str) -> str:
    """
    Download image from URL and convert to base64.

    Args:
        image_url: URL of the generated image

    Returns:
        Base64 encoded image string

    Raises:
        RuntimeError: If download fails
    """
    import base64

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(image_url)
            response.raise_for_status()

            image_bytes = response.content
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            logger.debug(f"Image downloaded: {len(image_bytes)/1024:.1f} KB")

            return image_b64

    except Exception as e:
        logger.error(f"Failed to download image: {str(e)}")
        raise RuntimeError(f"Image download failed: {str(e)}")


# (No API key health check — using public Pollinations endpoints without auth)
