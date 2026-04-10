import time
from typing import Dict, List

# -----------------------------
# In-memory stores (replace later with DB/Redis)
# -----------------------------
conversation_store: Dict[str, List[Dict]] = {}
session_store: Dict[str, Dict] = {}
profile_store: Dict[str, Dict] = {}

# -----------------------------
# Conversation Memory
# -----------------------------
def get_conversation(user_id: str) -> List[Dict]:
    return conversation_store.get(user_id, [])


def add_message(user_id: str, role: str, content: str):
    if user_id not in conversation_store:
        conversation_store[user_id] = []

    conversation_store[user_id].append({
        "role": role,
        "content": content,
        "timestamp": time.time()
    })


def trim_conversation(user_id: str, max_messages: int = 20):
    """Keep only last N messages to avoid token overflow"""
    if user_id in conversation_store:
        conversation_store[user_id] = conversation_store[user_id][-max_messages:]


# -----------------------------
# Session State (short-term)
# -----------------------------
def get_session(user_id: str) -> Dict:
    if user_id not in session_store:
        session_store[user_id] = {
            "mood": "neutral",
            "workflow": None,
            "step": 0,
            "last_updated": time.time()
        }
    return session_store[user_id]


def update_session(user_id: str, key: str, value):
    session = get_session(user_id)
    session[key] = value
    session["last_updated"] = time.time()


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


# -----------------------------
# User Profile (long-term)
# -----------------------------
def get_profile(user_id: str) -> Dict:
    if user_id not in profile_store:
        profile_store[user_id] = {
            "issues": [],
            "patterns": [],
            "preferences": [],
            "last_updated": time.time()
        }
    return profile_store[user_id]


def update_profile(user_id: str, message: str):
    """
    VERY simple rule-based profile extraction.
    Replace later with LLM extraction.
    """
    profile = get_profile(user_id)
    msg = message.lower()

    # Detect issues
    if "anxious" in msg and "anxiety" not in profile["issues"]:
        profile["issues"].append("anxiety")

    if "overthinking" in msg and "overthinking" not in profile["patterns"]:
        profile["patterns"].append("overthinking")

    if "short answers" in msg:
        if "prefers concise responses" not in profile["preferences"]:
            profile["preferences"].append("prefers concise responses")

    profile["last_updated"] = time.time()