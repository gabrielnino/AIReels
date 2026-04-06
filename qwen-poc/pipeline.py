import sys
import time

# ── Init the run directory FIRST so the log file is created immediately ───────
# This must happen before any engine import, because those modules call
# get_logger() at import time, which opens the FileHandler.
from utils.run_context import init_run
init_run()  # creates outputs/run_YYYYMMDD_HHMMSS/ and pipeline.log right away

from engine.memory_engine import init_db, save_topic, update_topic_status, clear_database
from engine.trend_engine import run_trend_engine
from engine.decision_engine import run_decision_engine
from engine.strategy_engine import run_strategy_engine
from engine.content_engine import run_content_engine
from utils.logger import get_logger

log = get_logger(__name__)


def run_reels_pipeline(execute_content: bool = True, language: str = "en"):
    from utils.run_context import get_run_dir
    run_dir = get_run_dir()
    log.info("=" * 44)
    log.info("🚀 STARTED REELS AUTOMATION PIPELINE")
    log.info(f"📁 Run output folder: {run_dir}")
    log.info(f"🌐 Language: {language}")
    log.info("=" * 44)

    init_db()

    log.step("run_reels_pipeline", "INFO", step="1/4 - Detecting trends")
    candidate_topics = run_trend_engine()

    if not candidate_topics:
        log.step("run_reels_pipeline", "OUT", result="exit", reason="No valid topics generated")
        return

    log.step("run_reels_pipeline", "INFO",
             message=f"Discovered {len(candidate_topics)} potential topic(s)",
             topics=candidate_topics)

    log.step("run_reels_pipeline", "INFO", step="2/4 - Decision engine (filtering & scoring)")
    winning_topic_data = run_decision_engine(candidate_topics)

    if not winning_topic_data:
        log.step("run_reels_pipeline", "OUT", result="exit",
                 reason="No topics survived filters and memory check")
        return

    topic = winning_topic_data.get("topic")
    score = winning_topic_data.get("final_score")
    reason = winning_topic_data.get("reason")
    category_tag = winning_topic_data.get("category_tag", "other")
    angle = winning_topic_data.get("angle", "")
    why_now = winning_topic_data.get("why_now", "")

    log.step("run_reels_pipeline", "INFO",
             message="🏆 Winning topic selected",
             topic=topic,
             score=score,
             category=category_tag,
             angle=angle,
             why_now=why_now,
             reason=reason)

    topic_id = save_topic(topic, status="selected", score=score, category_tag=category_tag)
    if topic_id:
        log.step("run_reels_pipeline", "INFO", message="Saved to memory", topic_id=topic_id)

    log.step("run_reels_pipeline", "INFO", step="3/4 - Strategy engine (content strategy)")
    strategy = run_strategy_engine(topic, score=score, reason=reason,
                                   angle=angle, why_now=why_now, language=language)

    log.step("run_reels_pipeline", "INFO",
             message="📋 Content strategy ready",
             narrative=strategy.get("narrative"),
             hook=strategy.get("hook"),
             emotion=strategy.get("emotion"),
             motion_prompt=strategy.get("motion_prompt"),
             cta=strategy.get("cta"),
             on_screen_text=strategy.get("on_screen_text"))

    if not execute_content:
        log.step("run_reels_pipeline", "OUT",
                 result="exit", reason="execute_content=False — stopping before asset generation")
        return

    log.step("run_reels_pipeline", "INFO", step="4/4 - Content engine (generating assets)")
    try:
        start_time = time.time()
        final_assets = run_content_engine(topic, strategy=strategy, language=language)
        elapsed = int(time.time() - start_time)

        log.info("=" * 44)
        log.info("🎉 REELS GENERATION COMPLETE!")
        log.step("run_reels_pipeline", "OUT",
                 time_taken_s=elapsed,
                 topic=final_assets["topic"],
                 emotion=final_assets["emotion"],
                 image_prompt=final_assets["base_prompt"],
                 style_anchor=final_assets["style_anchor"],
                 silent_video_path=final_assets["silent_video_path"],
                 audio_prompt=final_assets["audio_prompt"],
                 video_with_audio=final_assets["video_with_audio_path"],
                 final_video_path=final_assets["final_video_path"],
                 cta=final_assets["cta"],
                 on_screen_text=final_assets["on_screen_text"],
                 caption_preview=str(final_assets.get("caption", ""))[:120],
                 hashtags=final_assets.get("hashtags", []))
        log.info("=" * 44)

        update_topic_status(topic, "published")

    except Exception as e:
        log.step("run_reels_pipeline", "ERR",
                 step="4/4 - Content engine", error=str(e))
        update_topic_status(topic, "failed")
        raise


if __name__ == "__main__":
    # Parse --language flag (default: en)
    language = "en"
    if "--language" in sys.argv:
        idx = sys.argv.index("--language")
        if idx + 1 < len(sys.argv):
            language = sys.argv[idx + 1].lower()
            if language not in ("en", "es"):
                print(f"Unsupported language: {language}. Use 'en' or 'es'.")
                sys.exit(1)

    if "--clear-db" in sys.argv:
        count = clear_database()
        log.info(f"🗑️ Database cleared: {count} topic(s) deleted.")
        if "--no-run" in sys.argv:
            sys.exit(0)

    run_reels_pipeline(execute_content=True, language=language)
