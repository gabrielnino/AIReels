import os
import time
import uuid
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

DASHSCOPE_INTL_BASE = "https://dashscope-intl.aliyuncs.com/api/v1"


def _get_api_key() -> str:
    key = os.environ.get("DASHSCOPE_API_KEY")
    if not key:
        raise ValueError("DASHSCOPE_API_KEY not found in environment variables.")
    return key


def submit_video_task(
    img_url: str,
    prompt: str,
    resolution: str = "720P",
    duration: int = 5,
    audio: bool = False,
    prompt_extend: bool = True,
    shot_type: str = "multi",
) -> str:
    """
    Submits an async image-to-video generation task using wan2.6-i2v.
    Returns the task_id.
    """
    logging.info(f"[video_service.submit_video_task] input values - img_url: {img_url}, prompt: {prompt}, resolution: {resolution}, duration: {duration}, audio: {audio}, prompt_extend: {prompt_extend}, shot_type: {shot_type}")
    api_key = _get_api_key()
    headers = {
        "X-DashScope-Async": "enable",
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "wan2.6-i2v",
        "input": {
            "prompt": prompt,
            "img_url": img_url,
        },
        "parameters": {
            "resolution": resolution,
            "prompt_extend": prompt_extend,
            "duration": duration,
            "audio": audio,
            "shot_type": shot_type,
        },
    }

    response = requests.post(
        f"{DASHSCOPE_INTL_BASE}/services/aigc/video-generation/video-synthesis",
        headers=headers,
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    task_id = data["output"]["task_id"]
    print(f"[video] Task submitted. Task ID: {task_id}")
    logging.info(f"[video_service.submit_video_task] output values - task_id: {task_id}")
    return task_id


def poll_video_task(task_id: str, timeout: int = 600, interval: int = 10) -> str:
    """
    Polls the task status until SUCCEEDED and returns the video URL.
    Raises RuntimeError on failure, TimeoutError if exceeded.
    """
    logging.info(f"[video_service.poll_video_task] input values - task_id: {task_id}, timeout: {timeout}, interval: {interval}")
    api_key = _get_api_key()
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{DASHSCOPE_INTL_BASE}/tasks/{task_id}"

    start = time.time()
    while time.time() - start < timeout:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        status = data["output"]["task_status"]
        elapsed = int(time.time() - start)
        print(f"[video] Task status: {status} ({elapsed}s elapsed)")

        if status == "SUCCEEDED":
            video_url = data["output"].get("video_url")
            if not video_url:
                raise RuntimeError("Task succeeded but no video_url in response.")
            logging.info(f"[video_service.poll_video_task] output values - video_url: {video_url}")
            return video_url
        elif status in ("FAILED", "CANCELED"):
            raise RuntimeError(f"Video task {status}: {data.get('output', {}).get('message', 'No details')}")

        time.sleep(interval)

    raise TimeoutError(f"Video task timed out after {timeout}s. Task ID: {task_id}")


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
    duration: int = 5,
    audio: bool = False,
) -> str:
    """
    Full pipeline: submit task → poll → download.
    Returns local path to the downloaded .mp4 file.
    """
    logging.info(f"[video_service.generate_video] input values - img_url: {img_url}, prompt: {prompt}, resolution: {resolution}, duration: {duration}, audio: {audio}")
    task_id = submit_video_task(img_url, prompt, resolution=resolution, duration=duration, audio=audio)
    video_url = poll_video_task(task_id)
    result = download_video(video_url)
    logging.info(f"[video_service.generate_video] output values - result: {result}")
    return result
