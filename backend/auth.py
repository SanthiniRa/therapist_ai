from fastapi import FastAPI
from fastapi.responses import JSONResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings

auth = OAuth()

if not settings.google_client_id or not settings.google_client_secret:
    raise RuntimeError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables are required")

auth.register(
    name="google",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    max_age=settings.session_max_age,
    same_site=settings.session_same_site,
    https_only=settings.session_https_only,
)

@app.get("/login/google")
async def login(request: Request):
    redirect_uri = settings.oauth_callback_url
    return await auth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth/google/callback")
async def callback(request: Request):
    token = await auth.google.authorize_access_token(request)
    user = await auth.google.userinfo(token=token)
    request.session["user"] = {"email": user["email"], "name": user["name"]}
    return RedirectResponse(url=settings.oauth_post_login_redirect)

@app.get("/user")
async def get_user(request: Request):
    user = request.session.get("user")
    if user:
        return JSONResponse({"user": user})
    return JSONResponse({"user": None})