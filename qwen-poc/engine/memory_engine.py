"""
memory_engine.py
================
SQLite-backed memory for published Reels topics.

Improvements over v1:
  - Schema extended with `category_tag` column for diversity tracking
  - `get_recent_topics(days)` — returns topics from the last N days for
    semantic similarity and diversity checks in the decision engine
  - `is_topic_used` now respects a configurable recency window (default 30 days)
    so that a topic can resurface after it's no longer relevant
"""

import sqlite3
import os
import datetime
from utils.logger import get_logger

log = get_logger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sqllite", "reels_memory.db")

# Topics older than this are allowed to resurface
RECENCY_WINDOW_DAYS = 30


def init_db():
    """Initialises the SQLite database and ensures the schema is up to date."""
    log.step("init_db", "IN", db_path=DB_PATH)
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            original_topic   TEXT,
            normalized_topic TEXT UNIQUE,
            created_at       TEXT,
            status           TEXT,
            score            REAL,
            category_tag     TEXT DEFAULT 'other'
        )
    """)

    # Migration: add category_tag column if it doesn't exist yet (for existing DBs)
    try:
        cursor.execute("ALTER TABLE topics ADD COLUMN category_tag TEXT DEFAULT 'other'")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # column already exists

    conn.commit()
    conn.close()
    log.step("init_db", "OUT", message="DB ready")


def _normalize(topic: str) -> str:
    """Normalises a topic string for exact-match deduplication."""
    return ''.join(e for e in topic.lower() if e.isalnum() or e.isspace()).strip()


def is_topic_used(topic: str, days: int = RECENCY_WINDOW_DAYS) -> bool:
    """
    Returns True if this topic (normalised) was published within the last `days` days.
    Topics older than the window are allowed to resurface.
    """
    normalized = _normalize(topic)
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()

    log.step("is_topic_used", "IN", topic=topic, normalized=normalized, window_days=days)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM topics WHERE normalized_topic = ? AND created_at >= ?",
        (normalized, cutoff),
    )
    exists = cursor.fetchone() is not None
    conn.close()
    log.step("is_topic_used", "OUT", topic=topic, exists=exists)
    return exists


def get_recent_topics(days: int = 14) -> list[dict]:
    """
    Returns all topics published in the last `days` days as a list of dicts.
    Used by the decision engine for semantic similarity and category diversity checks.
    """
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT original_topic, category_tag, created_at, status, score "
        "FROM topics WHERE created_at >= ? ORDER BY created_at DESC",
        (cutoff,),
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    log.step("get_recent_topics", "OUT", days=days, count=len(rows))
    return rows


def save_topic(topic: str, status: str = "pending", score: float = 0.0,
               category_tag: str = "other") -> int | None:
    """
    Saves a new topic to the DB. Returns its ID, or None if it already existed.
    """
    normalized = _normalize(topic)
    log.step("save_topic", "IN", topic=topic, normalized=normalized,
             status=status, score=score, category_tag=category_tag)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    topic_id = None
    try:
        cursor.execute(
            """INSERT INTO topics
               (original_topic, normalized_topic, created_at, status, score, category_tag)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (topic, normalized, datetime.datetime.now().isoformat(),
             status, score, category_tag),
        )
        conn.commit()
        topic_id = cursor.lastrowid
        log.step("save_topic", "OUT", topic=topic, id=topic_id)
    except sqlite3.IntegrityError:
        log.step("save_topic", "INFO", topic=topic,
                 message="Already exists in DB, skipped insert")
    finally:
        conn.close()
    return topic_id


def update_topic_status(topic: str, status: str):
    """Updates the status of an existing topic (e.g. 'published', 'failed')."""
    normalized = _normalize(topic)
    log.step("update_topic_status", "IN", topic=topic, new_status=status)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE topics SET status = ? WHERE normalized_topic = ?",
        (status, normalized),
    )
    conn.commit()
    conn.close()
    log.step("update_topic_status", "OUT", topic=topic, status=status)


def clear_database() -> int:
    """
    Deletes all topics from the memory database.
    Returns the number of rows deleted.
    """
    log.step("clear_database", "IN", db_path=DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM topics")
    count = cursor.fetchone()[0]
    cursor.execute("DELETE FROM topics")
    conn.commit()
    conn.close()
    log.step("clear_database", "OUT", deleted=count)
    return count
