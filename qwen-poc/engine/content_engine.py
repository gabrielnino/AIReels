import os
import re
import shutil

import os
import re
import shutil

from service.llm_service import generate_text
from service.image_service import generate_image_urls
from service.video_service import generate_video
from service.audio_service import generate_audio_for_video, mix_voice_and_music
from service.voiceover_service import generate_voiceover
from service.audio_service import generate_audio_for_video, mix_voice_and_music
from service.voiceover_service import generate_voiceover
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
You are crafting the OPENING FRAME of a viral Instagram Reel (9:16 vertical format).
This image is what the viewer sees in the first split-second — it must stop the scroll.
You are crafting the OPENING FRAME of a viral Instagram Reel (9:16 vertical format).
This image is what the viewer sees in the first split-second — it must stop the scroll.

Topic       : '{topic}'
Emotion     : '{emotion}'
Hook moment : '{hook[:120]}'

CRITICAL RULES for the image prompt:
- Compose for VERTICAL 9:16 frame (portrait, not landscape)
- The subject must be large, close, and visually DOMINANT — no wide empty scenes
- Use tension, contrast, or unexpected detail that creates curiosity
- Real-world lighting (golden hour, neon at night, dramatic window light) — no studio sterility
- The image should feel like a screenshot from a viral reel, not a stock photo
- Maximum visual density: textures, colors, details that reward a second look

CRITICAL RULES for the image prompt:
- Compose for VERTICAL 9:16 frame (portrait, not landscape)
- The subject must be large, close, and visually DOMINANT — no wide empty scenes
- Use tension, contrast, or unexpected detail that creates curiosity
- Real-world lighting (golden hour, neon at night, dramatic window light) — no studio sterility
- The image should feel like a screenshot from a viral reel, not a stock photo
- Maximum visual density: textures, colors, details that reward a second look

