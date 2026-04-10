from datetime import datetime

# In-memory stores (replace later with DB)
mood_logs = {}
journal_logs = {}

# -----------------------------
# Mood Tracker Tool
# -----------------------------
def track_mood(user_id: str, mood: str):
    if user_id not in mood_logs:
        mood_logs[user_id] = []

    mood_logs[user_id].append({
        "mood": mood,
        "timestamp": datetime.utcnow().isoformat()
    })

    return f"I've noted that you're feeling {mood}."


def get_mood_history(user_id: str):
    return mood_logs.get(user_id, [])


# -----------------------------
# Journaling Tool
# -----------------------------
def save_journal_entry(user_id: str, text: str):
    if user_id not in journal_logs:
        journal_logs[user_id] = []

    journal_logs[user_id].append({
        "entry": text,
        "timestamp": datetime.utcnow().isoformat()
    })

    return "Your thoughts have been saved in your journal."


def get_journal_entries(user_id: str):
    return journal_logs.get(user_id, [])


# -----------------------------
# Therapy Tool (CBT)
# -----------------------------
def cbt_reframe(thought: str):
    return f"""
Let's gently reframe this thought:

Original thought:
"{thought}"

Try asking yourself:
- Is this thought 100% true?
- What evidence supports or challenges it?
- What would you say to a friend in this situation?

A more balanced perspective could be:
"I may be struggling right now, but that doesn't define me."
"""