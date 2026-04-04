"""
decision_engine.py
==================
Selects the single best topic for today's Reel from the trend engine output.

Improvements over v1:
  - Batch evaluation: scores ALL candidates in ONE LLM call (faster, cheaper,
    and forces the LLM to compare topics against each other)
  - Diversity enforcement: penalises categories already used recently
  - Richer scoring rubric: 5 dimensions (visual, viral, niche fit, FOMO,
    production feasibility) with explicit weights
  - Semantic similarity memory check via LLM (not just exact-match)
  - Returns enriched winner dict that feeds directly into strategy engine
"""

import json
from service.llm_service import generate_text
from engine.memory_engine import is_topic_used, get_recent_topics
from utils.logger import get_logger
from utils.json_utils import clean_llm_json

log = get_logger(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _topic_str(t) -> str:
    """Extracts the topic string from either a plain string or a dict."""
    if isinstance(t, dict):
        return t.get("topic", str(t))
    return str(t)


def _is_semantically_similar(new_topic: str, recent_topics: list[str]) -> bool:
    """
    Uses DeepSeek to check if new_topic is semantically too close to any
    of the recently published topics (last 14 days).
    Returns True if it's too similar (should be skipped).
    """
    if not recent_topics:
        return False

    recent_str = "\n".join(f"- {t}" for t in recent_topics)
    prompt = f"""
Is the following NEW topic semantically too similar to any of the RECENT topics?
"Too similar" means: same event, same venue, same theme, or overlapping audience.

NEW TOPIC: "{new_topic}"

RECENT TOPICS (published in last 14 days):
{recent_str}

Answer with ONLY a JSON object: {{"similar": true}} or {{"similar": false}}
No explanation, no markdown.
"""
    try:
        resp = generate_text(prompt, model="deepseek-chat",
                             system_prompt="You output only valid JSON.")
        result = json.loads(clean_llm_json(resp))
        return result.get("similar", False)
    except Exception:
        return False  # on error, allow the topic through


def _batch_score(candidates: list[dict], recent_category_tags: list[str]) -> list[dict]:
    """
    Scores all candidates in a single LLM call.

    Each candidate dict has: topic, angle, why_now
    Returns a list of scored dicts sorted descending by final_score.
    """
    if not candidates:
        return []

    recent_str = (
        "Recently published categories (slightly deprioritise these for diversity): "
        + ", ".join(recent_category_tags)
        if recent_category_tags
        else "None"
    )

    candidates_json = json.dumps(
        [{"id": i, "topic": c.get("topic", ""), "angle": c.get("angle", ""),
          "why_now": c.get("why_now", "")}
         for i, c in enumerate(candidates)],
        ensure_ascii=False,
        indent=2,
    )

    prompt = f"""
You are a ruthless Instagram Reels strategist for a Vancouver lifestyle brand.

Score each topic candidate below on a scale of 0-10.

HARD EXCLUSION (score = 0):
- Politics, crime, tragedy, pure weather/climate news
- Zero visual potential (abstract, text-heavy, or corporate)
- Anything that requires more than a 10-second clip to explain

SCORING DIMENSIONS (each 0-10, weighted):
  1. Visual potential     (weight 30%) — how cinematic, striking, scroll-stopping
  2. Viral / FOMO factor  (weight 25%) — shareability, urgency, "you had to be there"
  3. Niche fit            (weight 20%) — fits Vancouver lifestyle / events / food / culture
  4. Specificity          (weight 15%) — is it a REAL event/place/moment (not generic)?
  5. Timeliness           (weight 10%) — is it happening THIS week/month?

{recent_str}

CANDIDATES:
{candidates_json}

Return ONLY a valid JSON array — one object per candidate — ordered from HIGHEST to LOWEST final_score:
[
  {{
    "id": 0,
    "topic": "...",
    "final_score": 8.7,
    "category_tag": "food|music|outdoor|arts|nightlife|sports|family|other",
    "reason": "One sentence explaining the score."
  }},
  ...
]
No markdown, no code blocks, no extra text.
"""

    system_prompt = (
        "You are a data-driven social media analyst. "
        "Output ONLY valid JSON arrays. No prose."
    )

    log.step("_batch_score", "INFO",
             candidates_count=len(candidates),
             recent_categories=recent_category_tags)

    response = generate_text(prompt=prompt, model="deepseek-chat", system_prompt=system_prompt)
    log.step("_batch_score", "INFO", raw_llm_response=response)

    try:
        scored = json.loads(clean_llm_json(response))
        # Merge scores back into candidate dicts
        score_map = {s["id"]: s for s in scored if isinstance(s, dict)}
        result = []
        for i, c in enumerate(candidates):
            s = score_map.get(i, {})
            result.append({
                "topic": c.get("topic", ""),
                "angle": c.get("angle", ""),
                "why_now": c.get("why_now", ""),
                "final_score": float(s.get("final_score", 0)),
                "category_tag": s.get("category_tag", "other"),
                "reason": s.get("reason", ""),
            })
        result.sort(key=lambda x: x["final_score"], reverse=True)
        return result
    except Exception as e:
        log.step("_batch_score", "ERR", error=str(e))
        return []


# ── Main entry ────────────────────────────────────────────────────────────────

def run_decision_engine(raw_topics: list) -> dict | None:
    """
    Filters, scores, and selects the single best topic for today's Reel.

    Pipeline:
      1. Exact-match memory filter (O(1))
      2. Semantic similarity check vs last 14 days (LLM, only if needed)
      3. Batch scoring of all survivors (1 LLM call)
      4. Return highest scoring candidate above threshold
    """
    log.step("run_decision_engine", "IN",
             topics_count=len(raw_topics),
             topics=[_topic_str(t) for t in raw_topics])

    # ── Fetch recent context for diversity & similarity checks ────────────────
    recent_topics = get_recent_topics(days=14)
    recent_str_list = [t["original_topic"] for t in recent_topics]
    recent_categories = list({t.get("category_tag", "") for t in recent_topics
                               if t.get("category_tag")})

    log.step("run_decision_engine", "INFO",
             recent_topics_count=len(recent_str_list),
             recent_categories=recent_categories)

    # ── Step 1: Exact-match memory filter ────────────────────────────────────
    survivors = []
    for raw in raw_topics:
        topic_str = _topic_str(raw)
        if is_topic_used(topic_str):
            log.step("run_decision_engine", "INFO",
                     action="SKIPPED (exact-match memory)", topic=topic_str)
            continue
        survivors.append(raw if isinstance(raw, dict) else {"topic": topic_str, "angle": "", "why_now": ""})

    if not survivors:
        log.step("run_decision_engine", "OUT", result=None,
                 reason="all topics already used (exact match)")
        return None

    # ── Step 2: Semantic similarity filter ───────────────────────────────────
    if recent_str_list:
        fresh = []
        for candidate in survivors:
            topic_str = candidate["topic"]
            if _is_semantically_similar(topic_str, recent_str_list):
                log.step("run_decision_engine", "INFO",
                         action="SKIPPED (semantic similarity)", topic=topic_str)
            else:
                fresh.append(candidate)
        survivors = fresh if fresh else survivors  # fallback: keep all if all are similar

    if not survivors:
        log.step("run_decision_engine", "OUT", result=None,
                 reason="all topics too similar to recent content")
        return None

    # ── Step 3: Batch scoring ────────────────────────────────────────────────
    scored = _batch_score(survivors, recent_categories)

    if not scored:
        log.step("run_decision_engine", "OUT", result=None, reason="batch scoring returned empty")
        return None

    # ── Step 4: Pick winner above threshold ──────────────────────────────────
    MIN_SCORE = 6.0
    best = scored[0]

    if best["final_score"] < MIN_SCORE:
        log.step("run_decision_engine", "OUT", result=None,
                 reason=f"best score {best['final_score']} below threshold {MIN_SCORE}")
        return None

    log.step("run_decision_engine", "OUT",
             winner=best["topic"],
             score=best["final_score"],
             category=best["category_tag"],
             reason=best["reason"],
             all_scores=[(s["topic"], s["final_score"]) for s in scored])

    return best
