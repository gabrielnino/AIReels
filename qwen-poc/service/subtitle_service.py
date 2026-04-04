"""
subtitle_service.py
===================
Burns native-looking Instagram Reel text overlays using FFmpeg + libass (ASS format).

Layout (timed for a 10-second reel):
  0:00 – 0:03  →  hook_text   TOP-CENTRE, large bold white — scroll-stopper
  0:03 – 0:07  →  on_screen   CENTRE, large bold with dark background — main message
  0:07 – 0:10  →  cta         BOTTOM-CENTRE, white — call to action

Uses ASS subtitle format rendered with the 'ass' filter (libass), which supports
per-event positioning, font size, color, and bold — all available in the
bundled static FFmpeg binary.
"""

import os
import subprocess
import uuid
from utils.logger import get_logger

log = get_logger(__name__)

_PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
FFMPEG_BIN = os.path.join(_PROJECT_ROOT, "ffmpeg")

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
    return ""


def _safe(text: str) -> str:
    """Sanitise text for ASS format — escapes or removes problematic characters."""
    if not text:
        return ""
    return (
        text.replace("\\", "")
            .replace("{", "")
            .replace("}", "")
            .replace("\n", " ")
            .replace("\r", "")
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

    log.step("write_ass", "OUT", ass_path=ass_path)
    return ass_path


def burn_text_overlays(
    video_path: str,
    hook_text: str,
    on_screen_text: str,
    cta: str,
    run_dir: str,
) -> str:
    """
    Burns reel-style text overlays using FFmpeg's 'ass' filter (libass).
    Returns path to the final MP4 with text baked in.
    """
    log.step("burn_text_overlays", "IN",
             video=video_path,
             hook_text=hook_text[:60] if hook_text else "",
             on_screen_text=on_screen_text,
             cta=cta)

    # Resolve font name for ASS style header
    font_path = _find_font()
    font_name = "DejaVu Sans"
    if font_path:
        # Extract font family name from filename heuristic
        base = os.path.basename(font_path).replace("-Bold.ttf", "").replace(".ttf", "")
        font_name = base.replace("-", " ")

    ass_path = write_ass(hook_text, on_screen_text, cta, run_dir, font_name=font_name)
    out_path = os.path.join(run_dir, f"{uuid.uuid4()}_subtitled.mp4")

    # Escape path for FFmpeg filter argument (colons must be escaped on Linux too
    # when the path is inside a filter value)
    ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")

    # Build fontsdir arg if we have a font file
    fontsdir_arg = f":fontsdir='{os.path.dirname(font_path)}'" if font_path else ""

    vf = f"ass='{ass_escaped}'{fontsdir_arg}"

    cmd = [
        FFMPEG_BIN,
        "-y",
        "-i", video_path,
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "20",
        "-c:a", "copy",
        "-movflags", "+faststart",
        out_path,
    ]

    log.step("burn_text_overlays", "INFO", cmd=" ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        log.step("burn_text_overlays", "ERR", stderr=result.stderr[-800:])
        raise RuntimeError(f"FFmpeg ass filter failed:\n{result.stderr[-800:]}")

    size_kb = round(os.path.getsize(out_path) / 1024)
    log.step("burn_text_overlays", "OUT", output=out_path, size_kb=size_kb)
    return out_path


def add_subtitles_to_video(
    video_path: str,
    hook: str,
    on_screen_text: str,
    cta: str,
    run_dir: str,
    hook_text: str = "",
) -> str:
    """
    Main entry point. Burns reel-style text overlays onto the video.

    Args:
        hook_text  : Bold text for the first 2.8s (scroll-stopper). Falls back
                     to a short truncation of `hook` if not provided.
    """
    log.step("add_subtitles_to_video", "IN",
             hook_text=hook_text[:60] if hook_text else hook[:60],
             on_screen_text=on_screen_text,
             cta=cta)

    display_hook = hook_text or " ".join(hook.split()[:8]) if hook else ""

    final_path = burn_text_overlays(
        video_path=video_path,
        hook_text=display_hook,
        on_screen_text=on_screen_text,
        cta=cta,
        run_dir=run_dir,
    )

    log.step("add_subtitles_to_video", "OUT", final_path=final_path)
    return final_path
