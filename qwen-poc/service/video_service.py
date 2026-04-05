"""
video_service.py
================
Generates video for Reels by creating a sequence of images
with Ken Burns camera effects.

Flow:
  1. Split script into 5 scene descriptions
  2. Generate 5 images via Pollinations AI (free)
  3. Apply Ken Burns effect to each (~3s per scene)
  4. Concatenate all clips into final video
  5. Total: ~15s video, style-coherent

All local, no API costs.
"""

import os
import uuid
import json
import tempfile
import subprocess as sp
import requests
import urllib.parse
from utils.logger import get_logger
from utils.run_context import get_run_dir
from service.llm_service import generate_text

log = get_logger(__name__)


def _get_ffmpeg_path() -> str:
    return os.path.join(os.path.dirname(__file__), "..", "ffmpeg")


# ── Scene Generation ─────────────────────────────────────────────────────────

NUM_SCENES = 5


def _generate_scene_descriptions(voiceover_script: str, style_anchor: str = "") -> list[dict]:
    """
    Uses LLM to split the script into 5 visual scene descriptions.
    Returns list of {"image_prompt": ..., "camera": ...} dicts.
    """
    log.step("generate_scenes", "IN", script_len=len(voiceover_script))

    system_prompt = (
        "You are a storyboard artist for viral social media reels. "
        "Your job is to visualize each scene as a cinematic image."
    )

    style_note = ""
    if style_anchor:
        style_note = f"\nVisual DNA to maintain: {style_anchor}"

    instructions = f"""
Split this script into exactly {NUM_SCENES} discrete visual scenes.
Each scene should capture a different moment of the narrative.{style_note}

RULES:
- 9:16 vertical portrait composition
- Subject must be large, close, and visually dominant
- Cinematic lighting, no text/logos/watermarks in the image
- High visual density: textures, colors, detail
- Each scene must feel distinct but visually cohesive

Script:
\"\"\"
{voiceover_script}
\"\"\"

Return ONLY valid JSON (no markdown fences):
[
  {{
    "image_prompt": "Under 60 words. [subject + action], [setting + atmosphere], [camera angle + framing], [lighting quality], [color palette], [mood/texture]. Must feel native to Instagram Reels.",
    "camera": "slow zoom in, gentle camera pan"
  }}
  ... repeat {NUM_SCENES} times total
]
"""

    response = generate_text(
        prompt=instructions,
        model="deepseek-chat",
        system_prompt=system_prompt,
    )

    # Parse JSON response
    from utils.json_utils import clean_llm_json
    try:
        scenes = json.loads(clean_llm_json(response))
        if isinstance(scenes, dict):
            scenes = scenes.get("scenes", [scenes])
        scenes = [s for s in scenes if s.get("image_prompt")]
    except Exception as e:
        scenes = []
        log.step("generate_scenes", "WARN", error=str(e))

    # Ensure we always have NUM_SCENES
    if len(scenes) < NUM_SCENES:
        log.step("generate_scenes", "WARN", got=len(scenes), filling_to=NUM_SCENES)
        # Fill remaining with script segments
        remaining = NUM_SCENES - len(scenes)
        words = voiceover_script.split()
        chunk_size = max(3, len(words) // remaining)
        for i in range(remaining):
            start = i * chunk_size
            segment = " ".join(words[start:start + chunk_size])
            if not segment:
                segment = voiceover_script[:60]
            scenes.append({
                "image_prompt": f"Cinematic visual: {segment}",
                "camera": "slow zoom in" if (len(scenes) % 2 == 0) else "gentle camera pan",
            })
        scenes = scenes[:NUM_SCENES]

    log.step("generate_scenes", "OUT", num_scenes=len(scenes))
    return scenes


# ── Image Generation (Pollinations, free) ─────────────────────────────────────

_POLLINATIONS_BASE = "https://image.pollinations.ai/prompt"


def _generate_scene_image(image_prompt: str, idx: int, width: int = 720, height: int = 1280) -> str:
    """Generates a single image via Pollinations and saves locally."""
    # Use a deterministic seed per scene for consistency if re-run
    seed = hash(f"scene_{idx}_{image_prompt[:30]}") & 0xFFFFFFFF
    encoded = urllib.parse.quote(image_prompt)
    url = f"{_POLLINATIONS_BASE}/{encoded}?width={width}&height={height}&model=flux&seed={seed}&nologo=true"

    # Download
    r = requests.get(url, stream=True, timeout=180)
    r.raise_for_status()

    run_dir = get_run_dir()
    path = os.path.join(run_dir, f"scene_{idx:02d}_{uuid.uuid4().hex[:6]}.jpg")
    with open(path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    size_kb = round(os.path.getsize(path) / 1024)
    log.step("generate_scene_image", "OUT", scene=idx, path=path, size_kb=size_kb)
    return path


# ── Ken Burns Effect ─────────────────────────────────────────────────────────

def _ken_burns_effect(
    img_path: str,
    duration: int,
    width: int = 720,
    height: int = 1280,
    fps: int = 30,
    scene_idx: int = 0,
) -> str:
    """Creates a Ken Burns clip from a scene image."""
    log.step("ken_burns", "IN", scene=scene_idx, image=img_path, duration=duration)

    run_dir = get_run_dir()
    output = os.path.join(run_dir, f"clip_{scene_idx:02d}_{uuid.uuid4().hex[:6]}.mp4")
    ffmpeg = _get_ffmpeg_path()

    total_frames = duration * fps

    # Alternate zoom direction for variety
    if scene_idx % 2 == 0:
        zoom_expr = "z='min(1.4,zoom+0.0018)'"  # zoom in
        pan_y = f"y='ih/2-(ih/zoom/2)-sin(in/{total_frames}*3.14)*ih*0.06'"
    else:
        zoom_expr = "z='max(1.0,zoom-0.0012)'"  # zoom out
        pan_y = f"y='ih/2-(ih/zoom/2)+sin(in/{total_frames}*3.14)*ih*0.04'"

    pan_x = f"x='iw/2-(iw/zoom/2)+cos(in/{total_frames}*3.14)*iw*0.04'"

    filter_str = (
        f"scale={width * 1.6:.0f}:{height * 1.6:.0f},"
        f"zoompan={zoom_expr}:{pan_y}:{pan_x}:"
        f"d={total_frames}:s={width}x{height}:fps={fps}"
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

    result = sp.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        log.step("ken_burns", "ERR", scene=scene_idx, error=result.stderr[:300] if result.stderr else "Unknown")
        raise RuntimeError(f"Ken Burns scene {scene_idx} failed: {result.stderr[:300]}")

    size_kb = round(os.path.getsize(output) / 1024)
    log.step("ken_burns", "OUT", scene=scene_idx, output=output, size_kb=size_kb)
    return output


# ── Concatenation ─────────────────────────────────────────────────────────────

def _concatenate_clips(clips: list[str]) -> str:
    """Concatenates video clips using FFmpeg concat demuxer."""
    log.step("concatenate_clips", "IN", num_clips=len(clips))

    run_dir = get_run_dir()
    output = os.path.join(run_dir, f"video_{uuid.uuid4().hex[:6]}_concat.mp4")

    # Method 1: concat filter with re-encoding (safe)
    ffmpeg = _get_ffmpeg_path()

    # Build filter_complex for concat
    inputs = []
    filter_inputs = ""
    for i in range(len(clips)):
        inputs.extend(["-i", clips[i]])
        filter_inputs += f"[{i}:v]"
    filter_str = f"{filter_inputs}concat=n={len(clips)}:v=1:a=0[out]"

    cmd = [ffmpeg, "-y"] + inputs + [
        "-filter_complex", filter_str,
        "-map", "[out]",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "20",
        output,
    ]

    result = sp.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        # Fallback: use stream copy via concat demuxer
        log.step("concatenate_clips", "WARN", fallback="concat_demuxer")
        concat_file = os.path.join(run_dir, "concat_list.txt")
        with open(concat_file, "w") as f:
            for clip in clips:
                f.write(f"file '{os.path.abspath(clip)}'\n")

        cmd2 = [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", concat_file, "-c:v", "copy", output]
        result2 = sp.run(cmd2, capture_output=True, text=True, timeout=300)
        if result2.returncode != 0:
            log.step("concatenate_clips", "ERR", error=result2.stderr[:300] if result2.stderr else "Unknown")
            raise RuntimeError(f"Concat failed: {result2.stderr[:300]}")

    # Cleanup individual clips
    for clip in clips:
        try:
            os.remove(clip)
        except OSError:
            pass
    try:
        os.remove(os.path.join(run_dir, "concat_list.txt"))
    except OSError:
        pass

    size_kb = round(os.path.getsize(output) / 1024)
    log.step("concatenate_clips", "OUT", output=output, size_kb=size_kb)
    return output


# ── Orchestrator ──────────────────────────────────────────────────────────────

def generate_video(
    img_url: str,
    prompt: str,
    resolution: str = "720P",
    duration: int = 15,
    audio: bool = False,
    voiceover_script: str = None,
    style_anchor: str = "",
) -> str:
    """
    Generates a multi-scene video from AI-generated images.

    Flow:
      1. Split script into 5 scenes via LLM
      2. Generate image per scene via Pollinations
      3. Ken Burns effect per scene (duration / NUM_SCENES each)
      4. Concatenate clips into final video

    Args:
        img_url: Ignored (generates its own images).
        prompt: Fallback text prompt if script not provided.
        resolution: Video resolution (720P default).
        duration: Target total duration (15s default).
        audio: Ignored.
        voiceover_script: Script text to drive scene generation.
        style_anchor: Visual style to maintain across scenes.
    """
    scene_duration = duration // NUM_SCENES

    log.step("generate_video", "IN",
             prompt_preview=prompt[:80] if prompt else "",
             resolution=resolution,
             scenes=NUM_SCENES,
             scene_duration=scene_duration)

    width = int(resolution.lower().split("p")[0]) if resolution.lower().endswith("p") else 720
    height = int(width * 16 / 9)

    # 1. Generate scene descriptions from script
    script_text = voiceover_script or prompt or ""
    scenes = _generate_scene_descriptions(script_text, style_anchor)

    # 2. Generate images + Ken Burns clips for each scene
    clips = []
    for i, scene in enumerate(scenes[:NUM_SCENES]):
        img_path = _generate_scene_image(
            scene["image_prompt"], idx=i,
            width=width, height=height,
        )
        clip = _ken_burns_effect(
            img_path, duration=scene_duration,
            width=width, height=height,
            scene_idx=i,
        )
        clips.append(clip)
        # Clean up the scene image
        try:
            os.remove(img_path)
        except OSError:
            pass

    # 3. Concatenate all clips
    if len(clips) == 1:
        result = clips[0]
    else:
        result = _concatenate_clips(clips)

    log.step("generate_video", "OUT", local_path=result, num_clips=len(clips))
    return result
