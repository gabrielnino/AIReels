import time
import requests
from typing import List
from dotenv import load_dotenv
from utils.file_utils import download_image
from models.request_models import GenerateImageRequest
from utils.logger import get_logger
from service.fal_client import FAL_API_BASE, get_fal_headers

load_dotenv()
log = get_logger(__name__)

FAL_IMAGE_MODEL = "fal-ai/flux/dev"  # Flux Dev — high quality text-to-image ~$0.025/image


def _submit_image_task(prompt: str, n: int = 1, size: str = "1024*1024") -> dict:
    """Submits an async text-to-image task to fal.ai Flux Dev."""
    try:
        width, height = [int(x) for x in size.replace("x", "*").split("*")]
    except Exception:
        width, height = 1024, 1024

    log.step("_submit_image_task", "IN", prompt_preview=prompt[:80], n=n, width=width, height=height)

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
        headers=get_fal_headers(),
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    request_id = data.get("request_id")
    if not request_id:
        log.step("_submit_image_task", "ERR", error="No request_id in response", response=data)
        raise RuntimeError(f"No request_id in fal.ai response: {data}")

    task = {
        "request_id": request_id,
        "status_url": data.get("status_url"),
        "response_url": data.get("response_url"),
    }
    log.step("_submit_image_task", "OUT", request_id=request_id, status_url=task["status_url"])
    return task


def _poll_image_task(task: dict, timeout: int = 120, interval: int = 5) -> List[str]:
    """Polls fal.ai until COMPLETED and returns list of image CDN URLs."""
    request_id = task["request_id"]
    status_url = task["status_url"]
    response_url = task["response_url"]

    log.step("_poll_image_task", "IN", request_id=request_id)

    headers = get_fal_headers()
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(status_url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status", "UNKNOWN")
        elapsed = int(time.time() - start)
        log.step("_poll_image_task", "INFO", request_id=request_id, status=status, elapsed_s=elapsed)

        if status == "COMPLETED":
            result_resp = requests.get(response_url, headers=headers, timeout=30)
            result_resp.raise_for_status()
            result_data = result_resp.json()
            urls = [img.get("url") for img in result_data.get("images", []) if img.get("url")]
            log.step("_poll_image_task", "OUT", request_id=request_id, urls_count=len(urls), urls=urls)
            return urls

        elif status in ("FAILED", "CANCELLED"):
            log.step("_poll_image_task", "ERR", request_id=request_id, status=status, error=data.get("error"))
            raise RuntimeError(f"fal.ai image task {status}: {data.get('error', 'No details')}")

        time.sleep(interval)

    raise TimeoutError(f"Image task timed out after {timeout}s. Request ID: {request_id}")


def generate_image_urls(request_data: GenerateImageRequest) -> List[str]:
    """Generates images via fal.ai Flux Dev and returns CDN URLs (no download)."""
    log.step("generate_image_urls", "IN",
             prompt_preview=request_data.prompt[:80],
             n=request_data.n,
             size=request_data.size)

    task = _submit_image_task(
        prompt=request_data.prompt,
        n=request_data.n or 1,
        size=request_data.size or "1024*1024",
    )
    urls = _poll_image_task(task)
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
