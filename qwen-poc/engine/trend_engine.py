"""
trend_engine.py
===============
Fetches real-time signals from multiple query angles, deduplicates,
and uses DeepSeek to synthesize them into ranked, specific video topics.

Improvements over v1:
  - Wider query coverage (12 queries vs 7, including arts/outdoor/family)
  - Uses ALL unique results (up to 30 snippets) instead of just the first 10
  - Asks the LLM to rank topics by visual + viral potential
  - Returns richer topic objects {topic, angle, why_now} instead of bare strings
  - Filters out evergreen/non-time-sensitive content at synthesis time
"""

import json
from service.search_service import search
from service.llm_service import generate_text
from utils.logger import get_logger
from utils.json_utils import clean_llm_json

log = get_logger(__name__)

# ── Query bank: broad enough to surface diverse opportunities ─────────────────
SEARCH_QUERIES = [
    "events vancouver this week",
    "things to do vancouver this weekend",
    "trending food restaurants vancouver",
    "new openings bars restaurants vancouver",
    "live music concerts vancouver",
    "arts festivals cultural events vancouver",
    "outdoor activities nature vancouver",
    "sports games vancouver",
    "nightlife parties vancouver",
    "family events kids vancouver",
    "pop-ups markets vancouver",
    "trending vancouver instagram",
]


def fetch_search_trends() -> list:
    """Runs all queries and returns a flat deduplicated list of result dicts."""
    log.step("fetch_search_trends", "IN", total_queries=len(SEARCH_QUERIES))

    raw_results = []
    for q in SEARCH_QUERIES:
        try:
            res = search(q, count=10)
            if res and res.get("web", {}).get("results"):
                hits = res["web"]["results"]
                raw_results.extend(hits)
                log.step("fetch_search_trends", "INFO", query=q, hits=len(hits))
        except Exception as e:
            log.step("fetch_search_trends", "ERR", query=q, error=str(e))

    unique = deduplicate_results(raw_results)
    log.step("fetch_search_trends", "OUT", raw_total=len(raw_results), unique_total=len(unique))
    return unique


def deduplicate_results(results: list) -> list:
    """Removes results with duplicate title+url keys."""
    log.step("deduplicate_results", "IN", count=len(results))
    seen = set()
    unique = []
    for r in results:
        title = (r.get("title") or "").strip().lower()
        url = (r.get("url") or "").strip().lower()
        key = (title, url)
        if key not in seen:
            seen.add(key)
            unique.append(r)
    log.step("deduplicate_results", "OUT",
             duplicates_removed=len(results) - len(unique),
             unique=len(unique))
    return unique


def synthesize_topics(raw_results: list) -> list:
    """
    Uses DeepSeek to turn raw search results into 6-8 specific, ranked video topics.

    Returns a list of dicts:
      [{"topic": str, "angle": str, "why_now": str}, ...]

    - topic    : concise, specific reel subject (e.g. "Cherry Blossom Festival at Queen Elizabeth Park")
    - angle    : the unique visual hook / storytelling angle
    - why_now  : why this is timely and relevant RIGHT NOW
    """
    log.step("synthesize_topics", "IN", results_count=len(raw_results))

    if not raw_results:
        log.step("synthesize_topics", "OUT", topics=[], reason="no results to synthesize")
        return []

    # Use up to 30 snippets to give the LLM richer context
    snippets = [
        f"- {r.get('title', '')}: {r.get('description', '')}"
        for r in raw_results[:30]
    ]
    context_text = "\n".join(snippets)
    log.step("synthesize_topics", "INFO",
             snippets_used=len(snippets),
             context_preview=context_text[:200])

    prompt = f"""
You are a viral Instagram Reels strategist for a Vancouver lifestyle brand.

Here are fresh search results about what's happening in Vancouver RIGHT NOW:
{context_text}

Your task:
1. Identify 6-8 DISTINCT, SPECIFIC, TIME-SENSITIVE video topics from these results.
   - "Specific" means: name the event, venue, neighbourhood, or product — not just a category.
   - "Time-sensitive" means: happening this week/month — NOT evergreen content.
   - "Distinct" means: no two topics should be about the same event/theme.
2. For each topic, define:
   - "topic"    : the specific reel subject (≤12 words)
   - "angle"    : the unique visual storytelling hook (≤15 words)
   - "why_now"  : one sentence on why this is timely RIGHT NOW
3. Rank them from HIGHEST to LOWEST visual + viral potential for Instagram Reels.
4. Discard anything: political, tragic, criminal, weather-only, or with zero visual potential.

Respond ONLY with a valid JSON array. No markdown, no code blocks, no comments.
[
  {{"topic": "...", "angle": "...", "why_now": "..."}},
  ...
]
"""

    system_prompt = (
        "You are a sharp social media strategist. "
        "You output ONLY valid JSON arrays. No prose, no markdown."
    )
    log.step("synthesize_topics", "INFO", message="Calling DeepSeek to synthesize topics...")
    response = generate_text(prompt=prompt, model="deepseek-chat", system_prompt=system_prompt)
    log.step("synthesize_topics", "INFO", raw_llm_response=response)

    try:
        topics = json.loads(clean_llm_json(response))
        # Normalise: accept both plain strings (legacy) and dicts
        normalised = []
        for t in topics:
            if isinstance(t, dict):
                normalised.append(t)
            elif isinstance(t, str):
                normalised.append({"topic": t, "angle": "", "why_now": ""})

        log.step("synthesize_topics", "OUT", topics_count=len(normalised), topics=normalised)
        return normalised

    except json.JSONDecodeError as e:
        log.step("synthesize_topics", "ERR", error=str(e), raw_response=response)
        return []


def run_trend_engine() -> list:
    """Main entry: fetch → deduplicate → synthesize. Returns list of topic dicts."""
    log.step("run_trend_engine", "IN")
    results = fetch_search_trends()
    topics = synthesize_topics(results)
    log.step("run_trend_engine", "OUT", topics_found=len(topics), topics=topics)
    return topics
