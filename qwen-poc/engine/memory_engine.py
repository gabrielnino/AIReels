import sqlite3
import os
import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sqllite", "reels_memory.db")

def init_db():
    """Initializes the SQLite database and the topics table."""
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

def _normalize(topic: str) -> str:
    """Normalizes a topic string for deduplication."""
    return ''.join(e for e in topic.lower() if e.isalnum() or e.isspace()).strip()

def is_topic_used(topic: str) -> bool:
    """Checks if a normalized version of the topic exists in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM topics WHERE normalized_topic = ?", (_normalize(topic),))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def save_topic(topic: str, status: str = "pending", score: float = 0.0) -> int:
    """Saves a new topic and returns its ID. Silently ignores if it already exists."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    normalized = _normalize(topic)
    try:
        cursor.execute(
            "INSERT INTO topics (original_topic, normalized_topic, created_at, status, score) VALUES (?, ?, ?, ?, ?)",
            (topic, normalized, datetime.datetime.now().isoformat(), status, score)
        )
        conn.commit()
        topic_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        # Already exists
        topic_id = None
    finally:
        conn.close()
    return topic_id

def update_topic_status(topic: str, status: str):
    """Updates the status of an existing topic (e.g. 'selected')."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE topics SET status = ? WHERE normalized_topic = ?", (status, _normalize(topic)))
    conn.commit()
    conn.close()
