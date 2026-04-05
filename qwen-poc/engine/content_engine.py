import os
import re
import shutil

from service.llm_service import generate_text
from service.image_service import generate_image_urls
from service.video_service import generate_video
from service.audio_service import mix_voice_and_music
from service.subtitle_service import add_word_by_word_subtitles
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
      2. Generate voiceover
      3. Generate multi-scene video (5 images × 3s Ken Burns)
      4. Generate background music (Lyria 3, fallback: silent)
      5. Mix voice + music
      6. Burn word-by-word subtitles
      7. Append end-card (visual CTA)
      8. Generate SCRIPT.json + SCRIPT.md

    Args:
        language: "en" (default) or "es". Controls voice and CTA language.
    """
    from utils.run_context import get_run_dir

    VIDEO_DURATION = 15

    log.step("run_content_engine", "IN",
             topic=selected_topic, emotion=strategy.get("emotion"), video_duration=VIDEO_DURATION)

    # 1. Visual prompt expansion
    log.step("run_content_engine", "INFO", step="1/6 - Expanding topic to image prompt + style anchor")
    prompts = expand_to_prompt(selected_topic, strategy)
    image_prompt = prompts["image_prompt"]
    style_anchor = prompts["style_anchor"]

    # 2. Generate voiceover FIRST (needed for scene generation)
    voiceover_script = strategy.get("voiceover_script", "")
    if not voiceover_script:
        hook_text_tmp = strategy.get("hook_text", "") or strategy.get("hook", "")
        voiceover_script = f"{hook_text_tmp} Check the link in bio for details."

    cta_url = strategy.get("cta_url", "tudominio.com")
    cta_handle = strategy.get("cta_handle", "@tuusuario")

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

    log.step("run_content_engine", "INFO", step="2/6 - Generating voiceover", language=language)
    from service.voiceover_service import generate_voiceover
    voiceover_path = generate_voiceover(script=voiceover_script, language=language, cta_text=cta_voice)

    # 3. Generate multi-scene video from script
    log.step("run_content_engine", "INFO", step="3/6 - Generating multi-scene video", scenes=5, scene_duration=3)
    silent_video_path = generate_video(
        img_url=None,
        prompt=strategy.get("motion_prompt", "cinematic visual"),
        resolution="720P",
        duration=VIDEO_DURATION,
        voiceover_script=voiceover_script,
        style_anchor=style_anchor,
    )

    # 4. Generate music
    audio_prompt = build_audio_prompt(selected_topic, strategy)
    motion_prompt = build_coherent_motion_prompt(strategy, style_anchor)
    log.step("run_content_engine", "INFO", step="4/6 - Generating music", audio_prompt=audio_prompt[:80])

    music_path = None
    try:
        from service.lyria_service import generate_lyria_music, lyria_to_wav
        music_mp3 = generate_lyria_music(audio_prompt, duration=VIDEO_DURATION)
        music_wav = music_mp3.replace(".mp3", "_mixed.wav")
        music_path = lyria_to_wav(music_mp3, music_wav)
        log.step("run_content_engine", "INFO", music_source="lyria 3", music_path=music_path)
    except Exception as e:
        log.step("run_content_engine", "WARN", music_lyria_error=str(e), fallback="silent track")
        from utils.run_context import get_run_dir
        music_path = os.path.join(get_run_dir(), "silent_music.wav")
        sp = __import__("subprocess")
        sp.run([
            "./ffmpeg", "-y", "-f", "lavfi", "-i",
            "anullsrc=r=44100:cl=stereo",
            "-t", str(VIDEO_DURATION),
            "-acodec", "pcm_s16le",
            music_path,
        ], check=True, capture_output=True, timeout=30)

    # 5. Mix voice + music
    log.step("run_content_engine", "INFO", step="5/6 - Mixing voice + music")
    video_with_audio = mix_voice_and_music(
        video_path=silent_video_path,
        voiceover_path=voiceover_path,
        music_path=music_path,
    )

    # 6. Word-by-word subtitles
    from service.subtitle_service import add_word_by_word_subtitles
    hook = strategy.get("hook", "")
    hook_text = strategy.get("hook_text", "")
    on_screen_text = strategy.get("on_screen_text") or ""
    cta = strategy.get("cta", "")

    log.step("run_content_engine", "INFO", step="6/7 - Burning word-by-word subtitles")
    subtitled_path = add_word_by_word_subtitles(
        video_path=video_with_audio, transcript=voiceover_script,
        run_dir=get_run_dir(), duration=VIDEO_DURATION,
    )

    # 7. Append end-card
    from service.endcard_service import add_endcard
    log.step("run_content_engine", "INFO", step="7/7 - Appending end-card")
    with_endcard = add_endcard(
        video_path=subtitled_path, cta_follow=cta_handle,
        cta_url=cta_url, duration=3.0, run_dir=get_run_dir(),
    )

    # 8. Generate script document
    from service.script_service import generate_script as save_script_file
    log.step("run_content_engine", "INFO", step="8/8 - Generating script document")
    result_data = {
        "topic": selected_topic, "base_prompt": image_prompt, "style_anchor": style_anchor,
        "silent_video_path": silent_video_path,
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

    log.step("run_content_engine", "INFO", step="8/8 - Final video renamed", final_video_path=final_video_path)

    log.step("run_content_engine", "OUT",
             topic=selected_topic, final_video=final_video_path,
             caption_preview=str(strategy.get("caption", ""))[:80])
    return result_data
