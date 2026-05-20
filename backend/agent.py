import logging
import json
from google import genai
from backend.config import settings
from backend.tool import TOOLS
from backend.rag_faiss import get_context
from backend.memory import detect_mood, detect_mode

# --------------------------------------------------
# Logging
# --------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Load API Key
# --------------------------------------------------
API_KEY = settings.api_key
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY or GENAI_API_KEY environment variable is not set")

# --------------------------------------------------
# Gemini Client
# --------------------------------------------------
client = genai.Client(api_key=API_KEY)
MODEL_NAME = settings.model_name


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
MODE_INSTRUCTIONS = {
    "calm_support": """
    Be gentle and calming.
    Suggest 1 quick breathing or grounding exercise.
    Keep response short (2–4 sentences).
    Avoid overwhelming the user.
    """,

    "empathy_support": """
    Be warm and validating.
    Acknowledge feelings.
    Offer emotional support, not solutions immediately.
    """,

    "release_support": """
    Help user release frustration safely.
    Suggest physical or expressive outlet.
    Stay calm and non-judgmental.
    """,

    "general_support": """
    Be helpful and friendly.
    Provide simple guidance.
    Keep it concise.
    """
}

def therapist_response(user_message, history=None, session=None, profile=None, user_id=None):

    # -----------------------------
    # STEP 1: RAG
    # -----------------------------
    rag_context = get_context(user_message)
    if not rag_context:
        rag_context = "You can suggest general coping techniques like breathing, journaling, or grounding."

    rag_context = str(rag_context)[:1000]
    logger.info(f"RAG CONTEXT: {rag_context[:200]}")

    # -----------------------------
    # STEP 2: History
    # -----------------------------
    history_text = ""
    if history:
        history_text = "\n".join(
            [f"{m['role']}: {m['content']}" for m in history[-6:]]
        )
    
    mode = detect_mode(user_message)
    mode_instruction = MODE_INSTRUCTIONS[mode]

    # -----------------------------
    # STEP 3: FIRST LLM CALL (decide tool)
    # -----------------------------
    prompt = f"""
You are a compassionate AI therapist assistant.
Avoid repeating generic phrases like "it sounds like..."
Be natural, conversational, and slightly varied in tone.
Keep responses short (3–5 sentences).
Use at least one relevant item from retrieved context explicitly in the response.
Do not ignore retrieved knowledge.
If user message is short, respond briefly (max 2–3 sentences) and offer one suggestion
You can:
1. Respond empathetically
2. Use knowledge
3. Call tools when needed

Available tools:
- track_mood(mood)
- save_journal_entry(text)
- cbt_reframe(thought)
{mode_instruction}
If a tool is needed, respond ONLY in JSON:

{{
  "tool": "tool_name",
  "args": {{
    "param": "value"
  }}
}}

Otherwise respond normally.

Therapy Knowledge:
{rag_context}

Conversation:
{history_text}

User: {user_message}
"""

    try:
        logger.info("Calling Gemini (decision step)")
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if not response or not response.text:
            return "I'm here with you. Could you tell me more?"

        text = response.text.strip()

        # ✅ CLEAN JSON (important)
        text = text.replace("```json", "").replace("```", "").strip()

        logger.info(f"LLM RESPONSE: {text}")
        

    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return "I'm having trouble responding."

    # -----------------------------
    # STEP 4: Check if tool call
    # -----------------------------
    tool_output = None

    try:
        data = json.loads(text)

        tool_name = data.get("tool")
        args = data.get("args", {})

        logger.info(f"TOOL SELECTED BY LLM: {tool_name}")

        if tool_name in TOOLS:
            tool_output = TOOLS[tool_name](user_id, **args)
            logger.info(f"TOOL OUTPUT: {tool_output}")

        else:
            return text  # fallback if unknown tool

    except:
        # Not JSON → normal response
        return text

    # -----------------------------
    # STEP 5: SECOND LLM CALL (final response)
    # -----------------------------
    second_prompt = f"""
You are a compassionate therapist.

Tool result:
{tool_output}

User: {user_message}

Respond empathetically and helpfully.
"""

    try:
        final_response = client.models.generate_content(
            model=MODEL_NAME,
            contents=second_prompt
        )

        return final_response.text

    except Exception as e:
        logger.error(f"Final response error: {e}")
        return tool_output   

def decide_tool(user_message: str):
    msg = user_message.lower()

    if "journal" in msg or "write this down" in msg:
        return "journal"

    if "reframe" in msg or "negative thought" in msg:
        return "cbt"

    if any(word in msg for word in ["anxious", "sad", "angry", "happy"]):
        return "mood"

    return None