"""
audio_service.py
================
Generates a concert/music audio track via fal.ai MusicGen and muxes it
onto a silent MP4 using the bundled FFmpeg binary.

Flow:
  1. submit_audio_task()  → queues a MusicGen job on fal.ai
  2. poll_audio_task()    → waits until COMPLETED, returns CDN audio URL
  3. download_audio()     → saves .mp3/.wav to the run directory
  4. mux_audio_video()    → merges audio + video with FFmpeg into a new .mp4
  5. generate_audio_for_video() → orchestrates all four steps
"""

import os
import subprocess
import time
import uuid
import requests
from utils.logger import get_logger
from service.fal_client import FAL_API_BASE, get_fal_headers

log = get_logger(__name__)

FAL_AUDIO_MODEL = "fal-ai/stable-audio"

# Path to the bundled static FFmpeg binary (project root)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
FFMPEG_BIN = os.path.join(_PROJECT_ROOT, "ffmpeg")


# ── 1. Submit ─────────────────────────────────────────────────────────────────

def submit_audio_task(prompt: str, duration: int = 10) -> dict:
    """Submits an async text-to-music task to fal.ai MusicGen."""
    log.step("submit_audio_task", "IN", prompt_preview=prompt[:80], duration=duration)

    payload = {
        "prompt": prompt,
        "seconds_total": duration,
    }

    response = requests.post(
        f"{FAL_API_BASE}/{FAL_AUDIO_MODEL}",
        headers=get_fal_headers(),
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    request_id = data.get("request_id")
    if not request_id:
        log.step("submit_audio_task", "ERR", error="No request_id in response", response=data)
        raise RuntimeError(f"No request_id in fal.ai stable-audio response: {data}")

    task = {
        "request_id": request_id,
        "status_url": data.get("status_url"),
        "response_url": data.get("response_url"),
    }
    log.step("submit_audio_task", "OUT", request_id=request_id, status_url=task["status_url"])
    return task


# ── 2. Poll ───────────────────────────────────────────────────────────────────

def poll_audio_task(task: dict, timeout: int = 600, interval: int = 5) -> str:
    """Polls fal.ai queue until COMPLETED and returns the audio CDN URL."""
    request_id = task["request_id"]
    status_url = task["status_url"]
    response_url = task["response_url"]

    log.step("poll_audio_task", "IN", request_id=request_id)

    headers = get_fal_headers()
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(status_url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status", "UNKNOWN")
        elapsed = int(time.time() - start)
        log.step("poll_audio_task", "INFO", request_id=request_id, status=status, elapsed_s=elapsed)

        if status == "COMPLETED":
            result_resp = requests.get(response_url, headers=headers, timeout=30)
            result_resp.raise_for_status()
            result_data = result_resp.json()
            # stable-audio returns { audio_file: { url: "..." } }
            audio_url = (
                result_data.get("audio_file", {}).get("url")
                or result_data.get("audio", {}).get("url")
                or result_data.get("audio_url")
            )
            if not audio_url:
                log.step("poll_audio_task", "ERR",
                         request_id=request_id,
                         error="COMPLETED but no audio URL found",
                         result_data=result_data)
                raise RuntimeError(f"stable-audio completed but no audio URL: {result_data}")

            log.step("poll_audio_task", "OUT", request_id=request_id, audio_url=audio_url)
            return audio_url

        elif status in ("FAILED", "CANCELLED"):
            log.step("poll_audio_task", "ERR", request_id=request_id, status=status, error=data.get("error"))
            raise RuntimeError(f"fal.ai audio task {status}: {data.get('error', 'No details')}")

        time.sleep(interval)

    raise TimeoutError(f"Audio task timed out after {timeout}s. Request ID: {request_id}")


# ── 3. Download ───────────────────────────────────────────────────────────────

def download_audio(audio_url: str) -> str:
    """Downloads the generated audio and saves it to the current run directory."""
    from utils.run_context import get_run_dir
    log.step("download_audio", "IN", audio_url=audio_url)

    run_dir = get_run_dir()
    ext = ".mp3" if ".mp3" in audio_url else ".wav"  # stable-audio returns .wav
    filename = os.path.join(run_dir, f"{uuid.uuid4()}{ext}")

    r = requests.get(audio_url, stream=True, timeout=60)
    r.raise_for_status()
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    size_kb = round(os.path.getsize(filename) / 1024)
    log.step("download_audio", "OUT", filename=filename, size_kb=size_kb)
    return filename


# ── 4. Mux ────────────────────────────────────────────────────────────────────

def mux_audio_video(video_path: str, audio_path: str) -> str:
    """
    Merges audio onto the silent video using FFmpeg.
    The audio is looped/trimmed to exactly match the video duration.
    Returns the path to the new muxed MP4 (saved in the same run directory).
    """
    from utils.run_context import get_run_dir
    log.step("mux_audio_video", "IN", video=video_path, audio=audio_path)

    run_dir = get_run_dir()
    out_path = os.path.join(run_dir, f"{uuid.uuid4()}_with_audio.mp4")

    cmd = [
        FFMPEG_BIN,
        "-y",                        # overwrite without asking
        "-i", video_path,            # input: silent video
        "-i", audio_path,            # input: music track
        "-map", "0:v:0",             # use video stream from first input
        "-map", "1:a:0",             # use audio stream from second input
        "-c:v", "copy",              # copy video codec (no re-encode)
        "-c:a", "aac",               # encode audio to AAC for MP4 compatibility
        "-b:a", "192k",              # audio bitrate
        "-shortest",                 # trim to the shorter of video/audio
        "-movflags", "+faststart",   # web-optimised MP4
        out_path,
    ]

    log.step("mux_audio_video", "INFO", cmd=" ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        log.step("mux_audio_video", "ERR", stderr=result.stderr[-500:])
        raise RuntimeError(f"FFmpeg mux failed:\n{result.stderr[-500:]}")

    size_kb = round(os.path.getsize(out_path) / 1024)
    log.step("mux_audio_video", "OUT", output=out_path, size_kb=size_kb)
    return out_path


# ── 5. Orchestrator ───────────────────────────────────────────────────────────

def generate_audio_for_video(video_path: str, audio_prompt: str, duration: int = 10) -> str:
    """
    Full flow: MusicGen prompt → audio CDN → download → mux with video.
    Returns the final MP4 path (with audio embedded).
    """
    log.step("generate_audio_for_video", "IN",
             video_path=video_path,
             audio_prompt_preview=audio_prompt[:80],
             duration=duration)

    task = submit_audio_task(audio_prompt, duration=duration)
    audio_url = poll_audio_task(task)
    audio_path = download_audio(audio_url)
    final_path = mux_audio_video(video_path, audio_path)

    log.step("generate_audio_for_video", "OUT", final_path=final_path)
    return final_path
