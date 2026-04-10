import traceback

from fastapi import FastAPI, HTTPException,Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from .tool import get_mood_history, get_journal_entries
from .agent import therapist_response, safety_check
from .auth import app as auth_app
from slowapi import Limiter
from slowapi.util import get_remote_address
from .memory import (
    get_conversation,
    add_message,
    trim_conversation,
    get_session,
    update_session,
    detect_mood,
    get_profile,
    update_profile
)

app = auth_app
class ChatRequest(BaseModel):
    message: str

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/")
def home():
    return {"status": "Therapist AI running"}

@app.post("/chat")
@limiter.limit("5/minute")
async def chat(request: Request, req: ChatRequest):
    user = request.session.get("user")

    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = user["email"]
    user_message = req.message

    # -----------------------------
    # Memory retrieval
    # -----------------------------
    history = get_conversation(user_id)
    session = get_session(user_id)
    profile = get_profile(user_id)

    # -----------------------------
    # Update memory BEFORE response
    # -----------------------------
    add_message(user_id, "user", user_message)

    # Mood detection → session update
    mood = detect_mood(user_message)
    update_session(user_id, "mood", mood)

    # Update profile occasionally
    if len(history) % 5 == 0:
        update_profile(user_id, user_message)

    # Safety check
    if safety_check(user_message):
        return {"reply": "I'm really sorry you're feeling this way. Please reach out to a professional or a trusted person."}

    # -----------------------------
    # Generate response
    # -----------------------------
    try:
        reply = therapist_response(
            user_message,
            history=history,
            session=session,
            profile=profile
        )

    except Exception as e:
        print("FULL ERROR:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

    # -----------------------------
    # Store assistant response
    # -----------------------------
    add_message(user_id, "assistant", reply)

    # Trim history
    trim_conversation(user_id)

    return {"reply": reply}

@app.get("/mood")
async def mood_data(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401)

    user_id = user["email"]
    return {"moods": get_mood_history(user_id)}


@app.get("/journal")
async def journal_data(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401)

    user_id = user["email"]
    return {"entries": get_journal_entries(user_id)}