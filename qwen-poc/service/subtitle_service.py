"""
subtitle_service.py
===================
Generates a 3-line SRT subtitle file from the reel strategy and burns it
into the video using FFmpeg drawtext.

Layout (timed for a 10-second reel):
  0:00 – 0:03  →  hook  (scroll-stopper, top third of screen)
  0:03 – 0:07  →  on_screen_text  (main message, centre)
  0:07 – 0:10  →  cta   (call to action, bottom third)

The text is styled with a bold white font + semi-transparent black drop
shadow so it's legible on any background.
"""

import os
import subprocess
import uuid
from utils.logger import get_logger

log = get_logger(__name__)

_PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
FFMPEG_BIN = os.path.join(_PROJECT_ROOT, "ffmpeg")

# Font bundled with the project (fallback to system sans-serif if missing)
_FONT_CANDIDATES = [
    os.path.join(_PROJECT_ROOT, "assets", "fonts", "Roboto-Bold.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]


def _find_font() -> str:
    for path in _FONT_CANDIDATES:
        if os.path.isfile(path):
            return path
    return ""  # FFmpeg will use its built-in default font


def _clean_text(text: str) -> str:
    """Strips quotes, newlines and special chars that break FFmpeg drawtext."""
    if not text:
        return ""
    return (
        text.replace("'", "")
            .replace('"', "")
            .replace("\n", " ")
            .replace(":", " -")
            .replace("\\", "")
            .replace("%", "pct")
            .strip()
    )


def write_srt(hook: str, on_screen_text: str, cta: str, run_dir: str) -> str:
    """
    Writes a 3-entry SRT file to run_dir and returns its path.

    Timings are fixed for a 10-second reel:
      subtitle 1  00:00:00,000 → 00:00:03,000   hook
      subtitle 2  00:00:03,000 → 00:00:07,000   on_screen_text
      subtitle 3  00:00:07,000 → 00:00:10,000   cta
    """
    srt_path = os.path.join(run_dir, f"{uuid.uuid4()}.srt")

    lines = [
        "1",
        "00:00:00,000 --> 00:00:03,000",
        _clean_text(hook)[:80] or "Watch this",
        "",
        "2",
        "00:00:03,000 --> 00:00:07,000",
        _clean_text(on_screen_text)[:60] or "",
        "",
        "3",
        "00:00:07,000 --> 00:00:10,000",
        _clean_text(cta)[:50] or "",
        "",
    ]

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    log.step("write_srt", "OUT", srt_path=srt_path)
    return srt_path


def burn_subtitles(video_path: str, srt_path: str, run_dir: str) -> str:
    """
    Burns the SRT subtitles into the video using FFmpeg subtitles filter.
    Returns path to the new MP4 with baked-in subtitles.
    """
    log.step("burn_subtitles", "IN", video=video_path, srt=srt_path)

    out_path = os.path.join(run_dir, f"{uuid.uuid4()}_subtitled.mp4")
    font = _find_font()

    # Build subtitles filter string
    # force_style controls font size, color, bold, shadow
    style = (
        "Fontsize=22,"
        "PrimaryColour=&H00FFFFFF,"   # white text
        "OutlineColour=&H80000000,"   # semi-transparent black outline
        "BorderStyle=3,"              # opaque box behind text
        "BackColour=&H60000000,"      # semi-transparent dark background
        "Bold=1,"
        "Alignment=2"                 # centre-bottom (SRT default)
    )

    srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")
    if font:
        subtitle_filter = f"subtitles='{srt_escaped}':force_style='{style}':fontsdir='{os.path.dirname(font)}'"
    else:
        subtitle_filter = f"subtitles='{srt_escaped}':force_style='{style}'"

    cmd = [
        FFMPEG_BIN,
        "-y",
        "-i", video_path,
        "-vf", subtitle_filter,
        "-c:v", "libx264",        # re-encode video to bake in subtitles
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "copy",           # keep existing audio stream untouched
        "-movflags", "+faststart",
        out_path,
    ]

    log.step("burn_subtitles", "INFO", cmd=" ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        log.step("burn_subtitles", "ERR", stderr=result.stderr[-600:])
        raise RuntimeError(f"FFmpeg subtitle burn failed:\n{result.stderr[-600:]}")

    size_kb = round(os.path.getsize(out_path) / 1024)
    log.step("burn_subtitles", "OUT", output=out_path, size_kb=size_kb)
    return out_path


def add_subtitles_to_video(
    video_path: str,
    hook: str,
    on_screen_text: str,
    cta: str,
    run_dir: str,
) -> str:
    """
    Full flow: write SRT → burn into video.
    Returns path to the final subtitled MP4.
    """
    log.step("add_subtitles_to_video", "IN",
             hook=hook[:60],
             on_screen_text=on_screen_text,
             cta=cta)

    srt_path = write_srt(hook, on_screen_text, cta, run_dir)
    final_path = burn_subtitles(video_path, srt_path, run_dir)

    log.step("add_subtitles_to_video", "OUT", final_path=final_path)
    return final_path
