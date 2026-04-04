"""
endcard_service.py
==================
Appends a clean end-card (3s) to the video with a call-to-action:
  - Black background matching the video's resolution
  - "Síguenos en @usuario"
  - "tudominio.com"

Since the bundled FFmpeg lacks drawtext, we generate text as an ASS subtitle
burned onto a black frame, then concatenate via the concat demuxer.
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


def _ass_color(r: int, g: int, b: int, a: int = 0) -> str:
    """Convert RGBA to ASS &HAABBGGRR hex format."""
    return f"&H{a:02X}{b:02X}{g:02X}{r:02X}"


def _endcard_ass(
    line1: str,
    line2: str,
    run_dir: str,
    font_name: str = "DejaVu Sans",
    play_res_x: int = 720,
    play_res_y: int = 1280,
) -> str:
    """Generates an ASS subtitle file for the end-card."""
    ass_path = os.path.join(run_dir, f"{uuid.uuid4()}_endcard.ass")

    white = _ass_color(255, 255, 255)
    yellow = "&H0000D4FF"  # yellow BBGGRR with alpha
    black = _ass_color(0, 0, 0)
    shadow = _ass_color(0, 0, 0, 140)

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {play_res_x}
PlayResY: {play_res_y}
WrapStyle: 0

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: FollowLine,{font_name},{play_res_y//20},{white},{white},{black},{shadow},-1,0,0,0,100,100,0,0,1,3,2,5,60,60,{int(play_res_y * 0.4)},1
Style: UrlLine,{font_name},{play_res_y//25},{yellow},{yellow},{black},{shadow},-1,0,0,0,100,100,0,0,1,2,1,5,60,60,{int(play_res_y * 0.55)},1

[Events]
"""
    events = []
    if line1:
        events.append(f"Dialogue: 0,0:00:00.00,0:00:03.00,FollowLine,,0,0,0,,{line1}")
    if line2:
        events.append(f"Dialogue: 0,0:00:00.00,0:00:03.00,UrlLine,,0,0,0,,{line2}")

    content = header
    content += "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n"
    content += "\n".join(events) + "\n"

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(content)

    log.step("_endcard_ass", "OUT", ass_path=ass_path, line1=line1[:60], line2=line2[:60])
    return ass_path


def add_endcard(
    video_path: str,
    cta_follow: str = "",
    cta_url: str = "",
    duration: float = 3.0,
    run_dir: str = None,
) -> str:
    """
    Appends a clean end-card to the video.

    Two-step process:
      1. Generate black frame + burn ASS text → endcard_clip.mp4
      2. Concat original + endcard via FFmpeg concat demuxer

    Args:
        video_path  : Path to video (with audio, subtitles already applied).
        cta_follow  : Line 1 text (e.g. "Síganos en @usuario").
        cta_url     : Line 2 text (e.g. "tudominio.com").
        duration    : End-card duration in seconds.
        run_dir     : Output directory; defaults to same dir as video.

    Returns:
        Path to the new MP4 with end-card appended.
    """
    if run_dir is None:
        run_dir = os.path.dirname(video_path)

    log.step("add_endcard", "IN",
             video=video_path,
             cta_follow=cta_follow[:60] if cta_follow else "",
             cta_url=cta_url[:60] if cta_url else "",
             duration=duration)

    font_path = _find_font()
    font_name = "DejaVu Sans"
    if font_path:
        base = os.path.basename(font_path).replace("-Bold.ttf", "").replace("-Bold", "").replace(".ttf", "")
        font_name = base.replace("-", " ")

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

    line1 = cta_follow or "Síguenos para más"
    line2 = cta_url or ""

    # Step 1: Create end-card clip (black frame + burned text)
    ass_path = _endcard_ass(
        line1, line2, run_dir,
        font_name=font_name,
        play_res_x=w,
        play_res_y=h,
    )
    ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")
    fontsdir_arg = f":fontsdir='{os.path.dirname(font_path)}'" if font_path else ""
    vf = f"ass='{ass_escaped}'{fontsdir_arg}"

    endcard_clip = os.path.join(run_dir, f"{uuid.uuid4()}_endclip.mp4")

    # Create 3s black video with text burned in
    cmd1 = [
        FFMPEG_BIN,
        "-y",
        "-f", "lavfi", "-i", f"color=c=black:s={w}x{h}:d={duration}:r=30",
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-an",   # no audio
        endcard_clip,
    ]

    log.step("add_endcard", "INFO", step="1/2 - generating end-card clip", cmd1=" ".join(cmd1))
    result = subprocess.run(cmd1, capture_output=True, text=True)
    if result.returncode != 0:
        log.step("add_endcard", "ERR", stderr=result.stderr[-800:])
        raise RuntimeError(f"FFmpeg endcard clip failed:\n{result.stderr[-800:]}")

    # Step 2: Concat original + end-card clip
    # Use concat demuxer with a file list
    concat_list = os.path.join(run_dir, f"{uuid.uuid4()}_concat_list.txt")
    with open(concat_list, "w") as f:
        # Both clips are h264 + (optionally) audio; we use concat demuxer directly
        abs_video = os.path.abspath(video_path)
        abs_endcard = os.path.abspath(endcard_clip)
        f.write(f"file '{abs_video}'\n")
        f.write(f"file '{abs_endcard}'\n")

    out_path = os.path.join(run_dir, f"{uuid.uuid4()}_endcard.mp4")

    cmd2 = [
        FFMPEG_BIN,
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        "-movflags", "+faststart",
        out_path,
    ]

    log.step("add_endcard", "INFO", step="2/2 - concatenating", cmd2=" ".join(cmd2))
    result = subprocess.run(cmd2, capture_output=True, text=True)
    if result.returncode != 0:
        log.step("add_endcard", "ERR", stderr=result.stderr[-800:])
        raise RuntimeError(f"FFmpeg concat failed:\n{result.stderr[-800:]}")

    size_kb = round(os.path.getsize(out_path) / 1024)
    log.step("add_endcard", "OUT", output=out_path, size_kb=size_kb)
    return out_path
