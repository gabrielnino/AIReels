from utils.run_context import init_run
from utils.run_context import get_run_dir
from utils.logger import get_logger
from models.request_models import GenerateImageRequest
from service.image_service import generate_image_urls, download_image
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

test_images = [
    "https://thumbs.dreamstime.com/b/slim-teen-girl-blue-dress-white-background-girl-blue-dress-128302673.jpg",
]

image_prompt = (
    "A striking urban fantasy girl painted in neon spray-paint "
    "emerging from a concrete wall at night, dramatic streetlight, "
    "cinematic vertical composition, dark moody atmosphere, vibrant textures. "
    "9:16 portrait framing, subject dominant."
)

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
print("FULL PIPELINE TEST (Lyria 3 Music)")
print("=" * 60)

# Step 1: Generate Image
print("\nStep 1/7 — Generating base image...")
img_req = GenerateImageRequest(prompt=image_prompt, images=test_images, n=1)
image_urls = generate_image_urls(img_req)
generated_img_url = image_urls[0]
print(f"  -> Image CDN: {generated_img_url}")
local_img = download_image(generated_img_url)
print(f"  -> Local: {local_img} ({os.path.getsize(local_img)//1024}KB)")

# Step 2: Generate Video (15s)
print(f"\nStep 2/7 — Generating silent video ({VIDEO_DURATION}s)...")
silent_video_path = generate_video(
    img_url=generated_img_url, prompt=motion_prompt, resolution="720P", duration=VIDEO_DURATION, audio=False,
)
print(f"  -> Video: {silent_video_path} ({os.path.getsize(silent_video_path)//1024}KB)")

# Step 3: Voiceover with CTA
print("\nStep 3/7 — Generating voiceover with CTA...")
voiceover_path = generate_voiceover(script=voiceover_script, cta_text=cta_voice)
print(f"  -> Voiceover: {voiceover_path} ({os.path.getsize(voiceover_path)//1024}KB)")

# Step 4a: Generate Music with Lyria 3
print("\nStep 4a/7 — Generating music with Lyria 3 (OpenRouter)...")
music_mp3 = generate_lyria_music(audio_prompt, duration=VIDEO_DURATION)
print(f"  -> MP3: {music_mp3} ({os.path.getsize(music_mp3)//1024}KB)")

# Convert MP3 to WAV for mixing
music_wav = music_mp3.replace(".mp3", "_mixed.wav")
music_path = lyria_to_wav(music_mp3, music_wav)
print(f"  -> WAV: {music_path} ({os.path.getsize(music_path)//1024}KB)")

# Step 4b: Mix audio
print("\nStep 4b/7 — Mixing voiceover + Lyria music...")
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
print(f"\nChanges tested:")
print(f"  1. Lyria 3 music (OpenRouter) -> high quality MP3 -> WAV")
print(f"  2. Voice CTA (audio) -> '{cta_voice}'")
print(f"  3. Voice boosted 2x, music at 10%")
print(f"  4. Word-by-word subtitles (Alex Hormozi style)")
print(f"  5. End-card visual CTA -> @aireels + {cta_url}")
print(f"  6. 15s video duration -> 15s + 3s endcard = 18s total")
