"""
endcard_service.py
==================
Appends a branded end-card (3s) to the video using a pre-designed image.

Flow:
  1. Probe video dimensions
  2. Scale endcard image to match
  3. Create silent 3s video clip from image
  4. Concat original + end-card with re-encoding
"""

import os
import subprocess
import uuid
from utils.logger import get_logger

log = get_logger(__name__)

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FFMPEG_BIN = os.path.join(_PROJECT_ROOT, "ffmpeg")
ENDCARD_IMAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resources", "endvideo.jpg")


def add_endcard(
    video_path: str,
    cta_follow: str = "",
    cta_url: str = "",
    duration: float = 3.0,
    run_dir: str = None,
) -> str:
    """
    Appends a branded end-card to the video using a pre-designed JPEG image.

    Args:
        video_path  : Path to video (with audio, subtitles already applied).
        cta_follow  : Ignored (CTA is part of the image).
        cta_url     : Ignored (CTA is part of the image).
        duration    : End-card duration in seconds.
        run_dir     : Output directory; defaults to same dir as video.

    Returns:
        Path to the new MP4 with end-card appended.
    """
    if run_dir is None:
        run_dir = os.path.dirname(video_path)

    log.step("add_endcard", "IN",
             video=video_path,
             duration=duration,
             endcard_image=ENDCARD_IMAGE)

    if not os.path.isfile(ENDCARD_IMAGE):
        log.step("add_endcard", "ERR", message="Endcard image not found", path=ENDCARD_IMAGE)
        return video_path

    # Probe video dimensions
    probe_cmd = [
        FFMPEG_BIN, "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=s=x:p=0",
        video_path,
    ]
    result = subprocess.run(probe_cmd, capture_output=True, text=True)
    if result.returncode == 0 and "x" in result.stdout:
        w, h = result.stdout.strip().split("x")
        w, h = int(w), int(h)
    else:
        w, h = 720, 1280

    # Step 1: Scale image to match video, generate silent video clip
    endcard_clip = os.path.join(run_dir, f"{uuid.uuid4()}_endclip.mp4")

    cmd1 = [
        FFMPEG_BIN,
        "-y",
        "-loop", "1",
        "-i", ENDCARD_IMAGE,
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-vf", f"scale={w}:{h}",
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        endcard_clip,
    ]

    log.step("add_endcard", "INFO", step="1/2 - generating end-card clip from image", target_size=f"{w}x{h}")
    result = subprocess.run(cmd1, capture_output=True, text=True)
    if result.returncode != 0:
        log.step("add_endcard", "ERR", stderr=result.stderr[-800:])
        raise RuntimeError(f"FFmpeg endcard clip failed:\n{result.stderr[-800:]}")

    # Step 2: Concat original + end-card (re-encode to avoid resolution mismatch)
    out_path = os.path.join(run_dir, f"{uuid.uuid4()}_endcard.mp4")

    cmd2 = [
        FFMPEG_BIN,
        "-y",
        "-i", video_path,
        "-i", endcard_clip,
        "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[outv];[0:a][1:a]concat=n=2:v=0:a=1[outa]",
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-preset", "fast",
        "-crf", "20",
        "-movflags", "+faststart",
        out_path,
    ]

    log.step("add_endcard", "INFO", step="2/2 - concatenating")
    result = subprocess.run(cmd2, capture_output=True, text=True)
    if result.returncode != 0:
        log.step("add_endcard", "ERR", stderr=result.stderr[-800:])
        raise RuntimeError(f"FFmpeg concat failed:\n{result.stderr[-800:]}")

    # Cleanup intermediate clip
    try:
        os.remove(endcard_clip)
    except OSError:
        pass

    size_kb = round(os.path.getsize(out_path) / 1024)
    log.step("add_endcard", "OUT", output=out_path, size_kb=size_kb)
    return out_path
