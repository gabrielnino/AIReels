import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.run_context import init_run
from engine.content_engine import run_content_engine

init_run()

strategy = {
    "emotion": "surprise",
    "hook": "What if AI could create entire videos from scratch?",
    "hook_text": "IA creating videos from scratch, this is the future.",
    "voiceover_script": "La inteligencia artificial puede ahora crear videos completos desde cero. Imagen, video, voz, música y subtítulos, todo generado automáticamente. El futuro de la creación de contenido está aquí.",
    "cta_url": "aireels.com",
    "cta_handle": "@aireels",
    "cta": "Follow for more!",
    "audio_vibe": "dramatic cinematic, epic build, futuristic electronic",
    "motion_prompt": "futuristic holographic interface revealing AI capabilities, dynamic camera movement",
    "narrative": "AI content generation demo",
    "caption": "🤖 AI creating complete videos from scratch #AI #ContentGen",
    "hashtags": ["#AI", "#ContentGeneration", "#Future"],
    "on_screen_text": "AI Content Generation",
}

print("=" * 60)
print("FULL PIPELINE TEST — ESPAÑOL")
print("=" * 60)

result = run_content_engine(
    selected_topic="AI can create videos from scratch",
    strategy=strategy,
    language="es",
)

print("\n" + "=" * 60)
print("PIPELINE COMPLETO")
print("=" * 60)
final_video = result.get("final_video_path", "N/A")
print(f"Video final: {final_video}")
import os
if os.path.exists(final_video):
    print(f"Tamaño: {os.path.getsize(final_video)//1024} KB")
print(f"Voiceover: {result.get('voiceover_path', 'N/A')}")
print(f"Voiceover script: {result.get('voiceover_script', 'N/A')[:80]}")
print(f"CTA voz: {result.get('cta_voice', 'N/A')}")
