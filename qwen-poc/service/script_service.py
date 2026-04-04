"""
script_service.py
=================
Generates and persists a master video script document that consolidates
the complete creative blueprint for a single Reel:

  1. Image — full scene description, visual DNA, composition notes
  2. Video — shot-by-shot breakdown with timing, camera moves, action
  3. Caption — Instagram-ready caption + hashtags + posting notes
  4. Music  — audio prompt, voiceover full text, mix settings

This file is saved as `SCRIPT.json` in the run directory so anyone
can read the full creative intent without needing to reconstruct it
from separate strategy + content engine outputs.
"""

import json
import os
import textwrap
from utils.logger import get_logger

log = get_logger(__name__)


def format_shot_breakdown(voiceover_script: str, hook_text: str, cta: str,
                          emotion: str, duration: int = 15) -> list:
    """
    Breaks the voiceover into a timed shot list mapping to the 4-arc structure:
      0–3s: Hook
      3–8s: Payoff/Reveal
      8–12s: Emotional Peak
      12–15s: CTA + Loop
    """
    words = voiceover_script.split()
    words_per_sec = len(words) / duration

    shots = []
    # Arc definitions
    arcs = [
        ("HOOK", 0, 3, "Pattern interrupt — bold on-screen text stops the scroll"),
        ("PAYOFF", 3, 8, "Delivers on the hook's promise — the interesting reveal"),
        ("PEAK", 8, 12, "Emotional peak — desire/FOMO/surprise/delight"),
        ("CTA+LOOP", 12, 15, f"Clear action + loop back to hook: \"{cta}\""),
    ]

    start_idx = 0
    for arc_name, arc_start, arc_end, arc_desc in arcs:
        arc_word_count = int((arc_end - arc_start) * words_per_sec)
        end_idx = min(start_idx + arc_word_count, len(words))
        arc_words = " ".join(words[start_idx:end_idx])
        shots.append({
            "time": f"{arc_start}s – {arc_end}s",
            "arc": arc_name,
            "voiceover": arc_words,
            "on_screen_text": hook_text if arc_name == "HOOK" else None,
            "direction": arc_desc,
            "emotion_trigger": emotion,
            "word_count": len(arc_words.split()),
        })
        start_idx = end_idx

    return shots


def build_script(strategy: dict, content_data: dict) -> dict:
    """
    Assembles the full video script from strategy + content engine outputs.

    Args:
        strategy: dict from run_strategy_engine()
        content_data: dict from run_content_engine()

    Returns:
        A complete script dict ready for JSON or markdown rendering.
    """
    voiceover = strategy.get("voiceover_script", "")

    script = {
        # ── 1. IMAGE ───────────────────────────────────────────────
        "image": {
            "description": content_data.get("base_prompt", ""),
            "style_anchor": content_data.get("style_anchor", ""),
            "composition": "9:16 vertical portrait, subject dominant, no empty negative space",
            "lighting": "Cinematic — extracted from the image prompt",
            "purpose": "Opening frame / thumbnail — must stop the scroll in <0.5s",
            "generation_source": "Flux Dev (fal.ai)",
        },

        # ── 2. VIDEO ───────────────────────────────────────────────
        "video": {
            "description": f"{content_data.get('motion_prompt', '')}. "
                           f"Emotional arc: {strategy.get('narrative', '')}",
            "shot_breakdown": format_shot_breakdown(
                voiceover_script=voiceover,
                hook_text=strategy.get("hook_text", ""),
                cta=strategy.get("cta", ""),
                emotion=strategy.get("emotion", ""),
                duration=15,
            ),
            "camera_direction": content_data.get("motion_prompt", ""),
            "hook_visual": strategy.get("hook", ""),
            "hook_text": strategy.get("hook_text", ""),
            "loop_design": "The final voiceover line references the hook, creating a seamless replay feel",
            "duration_secs": 15,
            "resolution": "720x1280 (9:16 vertical)",
            "generation_source": "Wan 2.1 image-to-video (fal.ai)",
        },

        # ── 3. CAPTION ─────────────────────────────────────────────
        "caption": {
            "text": strategy.get("caption", ""),
            "hashtags": strategy.get("hashtags", []),
            "cta": strategy.get("cta", ""),
            "hook_line": "First line of the caption mirrors the hook energy",
            "emoji_policy": "1-2 max, used strategically not decoratively",
            "hashtag_policy": "15-20 hashtags, kept clean outside the caption body",
        },

        # ── 4. MUSIC ───────────────────────────────────────────────
        "music": {
            "prompt": content_data.get("audio_prompt", ""),
            "vibe": strategy.get("audio_vibe", ""),
            "duration_secs": 15,
            "volume": "Background music ducked to 18% to keep voiceover clear",
        },

        # ── 5. VOICEOVER ───────────────────────────────────────────
        "voiceover": {
            "script": voiceover,
            "cta_append": content_data.get("cta_voice", ""),
            "full_script": f"{voiceover} {content_data.get('cta_voice', '')}".strip(),
            "voice": "Kokoro TTS (af_sarah — warm American female)",
            "language": "English",
            "generation_source": "Kokoro (fal.ai)",
        },

        # ── 6. ON-SCREEN TEXT ──────────────────────────────────────
        "on_screen_text": {
            "hook": strategy.get("hook_text", ""),
            "mid_reel": strategy.get("on_screen_text") or "(none — visual is self-explanatory)",
            "subtitle_style": "Word-by-word, centered, bold. Keywords highlighted in yellow (Alex Hormozi style)",
        },

        # ── 7. END-CARD ────────────────────────────────────────────
        "end_card": {
            "duration_secs": 3,
            "follow_line": strategy.get("cta_handle", ""),
            "url_line": strategy.get("cta_url", ""),
            "background": "Black frame matching video resolution, ASS-burned text",
        },

        # ── 8. STRATEGY META ───────────────────────────────────────
        "meta": {
            "topic": content_data.get("topic", ""),
            "emotion": strategy.get("emotion", ""),
            "narrative": strategy.get("narrative", ""),
        },
    }
    log.step("build_script", "OUT",
             topic=content_data.get("topic"),
             emotion=strategy.get("emotion"),
             voiceover_words=len(voiceover.split()),
             caption_words=len(strategy.get("caption", "").split())
    )
    return script


