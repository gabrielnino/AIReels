import os
import time
import uuid
import requests
from dotenv import load_dotenv
from utils.logger import get_logger
from service.fal_client import FAL_API_BASE, get_fal_headers

load_dotenv()
log = get_logger(__name__)

FAL_MODEL = "fal-ai/wan/v2.2-a14b/image-to-video"  # Wan 2.1 i2v — ~$0.20/video (480p) or $0.40/video (720p)


def submit_video_task(
    img_url: str,
    prompt: str,
    resolution: str = "720p",
    duration: int = 10,
) -> dict:
    """Submits an async image-to-video task to fal.ai Wan 2.1 i2v."""
    log.step("submit_video_task", "IN",
             img_url=img_url,
             prompt_preview=prompt[:80],
             resolution=resolution,
             duration=duration)

    payload = {
        "image_url": img_url,
        "prompt": prompt,
        "num_frames": min(duration * 16, 161),  # ~16fps, max 161 frames (~10s)
        "resolution": resolution,
    }

    response = requests.post(
        f"{FAL_API_BASE}/{FAL_MODEL}",
        headers=get_fal_headers(),
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    request_id = data.get("request_id")
    if not request_id:
        log.step("submit_video_task", "ERR", error="No request_id in response", response=data)
        raise RuntimeError(f"No request_id in fal.ai response: {data}")

    task = {
        "request_id": request_id,
        "status_url": data.get("status_url"),
        "response_url": data.get("response_url"),
    }
    log.step("submit_video_task", "OUT", request_id=request_id, status_url=task["status_url"])
    return task


def poll_video_task(task: dict, timeout: int = 600, interval: int = 10) -> str:
    """Polls fal.ai queue status until COMPLETED and returns the video URL."""
    request_id = task["request_id"]
    status_url = task["status_url"]
    response_url = task["response_url"]

    log.step("poll_video_task", "IN", request_id=request_id)

    headers = get_fal_headers()
    start = time.time()
    while time.time() - start < timeout:
        response = requests.get(status_url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        status = data.get("status", "UNKNOWN")
        elapsed = int(time.time() - start)
        log.step("poll_video_task", "INFO", request_id=request_id, status=status, elapsed_s=elapsed)

        if status == "COMPLETED":
            result_resp = requests.get(response_url, headers=headers, timeout=30)
            result_resp.raise_for_status()
            result_data = result_resp.json()
            video_url = (
                result_data.get("video", {}).get("url")
                or result_data.get("video_url")
            )
            if not video_url:
                log.step("poll_video_task", "ERR",
                         request_id=request_id,
                         error="Task COMPLETED but no video URL in response",
                         result_data=result_data)
                raise RuntimeError(f"Task completed but no video URL found: {result_data}")

            log.step("poll_video_task", "OUT", request_id=request_id, video_url=video_url)
            return video_url

        elif status in ("FAILED", "CANCELLED"):
            log.step("poll_video_task", "ERR", request_id=request_id, status=status, error=data.get("error"))
            raise RuntimeError(f"fal.ai video task {status}: {data.get('error', 'No details')}")

        time.sleep(interval)

    raise TimeoutError(f"Video task timed out after {timeout}s. Request ID: {request_id}")


def download_video(video_url: str) -> str:
    """Downloads the video from CDN and saves it to the current run directory."""
    from utils.run_context import get_run_dir
    log.step("download_video", "IN", video_url=video_url)
    run_dir = get_run_dir()
    filename = os.path.join(run_dir, f"{uuid.uuid4()}.mp4")

    r = requests.get(video_url, stream=True, timeout=120)
    r.raise_for_status()
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    file_size_kb = round(os.path.getsize(filename) / 1024)
    log.step("download_video", "OUT", filename=filename, size_kb=file_size_kb)
    return filename


def generate_video(
    img_url: str,
    prompt: str,
    resolution: str = "720P",
    duration: int = 10,
    audio: bool = False,
) -> str:
    """Full pipeline: submit → poll → download. Returns local .mp4 path."""
    log.step("generate_video", "IN",
             img_url=img_url,
             prompt_preview=prompt[:80],
             resolution=resolution,
             duration=duration,
             audio=audio)

    fal_resolution = resolution.lower()
    task = submit_video_task(img_url, prompt, resolution=fal_resolution, duration=duration)
    video_url = poll_video_task(task)
    result = download_video(video_url)

    log.step("generate_video", "OUT", local_path=result)
    return result
