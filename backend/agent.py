import os
import logging
from google import genai
from .tool import track_mood, save_journal_entry, cbt_reframe
from .memory import detect_mood
# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Load API Key
# --------------------------------------------------

API_KEY = "AIzaSyCbsqht0mYD9-VsWYGJw7w_lHweVzFmvgg"

if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY environment variable is not set")

# --------------------------------------------------
# Gemini Client
# --------------------------------------------------

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "models/gemini-2.5-flash"


# --------------------------------------------------
# Safety Check
# --------------------------------------------------

def safety_check(text: str) -> bool:
    """
    Simple crisis detection.
    In production this should be replaced with
    LLM moderation or a classifier.
    """

    crisis_words = [
        "suicide",
        "kill myself",
        "self harm",
        "end my life"
    ]

    text_lower = text.lower()

    return any(word in text_lower for word in crisis_words)

def select_style(user_message: str):
    if any(word in user_message.lower() for word in ["stress", "anxious", "overwhelmed"]):
        return "empathetic"
    elif any(word in user_message.lower() for word in ["exercise", "cope", "technique"]):
        return "cbt"
    elif len(user_message.split()) < 5:
        return "concise"
    else:
        return "friendly"

# --------------------------------------------------
# Therapist AI Agent
# --------------------------------------------------

def therapist_response(user_message: str, history=None, session=None, profile=None) -> str:

    history_text = ""
    if history:
        history_text = "\n".join(
            [f"{m['role']}: {m['content']}" for m in history[-6:]]
        )

    prompt = f"""
You are a compassionate AI therapist assistant.

User Profile:
{profile}

Session State:
{session}

Conversation:
{history_text}

User: {user_message}

Guidelines:
- Be empathetic
- No medical diagnosis
- Encourage reflection
- Ask follow-up questions

Therapist:
"""

    try:

        logger.info("Sending prompt to Gemini")

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if not response or not response.text:
            logger.warning("Gemini returned empty response")
            return "I'm here with you. Could you tell me more about what you're experiencing?"

        return response.text

    except Exception as e:

        logger.error(f"Gemini API error: {e}")

        return "I'm sorry, I'm having trouble responding right now. Please try again in a moment."
    

def decide_tool(user_message: str):
    msg = user_message.lower()

    if "journal" in msg or "write this down" in msg:
        return "journal"

    if "help me reframe" in msg or "negative thought" in msg:
        return "cbt"

    if any(word in msg for word in ["anxious", "sad", "angry"]):
        return "mood"

    return None