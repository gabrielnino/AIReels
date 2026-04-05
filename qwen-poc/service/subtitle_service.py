"""
subtitle_service.py
===================
Burns word-by-word subtitles (Alex Hormozi style) onto 9:16 reel videos using FFmpeg + libass (ASS format).

Flow:
  1. Generate ASS subtitle file with per-word timing
  2. Burn subtitles onto video with FFmpeg's ass filter
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
    """Sanitise text for ASS format - escapes or removes problematic characters."""
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


def _format_time(seconds: float) -> str:
    """Convert seconds to ASS time format H:MM:SS.cc"""
    total_secs = int(seconds)
    hours = total_secs // 3600
    mins = (total_secs % 3600) // 60
    secs = total_secs % 60
    centisecs = int((seconds - int(seconds)) * 100)
    return f"{hours}:{mins:02d}:{secs:02d}.{centisecs:02d}"


def _word_by_word_ass_path(
    transcript: str,
    run_dir: str,
    duration: float = 10.0,
    font_name: str = "DejaVu Sans",
) -> str:
    """
    Generates an ASS subtitle file with word-by-word timing (Alex Hormozi style).

    Each word is rendered individually, centered, with keywords in yellow
    for visual emphasis. Timing is auto-generated from transcript + duration.
    """
    ass_path = os.path.join(run_dir, f"{uuid.uuid4()}_wbw.ass")

    white = _ass_color(255, 255, 255)
    black = _ass_color(0, 0, 0)
    shadow = _ass_color(0, 0, 0, 180)

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 960
PlayResY: 960
WrapStyle: 0

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: WordBold,{font_name},64,{white},{white},{black},{shadow},-1,0,0,0,100,100,0,0,1,3,2,5,50,50,380,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""

    words = transcript.split()
    if not words:
        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(header + "\n")
        return ass_path

    word_duration = duration / len(words)
    key_words = {
        "descubre", "gratuito", "gratis", "nuevo", "ahora", "especial",
        "secreto", "increible", "unico", "mejor", "top", "como", "que",
        "tutorial", "guia", "link", "enlace", "visita", "sigue",
        "suscribete", "exclusive", "free", "limited",
        "must", "need", "essential", "power", "ultimate", "secret",
        "naci", "presion", "corazon", "concreto", "dimension",
        "ritmo", "vibracion", "energia", "revolucion", "destino",
        "vision", "conexion", "calle", "noche", "fuego",
    }

    events = []
    current_time = 0.0
    for word in words:
        start_time = current_time
        end_time = min(current_time + word_duration, duration)

        clean_word = _safe(word)
        is_keyword = clean_word.lower().rstrip(".,!?;:") in key_words

        # Inline color override: yellow for keywords, white for rest
        color_hex = "00D4FF" if is_keyword else "FFFFFF"  # BBGGRR without &H prefix
        events.append(
            f"Dialogue: 0,{_format_time(start_time)},{_format_time(end_time)},WordBold,,0,0,0,,"
            f"{{\\c&H{color_hex}&}}{clean_word}"
        )

        current_time = end_time + 0.03

    content = header + "\n".join(events) + "\n"

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(content)

    log.step("_word_by_word_ass_path", "OUT", ass_path=ass_path, words=len(words))
    return ass_path


def add_word_by_word_subtitles(
    video_path: str,
    transcript: str,
    run_dir: str,
    duration: float = None,
) -> str:
    """
    Burns word-by-word subtitles (Alex Hormozi style) onto the video.

    Each word appears centered, large, and bold. Keywords are highlighted
    in yellow. Timing is calculated automatically from the transcript
    and video duration.

    Args:
        video_path  : Path to the video (with audio).
        transcript  : Full text that was spoken / the voiceover script.
        run_dir     : Output directory.
        duration    : Video duration in seconds. If None, auto-detected via ffprobe.

    Returns:
        Path to the subtitled MP4.
    """
    log.step("add_word_by_word_subtitles", "IN",
             video=video_path,
             transcript_preview=transcript[:60] if transcript else "",
             duration=duration)

    if not transcript or not transcript.strip():
        log.step("add_word_by_word_subtitles", "ERR", error="Empty transcript")
        return video_path

    # Auto-detect duration if not provided
    if duration is None:
        cmd = [
            FFMPEG_BIN, "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        try:
            duration = float(result.stdout.strip())
        except (ValueError, IndexError):
            duration = 10.0  # fallback
            log.step("add_word_by_word_subtitles", "WARN",
                     message="Could not detect video duration, using 10s default")

    # Resolve font
    font_path = _find_font()
    font_name = "DejaVu Sans"
    if font_path:
        base = os.path.basename(font_path).replace("-Bold", "").replace("-Regular", "").replace(".ttf", "")
        font_name = base.replace("-", " ")

    # Generate ASS file
    ass_path = _word_by_word_ass_path(transcript, run_dir, duration=duration, font_name=font_name)
    out_path = os.path.join(run_dir, f"{uuid.uuid4()}_wbw_subtitled.mp4")

    # Escape path for FFmpeg filter
    ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")
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

    log.step("add_word_by_word_subtitles", "INFO", cmd=" ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        log.step("add_word_by_word_subtitles", "ERR", stderr=result.stderr[-800:])
        raise RuntimeError(f"FFmpeg word-by-word subs failed:\n{result.stderr[-800:]}")

    size_kb = round(os.path.getsize(out_path) / 1024)
    log.step("add_word_by_word_subtitles", "OUT", output=out_path, size_kb=size_kb)
    return out_path


