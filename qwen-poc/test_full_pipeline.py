"""
test_full_pipeline.py
=====================
Tests the entire AIReels pipeline:
  image → video (15s) → voiceover+CTA → music → mix → subtitles → end-card
"""

from utils.run_context import init_run
init_run()

import os
from utils.run_context import get_run_dir
from utils.logger import get_logger

log = get_logger(__name__)

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

video_prompt = motion_prompt

voiceover_script = (
    "Wait — this girl just came to life from the wall. "
    "Spray paint, neon lights, pure energy. "
    "You gotta see the full story."
)

cta_voice = "Síguenos en @aireels y visita aireels.com para mas."

audio_prompt = "dark urban hip hop beat, cinematic bass, energetic rap beat, 15 seconds"

cta_url = "aireels.com"
cta_handle = "@aireels"


# ── Pipeline ───────────────────────────────────────────────────────────────
print("=" * 60)
print("FULL PIPELINE TEST")
print("=" * 60)
print(f"Output dir: {get_run_dir()}")
print()

# Step 1: Generate Image
print("Step 1/7 — Generating base image...")
from models.request_models import GenerateImageRequest
from service.image_service import generate_image_urls, download_image

img_req = GenerateImageRequest(prompt=image_prompt, images=test_images, n=1)
image_urls = generate_image_urls(img_req)
generated_img_url = image_urls[0]
print(f"  -> Image CDN: {generated_img_url}")

local_img = download_image(generated_img_url)
print(f"  -> Local: {local_img}")

# Step 2: Generate Video (15s)
print(f"\nStep 2/7 — Generating silent video ({VIDEO_DURATION}s)...")
from service.video_service import generate_video

silent_video_path = generate_video(
    img_url=generated_img_url,
    prompt=video_prompt,
    resolution="720P",
    duration=VIDEO_DURATION,
    audio=False,
)
print(f"  -> Video: {silent_video_path} ({os.path.getsize(silent_video_path) // 1024}KB)")

# Step 3: Generate Voiceover with CTA
print("\nStep 3/7 — Generating voiceover with CTA...")
from service.voiceover_service import generate_voiceover

voiceover_path = generate_voiceover(
    script=voiceover_script,
    cta_text=cta_voice,
)
print(f"  -> Voiceover: {voiceover_path} ({os.path.getsize(voiceover_path) // 1024}KB)")

# Step 4a: Generate Background Music
print("\nStep 4a/7 — Generating background music...")
from service.audio_service import submit_audio_task, poll_audio_task, download_audio

music_task = submit_audio_task(audio_prompt, duration=VIDEO_DURATION)
music_url = poll_audio_task(music_task)
music_path = download_audio(music_url)
print(f"  -> Music: {music_path} ({os.path.getsize(music_path) // 1024}KB)")

# Step 4b: Mix Voiceover + Music + Mux onto Video
print("\nStep 4b/7 — Mixing voiceover + music onto video...")
from service.audio_service import mix_voice_and_music

video_with_audio = mix_voice_and_music(
    video_path=silent_video_path,
    voiceover_path=voiceover_path,
    music_path=music_path,
    music_volume=0.18,
)
print(f"  -> Video+Audio: {video_with_audio} ({os.path.getsize(video_with_audio) // 1024}KB)")

# Step 5: Word-by-Word Subtitles
print("\nStep 5/7 — Burning word-by-word subtitles...")
from service.subtitle_service import add_word_by_word_subtitles

subtitled_path = add_word_by_word_subtitles(
    video_path=video_with_audio,
    transcript=voiceover_script,
    run_dir=get_run_dir(),
    duration=VIDEO_DURATION,
)
print(f"  -> Subtitled: {subtitled_path} ({os.path.getsize(subtitled_path) // 1024}KB)")

# Step 6: End-Card CTA
print("\nStep 6/7 — Appending end-card CTA...")
from service.endcard_service import add_endcard

final_video = add_endcard(
    video_path=subtitled_path,
    cta_follow=cta_handle,
    cta_url=cta_url,
    duration=3.0,
    run_dir=get_run_dir(),
)
print(f"  -> Final: {final_video} ({os.path.getsize(final_video) // 1024}KB)")

# Summary
print("\n" + "=" * 60)
print("PIPELINE COMPLETE")
print("=" * 60)
print(f"\nFinal video: {final_video}")
print(f"Size: {os.path.getsize(final_video) // 1024}KB")
print(f"\nChanges tested:")
print(f"  1. Hook with on-screen text  via strategy_engine prompt")
print(f"  2a. Voiceover CTA (audio)    -> '{cta_voice}'")
print(f"  2b. Visual end-card           -> @aireels + {cta_url}")
print(f"  3. Loop-aware strategy        -> voiceover ends with hook reference")
print(f"  4. Word-by-word subtitles     -> Alex Hormozi style")
print(f"  5. 15s video duration         -> {VIDEO_DURATION}s (+3s endcard)")
