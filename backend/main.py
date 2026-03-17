from fastapi import FastAPI, HTTPException,Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from .agent import therapist_response, safety_check
from .auth import app as auth_app
from slowapi import Limiter
from slowapi.util import get_remote_address

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

    user_message = req.message

    if safety_check(user_message):
        return {
            "reply": "I'm sorry, but I can't assist with that. Please seek help from a professional."
        }

    try:
        reply = therapist_response(user_message)

    except Exception as e:
        print("error generating therapist response:", e)

        raise HTTPException(
            status_code=500,
            detail="Therapist service unavailable"
        )

    return {"reply": reply}