import json
from service.llm_service import generate_text
from utils.logger import get_logger
from utils.json_utils import clean_llm_json

log = get_logger(__name__)


def run_strategy_engine(topic: str, score: float, reason: str) -> dict:
    """
    Given a winning topic, generates a full Instagram Reel content strategy:
      - narrative, hook, emotion, motion_prompt
      - caption, hashtags, cta, on_screen_text
    """
    log.step("run_strategy_engine", "IN", topic=topic, score=score, reason=reason)

    system_prompt = (
        "You are a world-class Instagram growth strategist and viral content director "
        "specializing in short-form video for local lifestyle brands in Vancouver, Canada. "
        "You deeply understand the Instagram algorithm, scroll-stopping hooks, and how to "
        "drive traffic from Reels to external portals."
    )

    prompt = f"""
A trending topic has been selected for an Instagram Reel in Vancouver:

Topic: "{topic}"
Virality Score: {score}/10
Why it was selected: {reason}

Your job is to design a complete content strategy for a 10-second Instagram Reel on this topic.
The goal is maximum engagement AND driving traffic to our portal (link in bio).

Respond STRICTLY with a single valid JSON object. No markdown, no code blocks, no comments.
{{
  "narrative": "What story this 10-second reel tells. One sentence describing the arc from frame 1 to last frame.",
  "hook": "What happens in the FIRST 2 SECONDS to stop the scroll. Be very specific and visual.",
  "emotion": "The primary emotion this reel must provoke. One word or short phrase.",
  "motion_prompt": "A specific vivid cinematic motion description for the AI video model. Focus on camera movement, energy, pacing. Under 20 words.",
  "caption": "The full Instagram caption. Start with a scroll-stopping first line, add context, end with a CTA pointing to link in bio. Max 150 words.",
  "hashtags": ["list", "of", "20", "relevant", "hashtags", "mix", "of", "niche", "geo", "trending"],
  "cta": "The exact call-to-action text to overlay or include. Short and punchy. Max 8 words.",
  "on_screen_text": "Short text to display on screen during the reel. Max 6 words. Use null if not needed."
}}
"""

    log.step("run_strategy_engine", "INFO", message="Calling DeepSeek for strategy generation...")
    response = generate_text(prompt=prompt, model="deepseek-chat", system_prompt=system_prompt)
    log.step("run_strategy_engine", "INFO", raw_llm_response=response)

    try:
        strategy = json.loads(clean_llm_json(response))

        log.step("run_strategy_engine", "OUT",
                 narrative=strategy.get("narrative"),
                 hook=strategy.get("hook"),
                 emotion=strategy.get("emotion"),
                 motion_prompt=strategy.get("motion_prompt"),
                 cta=strategy.get("cta"),
                 on_screen_text=strategy.get("on_screen_text"),
                 hashtags_count=len(strategy.get("hashtags", [])))
        return strategy

    except (json.JSONDecodeError, Exception) as e:
        log.step("run_strategy_engine", "ERR", error=str(e), raw_response=response)
        fallback = {
            "narrative": f"A dynamic visual showcase of {topic} in Vancouver.",
            "hook": "Fast-cut opening shot with bold energy.",
            "emotion": "curiosity",
            "motion_prompt": "dynamic cinematic pan, energetic movement, vibrant atmosphere",
            "caption": f"Vancouver's hottest right now 👀 {topic}\n\nDon't miss out — link in bio for more.",
            "hashtags": ["#vancouver", "#vancouverlife", "#yvr", "#vancouverfood",
                         "#604", "#explorebc", "#vancouverevents", "#instyvr",
                         "#vancouverrestaurants", "#bclife"],
            "cta": "Check the link in bio 🔗",
            "on_screen_text": None,
        }
        log.step("run_strategy_engine", "INFO", message="Using fallback strategy", fallback=fallback)
        return fallback
