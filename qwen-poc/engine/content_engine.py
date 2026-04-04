from service.llm_service import generate_text
from service.image_service import generate_image_urls
from service.video_service import generate_video
from service.audio_service import generate_audio_for_video
from service.subtitle_service import add_subtitles_to_video
from models.request_models import GenerateImageRequest
from utils.logger import get_logger

log = get_logger(__name__)


def expand_to_prompt(topic: str, strategy: dict) -> dict:
    """
    Uses DeepSeek to produce:
      - image_prompt   : rich cinematic prompt for the image generator
      - style_anchor   : concise visual DNA (palette, lighting, mood) that
                         must be injected into the video motion prompt to
                         keep image ↔ video visually coherent

    Returns a dict with keys: image_prompt, style_anchor
    """
    log.step("expand_to_prompt", "IN", topic=topic)

    emotion = strategy.get("emotion", "energetic")
    hook = strategy.get("hook", "")

    system_prompt = (
        "You are an elite creative director specialising in AI prompt engineering "
        "for visual generative models (image + video). "
        "Your outputs must be richly descriptive, visually specific and cinematically coherent."
    )

    instructions = f"""
You are creating the visual identity for a 10-second Instagram Reel.

Topic       : '{topic}'
Emotion     : '{emotion}'
Hook moment : '{hook[:120]}'

Produce TWO outputs in this exact JSON format (no markdown, no code blocks):
{{
  "image_prompt": "A single cinematic scene described in under 55 words. Include: subject, action, setting, camera angle, lighting quality, color palette, mood. This is the OPENING FRAME of the reel.",
  "style_anchor": "Under 20 words. Distil the visual DNA of the image into reusable descriptors: color palette, lighting style, mood, and texture. Example: 'warm golden-hour glow, teal and amber palette, shallow depth of field, energetic'"
}}
"""

    response = generate_text(prompt=instructions, model="deepseek-chat", system_prompt=system_prompt)

    import json
    from utils.json_utils import clean_llm_json
    try:
        result = json.loads(clean_llm_json(response))
        image_prompt = result.get("image_prompt", "").strip()
        style_anchor = result.get("style_anchor", "").strip()
    except Exception:
        # Fallback: treat whole response as image_prompt
        image_prompt = response.strip()
        style_anchor = f"{emotion} atmosphere, cinematic lighting, vibrant colors"

    log.step("expand_to_prompt", "OUT",
             topic=topic,
             image_prompt=image_prompt,
             style_anchor=style_anchor)
    return {"image_prompt": image_prompt, "style_anchor": style_anchor}


def build_coherent_motion_prompt(strategy: dict, style_anchor: str) -> str:
    """
    Combines the strategy motion_prompt with the image style_anchor so that
    the video model replicates the same visual language as the source image.
    """
    base_motion = strategy.get(
        "motion_prompt",
        "gentle dynamic motion, cinematic camera pan, lively movement",
    )
    return f"{base_motion}. Maintain visual style: {style_anchor}"


def build_audio_prompt(topic: str, strategy: dict) -> str:
    """
    Builds a stable-audio prompt that matches the reel's mood and energy.
    """
    emotion = strategy.get("emotion", "energetic")
    narrative = strategy.get("narrative", "")
    base = f"concert music, {emotion.lower()}, live performance energy, crowd atmosphere"
    if narrative:
        base += f", {narrative[:60]}"
    return base


def run_content_engine(selected_topic: str, strategy: dict) -> dict:
    """
    Full pipeline:
      1. Expand topic → image_prompt + style_anchor
      2. Generate base image (Flux Dev)
      3. Generate silent video (Wan i2v) — motion coherent with image style
      4. Generate concert audio (stable-audio) + mux onto video
      5. Burn subtitles (hook / on_screen_text / cta) onto final video
    """
    from utils.run_context import get_run_dir

    log.step("run_content_engine", "IN",
             topic=selected_topic,
             motion_prompt=strategy.get("motion_prompt"),
             emotion=strategy.get("emotion"))

    # ── 1. Visual prompt expansion ────────────────────────────────────────────
    log.step("run_content_engine", "INFO", step="1/5 - Expanding topic → image prompt + style anchor")
    prompts = expand_to_prompt(selected_topic, strategy)
    image_prompt = prompts["image_prompt"]
    style_anchor = prompts["style_anchor"]

    # ── 2. Image generation ───────────────────────────────────────────────────
    log.step("run_content_engine", "INFO", step="2/5 - Generating base image", prompt=image_prompt)
    img_req = GenerateImageRequest(prompt=image_prompt, images=[], n=1)
    image_urls = generate_image_urls(img_req)

    if not image_urls:
        log.step("run_content_engine", "ERR", step="2/5", error="Image generation returned no URLs")
        raise ValueError("Image generation failed to return a URL.")

    base_image_url = image_urls[0]
    log.step("run_content_engine", "INFO", step="2/5 - Image ready", image_url=base_image_url)

    # ── 3. Silent video — coherent with image style ───────────────────────────
    motion_prompt = build_coherent_motion_prompt(strategy, style_anchor)
    log.step("run_content_engine", "INFO",
             step="3/5 - Generating silent video (style-coherent)",
             motion_prompt=motion_prompt)

    silent_video_path = generate_video(
        img_url=base_image_url,
        prompt=motion_prompt,
        resolution="720P",
        duration=10,
        audio=False,
    )

    # ── 4. Concert audio + mux ────────────────────────────────────────────────
    audio_prompt = build_audio_prompt(selected_topic, strategy)
    log.step("run_content_engine", "INFO",
             step="4/5 - Generating concert audio & muxing",
             audio_prompt=audio_prompt)

    video_with_audio = generate_audio_for_video(
        video_path=silent_video_path,
        audio_prompt=audio_prompt,
        duration=10,
    )

    # ── 5. Burn subtitles ─────────────────────────────────────────────────────
    hook = strategy.get("hook", "")
    on_screen_text = strategy.get("on_screen_text") or ""
    cta = strategy.get("cta", "")

    log.step("run_content_engine", "INFO",
             step="5/5 - Burning subtitles",
             hook=hook[:60],
             on_screen_text=on_screen_text,
             cta=cta)

    final_video_path = add_subtitles_to_video(
        video_path=video_with_audio,
        hook=hook,
        on_screen_text=on_screen_text,
        cta=cta,
        run_dir=get_run_dir(),
    )

    result = {
        "topic": selected_topic,
        "base_prompt": image_prompt,
        "style_anchor": style_anchor,
        "image_url": base_image_url,
        "silent_video_path": silent_video_path,
        "video_with_audio_path": video_with_audio,
        "final_video_path": final_video_path,
        "audio_prompt": audio_prompt,
        "motion_prompt": motion_prompt,
        "narrative": strategy.get("narrative"),
        "hook": hook,
        "emotion": strategy.get("emotion"),
        "caption": strategy.get("caption"),
        "hashtags": strategy.get("hashtags", []),
        "cta": cta,
        "on_screen_text": on_screen_text,
    }

    log.step("run_content_engine", "OUT",
             topic=selected_topic,
             image_url=base_image_url,
             style_anchor=style_anchor,
             silent_video=silent_video_path,
             video_with_audio=video_with_audio,
             final_video=final_video_path,
             caption_preview=str(strategy.get("caption", ""))[:80])
    return result
