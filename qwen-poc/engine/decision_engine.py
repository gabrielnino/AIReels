import json
from service.llm_service import generate_text
from engine.memory_engine import is_topic_used

def evaluate_topic(topic: str) -> dict:
    """Uses Qwen Max to enforce hard rules and score the topic's visual/viral value."""
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
    
    RESPOND STRICTLY WITH A JSON OBJECT IN THIS EXACT FORMAT:
    {{
      "topic": "{topic}",
      "final_score": 8.7, // 0.0 to 10.0 scale, use 0.0 if excluded by hard rules
      "reason": "Brief explanation of why it scored this."
    }}
    Do not output any markdown code blocks, just raw valid JSON.
    """
    
    print(f"[Decision Engine] Evaluating topic: '{topic}'")
    
    try:
        response = generate_text(prompt, model="deepseek-chat", system_prompt=system_prompt)
        
        clean_json = response.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json.split("```json")[1]
        elif clean_json.startswith("```"):
            clean_json = clean_json.split("```")[1]
        if clean_json.endswith("```"):
            clean_json = clean_json.rsplit("```", 1)[0]
        
        return json.loads(clean_json.strip())
    except Exception as e:
        print(f"[Decision Engine] Failed evaluation for '{topic}'. Using fallback score. Error: {e}")
        return {"topic": topic, "final_score": 0.0, "reason": f"API/Parse Error: {e}"}

def run_decision_engine(raw_topics: list) -> dict:
    """Filters, evals via DeepSeek, checks Memory, and returns the highest scoring topic."""
    evaluated = []
    
    for raw in raw_topics:
        # Step 1: Memory Check
        if is_topic_used(raw):
            print(f"[Decision Engine] SKIPPING '{raw}' (Already explored recently)")
            continue
            
        # Step 2: LLM Scoring
        result = evaluate_topic(raw)
        evaluated.append(result)
        
    if not evaluated:
        return None
        
    # Sort descending by final_score
    evaluated.sort(key=lambda x: x.get("final_score", 0), reverse=True)
    best_topic = evaluated[0]
    
    if best_topic.get("final_score", 0) <= 0.0:
        print("[Decision Engine] All candidate topics scored 0 (Triggered Exclusion Rules).")
        return None
        
    return best_topic
