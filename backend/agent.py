import os
import logging
from dotenv import load_dotenv
from google import genai
from tool import TOOLS
from rag_faiss import get_context
from memory import detect_mood

load_dotenv()
# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Load API Key
# --------------------------------------------------

API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GENAI_API_KEY") or ""

if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY or GENAI_API_KEY environment variable is not set")

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

def therapist_response(user_message, history=None, session=None, profile=None, user_id=None):

    # -----------------------------
    # STEP 1: Decide tool
    # -----------------------------
    tool_name = decide_tool(user_message)
    logger.info(f"TOOL SELECTED: {tool_name}")
    tool_output = None

    if tool_name == "mood":
        tool_output = TOOLS["track_mood"](user_id, detect_mood(user_message))

    elif tool_name == "journal":
        tool_output = TOOLS["save_journal_entry"](user_id, user_message)

    elif tool_name == "cbt":
        tool_output = TOOLS["cbt_reframe"](user_message)


    rag_context = get_context(user_message)[:1000]
    if not rag_context:
     rag_context = "You can suggest general coping techniques like breathing, journaling, or grounding."
    logger.info(f"RAG CONTEXT: {rag_context[:200]}")
    # -----------------------------
    # STEP 2: Prepare history
    # -----------------------------
    history_text = ""
    if history:
        history_text = "\n".join(
            [f"{m['role']}: {m['content']}" for m in history[-6:]]
        )

    # -----------------------------
    # STEP 3: Add tool context
    # -----------------------------
    tool_text = ""
    if tool_output:
        tool_text = f"\nTool Result:\n{tool_output}\n"
    logger.info(f"TOOL OUTPUT: {tool_output}")
    # -----------------------------
    # STEP 4: Create prompt
    # -----------------------------
    prompt = f"""
You are a compassionate AI therapist assistant.

Use the knowledge provided below when relevant.

Therapy Knowledge:
{rag_context}

User Profile:
{profile}

Session State:
{session}

Conversation:
{history_text}

{tool_text}

User: {user_message}

Guidelines:
- Be empathetic
- Encourage reflection
- Use CBT techniques when appropriate
- Ask follow-up questions
- Use provided knowledge when useful

Therapist:
"""

    try:
        logger.info("Sending prompt to Gemini")

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if not response or not response.text:
            return "I'm here with you. Could you tell me more?"

        return response.text

    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return "I'm having trouble responding. Please try again."    

def decide_tool(user_message: str):
    msg = user_message.lower()

    if "journal" in msg or "write this down" in msg:
        return "journal"

    if "reframe" in msg or "negative thought" in msg:
        return "cbt"

    if any(word in msg for word in ["anxious", "sad", "angry", "happy"]):
        return "mood"

    return None