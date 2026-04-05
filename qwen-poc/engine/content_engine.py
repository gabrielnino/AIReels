import os
import re
import shutil

from service.llm_service import generate_text
from service.image_service import generate_image_urls
from service.video_service import generate_video
from service.audio_service import mix_voice_and_music
from service.voiceover_service import generate_voiceover
from service.subtitle_service import add_subtitles_to_video
from models.request_models import GenerateImageRequest
from utils.logger import get_logger

log = get_logger(__name__)


def expand_to_prompt(topic: str, strategy: dict) -> dict:
    """Generate image prompt + style anchor from topic + strategy."""
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
This image is what the viewer sees in the first split-second - it must stop the scroll.

Topic       : '{topic}'
Emotion     : '{emotion}'
Hook moment : '{hook[:120]}'

CRITICAL RULES for the image prompt:
- Compose for VERTICAL 9:16 frame (portrait, not landscape)
- The subject must be large, close, and visually DOMINANT - no wide empty scenes
- Use tension, contrast, or unexpected detail that creates curiosity
- Real-world lighting (golden hour, neon at night, dramatic window light)
- The image should feel like a screenshot from a viral reel, not a stock photo
- Maximum visual density: textures, colors, details that reward a second look

Produce TWO outputs in this exact JSON format (no markdown, no code blocks):
{{
  "image_prompt": "A hyper-specific cinematic scene in under 65 words. Format: [subject + action], [setting + atmosphere], [camera angle + framing], [lighting quality], [color palette], [mood/texture detail]. Must feel NATIVE to Instagram Reels - not a stock photo.",
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
        image_prompt = response.strip()
        style_anchor = f"{emotion} atmosphere, cinematic lighting, vibrant colors"

    log.step("expand_to_prompt", "OUT", topic=topic, image_prompt=image_prompt, style_anchor=style_anchor)
    return {"image_prompt": image_prompt, "style_anchor": style_anchor}


def build_coherent_motion_prompt(strategy: dict, style_anchor: str) -> str:
    base_motion = strategy.get("motion_prompt", "gentle dynamic motion, cinematic camera pan, lively movement")
    return f"{base_motion}. Maintain visual style: {style_anchor}"


def build_audio_prompt(topic: str, strategy: dict) -> str:
    emotion = strategy.get("emotion", "energetic")
    audio_vibe = strategy.get("audio_vibe", "")

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
        return f"{audio_vibe}, {emotion_music}, short-form social media energy"
    return f"{emotion_music}, short-form social media energy, punchy intro"


def run_content_engine(selected_topic: str, strategy: dict, language: str = "en") -> dict:
    """
    Full pipeline:
      1. Expand topic -> image prompt + style anchor
      2. Generate base image (Flux Dev)
      3. Generate silent video (Wan i2v) - 15s, style-coherent
      4a. Generate background music (Google Lyria 3 via OpenRouter, fallback: stable-audio)
      4b. Generate voiceover with audio CTA (language-aware)
      4c. Mix voice + music (voice boosted 2x, music at 10%)
      5. Burn word-by-word subtitles (Alex Hormozi style)
      6. Append end-card (visual CTA)
      7. Generate SCRIPT.json + SCRIPT.md

    Args:
        language: "en" (default) or "es". Controls voice and CTA language.
    """
    from utils.run_context import get_run_dir

    VIDEO_DURATION = 15

    log.step("run_content_engine", "IN",
             topic=selected_topic, emotion=strategy.get("emotion"), video_duration=VIDEO_DURATION)

    # 1. Visual prompt expansion
    log.step("run_content_engine", "INFO", step="1/7 - Expanding topic to image prompt + style anchor")
    prompts = expand_to_prompt(selected_topic, strategy)
    image_prompt = prompts["image_prompt"]
    style_anchor = prompts["style_anchor"]

    # 2. Image generation
    log.step("run_content_engine", "INFO", step="2/7 - Generating base image", prompt=image_prompt)
    img_req = GenerateImageRequest(prompt=image_prompt, images=[], n=1)
    image_urls = generate_image_urls(img_req)

    if not image_urls:
        log.step("run_content_engine", "ERR", step="2/7", error="Image generation returned no URLs")
        raise ValueError("Image generation failed to return a URL.")

    base_image_url = image_urls[0]
    log.step("run_content_engine", "INFO", step="2/7 - Image ready", image_url=base_image_url)

    # 3. Silent video - 15s
    motion_prompt = build_coherent_motion_prompt(strategy, style_anchor)
    log.step("run_content_engine", "INFO", step="3/7 - Generating silent video (15s)", motion_prompt=motion_prompt)

    silent_video_path = generate_video(
        img_url=base_image_url, prompt=motion_prompt, resolution="720P", duration=VIDEO_DURATION, audio=False,
    )

    # 4a. Background music via Lyria 3 (OpenRouter)
    audio_prompt = build_audio_prompt(selected_topic, strategy)
    log.step("run_content_engine", "INFO", step="4a/7 - Generating music with Lyria 3", audio_prompt=audio_prompt[:80])

    music_path = None
    try:
        from service.lyria_service import generate_lyria_music, lyria_to_wav
        music_mp3 = generate_lyria_music(audio_prompt, duration=VIDEO_DURATION)
        music_wav = music_mp3.replace(".mp3", "_mixed.wav")
        music_path = lyria_to_wav(music_mp3, music_wav)
        log.step("run_content_engine", "INFO", music_source="lyria 3", music_path=music_path)
    except Exception as e:
        log.step("run_content_engine", "WARN", music_lyria_error=str(e), fallback="stable-audio")
        try:
            from service.audio_service import submit_audio_task, poll_audio_task, download_audio
            music_task = submit_audio_task(audio_prompt, duration=VIDEO_DURATION)
            music_url = poll_audio_task(music_task)
            music_path = download_audio(music_url)
            log.step("run_content_engine", "INFO", music_source="stable-audio (fallback)", music_path=music_path)
        except Exception as e2:
            log.step("run_content_engine", "WARN", music_fallback2_error=str(e2), fallback="silent track")
            # Generate silent audio as final fallback
            from utils.run_context import get_run_dir
            import subprocess
            run_dir = get_run_dir()
            silent_music = os.path.join(run_dir, "silent_music.wav")
            subprocess.run([
                "./ffmpeg", "-y", "-f", "lavfi", "-i",
                f"anullsrc=r=44100:cl=stereo",
                "-t", str(VIDEO_DURATION),
                "-acodec", "pcm_s16le",
                silent_music,
            ], check=True, capture_output=True, timeout=30)
            music_path = silent_music
            log.step("run_content_engine", "INFO", music_source="silent (no music)", music_path=music_path)

    # 4b. Voiceover with CTA
    voiceover_script = strategy.get("voiceover_script", "")
    if not voiceover_script:
        hook_text_tmp = strategy.get("hook_text", "") or strategy.get("hook", "")
        voiceover_script = f"{hook_text_tmp} Check the link in bio for details."

    cta_url = strategy.get("cta_url", "tudominio.com")
    cta_handle = strategy.get("cta_handle", "@tuusuario")

    # Language-aware CTA generation
    if language == "es":
        if cta_handle and cta_url:
            cta_voice = f"Síguenos en {cta_handle} y visita {cta_url} para más."
        elif cta_handle:
            cta_voice = f"Síguenos en {cta_handle} para más contenido así."
        elif cta_url:
            cta_voice = f"Visita {cta_url} para más contenido."
        else:
            cta_voice = ""
    else:
        if cta_handle and cta_url:
            cta_voice = f"Follow {cta_handle} and visit {cta_url} for more."
        elif cta_handle:
            cta_voice = f"Follow {cta_handle} for more content like this."
        elif cta_url:
            cta_voice = f"Visit {cta_url} for more content."
        else:
            cta_voice = ""

    log.step("run_content_engine", "INFO", step="4b/7 - Generating voiceover", language=language, cta_voice=cta_voice[:60] if cta_voice else "")
    voiceover_path = generate_voiceover(script=voiceover_script, language=language, cta_text=cta_voice)

    # 4c. Mix voice + music (voice 2x, music 10%)
    log.step("run_content_engine", "INFO", step="4c/7 - Mixing voice + music")
    video_with_audio = mix_voice_and_music(
        video_path=silent_video_path,
        voiceover_path=voiceover_path,
        music_path=music_path,
    )

    # 5. Word-by-word subtitles
    from service.subtitle_service import add_word_by_word_subtitles
    hook = strategy.get("hook", "")
    hook_text = strategy.get("hook_text", "")
    on_screen_text = strategy.get("on_screen_text") or ""
    cta = strategy.get("cta", "")

    log.step("run_content_engine", "INFO", step="5/7 - Burning word-by-word subtitles")
    subtitled_path = add_word_by_word_subtitles(
        video_path=video_with_audio, transcript=voiceover_script,
        run_dir=get_run_dir(), duration=VIDEO_DURATION,
    )

    # 6. Append end-card
    from service.endcard_service import add_endcard
    log.step("run_content_engine", "INFO", step="6/7 - Appending end-card")
    with_endcard = add_endcard(
        video_path=subtitled_path, cta_follow=cta_handle,
        cta_url=cta_url, duration=3.0, run_dir=get_run_dir(),
    )

    # 7. Generate script document
    from service.script_service import generate_script as save_script_file
    log.step("run_content_engine", "INFO", step="7/7 - Generating script document")
    result_data = {
        "topic": selected_topic, "base_prompt": image_prompt, "style_anchor": style_anchor,
        "image_url": base_image_url, "silent_video_path": silent_video_path,
        "video_with_audio_path": video_with_audio, "final_video_path": with_endcard,
        "audio_prompt": audio_prompt, "motion_prompt": motion_prompt,
        "narrative": strategy.get("narrative"), "hook": hook, "hook_text": hook_text,
        "voiceover_script": voiceover_script, "voiceover_path": voiceover_path,
        "cta_voice": cta_voice, "emotion": strategy.get("emotion"),
        "caption": strategy.get("caption"), "hashtags": strategy.get("hashtags", []),
        "cta": cta, "cta_url": cta_url, "cta_handle": cta_handle,
        "on_screen_text": on_screen_text,
    }
    try:
        script_path = save_script_file(strategy, result_data, get_run_dir())
        log.step("run_content_engine", "INFO", script_generated=script_path)
    except Exception as e:
        log.step("run_content_engine", "WARN", script_error=str(e))

    # Rename final video
    slug = re.sub(r"[^\w\s-]", "", selected_topic.lower())
    slug = re.sub(r"[\s]+", "_", slug.strip())[:50]
    final_video_path = os.path.join(get_run_dir(), f"REEL_{slug}.mp4")
    shutil.move(with_endcard, final_video_path)
    result_data["final_video_path"] = final_video_path

    log.step("run_content_engine", "INFO", step="7/7 - Final video renamed", final_video_path=final_video_path)

    log.step("run_content_engine", "OUT",
             topic=selected_topic, final_video=final_video_path,
             caption_preview=str(strategy.get("caption", ""))[:80])
    return result_data
