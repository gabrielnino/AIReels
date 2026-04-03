from engine.memory_engine import init_db, save_topic, update_topic_status
from engine.trend_engine import run_trend_engine
from engine.decision_engine import run_decision_engine
from engine.strategy_engine import run_strategy_engine
from engine.content_engine import run_content_engine
import time
import sys
import os

class LoggerWriter:
    def __init__(self, filepath):
        self.terminal = sys.stdout
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.log = open(filepath, "a", encoding="utf-8")
        self.log.write(f"\n\n--- NEW RUN: {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()
        
    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = LoggerWriter("logs/pipeline.log")
def run_reels_pipeline(execute_content: bool = True):
    print("====================================")
    print("🚀 STARTED REELS AUTOMATION PIPELINE")
    print("====================================")
    
    # 0. Initialize Memory DB
    init_db()
    
    # 1. Trend Engine: Extract candidates
    print("\n>>> STEP 1: DETECTING TRENDS")
    candidate_topics = run_trend_engine()
    
    if not candidate_topics:
        print("[Pipeline] No valid topics generated. Exiting.")
        return
        
    print(f"[Pipeline] Discovered {len(candidate_topics)} potential topic(s):")
    for t in candidate_topics:
        print(f" - {t}")
     
    # 2. Decision Engine: Filter & LLM Score via DeepSeek
    print("\n>>> STEP 2: DECISION ENGINE (FILTERING & SCORING)")
    winning_topic_data = run_decision_engine(candidate_topics)
    
    if not winning_topic_data:
        print("[Pipeline] No topics survived the filters and memory check. Exiting.")
        return
        
    topic = winning_topic_data.get("topic")
    score = winning_topic_data.get("final_score")
    reason = winning_topic_data.get("reason")
    
    print(f"\n[Pipeline] 🏆 WINNING TOPIC SELECTED: '{topic}'")
    print(f"[Pipeline] Score: {score}/10")
    print(f"[Pipeline] Rationale: {reason}")
    
    # 3. Store Memory Context
    # Add winning topic to database to prevent immediate reuse
    topic_id = save_topic(topic, status="selected", score=score)
    if topic_id:
        print(f"[Pipeline] Saved to memory (ID: {topic_id})")

    # 4. Strategy Engine: Define narrative, hook, caption, hashtags, CTA, motion prompt
    print("\n>>> STEP 3: STRATEGY ENGINE (CONTENT STRATEGY)")
    strategy = run_strategy_engine(topic, score=score, reason=reason)

    print(f"\n[Pipeline] 📋 CONTENT STRATEGY READY:")
    print(f"  Narrative:     {strategy.get('narrative')}")
    print(f"  Hook:          {strategy.get('hook')}")
    print(f"  Emotion:       {strategy.get('emotion')}")
    print(f"  Motion Prompt: {strategy.get('motion_prompt')}")
    print(f"  CTA:           {strategy.get('cta')}")
    print(f"  On-screen:     {strategy.get('on_screen_text')}")

    if not execute_content:
        print("\n[Pipeline] Execution completed (run_content disabled in param).")
        return

    # 5. Content Engine: Generation
    print("\n>>> STEP 4: CONTENT ENGINE (GENERATING ASSETS)")
    try:
        start_time = time.time()
        final_assets = run_content_engine(topic, strategy=strategy)

        # Output artifacts
        print("\n====================================")
        print("🎉 REELS GENERATION COMPLETE!")
        print(f"Time Taken:      {int(time.time() - start_time)} seconds")
        print(f"Theme:           {final_assets['topic']}")
        print(f"Emotion:         {final_assets['emotion']}")
        print(f"Image Prompt:    {final_assets['base_prompt']}")
        print(f"Base Image URL:  {final_assets['image_url']}")
        print(f"Video Path:      {final_assets['final_video_path']}")
        print(f"CTA:             {final_assets['cta']}")
        print(f"On-screen Text:  {final_assets['on_screen_text']}")
        print(f"\n📝 CAPTION READY TO PUBLISH:")
        print(f"{final_assets['caption']}")
        print(f"\n🏷️  HASHTAGS:")
        print(" ".join(final_assets.get('hashtags', [])))
        print("====================================")

        # 6. Finalize DB entry
        update_topic_status(topic, "published")

    except Exception as e:
        print(f"\n[Pipeline] Fatal error during content generation: {e}")
        update_topic_status(topic, "failed")


if __name__ == "__main__":
    # execute_content determines if the full pipeline runs. If false it only searches and decides
    run_reels_pipeline(execute_content=True)
