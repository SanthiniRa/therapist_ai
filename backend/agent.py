import os
import logging
from google import genai

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


# --------------------------------------------------
# Therapist AI Agent
# --------------------------------------------------

def therapist_response(user_message: str, style: str = "friendly") -> str:
    """
    Generate an empathetic therapist response using Gemini.
    """

    prompt = f"""
You are a compassionate AI therapist assistant.

Guidelines:
-Respond primarily in English, but occasionally include a relevant Tamil cinema dialogue that matches the situation or feeling.
-Make sure the dialogue fits naturally in the response and enhances encouragement, humor, or reflection.
- Be empathetic and supportive
- Use a {style} tone
- Do not give medical diagnoses
- Encourage reflection and emotional awareness
- Ask gentle follow-up questions when appropriate

User message:
{user_message}
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