from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from .agent import therapist_response, safety_check
from .auth import app as auth_app

app = auth_app
class ChatRequest(BaseModel):
    message: str

#app = FastAPI()

@app.get("/")
def home():
    return {"status": "Therapist AI running"}

@app.post("/chat")
def chat(req: ChatRequest):

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