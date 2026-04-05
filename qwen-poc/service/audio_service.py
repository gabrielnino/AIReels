"""
audio_service.py
================
Mixes voiceover + background music tracks onto a silent video using FFmpeg.
"""

import os
import subprocess
import uuid
from utils.logger import get_logger

log = get_logger(__name__)

_PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
FFMPEG_BIN = os.path.join(_PROJECT_ROOT, "ffmpeg")


def mix_voice_and_music(
    video_path: str,
    voiceover_path: str,
    music_path: str,
) -> str:
    """
    Mixes a voiceover track over background music, then muxes both onto the video.

    Default volumes: voice at 80% (0.8x), music at 8% (0.08x).
    """
    from utils.run_context import get_run_dir

    voice_volume = 0.8
    music_volume = 0.08

    log.step("mix_voice_and_music", "IN",
             video=video_path,
             voiceover=voiceover_path,
             music=music_path,
             music_percent=8,
             voice_percent=80,
             music_volume=music_volume,
             voice_volume=voice_volume)

    run_dir = get_run_dir()
    out_path = os.path.join(run_dir, f"{uuid.uuid4()}_mixed.mp4")

    audio_filter = (
        f"[1:a]volume={voice_volume}[voice_boost];"
        f"[2:a]volume={music_volume}[music_low];"
        f"[voice_boost][music_low]amix=inputs=2:duration=shortest:dropout_transition=0[mixed]"
    )

    cmd = [
        FFMPEG_BIN,
        "-y",
        "-i", video_path,
        "-i", voiceover_path,
        "-i", music_path,
        "-filter_complex", audio_filter,
        "-map", "0:v:0",
        "-map", "[mixed]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        out_path,
    ]

    log.step("mix_voice_and_music", "INFO", cmd=" ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        log.step("mix_voice_and_music", "ERR", stderr=result.stderr[-600:])
        raise RuntimeError(f"FFmpeg mix_voice_and_music failed:\n{result.stderr[-600:]}")

    size_kb = round(os.path.getsize(out_path) / 1024)
    log.step("mix_voice_and_music", "OUT", output=out_path, size_kb=size_kb)
    return out_path