Produce TWO outputs in this exact JSON format (no markdown, no code blocks):
{{
  "image_prompt": "A hyper-specific cinematic scene in under 65 words. Format: [subject + action], [setting + atmosphere], [camera angle + framing], [lighting quality], [color palette], [mood/texture detail]. Must feel NATIVE to Instagram Reels — not a stock photo.",
  "style_anchor": "Under 20 words. The visual DNA to replicate in the video: color palette, lighting type, mood, texture, energy level."
  "image_prompt": "A hyper-specific cinematic scene in under 65 words. Format: [subject + action], [setting + atmosphere], [camera angle + framing], [lighting quality], [color palette], [mood/texture detail]. Must feel NATIVE to Instagram Reels — not a stock photo.",
  "style_anchor": "Under 20 words. The visual DNA to replicate in the video: color palette, lighting type, mood, texture, energy level."
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
    Uses audio_vibe from strategy when available for a more specific sound.
    Uses audio_vibe from strategy when available for a more specific sound.
    """
    emotion = strategy.get("emotion", "energetic")
    audio_vibe = strategy.get("audio_vibe", "")

    # Map emotions to concrete music descriptors
    emotion_map = {
        "desire": "smooth, seductive R&B groove, bass-forward, slow burn build",
        "fomo": "upbeat pop, driving beat, energetic rise, punchy drops",
        "surprise": "dramatic cinematic swell, sudden hit, tension-release",
        "delight": "bright indie pop, feel-good melody, clapping rhythm, joyful",
        "curiosity": "lo-fi hip hop, mysterious pads, subtle tension, chill groove",
        "nostalgia": "warm acoustic guitar, soft piano, nostalgic Americana feel",
        "pride": "triumphant brass, anthemic build, punchy percussion",
    }
    emotion_music = emotion_map.get(emotion.lower(), "upbeat pop, energetic, driving beat")

    if audio_vibe:
        return f"{audio_vibe}, {emotion_music}, short-form social media energy, 10 seconds"
    return f"{emotion_music}, short-form social media energy, punchy intro, 10 seconds"
    audio_vibe = strategy.get("audio_vibe", "")

    # Map emotions to concrete music descriptors
    emotion_map = {
        "desire": "smooth, seductive R&B groove, bass-forward, slow burn build",
        "fomo": "upbeat pop, driving beat, energetic rise, punchy drops",
        "surprise": "dramatic cinematic swell, sudden hit, tension-release",
        "delight": "bright indie pop, feel-good melody, clapping rhythm, joyful",
        "curiosity": "lo-fi hip hop, mysterious pads, subtle tension, chill groove",
        "nostalgia": "warm acoustic guitar, soft piano, nostalgic Americana feel",
        "pride": "triumphant brass, anthemic build, punchy percussion",
    }
    emotion_music = emotion_map.get(emotion.lower(), "upbeat pop, energetic, driving beat")

    if audio_vibe:
        return f"{audio_vibe}, {emotion_music}, short-form social media energy, 10 seconds"
    return f"{emotion_music}, short-form social media energy, punchy intro, 10 seconds"


def run_content_engine(selected_topic: str, strategy: dict) -> dict:
    """
    Full pipeline:
      1. Expand topic → image prompt + style anchor
      2. Generate base image (Flux Dev)
      3. Generate silent video (Wan i2v) — 15s, motion coherent
      4. Generate background music (stable-audio)
      5. Generate voiceover (Kokoro TTS) with audio CTA
      6. Mix voice + music → mux onto video
      7. Burn word-by-word subtitles (Alex Hormozi style)
      8. Append end-card (visual CTA)
    """
    from utils.run_context import get_run_dir

    VIDEO_DURATION = 15  # 15s optimised for retention + algorithm push

    log.step("run_content_engine", "IN",
             topic=selected_topic,
             motion_prompt=strategy.get("motion_prompt"),
             emotion=strategy.get("emotion"),
             video_duration=VIDEO_DURATION)

    # ── 1. Visual prompt expansion ────────────────────────────────────────────
    log.step("run_content_engine", "INFO",
             step="1/8 - Expanding topic → image prompt + style anchor")
    prompts = expand_to_prompt(selected_topic, strategy)
    image_prompt = prompts["image_prompt"]
    style_anchor = prompts["style_anchor"]

    # ── 2. Image generation ───────────────────────────────────────────────────
    log.step("run_content_engine", "INFO",
             step="2/8 - Generating base image", prompt=image_prompt)
    img_req = GenerateImageRequest(prompt=image_prompt, images=[], n=1)
    image_urls = generate_image_urls(img_req)

    if not image_urls:
        log.step("run_content_engine", "ERR", step="2/8",
                 error="Image generation returned no URLs")
        raise ValueError("Image generation failed to return a URL.")

    base_image_url = image_urls[0]
    log.step("run_content_engine", "INFO", step="2/8 - Image ready",
             image_url=base_image_url)

    # ── 3. Silent video — style-coherent, 15s ────────────────────────────────
    motion_prompt = build_coherent_motion_prompt(strategy, style_anchor)
    log.step("run_content_engine", "INFO",
             step="3/8 - Generating silent video (15s, style-coherent)",
             motion_prompt=motion_prompt)

    silent_video_path = generate_video(
        img_url=base_image_url,
        prompt=motion_prompt,
        resolution="720P",
        duration=VIDEO_DURATION,
        audio=False,
    )

    # ── 4a. Background music ────────────────────────────────────────────────
    # ── 4a. Background music ──────────────────────────────────────────────────
    audio_prompt = build_audio_prompt(selected_topic, strategy)
    log.step("run_content_engine", "INFO",
             step="4a/8 - Generating background music",
             step="4a/6 - Generating background music",
             audio_prompt=audio_prompt)

    from service.audio_service import submit_audio_task, poll_audio_task, download_audio
    music_task = submit_audio_task(audio_prompt, duration=VIDEO_DURATION)

    # ── 4b. Voiceover with CTA ──────────────────────────────────────────────
    voiceover_script = strategy.get("voiceover_script", "")
    if not voiceover_script:
        hook_text_tmp = strategy.get("hook_text", "") or strategy.get("hook", "")
        voiceover_script = f"{hook_text_tmp} Check the link in bio for details."

    # Build audio CTA from strategy fields
    cta_url = strategy.get("cta_url", "")
    cta_handle = strategy.get("cta_handle", "")
    cta_voice = ""
    if cta_handle and cta_url:
        cta_voice = f"Síguenos en {cta_handle} y visita {cta_url} para más."
    elif cta_handle:
        cta_voice = f"Síguenos en {cta_handle} para más contenido así."
    elif cta_url:
        cta_voice = f"Visita {cta_url} para más contenido."

    log.step("run_content_engine", "INFO",
             step="4b/8 - Generating voiceover with audio CTA",
             voiceover_script=voiceover_script,
             cta_voice=cta_voice)

    voiceover_path = generate_voiceover(
        script=voiceover_script,
        cta_text=cta_voice,
    )

    # ── 4c. Wait for music + mix + mux onto video ───────────────────────────
    log.step("run_content_engine", "INFO",
             step="4c/8 - Waiting for music, then mixing")
    music_url = poll_audio_task(music_task)
    music_path = download_audio(music_url)

    video_with_audio = mix_voice_and_music(
    from utils.run_context import get_run_dir as _get_run_dir
    from service.audio_service import submit_audio_task, poll_audio_task, download_audio
    music_task = submit_audio_task(audio_prompt, duration=10)

    # ── 4b. Voiceover (parallel while music generates) ───────────────────────
    voiceover_script = strategy.get("voiceover_script", "")
    if not voiceover_script:
        # Fallback: derive from hook_text + cta
        hook_text_tmp = strategy.get("hook_text", "") or strategy.get("hook", "")
        voiceover_script = f"{hook_text_tmp} Check the link in bio for details."

    log.step("run_content_engine", "INFO",
             step="4b/6 - Generating English voiceover (Kokoro TTS)",
             voiceover_script=voiceover_script)

    voiceover_path = generate_voiceover(script=voiceover_script)

    # ── 4c. Wait for music + mix voice over music + mux onto video ────────────
    log.step("run_content_engine", "INFO", step="4c/6 - Waiting for music, then mixing")
    music_url = poll_audio_task(music_task)
    music_path = download_audio(music_url)

    video_with_audio = mix_voice_and_music(
        video_path=silent_video_path,
        voiceover_path=voiceover_path,
        music_path=music_path,
        music_volume=0.18,
        voiceover_path=voiceover_path,
        music_path=music_path,
        music_volume=0.18,   # music at 18% — voice is always clear
    )

    # ── 5. Word-by-word subtitles (Alex Hormozi style) ─────────────────────
    from service.subtitle_service import add_word_by_word_subtitles

    # ── 5. Burn text overlays (reel-native style) ─────────────────────────────
    hook = strategy.get("hook", "")
    hook_text = strategy.get("hook_text", "")
    hook_text = strategy.get("hook_text", "")
    on_screen_text = strategy.get("on_screen_text") or ""
    cta_text_overlay = strategy.get("cta", "")

    log.step("run_content_engine", "INFO",
             step="5/8 - Burning word-by-word subtitles",
             transcript=voiceover_script[:60],
             hook_text=hook_text[:60] if hook_text else hook[:60])
             step="5/6 - Burning text overlays",
             hook_text=hook_text[:60] if hook_text else hook[:60],
             on_screen_text=on_screen_text,
             cta=cta)

    subtitled_path = add_word_by_word_subtitles(
    subtitled_path = add_subtitles_to_video(
        video_path=video_with_audio,
        transcript=voiceover_script,
        run_dir=get_run_dir(),
        duration=VIDEO_DURATION,
    )

    # ── 6. Append end-card (visual CTA) ──────────────────────────────────────
    from service.endcard_service import add_endcard

    log.step("run_content_engine", "INFO",
             step="6/8 - Appending end-card CTA",
             cta_follow=cta_handle or "",
             cta_url=cta_url or "")

    with_endcard = add_endcard(
        video_path=subtitled_path,
        cta_follow=cta_handle or "",
        cta_url=cta_url or "",
        duration=3.0,
        hook=hook,
        hook_text=hook_text,
        on_screen_text=on_screen_text,
        cta=cta,
        run_dir=get_run_dir(),
    )

    # ── Rename final video to a human-readable name ─────────────────────────
    slug = re.sub(r"[^\w\s-]", "", selected_topic.lower())
    slug = re.sub(r"[\s]+", "_", slug.strip())[:50]
    final_video_path = os.path.join(get_run_dir(), f"REEL_{slug}.mp4")
    shutil.move(with_endcard, final_video_path)
    log.step("run_content_engine", "INFO",
             step="8/8 - Final video renamed",
             final_video_path=final_video_path)

    # ── Rename final video to a human-readable name ───────────────────────────
    slug = re.sub(r"[^\w\s-]", "", selected_topic.lower())
    slug = re.sub(r"[\s]+", "_", slug.strip())[:50]
    final_video_path = os.path.join(get_run_dir(), f"REEL_{slug}.mp4")
    shutil.move(subtitled_path, final_video_path)
    log.step("run_content_engine", "INFO",
             step="6/6 - Final video renamed",
             final_video_path=final_video_path)

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
        "hook_text": hook_text,
        "voiceover_script": voiceover_script,
        "voiceover_path": voiceover_path,
        "cta_voice": cta_voice,
        "hook_text": hook_text,
        "voiceover_script": voiceover_script,
        "voiceover_path": voiceover_path,
        "emotion": strategy.get("emotion"),
        "caption": strategy.get("caption"),
        "hashtags": strategy.get("hashtags", []),
        "cta": cta_text_overlay,
        "cta_url": cta_url,
        "cta_handle": cta_handle,
        "on_screen_text": on_screen_text,
    }

    log.step("run_content_engine", "OUT",
             topic=selected_topic,
             image_url=base_image_url,
             style_anchor=style_anchor,
             silent_video=silent_video_path,
             voiceover_script=voiceover_script,
             cta_voice=cta_voice,
             voiceover_script=voiceover_script,
             video_with_audio=video_with_audio,
             final_video=final_video_path,
             caption_preview=str(strategy.get("caption", ""))[:80])
    return result
