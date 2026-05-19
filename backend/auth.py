from fastapi import FastAPI
from fastapi.responses import JSONResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()
config = Config(".env")
oauth = OAuth(config)

oauth.register(
    name='google',
    client_id=config('GOOGLE_CLIENT_ID'),
    client_secret=config('GOOGLE_CLIENT_SECRET'),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={'scope': 'openid email profile'}
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://special-happiness-69jgqpw6q5gwf5gj6-3000.app.github.dev"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "super-secret-key-change-this"),
    max_age=3600,
    same_site="lax",      # For dev, use 'lax'; for prod 'none'
    https_only=False      # True in prod (requires HTTPS)
)

@app.get("/login/google")
async def login(request: Request):

    redirect_uri = "https://special-happiness-69jgqpw6q5gwf5gj6-8000.app.github.dev/auth/google/callback"

    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth/google/callback")
async def callback(request: Request):
    # Get token
    token = await oauth.google.authorize_access_token(request)

    # Get user info
    user = await oauth.google.userinfo(token=token)

    # Store user info in session
    request.session["user"] = {"email": user["email"], "name": user["name"]}

    # Redirect to the AI chat page (React frontend)
    return RedirectResponse(url="https://special-happiness-69jgqpw6q5gwf5gj6-3000.app.github.dev/chat")

@app.get("/user")
async def get_user(request: Request):
    user = request.session.get("user")
    if user:
        return JSONResponse({"user": user})
    return JSONResponse({"user": None})