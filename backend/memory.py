import json
import sqlite3
import time
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "memory.db"
JSON_PATH = BASE_DIR / "memory.json"

SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS conversation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp REAL NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS session (
        user_id TEXT PRIMARY KEY,
        data TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS profile (
        user_id TEXT PRIMARY KEY,
        data TEXT NOT NULL
    )
    """
]


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        for stmt in SCHEMA:
            conn.execute(stmt)
        conn.commit()

        if JSON_PATH.exists() and is_db_empty(conn):
            migrate_json_to_db(conn)


def is_db_empty(conn) -> bool:
    cursor = conn.execute("SELECT COUNT(1) as count FROM conversation")
    return cursor.fetchone()[0] == 0


def migrate_json_to_db(conn):
    try:
        with JSON_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return

    conversations = data.get("conversation", {})
    sessions = data.get("session", {})
    profiles = data.get("profile", {})

    for user_id, messages in conversations.items():
        for message in messages:
            conn.execute(
                "INSERT INTO conversation (user_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (
                    user_id,
                    message.get("role", "user"),
                    message.get("content", ""),
                    message.get("timestamp", time.time()),
                ),
            )

    for user_id, session_data in sessions.items():
        conn.execute(
            "INSERT OR REPLACE INTO session (user_id, data) VALUES (?, ?)",
            (user_id, json.dumps(session_data)),
        )

    for user_id, profile_data in profiles.items():
        conn.execute(
            "INSERT OR REPLACE INTO profile (user_id, data) VALUES (?, ?)",
            (user_id, json.dumps(profile_data)),
        )

    conn.commit()


# -----------------------------
# Conversation Memory
# -----------------------------

def get_conversation(user_id: str) -> List[Dict]:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT role, content, timestamp FROM conversation WHERE user_id = ? ORDER BY id ASC",
            (user_id,),
        )
        return [dict(row) for row in cursor.fetchall()]


def add_message(user_id: str, role: str, content: str):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO conversation (user_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, role, content, time.time()),
        )
        conn.commit()

    trim_conversation(user_id)


def trim_conversation(user_id: str, max_messages: int = 20):
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT id FROM conversation WHERE user_id = ? ORDER BY id ASC",
            (user_id,),
        )
        ids = [row["id"] for row in cursor.fetchall()]
        if len(ids) > max_messages:
            remove_ids = ids[: len(ids) - max_messages]
            conn.executemany(
                "DELETE FROM conversation WHERE id = ?",
                [(message_id,) for message_id in remove_ids],
            )
            conn.commit()


# -----------------------------
# Session State (short-term)
# -----------------------------

def get_session(user_id: str) -> Dict:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT data FROM session WHERE user_id = ?",
            (user_id,),
        )
        row = cursor.fetchone()
        if row:
            return json.loads(row["data"])

        session = {
            "mood": "neutral",
            "workflow": None,
            "step": 0,
            "last_updated": time.time(),
        }
        conn.execute(
            "INSERT INTO session (user_id, data) VALUES (?, ?)",
            (user_id, json.dumps(session)),
        )
        conn.commit()
        return session


def update_session(user_id: str, key: str, value):
    session = get_session(user_id)
    session[key] = value
    session["last_updated"] = time.time()

    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO session (user_id, data) VALUES (?, ?)",
            (user_id, json.dumps(session)),
        )
        conn.commit()


# -----------------------------
# Simple Mood Detection
# -----------------------------

def detect_mood(message: str) -> str:
    msg = message.lower()

    if any(word in msg for word in ["anxious", "nervous", "panic"]):
        return "anxious"
    elif any(word in msg for word in ["sad", "depressed", "down"]):
        return "sad"
    elif any(word in msg for word in ["angry", "frustrated"]):
        return "angry"
    else:
        return "neutral"


def detect_mode(user_input: str):
    text = user_input.lower()

    if "anxious" in text or "nervous" in text:
        return "calm_support"
    elif "sad" in text or "depressed" in text:
        return "empathy_support"
    elif "angry" in text:
        return "release_support"
    else:
        return "general_support"


# -----------------------------
# User Profile (long-term)
# -----------------------------

def get_profile(user_id: str) -> Dict:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT data FROM profile WHERE user_id = ?",
            (user_id,),
        )
        row = cursor.fetchone()
        if row:
            return json.loads(row["data"])

        profile = {
            "issues": [],
            "patterns": [],
            "preferences": [],
            "last_updated": time.time(),
        }
        conn.execute(
            "INSERT INTO profile (user_id, data) VALUES (?, ?)",
            (user_id, json.dumps(profile)),
        )
        conn.commit()
        return profile


def update_profile(user_id: str, message: str):
    profile = get_profile(user_id)
    msg = message.lower()

    if "anxious" in msg and "anxiety" not in profile["issues"]:
        profile["issues"].append("anxiety")

    if "overthinking" in msg and "overthinking" not in profile["patterns"]:
        profile["patterns"].append("overthinking")

    if "short answers" in msg:
        if "prefers concise responses" not in profile["preferences"]:
            profile["preferences"].append("prefers concise responses")

    profile["last_updated"] = time.time()

    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO profile (user_id, data) VALUES (?, ?)",
            (user_id, json.dumps(profile)),
        )
        conn.commit()


def save_memory():
    # Persistence is now handled by the database on every write.
    pass


def load_memory():
    init_db()
