import json
from service.llm_service import generate_text


def run_strategy_engine(topic: str, score: float, reason: str) -> dict:
    """
    Given a winning topic, generates a full Instagram Reel content strategy:
    - narrative: what story the reel tells in 10 seconds
    - hook: what happens in the first 2 seconds to stop the scroll
    - emotion: the feeling it must provoke (FOMO, awe, humor, curiosity)
    - motion_prompt: specific cinematic motion prompt for the video model
    - caption: full Instagram caption with hook + context + CTA
    - hashtags: segmented hashtag list (niche + geo + trending)
    - cta: exact call to action text
    - on_screen_text: optional text overlay to display on the video
    """
    print(f"[Strategy Engine] Building content strategy for: '{topic}'")

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

Respond STRICTLY with a single valid JSON object in this exact format (no markdown, no explanation):
{{
  "narrative": "What story this 10-second reel tells. One sentence describing the arc from frame 1 to last frame.",
  "hook": "What happens in the FIRST 2 SECONDS to stop the scroll. Be very specific and visual.",
  "emotion": "The primary emotion this reel must provoke. One word or short phrase.",
  "motion_prompt": "A specific, vivid cinematic motion description for the AI video model. Focus on camera movement, energy, pacing. Under 20 words.",
  "caption": "The full Instagram caption. Start with a scroll-stopping first line, add context, end with a CTA pointing to link in bio. Max 150 words.",
  "hashtags": ["list", "of", "20", "relevant", "hashtags", "mix", "of", "niche", "geo", "trending"],
  "cta": "The exact call-to-action text to overlay or include. Short and punchy. Max 8 words.",
  "on_screen_text": "Short text to display on screen during the reel. Max 6 words. Optional, use null if not needed."
}}
"""

    print("[Strategy Engine] Calling DeepSeek for strategy generation...")
    response = generate_text(prompt=prompt, model="deepseek-chat", system_prompt=system_prompt)

    try:
        clean = response.strip()
        if clean.startswith("```json"):
            clean = clean.split("```json")[1]
        if clean.startswith("```"):
            clean = clean.split("```")[1]
        if clean.endswith("```"):
            clean = clean.rsplit("```", 1)[0]

        strategy = json.loads(clean.strip())

        print(f"[Strategy Engine] Narrative:     {strategy.get('narrative')}")
        print(f"[Strategy Engine] Hook:          {strategy.get('hook')}")
        print(f"[Strategy Engine] Emotion:       {strategy.get('emotion')}")
        print(f"[Strategy Engine] Motion Prompt: {strategy.get('motion_prompt')}")
        print(f"[Strategy Engine] CTA:           {strategy.get('cta')}")

        return strategy

    except (json.JSONDecodeError, Exception) as e:
        print(f"[Strategy Engine] Failed to parse strategy JSON: {e}. Using defaults.")
        return {
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
