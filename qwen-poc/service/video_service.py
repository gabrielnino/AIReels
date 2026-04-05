"""
video_service.py
================
Generates video for Reels.

Providers (auto-detected by priority):
  1. Ken Burns effect via FFmpeg (free, local, no API key)
     Creates a dynamic video from the image with slow pan + zoom.
     Perfect for 15s social media reels.
  2. fal.ai Wan i2v (requires FAL_API_KEY)
     AI generates actual motion from the image.

Flow:
  1. download_image()        → saves image to run directory
  2a. ken_burns_effect()     → creates video with pan/zoom (FFmpeg)
  2b. submit_video_task()   → queues AI video task (fal.ai)
  3. Returns local .mp4 path
"""

import os
import uuid
import time
import requests
from utils.logger import get_logger
from utils.run_context import get_run_dir
from service.fal_client import FAL_API_BASE, get_fal_headers
import subprocess as sp

log = get_logger(__name__)

FAL_MODEL = "fal-ai/wan/v2.2-a14b/image-to-video"


def _get_ffmpeg_path() -> str:
    """Gets the path to the bundled FFmpeg binary."""
    return os.path.join(os.path.dirname(__file__), "..", "ffmpeg")


def _fal_available() -> bool:
    """Quick check — FAL_API_KEY exists in environment."""
    try:
        return bool(os.environ.get("FAL_API_KEY"))
    except Exception:
        return False


def _download_image_for_video(img_url: str) -> str:
    """Downloads image from URL to run directory."""
    run_dir = get_run_dir()
    ext = ".png" if ".png" in img_url else ".jpg"
    filename = os.path.join(run_dir, f"base_image_{uuid.uuid4().hex[:8]}{ext}")

    r = requests.get(img_url, stream=True, timeout=60)
    r.raise_for_status()
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    size_kb = round(os.path.getsize(filename) / 1024)
    log.step("download_image", "OUT", filename=filename, size_kb=size_kb)
    return filename


# ── Ken Burns Effect (FFmpeg, free) ───────────────────────────────────────────

def _ken_burns_effect(
    img_path: str,
    duration: int = 15,
    width: int = 720,
    height: int = 1280,
    fps: int = 30,
) -> str:
    """
    Creates a Ken Burns video from an image: slow zoom in + pan effect.
    Uses FFmpeg's zoompan filter for smooth motion.
    """
    log.step("ken_burns_effect", "IN",
             image=img_path, duration=duration, resolution=f"{width}x{height}")

    run_dir = get_run_dir()
    output = os.path.join(run_dir, f"video_{uuid.uuid4().hex[:8]}_kenburns.mp4")
    ffmpeg = _get_ffmpeg_path()

    # Ken Burns: slow zoom (1.0 to 1.3x) + subtle pan
    # zoompan creates the motion effect over duration * fps frames
    total_frames = duration * fps
    filter_str = (
        f"scale={width * 1.5:.0f}:{height * 1.5:.0f},"  # upscale for zoom room
        f"zoompan="
        f"z='min(1.3,zoom+0.0015)':"  # slow zoom 1.0 -> 1.3
        f"y='ih/2-(ih/zoom/2)-sin(in/{total_frames}*3.14)*ih*0.05':"  # subtle vertical pan
        f"x='iw/2-(iw/zoom/2)+sin(in/{total_frames}*3.14)*iw*0.05':"  # subtle horizontal pan
        f"d={total_frames}:"  # duration in frames
        f"s={width}x{height}:"
        f"fps={fps}"
    )

    cmd = [
        ffmpeg, "-y",
        "-loop", "1", "-i", img_path,
        "-vf", filter_str,
        "-t", str(duration),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "23",
        "-an",
        output,
    ]

    log.step("ken_burns_effect", "INFO", cmd=" ".join(cmd[:6]) + "...")
    result = sp.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        log.step("ken_burns_effect", "ERR", error=result.stderr[:300] if result.stderr else "Unknown error")
        raise RuntimeError(f"FFmpeg Ken Burns failed: {result.stderr[:300]}")

    size_kb = round(os.path.getsize(output) / 1024)
    log.step("ken_burns_effect", "OUT", output=output, size_kb=size_kb)
    return output


# ── fal.ai Wan i2v (API key required) ─────────────────────────────────────────

def _submit_video_task(
    img_url: str,
    prompt: str,
    resolution: str = "720p",
    duration: int = 15,
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
        "num_frames": min(duration * 16, 161),
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


def _poll_video_task(task: dict, timeout: int = 600, interval: int = 10) -> str:
    """Polls fal.ai queue status until COMPLETED and returns the video URL."""
    headers = get_fal_headers()
    start = time.time()
    while time.time() - start < timeout:
        response = requests.get(task["status_url"], headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        status = data.get("status", "UNKNOWN")
        elapsed = int(time.time() - start)
        log.step("poll_video_task", "INFO", status=status, elapsed_s=elapsed)

        if status == "COMPLETED":
            result_resp = requests.get(task["response_url"], headers=headers, timeout=30)
            result_resp.raise_for_status()
            result_data = result_resp.json()
            video_url = (
                result_data.get("video", {}).get("url")
                or result_data.get("video_url")
            )
            if not video_url:
                raise RuntimeError(f"Task completed but no video URL found: {result_data}")

            log.step("poll_video_task", "OUT", video_url=video_url)
            return video_url

        elif status in ("FAILED", "CANCELLED"):
            raise RuntimeError(f"fal.ai video task {status}: {data.get('error', 'No details')}")

        time.sleep(interval)

    raise TimeoutError(f"Video task timed out after {timeout}s.")


def _download_video(video_url: str) -> str:
    """Downloads the video from CDN and saves it to the current run directory."""
    run_dir = get_run_dir()
    filename = os.path.join(run_dir, f"{uuid.uuid4().hex[:8]}_wan.mp4")

    r = requests.get(video_url, stream=True, timeout=120)
    r.raise_for_status()
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    file_size_kb = round(os.path.getsize(filename) / 1024)
    log.step("download_video", "OUT", filename=filename, size_kb=file_size_kb)
    return filename


# ── Orchestrator ──────────────────────────────────────────────────────────────

def generate_video(
    img_url: str,
    prompt: str,
    resolution: str = "720P",
    duration: int = 10,
    audio: bool = False,
) -> str:
    """
    Full pipeline: image → video (.mp4).

    Ken Burns effect (free, local, no API key) — always used.

    To use fal.ai (requires credit), set VIDEO_PROVIDER=fal in .env.
    """
    log.step("generate_video", "IN",
             img_url=img_url,
             prompt_preview=prompt[:80],
             resolution=resolution,
             duration=duration,
             audio=audio)

    width = int(resolution.lower().split("p")[0]) if resolution.lower().endswith("p") else 720
    height = int(width * 16 / 9)

    # img_url can be a local path (Pollinations) or remote URL (fal.ai)
    if os.path.isfile(img_url):
        img_path = img_url
    else:
        img_path = _download_image_for_video(img_url)

    result = _ken_burns_effect(img_path, duration=duration, width=width, height=height)

    log.step("generate_video", "OUT", local_path=result)
    return result
