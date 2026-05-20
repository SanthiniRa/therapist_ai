from datetime import datetime
import inspect

mood_logs = {}
journal_logs = {}

VALID_MOODS = ["happy", "sad", "anxious", "angry", "neutral"]

# -----------------------------
# Mood Tracker Tool
# -----------------------------
def track_mood(user_id: str, mood: str):
    if mood.lower() not in VALID_MOODS:
        return f"Invalid mood. Choose from {VALID_MOODS}"

    if user_id not in mood_logs:
        mood_logs[user_id] = []

    mood_logs[user_id].append({
        "mood": mood.lower(),
        "timestamp": datetime.utcnow().isoformat()
    })

    return f"I've noted that you're feeling {mood}."


def get_mood_history(user_id: str):
    history = mood_logs.get(user_id, [])

    if not history:
        return "No mood history found."

    return [
        f"{entry['timestamp']} → {entry['mood']}"
        for entry in history
    ]


# -----------------------------
# Journaling Tool
# -----------------------------
def save_journal_entry(user_id: str, text: str, emotion: str = None):
    if user_id not in journal_logs:
        journal_logs[user_id] = []

    journal_logs[user_id].append({
        "entry": text,
        "emotion": emotion,
        "timestamp": datetime.utcnow().isoformat()
    })

    return "Your thoughts have been saved in your journal."


def get_journal_entries(user_id: str):
    entries = journal_logs.get(user_id, [])

    if not entries:
        return "No journal entries found."

    return [
        f"{e['timestamp']} → {e['entry']}"
        for e in entries
    ]


def search_journal(user_id: str, keyword: str):
    entries = journal_logs.get(user_id, [])

    results = [
        e for e in entries if keyword.lower() in e["entry"].lower()
    ]

    if not results:
        return "No matching entries found."

    return [
        f"{e['timestamp']} → {e['entry']}"
        for e in results
    ]


# -----------------------------
# Therapy Tool (CBT)
# -----------------------------
def cbt_reframe(thought: str):
    return {
        "original_thought": thought,
        "questions": [
            "Is this thought 100% true?",
            "What evidence supports or challenges it?",
            "What would you say to a friend?"
        ],
        "reframed_thought":
            "I may be struggling right now, but that doesn't define me."
    }


def breathing_tool():
    return "Try this: inhale 4 sec, hold 7 sec, exhale 8 sec."


def maybe_call_tool(mode):
    if mode == "calm_support":
        return breathing_tool()
    return None

# -----------------------------
# Tool Registry (MUST BE LAST)
# -----------------------------
TOOLS = {
    "track_mood": track_mood,
    "get_mood_history": get_mood_history,
    "save_journal_entry": save_journal_entry,
    "get_journal_entries": get_journal_entries,
    "search_journal": search_journal,
    "cbt_reframe": cbt_reframe,
    "breathing_tool": breathing_tool,
    "maybe_call_tool": maybe_call_tool
}


def validate_tool_args(tool_name: str, args: dict):
    if tool_name not in TOOLS:
        raise ValueError(f"Unknown tool: {tool_name}")

    tool_func = TOOLS[tool_name]
    signature = inspect.signature(tool_func)
    expected_params = [p for p in signature.parameters.values() if p.name != "user_id"]
    required_params = [p.name for p in expected_params if p.default is inspect._empty]
    allowed_params = [p.name for p in expected_params]

    extra = set(args) - set(allowed_params)
    if extra:
        raise ValueError(f"Unexpected tool arguments: {sorted(extra)}")

    missing = [name for name in required_params if name not in args]
    if missing:
        raise ValueError(f"Missing tool arguments: {sorted(missing)}")

    return True


def execute_tool(user_id: str, tool_name: str, args: dict):
    validate_tool_args(tool_name, args)
    tool_func = TOOLS[tool_name]
    signature = inspect.signature(tool_func)

    if "user_id" in signature.parameters:
        return tool_func(user_id, **args)

    return tool_func(**args)
