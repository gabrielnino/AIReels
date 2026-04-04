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


def _ass_color(r: int, g: int, b: int, a: int = 0) -> str:
    """Convert RGBA to ASS &HAABBGGRR hex color format."""
    return f"&H{a:02X}{b:02X}{g:02X}{r:02X}"


def write_ass(
    hook_text: str,
    on_screen_text: str,
    cta: str,
    run_dir: str,
    font_name: str = "DejaVu Sans",
) -> str:
    """
    Writes a native ASS subtitle file with three timed text layers.

    ASS format supports per-event positioning via \\an (alignment) and
    \\pos(x,y) override tags — this gives us full control of where each
    text block appears.

    Zones (for a 960x960 or 720x1280 frame):
      hook_text  → \an8 (top-centre), 0s–2.8s, fontsize 56, white bold
      on_screen  → \an5 (middle-centre), 2.8s–7.0s, fontsize 50, white bold + dark box
      cta        → \an2 (bottom-centre), 7.0s–10.0s, fontsize 42, white bold
    """
    ass_path = os.path.join(run_dir, f"{uuid.uuid4()}.ass")

    white = _ass_color(255, 255, 255)
    black = _ass_color(0, 0, 0)
    dark_bg = _ass_color(0, 0, 0, 100)   # semi-transparent black box

    # ASS header — define three named styles
    header = f"""\
[Script Info]
ScriptType: v4.00+
PlayResX: 960
PlayResY: 960
WrapStyle: 0

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Hook,{font_name},56,{white},{white},{black},{dark_bg},-1,0,0,0,100,100,0,0,1,4,2,8,40,40,60,1
Style: OnScreen,{font_name},50,{white},{white},{black},{dark_bg},-1,0,0,0,100,100,0,0,3,3,0,5,40,40,40,1
Style: CTA,{font_name},42,{white},{white},{black},{dark_bg},-1,0,0,0,100,100,0,0,1,3,1,2,40,40,60,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""

    events = []

    # Dialogue: hook text — top-centre (\an8 already set by Style Alignment=8)
    if hook_text:
        h = _safe(hook_text)
        events.append(f"Dialogue: 0,0:00:00.00,0:00:02.80,Hook,,0,0,0,,{h}")

    # Dialogue: on-screen — middle-centre (Alignment=5)
    if on_screen_text:
        m = _safe(on_screen_text)
        events.append(f"Dialogue: 0,0:00:02.80,0:00:07.00,OnScreen,,0,0,0,,{m}")

    # Dialogue: CTA — bottom-centre (Alignment=2)
    if cta:
        c = _safe(cta)
        events.append(f"Dialogue: 0,0:00:07.00,0:00:10.00,CTA,,0,0,0,,{c}")

    content = header + "\n".join(events) + "\n"

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(content)

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
