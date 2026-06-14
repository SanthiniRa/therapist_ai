import os
import logging
from google import genai
from .tool import track_mood, save_journal_entry, cbt_reframe
from .memory import detect_mood
from dotenv import load_dotenv

# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Load API Key
# --------------------------------------------------

load_dotenv()
API_KEY = (os.getenv("GENAI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")).strip()

if not API_KEY:
    raise RuntimeError("GENAI_API_KEY or GOOGLE_API_KEY environment variable is not set")

# Ensure API key is ASCII-compatible
try:
    API_KEY.encode('ascii')
except UnicodeEncodeError:
    logger.error("API_KEY contains invalid Unicode characters. Please use a valid ASCII API key.")
    raise RuntimeError("Invalid API key format - contains non-ASCII characters")

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

    # Get relevant knowledge from RAG
    from .rag import get_rag_context
    rag_context = get_rag_context(user_message, top_k=2)

    prompt = f"""
You are a compassionate AI therapist assistant.

User Profile:
{profile}

Session State:
{session}

Conversation:
{history_text}

Relevant Knowledge:
{rag_context}

User: {user_message}

Guidelines:
- Be empathetic
- No medical diagnosis
- Encourage reflection
- Ask follow-up questions
- Use the relevant knowledge when appropriate

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
