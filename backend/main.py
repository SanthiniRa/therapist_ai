import logging
import traceback

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from backend.tool import get_mood_history, get_journal_entries
from backend.agent import client
from backend.agent_controller import agent_controller
from backend.auth import app as auth_app
from slowapi import Limiter
from slowapi.util import get_remote_address
from backend.rag_faiss import init_rag, add_knowledge
from backend.memory import (
    get_conversation,
    add_message,
    trim_conversation,
    get_session,
    update_session,
    detect_mood,
    get_profile,
    update_profile,
    load_memory,
    save_memory,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("therapist_ai")

app = auth_app

class ChatRequest(BaseModel):
    message: str

class KnowledgeRequest(BaseModel):
    text: str


@app.on_event("startup")
async def startup_event():
    logger.info("Therapist AI startup: loading memory and initializing RAG.")
    try:
        load_memory()
        init_rag()
        logger.info("Startup complete.")
    except Exception as exc:
        logger.exception("Startup failed")
        raise


@app.post("/add-knowledge")
async def add_knowledge_endpoint(req: KnowledgeRequest):
    result = add_knowledge(req.text)
    return {"status": result}


limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/")
def home():
    return {"status": "Therapist AI running"}

@app.get("/health")
def health():
    return {"status": "ok", "message": "Therapist AI is healthy"}

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
    # Store user message
    # -----------------------------
    add_message(user_id, "user", user_message)

    # -----------------------------
    # Session updates
    # -----------------------------
    mood = detect_mood(user_message)
    update_session(user_id, "mood", mood)

    if len(history) % 5 == 0:
        update_profile(user_id, user_message)

    # -----------------------------
    # DEBUG (optional)
    # -----------------------------
    logger.info("USER: %s", user_message)

    # -----------------------------
    # AI RESPONSE
    # -----------------------------
    try:
        result = agent_controller(
            user_message,
            user,
            client.models,
            history=history,
            session=session,
            profile=profile,
            user_id=user_id
        )
        reply = result["response"]

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

    # -----------------------------
    # Save AI response
    # -----------------------------
    add_message(user_id, "assistant", reply)

    trim_conversation(user_id)
    save_memory()

    logger.info("BOT: %s", reply)

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