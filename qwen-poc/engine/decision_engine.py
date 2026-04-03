import json
from service.llm_service import generate_text
from engine.memory_engine import is_topic_used
from utils.logger import get_logger
from utils.json_utils import clean_llm_json

log = get_logger(__name__)


def evaluate_topic(topic: str) -> dict:
    """Uses DeepSeek to enforce hard rules and score the topic's visual/viral value."""
    log.step("evaluate_topic", "IN", topic=topic)

    system_prompt = "You are a ruthless social media strategist and content filter."
    prompt = f"""
    Evaluate the following topic for a short-form video (Reel): '{topic}'

    HARD RULES:
    1. EXCLUDE immediately (final_score = 0) if it involves: politics, tragedies, crime, weather/climate, or anything with zero visual potential.
    2. KEEP if it heavily features: events, food/culinary, entertainment, or social culture.

    SCORING CRITERIA:
    Assess its:
    - Relevance to the niche
    - Visual potential (how cinematic/striking can it be?)
    - Viral potential (shareability, FOMO)
    - Commercial or engagement potential

    RESPOND STRICTLY WITH A VALID JSON OBJECT IN THIS EXACT FORMAT (no comments, no markdown):
    {{
      "topic": "{topic}",
      "final_score": 8.7,
      "reason": "Brief explanation of why it scored this."
    }}
    """

    try:
        response = generate_text(prompt, model="deepseek-chat", system_prompt=system_prompt)
        log.step("evaluate_topic", "INFO", topic=topic, raw_llm_response=response)

        result = json.loads(clean_llm_json(response))
        log.step("evaluate_topic", "OUT", topic=topic, final_score=result.get("final_score"), reason=result.get("reason"))
        return result

    except Exception as e:
        log.step("evaluate_topic", "ERR", topic=topic, error=str(e))
        return {"topic": topic, "final_score": 0.0, "reason": f"Parse/API Error: {e}"}


def run_decision_engine(raw_topics: list) -> dict:
    """Filters topics via memory, scores them via LLM, returns the highest scoring one."""
    log.step("run_decision_engine", "IN", topics_count=len(raw_topics), topics=raw_topics)

    evaluated = []
    for raw in raw_topics:
        # Step 1: Memory check — skip already used topics
        if is_topic_used(raw):
            log.step("run_decision_engine", "INFO", action="SKIPPED (memory)", topic=raw)
            continue

        # Step 2: LLM scoring
        result = evaluate_topic(raw)
        evaluated.append(result)

    if not evaluated:
        log.step("run_decision_engine", "OUT", result=None, reason="all topics filtered or skipped")
        return None

    # Sort descending by score
    evaluated.sort(key=lambda x: x.get("final_score", 0), reverse=True)
    best = evaluated[0]

    if best.get("final_score", 0) <= 0.0:
        log.step("run_decision_engine", "OUT", result=None, reason="all scores were 0 (hard rule exclusion)")
        return None

    log.step("run_decision_engine", "OUT",
             winner=best.get("topic"),
             score=best.get("final_score"),
             reason=best.get("reason"))
    return best
