import sqlite3
import os
import datetime
from utils.logger import get_logger

log = get_logger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sqllite", "reels_memory.db")


def init_db():
    """Initializes the SQLite database and the topics table."""
    log.step("init_db", "IN", db_path=DB_PATH)
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_topic TEXT,
            normalized_topic TEXT UNIQUE,
            created_at TEXT,
            status TEXT,
            score REAL
        )
    """)
    conn.commit()
    conn.close()
    log.step("init_db", "OUT", message="DB ready")


def _normalize(topic: str) -> str:
    """Normalizes a topic string for deduplication."""
    return ''.join(e for e in topic.lower() if e.isalnum() or e.isspace()).strip()


def is_topic_used(topic: str) -> bool:
    """Returns True if this topic (normalized) already exists in the DB."""
    normalized = _normalize(topic)
    log.step("is_topic_used", "IN", topic=topic, normalized=normalized)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM topics WHERE normalized_topic = ?", (normalized,))
    exists = cursor.fetchone() is not None
    conn.close()
    log.step("is_topic_used", "OUT", topic=topic, exists=exists)
    return exists


def save_topic(topic: str, status: str = "pending", score: float = 0.0) -> int:
    """Saves a new topic to the DB. Returns its ID, or None if it already existed."""
    normalized = _normalize(topic)
    log.step("save_topic", "IN", topic=topic, normalized=normalized, status=status, score=score)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    topic_id = None
    try:
        cursor.execute(
            "INSERT INTO topics (original_topic, normalized_topic, created_at, status, score) VALUES (?, ?, ?, ?, ?)",
            (topic, normalized, datetime.datetime.now().isoformat(), status, score)
        )
        conn.commit()
        topic_id = cursor.lastrowid
        log.step("save_topic", "OUT", topic=topic, id=topic_id)
    except sqlite3.IntegrityError:
        log.step("save_topic", "INFO", topic=topic, message="Already exists in DB, skipped insert")
    finally:
        conn.close()
    return topic_id


def update_topic_status(topic: str, status: str):
    """Updates the status of an existing topic (e.g. 'published', 'failed')."""
    normalized = _normalize(topic)
    log.step("update_topic_status", "IN", topic=topic, new_status=status)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE topics SET status = ? WHERE normalized_topic = ?", (status, normalized))
    conn.commit()
    conn.close()
    log.step("update_topic_status", "OUT", topic=topic, status=status)
