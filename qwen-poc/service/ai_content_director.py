#!/usr/bin/env python3
"""
AI Content Director — Interactive viral short-form video creative tool.

Runs strictly step-by-step. Waits for user confirmation before advancing.
Feeds final assets into the existing content engine pipeline.
"""

import json
import sys

from service.llm_service import generate_text
from utils.json_utils import clean_llm_json


# ── Colors / helpers ─────────────────────────────────────────────────────────
class C:
    BOLD = "\033[1m"
    RESET = "\033[0m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    DIM = "\033[2m"
    RED = "\033[91m"


def banner(text: str) -> None:
    print(f"\n{C.BOLD}{'=' * 60}{C.RESET}")
    print(f"{C.BOLD}  {text}{C.RESET}")
    print(f"{C.BOLD}{'=' * 60}{C.RESET}")


def step_label(step: str, title: str) -> None:
    print(f"\n{C.CYAN}{C.BOLD}{step}{C.RESET} — {C.BOLD}{title}{C.RESET}")


def show_output(key: str, value: str) -> None:
    print(f"  {C.GREEN}{key}{C.RESET}: {value}")


def ask_confirm() -> bool:
    """Return True if user proceeds, False otherwise."""
    while True:
        ans = input(f"\n  {C.YELLOW}Proceed? [y/n/edit]: {C.RESET}").strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        if ans == "edit":
            return True  # will be handled separately
        print(f"  {C.DIM}Type 'y' to proceed, 'n' to abort, or 'edit' to modify.{C.RESET}")


def ask_edit(current: str) -> str:
    """Allow user to edit a generated value."""
    print(f"  {C.DIM}Current: {current}{C.RESET}")
    new_val = input(f"  {C.YELLOW}New value (or blank to keep): {C.RESET}").strip()
    return new_val if new_val else current


# ── STEP 0 — Topic Definition ────────────────────────────────────────────────
def step0_topic(language: str = "en") -> dict:
    """Step 0 — Topic Definition. Language affects LLM response."""
    banner("STEP 0 — TOPIC DEFINITION")

    lang_instruction = "Response language: Spanish" if language == "es" else "Response language: English"

    print(f"\n  {C.DIM}Tell me about your video's purpose. Fill what you can.{C.RESET}\n")

    business_goal = input(f"  business_goal (e.g., 'generate traffic to website'): ").strip()
    if not business_goal:
        print(f"  {C.RED}business_goal is required. Aborting.{C.RESET}")
        sys.exit(1)

    business_context = input(f"  business_context (describe your product/service): ").strip()
    target_audience = input(f"  target_audience (optional): ").strip()
    geography = input(f"  geography (optional): ").strip()
    tone = input(f"  tone (fun, aggressive, emotional, luxury, etc.): ").strip()

    # Build LLM prompt
    inputs = {
        "business_goal": business_goal,
        "business_context": business_context,
        "target_audience": target_audience,
        "geography": geography,
        "tone": tone,
    }

    prompt = f"""
You are an elite AI Content Director specialized in short-form viral video generation (Reels/TikTok/Shorts).
{lang_instruction}

USER INPUT:
- Business goal: {inputs['business_goal']}
- Business context: {inputs['business_context']}
- Target audience: {inputs['target_audience'] if inputs['target_audience'] else 'Not specified'}
- Geography: {inputs['geography'] if inputs['geography'] else 'Not specified'}
- Tone: {inputs['tone'] if inputs['tone'] else 'Not specified'}

TASK:
1. Identify 3-5 trending topics related to the business domain.
   - Trends must align with:
     - Social media virality (Reels/TikTok)
     - Audience psychology (curiosity, emotion, urgency)
     - Business objective (conversion, traffic, awareness)
2. Select ONE best topic based on viral potential, alignment with goal, and simplicity for short-form.

Output ONLY a valid JSON object. No markdown, no code blocks.
{{
  "candidate_topics": ["topic 1", "topic 2", "topic 3", ...],
  "selected_topic": "the best one",
  "reasoning": "why this was selected",
  "content_angle": "the creative angle to exploit",
  "emotional_trigger": "curiosity/FOMO/surprise/delight/nostalgia/pride",
  "hook_idea": "a one-line hook idea"
}}
"""

    print(f"\n  {C.DIM}Analyzing business context and generating topic candidates...{C.RESET}")

    response = generate_text(
        prompt=prompt,
        model="deepseek-chat",
        system_prompt="You are an elite AI Content Director. Output ONLY valid JSON. No markdown.",
    )

    try:
        result = json.loads(clean_llm_json(response))
    except Exception as e:
        print(f"\n  {C.RED}Failed to parse LLM response: {e}{C.RESET}")
        print(f"  Raw response: {response[:500]}")
        sys.exit(1)

    print(f"\n  {C.BOLD}Candidate topics:{C.RESET}")
    for i, t in enumerate(result.get("candidate_topics", []), 1):
        print(f"    {i}. {t}")

    print(f"\n  {C.BOLD}Selected:{C.RESET} {result.get('selected_topic', '')}")
    print(f"  {C.BOLD}Reasoning:{C.RESET} {result.get('reasoning', '')}")
    print(f"  {C.BOLD}Content angle:{C.RESET} {result.get('content_angle', '')}")
    print(f"  {C.BOLD}Emotional trigger:{C.RESET} {result.get('emotional_trigger', '')}")
    print(f"  {C.BOLD}Hook idea:{C.RESET} {result.get('hook_idea', '')}")

    print(f"\n  {C.DIM}Type 'y' to accept the selected topic, 'n' to abort.{C.RESET}")
    if not ask_confirm():
        print(f"\n  {C.RED}Aborted.{C.RESET}")
        sys.exit(0)

    return result


# ── STEP 1 — Visual Concept (Image Prompt) ──────────────────────────────────
def step1_image_prompt(topic_data: dict) -> str:
    step_label("STEP 1", "VISUAL CONCEPT (IMAGE PROMPT)")

    selected_topic = topic_data.get("selected_topic", "")
    emotion = topic_data.get("emotional_trigger", "")
    hook_idea = topic_data.get("hook_idea", "")
    content_angle = topic_data.get("content_angle", "")

    prompt = f"""
Generate a cinematic, highly engaging image prompt for the FIRST FRAME of a viral Instagram Reel.

Topic            : {selected_topic}
Emotion to trigger: {emotion}
Hook idea        : {hook_idea}
Content angle    : {content_angle}

RULES:
- Under 50 words
- Vertical (9:16)
- Strong hook visual - scroll-stopping
- High contrast, cinematic
- No filler text
- Subject must be large, close, and visually DOMINANT
- Real-world lighting (golden hour, neon at night, dramatic window light)
- Maximum visual density: textures, colors, details that reward a second look

Output ONLY the image_prompt string, nothing else.
"""

    response = generate_text(
        prompt=prompt,
        model="deepseek-chat",
        system_prompt="You are an elite creative director for image generation. Be hyper-specific. Under 50 words.",
    )

    image_prompt = response.strip().strip('"').strip()
    show_output("image_prompt", image_prompt)

    print(f"\n  {C.DIM}Type 'y' to accept, 'edit' to change, 'n' to abort.{C.RESET}")
    if not ask_confirm():
        print(f"\n  {C.RED}Aborting image prompt generation.{C.RESET}")
        sys.exit(0)

    current = image_prompt
    while True:
        current = ask_edit(current)
        if current and current != image_prompt:
            image_prompt = current
            break
        if not current or current == image_prompt:
            break

    return image_prompt


# ── STEP 2 — Style Anchor ───────────────────────────────────────────────────
def step2_style_anchor(topic_data: dict, image_prompt: str) -> str:
    step_label("STEP 2", "STYLE ANCHOR")

    emotion = topic_data.get("emotional_trigger", "")

    prompt = f"""
Define a reusable visual style reference (style anchor) based on this image prompt.

Image prompt: {image_prompt}
Emotion: {emotion}

The style_anchor should be a comma-separated list of visual DNA elements:
color palette, lighting type, mood, texture, energy level.
Under 20 words.

Output ONLY the style_anchor text, nothing else.
"""

    response = generate_text(
        prompt=prompt,
        model="deepseek-chat",
        system_prompt="You are a visual style director. Be concise. Under 20 words. Output ONLY the style anchor.",
    )

    style_anchor = response.strip().strip('"').strip()
    show_output("style_anchor", style_anchor)

    print(f"\n  {C.DIM}Type 'y' to accept, 'edit' to change, 'n' to abort.{C.RESET}")
    if not ask_confirm():
        print(f"\n  {C.RED}Aborting style anchor generation.{C.RESET}")
        sys.exit(0)

    return ask_edit(style_anchor) or style_anchor


# ── STEP 3 — Motion Prompt ─────────────────────────────────────────────────
def step3_motion_prompt(topic_data: dict, style_anchor: str) -> str:
    step_label("STEP 3", "MOTION PROMPT (VIDEO GENERATION)")

    selected_topic = topic_data.get("selected_topic", "")
    emotional_trigger = topic_data.get("emotional_trigger", "")

    prompt = f"""
Define the subject movement + camera behavior for a 15-second vertical Reel.

Topic: {selected_topic}
Emotion: {emotional_trigger}
Style to maintain: {style_anchor}

RULES:
- Specify camera move, pacing, and key visual moment
- Under 25 words
- Must maintain style anchor consistency

Output ONLY the motion_prompt text, nothing else.
"""

    response = generate_text(
        prompt=prompt,
        model="deepseek-chat",
        system_prompt="You are a video director. Be specific and cinematic. Under 25 words. Output ONLY the motion prompt.",
    )

    motion_prompt = response.strip().strip('"').strip()
    show_output("motion_prompt", motion_prompt)

    print(f"\n  {C.DIM}Type 'y' to accept, 'edit' to change, 'n' to abort.{C.RESET}")
    if not ask_confirm():
        print(f"\n  {C.RED}Aborting motion prompt generation.{C.RESET}")
        sys.exit(0)

    return ask_edit(motion_prompt) or motion_prompt


# ── STEP 4 — Voiceover Script ──────────────────────────────────────────────
def step4_voiceover(topic_data: dict) -> str:
    step_label("STEP 4", "VOICEOVER SCRIPT")

    selected_topic = topic_data.get("selected_topic", "")
    emotion = topic_data.get("emotional_trigger", "")
    hook_idea = topic_data.get("hook_idea", "")
    angle = topic_data.get("content_angle", "")

    prompt = f"""
Generate a short, high-conversion voiceover script for a 15-second Instagram Reel.

Topic: {selected_topic}
Emotional trigger: {emotion}
Hook idea: {hook_idea}
Content angle: {angle}

RULES:
- Hook in first sentence
- Maintain curiosity gap
- Natural spoken tone
- 3-4 short sentences (~35-40 words) for a 15-second reel
- End with a line that creates urgency to keep watching

Output ONLY the voiceover script text, nothing else.
"""

    response = generate_text(
        prompt=prompt,
        model="deepseek-chat",
        system_prompt="You are a viral content scriptwriter. Write natural, punchy, scroll-stopping narration. Under 40 words. Output ONLY the script.",
    )

    voiceover_script = response.strip().strip('"').strip()
    show_output("voiceover_script", voiceover_script)

    print(f"\n  {C.DIM}Type 'y' to accept, 'edit' to change, 'n' to abort.{C.RESET}")
    if not ask_confirm():
        print(f"\n  {C.RED}Aborting voiceover script generation.{C.RESET}")
        sys.exit(0)

    return ask_edit(voiceover_script) or voiceover_script


# ── STEP 5 — Audio Prompt ──────────────────────────────────────────────────
def step5_audio_prompt(topic_data: dict) -> str:
    step_label("STEP 5", "AUDIO PROMPT")

    selected_topic = topic_data.get("selected_topic", "")
    emotion = topic_data.get("emotional_trigger", "")
    voiceover = topic_data.get("hook_idea", "")

    prompt = f"""
Define the background music style for a 15-second viral Reel.

Topic: {selected_topic}
Emotion: {emotion}
Voiceover hook: {voiceover}

Output an audio direction string: genre, mood, tempo, instrumentation.
Keep it concise.

Output ONLY the audio_prompt text, nothing else.
"""

    response = generate_text(
        prompt=prompt,
        model="deepseek-chat",
        system_prompt="You are a music director for viral social content. Be specific about genre and mood. Output ONLY the audio prompt.",
    )

    audio_prompt = response.strip().strip('"').strip()
    show_output("audio_prompt", audio_prompt)

    print(f"\n  {C.DIM}Type 'y' to accept, 'edit' to change, 'n' to abort.{C.RESET}")
    if not ask_confirm():
        print(f"\n  {C.RED}Aborting audio prompt generation.{C.RESET}")
        sys.exit(0)

    return ask_edit(audio_prompt) or audio_prompt


# ── STEP 6 — CTA (Configurable) ────────────────────────────────────────────
def step6_cta(existing_config: dict | None = None) -> dict:
    step_label("STEP 6", "CTA (CONFIGURABLE)")

    if existing_config:
        default_handle = existing_config.get("cta_handle", "@fiestacotoday")
        default_url = existing_config.get("cta_url", "fiestaco.today")
    else:
        default_handle = "@fiestacotoday"
        default_url = "fiestaco.today"

    print(f"  {C.DIM}Configure your CTA details.{C.RESET}\n")

    cta_handle = input(f"  cta_handle (default: {default_handle}): ").strip() or default_handle
    cta_url = input(f"  cta_url (default: {default_url}): ").strip() or default_url

    cta_voice = "Síguenos en Fiesta Co Today"
    show_output("cta_handle", cta_handle)
    show_output("cta_url", cta_url)
    show_output("cta_voice", cta_voice)

    print(f"\n  {C.DIM}Type 'y' to accept, 'edit' to change.{C.RESET}")
    if not ask_confirm():
        print(f"\n  {C.RED}Aborting CTA configuration.{C.RESET}")
        sys.exit(0)

    return {
        "cta_handle": cta_handle,
        "cta_url": cta_url,
        "cta_voice": cta_voice,
    }


# ── Summary & Run Pipeline ──────────────────────────────────────────────────
def show_summary(assets: dict) -> None:
    banner("ALL ASSETS PREVIEW")
    for key, value in assets.items():
        if isinstance(value, str):
            display = value if len(value) <= 100 else value[:100] + "..."
            show_output(key, display)


def run_generation(assets: dict) -> None:
    """Feed assets into the existing pipeline for actual generation."""
    banner("GENERATING CONTENT...")
    print(f"\n  {C.DIM}The following will now run through the content generation pipeline.{C.RESET}")
    print(f"  {C.DIM}This will call external APIs (fal.ai, OpenRouter, etc.) and may take several minutes.{C.RESET}")

    print(f"\n  {C.DIM}Type 'y' to start generation, 'n' to just save the script.{C.RESET}")
    answer = input(f"\n  {C.YELLOW}Start generation? [y/n]: {C.RESET}").strip().lower()

    if answer not in ("y", "yes"):
        print(f"\n  {C.YELLOW}Scripts saved. Run the pipeline manually later.{C.RESET}")
        return

    # Build strategy dict matching what run_content_engine expects
    strategy = {
        "emotion": assets.get("emotional_trigger", "curiosity"),
        "hook": assets.get("hook_idea", ""),
        "hook_text": "",
        "motion_prompt": assets["motion_prompt"],
        "audio_vibe": assets["audio_prompt"],
        "voiceover_script": assets["voiceover_script"],
        "cta_url": assets["cta_url"],
        "cta_handle": assets["cta_handle"],
        "caption": "",
        "hashtags": [],
        "narrative": assets.get("selected_topic", ""),
        "on_screen_text": None,
    }

    topic = assets["selected_topic"]
    language = assets.get("language", "en")

    print(f"\n  {C.BOLD}Running content engine for:{C.RESET} {topic} | Language: {language}")

    from engine.content_engine import run_content_engine
    result = run_content_engine(topic, strategy=strategy, language=language)

    print(f"\n{C.GREEN}{C.BOLD}Generation complete!{C.RESET}")
    print(f"  Final video: {result.get('final_video_path', 'unknown')}")
    print(f"  Caption preview: {result.get('caption', '')[:120]}")


# ── Load config ──────────────────────────────────────────────────────────────
def load_config() -> dict:
    config_path = "config.json"
    try:
        with open(config_path) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    banner(" AI CONTENT DIRECTOR ")
    print(f"\n  {C.DIM}Interactive viral video creative tool.{C.RESET}")
    print(f"  {C.DIM}Each step requires your confirmation before proceeding.{C.RESET}")

    config = load_config()

    # Parse language from CLI or prompt
    import sys
    language = "en"
    if "--language" in sys.argv:
        idx = sys.argv.index("--language")
        if idx + 1 < len(sys.argv):
            language = sys.argv[idx + 1].lower()
    else:
        lang_input = input(f"\n  Language (default: en, options: en/es): ").strip().lower()
        language = lang_input if lang_input == "es" else "en"
    if language == "es":
        print(f"  {C.DIM}Modo español activado.{C.RESET}")

    # STEP 0: Topic
    topic_data = step0_topic(language)

    # STEP 1: Image prompt
    image_prompt = step1_image_prompt(topic_data)

    # STEP 2: Style anchor
    style_anchor = step2_style_anchor(topic_data, image_prompt)

    # STEP 3: Motion prompt
    motion_prompt = step3_motion_prompt(topic_data, style_anchor)

    # STEP 4: Voiceover script
    voiceover_script = step4_voiceover(topic_data)

    # STEP 5: Audio prompt
    audio_prompt = step5_audio_prompt(topic_data)

    # STEP 6: CTA
    cta_data = step6_cta(config)

    # Merge all assets
    assets = {
        **topic_data,
        "language": language,
        "image_prompt": image_prompt,
        "style_anchor": style_anchor,
        "motion_prompt": motion_prompt,
        "voiceover_script": voiceover_script,
        "audio_prompt": audio_prompt,
        **cta_data,
    }

    show_summary(assets)

    run_generation(assets)


if __name__ == "__main__":
    main()
