import os
import time
import uuid
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

FAL_API_BASE = "https://queue.fal.run"
FAL_MODEL = "fal-ai/wan/v2.2-a14b/image-to-video"  # Wan 2.1 Image-to-Video — ~$0.20/video (480p) or $0.40/video (720p)


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


def submit_video_task(
    img_url: str,
    prompt: str,
    resolution: str = "720p",
    duration: int = 10,
) -> dict:
    """
    Submits an async image-to-video task to fal.ai (Wan 2.1 i2v).
    Returns a dict with request_id, status_url and response_url.
    """
    logging.info(f"[video_service.submit_video_task] input values - img_url: {img_url}, prompt: {prompt}, resolution: {resolution}, duration: {duration}")

    payload = {
        "image_url": img_url,
        "prompt": prompt,
        "num_frames": min(duration * 16, 161),  # ~16fps, max 161 frames (~10s)
        "resolution": resolution,
    }

    response = requests.post(
        f"{FAL_API_BASE}/{FAL_MODEL}",
        headers=_get_headers(),
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    request_id = data.get("request_id")
    if not request_id:
        raise RuntimeError(f"[video] No request_id in fal.ai response: {data}")

    print(f"[video] Task submitted to fal.ai. Request ID: {request_id}")
    logging.info(f"[video_service.submit_video_task] output values - {data}")
    return {
        "request_id": request_id,
        "status_url": data.get("status_url"),
        "response_url": data.get("response_url"),
    }


def poll_video_task(task: dict, timeout: int = 600, interval: int = 10) -> str:
    """
    Polls fal.ai queue status until COMPLETED and returns the video URL.
    Uses the status_url and response_url returned directly by submit_video_task.
    Raises RuntimeError on failure, TimeoutError if exceeded.
    """
    request_id = task["request_id"]
    status_url = task["status_url"]
    response_url = task["response_url"]

    logging.info(f"[video_service.poll_video_task] input values - request_id: {request_id}")

    start = time.time()
    while time.time() - start < timeout:
        response = requests.get(status_url, headers=_get_headers(), timeout=30)
        response.raise_for_status()
        data = response.json()
        status = data.get("status", "UNKNOWN")
        elapsed = int(time.time() - start)
        print(f"[video] Task status: {status} ({elapsed}s elapsed)")

        if status == "COMPLETED":
            result_resp = requests.get(response_url, headers=_get_headers(), timeout=30)
            result_resp.raise_for_status()
            result_data = result_resp.json()
            video_url = (
                result_data.get("video", {}).get("url")
                or result_data.get("video_url")
            )
            if not video_url:
                raise RuntimeError(f"[video] Task completed but no video URL found: {result_data}")
            logging.info(f"[video_service.poll_video_task] output values - video_url: {video_url}")
            return video_url

        elif status in ("FAILED", "CANCELLED"):
            raise RuntimeError(f"[video] fal.ai task {status}: {data.get('error', 'No details')}")

        time.sleep(interval)

    raise TimeoutError(f"[video] Task timed out after {timeout}s. Request ID: {request_id}")


def download_video(video_url: str) -> str:
    """Downloads the video and saves it to outputs/. Returns the local file path."""
    logging.info(f"[video_service.download_video] input values - video_url: {video_url}")
    os.makedirs("outputs", exist_ok=True)
    filename = f"outputs/{uuid.uuid4()}.mp4"
    print(f"[video] Downloading video from {video_url}")
    r = requests.get(video_url, stream=True, timeout=120)
    r.raise_for_status()
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"[video] Saved to {filename}")
    logging.info(f"[video_service.download_video] output values - filename: {filename}")
    return filename


def generate_video(
    img_url: str,
    prompt: str,
    resolution: str = "720P",
    duration: int = 10,
    audio: bool = False,
) -> str:
    """
    Full pipeline using fal.ai Wan 2.1 i2v (~$0.40/video 720p):
    submit task → poll → download.
    Returns local path to the downloaded .mp4 file.
    """
    logging.info(f"[video_service.generate_video] input values - img_url: {img_url}, prompt: {prompt}, resolution: {resolution}, duration: {duration}, audio: {audio}")

    # fal.ai uses lowercase resolution ("720p" vs legacy "720P")
    fal_resolution = resolution.lower()

    task = submit_video_task(img_url, prompt, resolution=fal_resolution, duration=duration)
    video_url = poll_video_task(task)
    result = download_video(video_url)
    logging.info(f"[video_service.generate_video] output values - result: {result}")
    return result
