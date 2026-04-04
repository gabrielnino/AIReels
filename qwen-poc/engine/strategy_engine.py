import json
from service.llm_service import generate_text
from utils.logger import get_logger
from utils.json_utils import clean_llm_json

log = get_logger(__name__)


def run_strategy_engine(topic: str, score: float, reason: str,
                        angle: str = "", why_now: str = "") -> dict:
    """
    Given a winning topic, generates a full Instagram Reel content strategy:
      - narrative, hook, emotion, motion_prompt
      - caption, hashtags, cta, on_screen_text
    """
    log.step("run_strategy_engine", "IN", topic=topic, score=score,
             reason=reason, angle=angle, why_now=why_now)

    system_prompt = (
        "You are a top-tier Instagram Reels creator with 2M+ followers and a proven track record "
        "of generating viral content for local lifestyle brands in Vancouver, Canada. "
        "You know exactly what stops the scroll in the first 2 seconds, how to build tension "
        "through a 10-second arc, and how to convert views into link-in-bio clicks. "
        "You write hooks that feel NATIVE to Instagram — not like ads. "
        "You never use corporate language. You always write like a real person who lives in Vancouver."
    )

    angle_line = f"Visual angle to exploit: {angle}" if angle else ""
    why_now_line = f"Why it's blowing up RIGHT NOW: {why_now}" if why_now else ""

    prompt = f"""
You're scripting a 10-second Instagram Reel that will stop the scroll, get saved, and drive traffic.

Topic: "{topic}"
Virality Score: {score}/10
Why selected: {reason}
{angle_line}
{why_now_line}

REEL STRUCTURE (strict 10-second arc):
- 0–2s: PATTERN INTERRUPT hook — something unexpected, bold, or controversial that freezes the thumb
- 2–6s: PAYOFF / REVEAL — the interesting thing that delivers on the hook's promise
- 6–8s: EMOTIONAL PEAK — the moment that makes them feel something (desire, FOMO, surprise, delight)
- 8–10s: CTA — one clear action they can take RIGHT NOW

HOOK FORMULAS to choose from (pick the best fit for this topic):
  - "POV: you just discovered [X] in Vancouver"
  - "Nobody is talking about [X] but it's actually insane"
  - "Wait until you see [X] — I was shook"
  - "I tried [X] so you don't have to (here's the truth)"
  - Bold TEXT ON SCREEN with no explanation — let curiosity do the work
  - A shocking close-up or extreme detail that makes them wonder "what IS that?"

CAPTION RULES:
  - First line = same energy as the hook (must work without seeing the video)
  - Use line breaks for readability
  - 1–2 emojis max, used strategically not decoratively
  - End with a soft CTA: "Details in bio 👆" or "Link in bio to explore"
  - No hashtags in the caption body — keep them clean

AUDIO DIRECTION:
  - Pick a vibe: trending upbeat pop, lo-fi chill, hype trap, cinematic swell, or viral sound-bite style
  - Match the emotional arc of the reel (builds to the peak moment)

Respond STRICTLY with a single valid JSON object. No markdown, no code blocks, no comments.
{{
  "narrative": "One sentence: the full 10-second emotional arc from first frame to last.",
  "hook": "EXACT visual description of seconds 0–2. What does the viewer SEE that stops them? Be hyper-specific about subject, framing, action.",
  "hook_text": "The bold on-screen text that appears in the first 2 seconds. Short, punchy, native Instagram. Max 8 words. Can be a question, bold claim, or POV opener.",
  "emotion": "The ONE emotion the reel must trigger. Choose: desire / FOMO / surprise / delight / curiosity / nostalgia / pride",
  "motion_prompt": "Cinematic AI video direction. Specify: camera move (push-in, whip pan, slow zoom, handheld shake), pacing (fast cuts / slow burn), and key visual moment. Under 25 words.",
  "audio_vibe": "One of: upbeat pop / lo-fi chill / hype trap / cinematic swell / viral sound-bite. Add 5 words of mood description.",
  "voiceover_script": "A punchy English narration script for a 10-second reel voiceover. Natural, conversational, NOT corporate. Mirrors the hook_text energy. 2–3 short sentences max (~25 words total). Must feel like a real Vancouver local talking. Example: 'Okay wait — this literally just opened in Gastown. Cheez Whiz AND caviar on a hot dog. I can't stop thinking about it.'",
  "caption": "Full Instagram caption. First line is a hook. Use line breaks. 2 emojis max. End with soft CTA to bio link. Max 120 words.",
  "hashtags": ["exactly", "20", "hashtags", "without", "hash", "symbol", "mix", "of", "niche", "geo", "trending"],
  "cta": "On-screen CTA text for seconds 8–10. Ultra-short action. Max 6 words. Example: 'Link in bio 👆' or 'Save this 🔖'",
  "on_screen_text": "Mid-reel text overlay (seconds 3–7). The KEY MESSAGE in max 5 words. Use null only if the visual is self-explanatory."
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
                 hook_text=strategy.get("hook_text"),
                 emotion=strategy.get("emotion"),
                 motion_prompt=strategy.get("motion_prompt"),
                 audio_vibe=strategy.get("audio_vibe"),
                 voiceover_script=strategy.get("voiceover_script"),
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
