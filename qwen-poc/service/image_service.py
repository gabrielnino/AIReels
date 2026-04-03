import os
import time
import logging
import requests
from typing import List
from dotenv import load_dotenv
from utils.file_utils import download_image
from models.request_models import GenerateImageRequest

load_dotenv()

FAL_API_BASE = "https://queue.fal.run"
FAL_IMAGE_MODEL = "fal-ai/flux/dev"  # Flux Dev — high quality text-to-image ~$0.025/image


def _get_api_key() -> str:
    key = os.environ.get("FAL_API_KEY")
    if not key:
        raise ValueError("FAL_API_KEY not found in environment variables.")
    return key


def _get_headers() -> dict:
    return {
        "Authorization": f"Key {_get_api_key()}",
        "Content-Type": "application/json",
    }


def _submit_image_task(prompt: str, n: int = 1, size: str = "1024*1024") -> dict:
    """
    Submits an async text-to-image task to fal.ai (Flux Dev).
    Returns dict with request_id, status_url and response_url.
    """
    # Parse size format "1024*1024" → width/height
    try:
        width, height = [int(x) for x in size.replace("x", "*").split("*")]
    except Exception:
        width, height = 1024, 1024

    payload = {
        "prompt": prompt,
        "num_images": n,
        "image_size": {"width": width, "height": height},
        "num_inference_steps": 28,
        "guidance_scale": 3.5,
        "enable_safety_checker": True,
    }

    response = requests.post(
        f"{FAL_API_BASE}/{FAL_IMAGE_MODEL}",
        headers=_get_headers(),
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    request_id = data.get("request_id")
    if not request_id:
        raise RuntimeError(f"[image] No request_id in fal.ai response: {data}")

    print(f"[image] Task submitted to fal.ai. Request ID: {request_id}")
    logging.info(f"[image_service._submit_image_task] request_id: {request_id}")
    return {
        "request_id": request_id,
        "status_url": data.get("status_url"),
        "response_url": data.get("response_url"),
    }


def _poll_image_task(task: dict, timeout: int = 120, interval: int = 5) -> List[str]:
    """
    Polls fal.ai until COMPLETED and returns list of image CDN URLs.
    """
    status_url = task["status_url"]
    response_url = task["response_url"]

    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(status_url, headers=_get_headers(), timeout=30)
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status", "UNKNOWN")
        elapsed = int(time.time() - start)
        print(f"[image] Task status: {status} ({elapsed}s elapsed)")

        if status == "COMPLETED":
            result_resp = requests.get(response_url, headers=_get_headers(), timeout=30)
            result_resp.raise_for_status()
            result_data = result_resp.json()
            images = result_data.get("images", [])
            urls = [img.get("url") for img in images if img.get("url")]
            logging.info(f"[image_service._poll_image_task] image URLs: {urls}")
            return urls

        elif status in ("FAILED", "CANCELLED"):
            raise RuntimeError(f"[image] fal.ai task {status}: {data.get('error', 'No details')}")

        time.sleep(interval)

    raise TimeoutError(f"[image] Task timed out after {timeout}s.")


def generate_image_urls(request_data: GenerateImageRequest) -> List[str]:
    """
    Generates images via fal.ai Flux Dev and returns CDN URLs (no download).
    Used for chaining directly into video generation.
    """
    logging.info(f"[image_service.generate_image_urls] prompt: {request_data.prompt[:80]}")
    task = _submit_image_task(
        prompt=request_data.prompt,
        n=request_data.n or 1,
        size=request_data.size or "1024*1024",
    )
    urls = _poll_image_task(task)
    print(f"[image] Generated {len(urls)} image URL(s)")
    logging.info(f"[image_service.generate_image_urls] output: {urls}")
    return urls


def generate_images(request_data: GenerateImageRequest) -> List[str]:
    """
    Generates images via fal.ai Flux Dev, downloads them to outputs/,
    and returns local file paths.
    """
    logging.info(f"[image_service.generate_images] prompt: {request_data.prompt[:80]}")
    try:
        urls = generate_image_urls(request_data)
        output_paths = []
        for url in urls:
            local_file = download_image(url)
            if local_file:
                output_paths.append(local_file)
        logging.info(f"[image_service.generate_images] output: {output_paths}")
        return output_paths
    except Exception as e:
        print(f"[image] Exception during fal.ai image generation: {e}")
        raise
