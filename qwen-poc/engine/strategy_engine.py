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
      - caption, hashtags, cta, cta_url, cta_handle, on_screen_text
      - loop-aware (final line references the hook for seamless replay)
    """
    log.step("run_strategy_engine", "IN", topic=topic, score=score,
             reason=reason, angle=angle, why_now=why_now)

    system_prompt = (
        "You are a top-tier Instagram Reels creator with 2M+ followers and a proven track record "
        "of generating viral content for local lifestyle brands in Vancouver, Canada. "
        "You know exactly what stops the scroll in the first 2 seconds, how to build tension "
        "through a 15-second arc, and how to convert views into link-in-bio clicks. "
        "You write hooks that feel NATIVE to Instagram - not like ads. "
        "You never use corporate language. You always write like a real person who lives in Vancouver."
    )

    angle_line = f"Visual angle to exploit: {angle}" if angle else ""
    why_now_line = f"Why it's blowing up RIGHT NOW: {why_now}" if why_now else ""

    prompt = f"""
You're scripting a 15-second Instagram Reel that will stop the scroll, get saved, and drive traffic.

Topic: "{topic}"
Virality Score: {score}/10
Why selected: {reason}
{angle_line}
{why_now_line}

REEL STRUCTURE (strict 15-second arc):
- 0-3s: PATTERN INTERRUPT hook - bold on-screen text, the scroll-stopper
- 3-8s: PAYOFF / REVEAL - delivers on the hook's promise
- 8-12s: EMOTIONAL PEAK - desire, FOMO, surprise, delight
- 12-15s: CTA + LOOP - clear action + line that references the hook for seamless replay

HOOK FORMULAS (choose the best fit for this topic):
  - "POV: you just discovered [X] in Vancouver"
  - "Nobody is talking about [X] but it's actually insane"
  - "Wait until you see [X] - I was shook"
  - "I tried [X] so you don't have to (here's the truth)"
  - BOLD TEXT ON SCREEN with no explanation - let curiosity do the work
  - A shocking close-up or extreme detail that makes them wonder "what IS that?"

LOOP RULE:
  - The final voiceover line must reference or echo the hook so replay feels seamless.

CAPTION RULES:
  - First line = same energy as the hook (must work without seeing the video)
  - Use line breaks for readability
  - 1-2 emojis max, used strategically not decoratively
  - End with soft CTA: "Details in bio" or "Link in bio to explore"
  - No hashtags in the caption body - keep them clean

AUDIO DIRECTION:
  - Pick a vibe: trending upbeat pop, lo-fi chill, hype trap, cinematic swell, or viral sound-bite style
  - Match the emotional arc of the reel (builds to the peak moment)

VOICEOVER RULES:
  - Natural, conversational English - NOT corporate
  - 3-4 short sentences (~35-40 words) for a 15-second reel
  - End with a line that references the hook to create a seamless loop

Respond STRICTLY with a single valid JSON object. No markdown, no code blocks, no comments.
{{
  "narrative": "One sentence: the full 15-second emotional arc from first frame to last.",
  "hook": "EXACT visual description of seconds 0-3. What does the viewer SEE that stops them? Be hyper-specific about subject, framing, action.",
  "hook_text": "The bold on-screen text that appears in the first 3 seconds. Short, punchy, native Instagram. Max 8 words.",
  "emotion": "The ONE emotion the reel must trigger. Choose: desire / FOMO / surprise / delight / curiosity / nostalgia / pride",
  "motion_prompt": "Cinematic AI video direction. Specify: camera move, pacing, and key visual moment. Under 25 words.",
  "audio_vibe": "One of: upbeat pop / lo-fi chill / hype trap / cinematic swell / viral sound-bite. Add 5 words of mood description.",
  "voiceover_script": "A punchy English narration script for a 15-second reel. Natural, conversational, NOT corporate. 3-4 short sentences (~35-40 words). End with a line that references the hook to create seamless loop.",
  "caption": "Full Instagram caption. First line is a hook. Use line breaks. 2 emojis max. End with soft CTA to bio link. Max 120 words.",
  "hashtags": ["exactly", "20", "hashtags", "without", "hash", "symbol", "mix", "of", "niche", "geo", "trending"],
  "cta": "On-screen CTA text for seconds 12-15. Ultra-short action. Max 6 words. Example: 'Link in bio' or 'Save this'",
  "cta_url": "The website URL to promote. Use 'tudominio.com' as placeholder.",
  "cta_handle": "The social media handle to promote. Use '@tuusuario' as placeholder.",
  "on_screen_text": "Mid-reel text overlay (seconds 3-8). The KEY MESSAGE in max 5 words. Use null only if the visual is self-explanatory."
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
            "narrative": f"A dynamic 15-second visual showcase of {topic} in Vancouver with a loop ending.",
            "hook": f"Did you know about {topic}? POV opening with bold close-up.",
            "hook_text": f"POV: {topic[:40]}",
            "emotion": "curiosity",
            "motion_prompt": "dynamic cinematic pan, energetic movement, vibrant atmosphere",
            "audio_vibe": "upbeat pop, driving beat, energetic rise, punchy drops",
            "voiceover_script": f"Okay wait — {topic} is literally trending in Vancouver right now. You need to see this. If that sounds wild, wait till you see this:",
            "caption": f"Vancouver's hottest right now: {topic} 👀\n\nDon't miss out - link in bio for more.",
            "hashtags": ["vancouver", "vancouverlife", "yvr", "trending",
                         "604", "explorebc", "vancouverevents", "instyvr",
                         "vancouverthings", "bclife"],
            "cta": "Link in bio",
            "cta_url": "tudominio.com",
            "cta_handle": "@tuusuario",
            "on_screen_text": None,
        }
        log.step("run_strategy_engine", "INFO", message="Using fallback strategy", fallback=fallback)
        return fallback
