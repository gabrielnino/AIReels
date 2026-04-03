import json
from service.search_service import search
from service.llm_service import generate_text
from utils.logger import get_logger
from utils.json_utils import clean_llm_json

log = get_logger(__name__)


def fetch_search_trends() -> list:
    """Executes strategic queries to find recent events and trends in Vancouver."""
    queries = [
        "events vancouver this week",
        "trending food vancouver",
        "trending news vancouver",
        "trending sports vancouver",
        "beer, wine, spirits vancouver",
        "nightlife vancouver",
        "live music vancouver",
    ]
    log.step("fetch_search_trends", "IN", total_queries=len(queries))

    raw_results = []
    for q in queries:
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
    """Removes duplicate search results by title+url key."""
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
    log.step("deduplicate_results", "OUT", duplicates_removed=len(results) - len(unique), unique=len(unique))
    return unique


def synthesize_topics(raw_results: list) -> list:
    """Uses DeepSeek to synthesize raw search results into clear video topics."""
    log.step("synthesize_topics", "IN", results_count=len(raw_results))

    if not raw_results:
        log.step("synthesize_topics", "OUT", topics=[], reason="no results to synthesize")
        return []

    snippets = [f"- {r.get('title')}: {r.get('description')}" for r in raw_results[:10]]
    context_text = "\n".join(snippets)
    log.step("synthesize_topics", "INFO", snippets_used=len(snippets), context_preview=context_text[:200])

    prompt = f"""
    Given the following search results about what's happening in Vancouver right now:
    {context_text}

    Your task is to synthesize this noise into 3-5 distinct, clear, highly engaging video ideas (topics).
    Group similar results. Eliminate exact duplicates. Keep the output strictly as a JSON list of strings.
    Example: ["Canucks hockey game tonight", "Food festivals downtown", "Outdoor movie watch party"]
    Output ONLY a valid JSON list. No comments, no markdown.
    """

    system_prompt = "You are a highly analytical AI capable of extreme conciseness and valid JSON output."
    log.step("synthesize_topics", "INFO", message="Calling DeepSeek to synthesize topics...")

    response = generate_text(prompt=prompt, model="deepseek-chat", system_prompt=system_prompt)
    log.step("synthesize_topics", "INFO", raw_llm_response=response)

    try:
        topics = json.loads(clean_llm_json(response))
        log.step("synthesize_topics", "OUT", topics=topics)
        return topics

    except json.JSONDecodeError as e:
        log.step("synthesize_topics", "ERR", error=str(e), raw_response=response)
        return []


def run_trend_engine() -> list:
    """Main entry point: fetch trends → deduplicate → synthesize topics."""
    log.step("run_trend_engine", "IN")
    results = fetch_search_trends()
    topics = synthesize_topics(results)
    log.step("run_trend_engine", "OUT", topics_found=len(topics), topics=topics)
    return topics
