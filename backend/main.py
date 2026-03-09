from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from agent import therapist_response, safety_check

class ChatRequest(BaseModel):
    message: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Therapist AI running"}

@app.post("/chat")
def chat(req: ChatRequest):
    user_message = req.message

    if safety_check(user_message):
        reply = "I'm sorry, but I can't assist with that. Please seek help from a professional."
    else:
        reply = therapist_response(user_message)

    return {"reply": reply}