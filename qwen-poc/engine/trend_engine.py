import json
from service.search_service import search
from service.llm_service import generate_text

def fetch_search_trends() -> list:
    """Executes strategic queries to find recent events and trends."""
    queries = [
        "events vancouver this week",
        "trending food vancouver",
        "trending news vancouver",
        "trending sports vancouver",
        "beer, wine, spirits vancouver",
        "nightlife vancouver",
        "live music vancouver"
    ]
    
    raw_results = []
    for q in queries:
        try:
            res = search(q, count=10)
            # Safe extraction for Brave Search format
            if res and res.get("web", {}).get("results"):
                raw_results.extend(res["web"]["results"])
        except Exception as e:
            print(f"[Trend Engine] Search failed for '{q}': {e}")
            
    extracted_value = deduplicate_results(raw_results)
    return extracted_value

def deduplicate_results(results: list) -> list:
    seen = set()
    unique = []

    for r in results:
        title = (r.get("title") or "").strip().lower()
        url = (r.get("url") or "").strip().lower()
        key = (title, url)

        if key in seen:
            continue

        seen.add(key)
        unique.append(r)

    return unique

def synthesize_topics(raw_results: list) -> list:
    """Uses Qwen Max to group noise into clear, actionable topics."""
    if not raw_results:
        return []
        
    snippets = [f"- {r.get('title')}: {r.get('description')}" for r in raw_results[:10]]
    context_text = "\n".join(snippets)
    
    prompt = f"""
    Given the following search results about what's happening in Vancouver right now:
    {context_text}
    
    Your task is to synthesize this noise into 3-5 distinct, clear, highly engaging video ideas (topics). 
    Group similar results. Eliminate exact duplicates. Keep the output strictly as a JSON list of strings.
    Example: ["Canucks hockey game tonight", "Food festivals downtown", "Outdoor movie watch party"]
    Output ONLY a valid JSON list.
    """
    
    print("[Trend Engine] Synthesizing raw searches into topics via Qwen-Max...")
    system_prompt = "You are a highly analytical AI capable of extreme conciseness and valid JSON output."
    
    response = generate_text(prompt=prompt, model="qwen-max", system_prompt=system_prompt)
    
    try:
        # Clean up any potential markdown formatting the LLM might append automatically
        clean_json = response.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json.split("```json")[1]
        if clean_json.endswith("```"):
            clean_json = clean_json.rsplit("```", 1)[0]
            
        topics = json.loads(clean_json.strip())
        return topics
    except json.JSONDecodeError as e:
        print(f"[Trend Engine] Failed to parse Qwen JSON output: {e}\nRaw Response:\n{response}")
        return []

def run_trend_engine() -> list:
    results = fetch_search_trends()
    return synthesize_topics(results)