def save_script(script: dict, run_dir: str) -> str:
    """
    Writes the script dict to `SCRIPT.json` in the run directory.
    Returns the file path.
    """
    script_path = os.path.join(run_dir, "SCRIPT.json")

    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script, f, indent=2, ensure_ascii=False)

    log.step("save_script", "OUT", script_path=script_path)
    return script_path


def script_to_markdown(script: dict) -> str:
    """
    Renders the script dict as a clean, human-readable Markdown document.
    Useful for copy-pasting into Notion, Google Docs, etc.
    """
    lines = []
    lines.append("# Video Script\n")

    # Image
    img = script.get("image", {})
    lines.append("## 1. Imagen\n")
    lines.append(f"**Descripción:** {img.get('description', '')}\n")
    lines.append(f"**Estilo visual:** {img.get('style_anchor', '')}\n")
    lines.append(f"**Composición:** {img.get('composition', '')}\n")
    lines.append(f"**Propósito:** {img.get('purpose', '')}\n")
    lines.append("")

    # Video
    vid = script.get("video", {})
    lines.append("## 2. Video\n")
    lines.append(f"**Descripción:** {vid.get('description', '')}\n")
    lines.append(f"**Duración:** {vid.get('duration_secs', 15)}s\n")
    lines.append(f"**Resolución:** {vid.get('resolution', '')}\n")
    lines.append(f"**Hook visual:** {vid.get('hook_visual', '')}\n")
    lines.append(f"**Hook texto:** {vid.get('hook_text', '')}\n")
    lines.append(f"**Loop:** {vid.get('loop_design', '')}\n")
    lines.append("")

    # Shot breakdown
    shots = vid.get("shot_breakdown", [])
    if shots:
        lines.append("### Shot Breakdown\n")
        lines.append("| Tiempo | Arco | Voiceover | Texto en pantalla | Dirección |")
        lines.append("|--------|------|-----------|-------------------|-----------|")
        for s in shots:
            lines.append(
                f"| {s['time']} | {s['arc']} | {s['voiceover']} | {s.get('on_screen_text') or '-'} | {s['direction']} |"
            )
        lines.append("")

    # Caption
    cap = script.get("caption", {})
    lines.append("## 3. Caption\n")
    lines.append(f"```\n{cap.get('text', '')}\n```\n")
    lines.append(f"**Hashtags ({len(cap.get('hashtags', []))}):** {', '.join('#' + h for h in cap.get('hashtags', []))}\n")
    lines.append(f"**CTA:** {cap.get('cta', '')}\n")
    lines.append("")

    # Music
    mus = script.get("music", {})
    lines.append("## 4. Música\n")
    lines.append(f"**Prompt:** {mus.get('prompt', '')}\n")
    lines.append(f"**Vibe:** {mus.get('vibe', '')}\n")
    lines.append(f"**Duración:** {mus.get('duration_secs', 15)}s\n")
    lines.append(f"**Volumen:** {mus.get('volume', '')}\n")
    lines.append("")

    # Voiceover
    vo = script.get("voiceover", {})
    lines.append("## 5. Voiceover\n")
    lines.append(f"**Full script:** {vo.get('full_script', '')}\n")
    lines.append(f"**Voz:** {vo.get('voice', '')}\n")
    lines.append("")

    # End-card
    ec = script.get("end_card", {})
    lines.append("## 6. End-Card (3s)\n")
    lines.append(f"**Follow:** {ec.get('follow_line', '')}\n")
    lines.append(f"**URL:** {ec.get('url_line', '')}\n")
    lines.append("")

    # Meta
    meta_ = script.get("meta", {})
    lines.append("## 7. Estrategia\n")
    lines.append(f"**Tema:** {meta_.get('topic', '')}\n")
    lines.append(f"**Emoción:** {meta_.get('emotion', '')}\n")
    lines.append(f"**Narrativa:** {meta_.get('narrative', '')}\n")

    return "\n".join(lines)


def generate_script(strategy: dict, content_data: dict, run_dir: str) -> str:
    """
    Full flow: build → save JSON → save Markdown → return path.
    """
    log.step("generate_script", "IN",
             topic=content_data.get("topic"),
             emotion=strategy.get("emotion"))

    script = build_script(strategy, content_data)

    # Save JSON
    json_path = save_script(script, run_dir)

    # Save Markdown companion
    md_content = script_to_markdown(script)
    md_path = os.path.join(run_dir, "SCRIPT.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    log.step("generate_script", "OUT",
             json_path=json_path,
             md_path=md_path)

    return json_path
