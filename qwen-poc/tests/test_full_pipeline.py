from utils.run_context import init_run
from utils.run_context import get_run_dir
from utils.logger import get_logger
from service.video_service import generate_video
from service.audio_service import mix_voice_and_music
from service.subtitle_service import add_word_by_word_subtitles
from service.endcard_service import add_endcard
from service.lyria_service import generate_lyria_music, lyria_to_wav
from service.voiceover_service import generate_voiceover
import os

init_run()

log = get_logger(__name__)
run_dir = get_run_dir()
print(f"Run dir: {run_dir}")

# ── Config ───────────────────────────────────────────────────────────────────
VIDEO_DURATION = 15

voiceover_script = (
    "Wait — this girl just came to life from the wall. "
    "Spray paint, neon lights, pure energy. "
    "You gotta see the full story."
)

cta_voice = "Siguenos en @aireels y visita aireels.com para mas."

style_anchor = "neon spray-paint textures, cinematic streetlight, dark moody, urban night"

motion_prompt = (
    f"The girl performs an energetic rap with dynamic gestures and movement. "
    f"Camera slowly pushes in. Maintain visual style: {style_anchor}"
)

voiceover_script = (
    "Wait — this girl just came to life from the wall. "
    "Spray paint, neon lights, pure energy. "
    "You gotta see the full story."
)

cta_voice = "Siguenos en @aireels y visita aireels.com para mas."

audio_prompt = "dark urban hip hop beat, cinematic bass, energetic rap beat, instrumental"

cta_url = "aireels.com"
cta_handle = "@aireels"


# ── Pipeline ───────────────────────────────────────────────────────────────
print("=" * 60)
print("FULL PIPELINE TEST (Multi-Scene Video)")
print("=" * 60)

# Step 1: Voiceover with CTA
print(f"\nStep 1/6 — Generating voiceover with CTA...")
voiceover_path = generate_voiceover(script=voiceover_script, cta_text=cta_voice)
print(f"  -> Voiceover: {voiceover_path} ({os.path.getsize(voiceover_path)//1024}KB)")

# Step 2: Generate multi-scene video from script
print(f"\nStep 2/6 — Generating multi-scene video ({VIDEO_DURATION}s)...")
silent_video_path = generate_video(
    img_url=None,
    prompt=motion_prompt,
    resolution="720P",
    duration=VIDEO_DURATION,
    voiceover_script=voiceover_script,
    style_anchor=style_anchor,
)
print(f"  -> Video: {silent_video_path} ({os.path.getsize(silent_video_path)//1024}KB)")

# Step 3: Generate Music with Lyria 3
print("\nStep 3/6 — Generating music with Lyria 3 (OpenRouter)...")
music_mp3 = generate_lyria_music(audio_prompt, duration=VIDEO_DURATION)
print(f"  -> MP3: {music_mp3} ({os.path.getsize(music_mp3)//1024}KB)")

# Convert MP3 to WAV for mixing
music_wav = music_mp3.replace(".mp3", "_mixed.wav")
music_path = lyria_to_wav(music_mp3, music_wav)
print(f"  -> WAV: {music_path} ({os.path.getsize(music_path)//1024}KB)")

# Step 4: Mix audio
print("\nStep 4/6 — Mixing voiceover + Lyria music...")
video_with_audio = mix_voice_and_music(
    video_path=silent_video_path,
    voiceover_path=voiceover_path,
    music_path=music_path,
    # volumes from config.json: voice=5.0, music=0.08
)
print(f"  -> Video+Audio: {video_with_audio} ({os.path.getsize(video_with_audio)//1024}KB)")

# Step 5: Word-by-word subtitles
print("\nStep 5/7 — Burning word-by-word subtitles...")
subtitled_path = add_word_by_word_subtitles(
    video_path=video_with_audio, transcript=voiceover_script,
    run_dir=run_dir, duration=VIDEO_DURATION,
)
print(f"  -> Subtitled: {subtitled_path} ({os.path.getsize(subtitled_path)//1024}KB)")

# Step 6: End-card
print("\nStep 6/7 — Appending end-card CTA...")
final_video = add_endcard(
    video_path=subtitled_path, cta_follow=cta_handle,
    cta_url=cta_url, duration=3.0, run_dir=run_dir,
)
print(f"  -> Final: {final_video} ({os.path.getsize(final_video)//1024}KB)")

# Summary
print("\n" + "=" * 60)
print("PIPELINE COMPLETE")
print("=" * 60)
print(f"\nFinal video: {final_video}")
print(f"Size: {os.path.getsize(final_video)//1024}KB")
print(f"\nPipeline:")
print(f"  1. Voiceover + CTA (Edge TTS)")
print(f"  2. Multi-scene video (5 images × 3s Ken Burns)")
print(f"  3. Lyria 3 music (OpenRouter)")
print(f"  4. Voice + music mix (voice boosted, music at 10%)")
print(f"  5. Word-by-word subtitles (Alex Hormozi style)")
print(f"  6. End-card CTA -> {cta_handle} + {cta_url}")
