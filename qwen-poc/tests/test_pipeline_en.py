import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.run_context import init_run
from engine.content_engine import run_content_engine

init_run()

strategy = {
    "emotion": "curiosity",
    "hook": "The future of AI is already here.",
    "hook_text": "AI is transforming how we create content forever.",
    "voiceover_script": "Artificial intelligence can now create complete videos from scratch. Image, video, voice, music and subtitles, all generated automatically. The future of content creation is here.",
    "cta_url": "aireels.com",
    "cta_handle": "@aireels",
    "cta": "Follow for more!",
    "audio_vibe": "lo-fi electronic, mysterious atmosphere, chill techno",
    "motion_prompt": "futuristic AI interface, holographic displays, dynamic data flow",
    "narrative": "AI content generation demo",
    "caption": "🤖 AI creating complete videos from scratch #AI #ContentGen",
    "hashtags": ["#AI", "#ContentGeneration", "#Future"],
    "on_screen_text": "AI Content Generation",
}

print("=" * 60)
print("FULL PIPELINE TEST — ENGLISH")
print("=" * 60)

result = run_content_engine(
    selected_topic="AI transforming content creation",
    strategy=strategy,
    language="en",
)

print("\n" + "=" * 60)
print("PIPELINE COMPLETE")
print("=" * 60)
final_video = result.get("final_video_path", "N/A")
print(f"Final video: {final_video}")
import os
if os.path.exists(final_video):
    print(f"Size: {os.path.getsize(final_video)//1024} KB")
print(f"Voiceover: {result.get('voiceover_path', 'N/A')}")
print(f"Voiceover script: {result.get('voiceover_script', 'N/A')[:80]}...")
print(f"CTA voice: {result.get('cta_voice', 'N/A')}")
