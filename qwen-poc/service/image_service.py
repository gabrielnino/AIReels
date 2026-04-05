"""
image_service.py
================
Generates images for Reels.

Provider: Pollinations AI (free, no API key)
  - Uses Flux model via polling
  - Supports custom width/height
  - URL-based API, no authentication needed

Usage:
  generate_image_urls(request)  → returns CDN URLs
  generate_images(request)      → returns local file paths
"""

import os
import time
import uuid
import requests
from typing import List
from utils.file_utils import download_image
from models.request_models import GenerateImageRequest
from utils.logger import get_logger

log = get_logger(__name__)

POLLINATIONS_BASE = "https://image.pollinations.ai/prompt"

# Model registry — Pollinations supports multiple models
MODEL = "flux"  # flux is free and good quality

import urllib.parse


def _build_pollinations_url(prompt: str, width: int = 1024, height: int = 1024) -> str:
    """Builds a direct image URL from Pollinations AI."""
    encoded_prompt = urllib.parse.quote(prompt)
    return f"{POLLINATIONS_BASE}/{encoded_prompt}?width={width}&height={height}&model={MODEL}&seed={uuid.uuid4().hex[:8]}"


def _generate_single_image(prompt: str, width: int = 1024, height: int = 1024) -> str:
    """Generates a single image and returns the CDN URL."""
    url = _build_pollinations_url(prompt, width, height)

    # Pollinations generates on-demand, so we download immediately to cache the image
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    if len(response.content) == 0:
        raise RuntimeError("Pollinations returned empty content")

    # Save the downloaded image to the run directory
    from utils.run_context import get_run_dir
    run_dir = get_run_dir()
    local_path = os.path.join(run_dir, f"image_{uuid.uuid4().hex[:8]}.jpg")
    with open(local_path, "wb") as f:
        f.write(response.content)

    log.step("_generate_single_image", "OUT", path=local_path, size_kb=round(len(response.content)/1024))
    return local_path


def generate_image_urls(request_data: GenerateImageRequest) -> List[str]:
    """Generates images via Pollinations AI (Pollinations) and returns CDN URLs."""
    log.step("generate_image_urls", "IN",
             prompt_preview=request_data.prompt[:80],
             n=request_data.n,
             size=request_data.size)

    try:
        width, height = [int(x) for x in (request_data.size or "1024*1024").replace("x", "*").split("*")]
    except Exception:
        width, height = 1024, 1024

    urls = []
    for i in range(request_data.n or 1):
        url = _generate_single_image(request_data.prompt, width, height)
        urls.append(url)
        log.step("generate_image_urls", "INFO", image_idx=i+1, url=url)

    log.step("generate_image_urls", "OUT", urls_count=len(urls), urls=urls)
    return urls


def generate_images(request_data: GenerateImageRequest) -> List[str]:
    """Generates images, downloads them to outputs/, and returns local file paths."""
    log.step("generate_images", "IN", prompt_preview=request_data.prompt[:80])
    try:
        urls = generate_image_urls(request_data)
        output_paths = []
        for url in urls:
            local_file = download_image(url)
            if local_file:
                output_paths.append(local_file)
                log.step("generate_images", "INFO", downloaded_to=local_file)
        log.step("generate_images", "OUT", local_paths=output_paths)
        return output_paths
    except Exception as e:
        log.step("generate_images", "ERR", error=str(e))
        raise
