from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
import os

load_dotenv()


def comma_split(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_bool(value: Optional[str], default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class Settings:
    google_api_key: Optional[str] = None
    genai_api_key: Optional[str] = None
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    model_name: str = "models/gemini-2.5-flash"
    session_secret: str = "super-secret-key-change-this"
    cors_allow_origins: List[str] = field(default_factory=lambda: ["http://localhost:3000"])
    session_max_age: int = 3600
    session_same_site: str = "lax"
    session_https_only: bool = False
    frontend_url: str = "http://localhost:3000"
    oauth_callback_url: str = "http://localhost:8000/auth/google/callback"
    oauth_post_login_redirect: str = "http://localhost:3000/chat"
    rag_data_dir: str = field(default_factory=lambda: str(Path(__file__).resolve().parent / "data"))

    def __post_init__(self):
        env_values = {
            "google_api_key": os.getenv("GOOGLE_API_KEY"),
            "genai_api_key": os.getenv("GENAI_API_KEY"),
            "google_client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "google_client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "model_name": os.getenv("MODEL_NAME"),
            "session_secret": os.getenv("SESSION_SECRET"),
            "cors_allow_origins": os.getenv("CORS_ALLOW_ORIGINS"),
            "session_max_age": os.getenv("SESSION_MAX_AGE"),
            "session_same_site": os.getenv("SESSION_SAME_SITE"),
            "session_https_only": os.getenv("SESSION_HTTPS_ONLY"),
            "frontend_url": os.getenv("FRONTEND_URL"),
            "oauth_callback_url": os.getenv("OAUTH_CALLBACK_URL"),
            "oauth_post_login_redirect": os.getenv("OAUTH_POST_LOGIN_REDIRECT"),
            "rag_data_dir": os.getenv("RAG_DATA_DIR"),
        }

        for key, value in env_values.items():
            if value is not None:
                if key == "cors_allow_origins":
                    self.cors_allow_origins = comma_split(value)
                elif key == "session_max_age":
                    self.session_max_age = int(value)
                elif key == "session_https_only":
                    self.session_https_only = parse_bool(value, self.session_https_only)
                else:
                    setattr(self, key, value)

        if isinstance(self.cors_allow_origins, str):
            self.cors_allow_origins = comma_split(self.cors_allow_origins)

    @property
    def api_key(self) -> Optional[str]:
        return self.google_api_key or self.genai_api_key


settings = Settings(
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    genai_api_key=os.getenv("GENAI_API_KEY"),
    google_client_id=os.getenv("GOOGLE_CLIENT_ID"),
    google_client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    model_name=os.getenv("MODEL_NAME", "models/gemini-2.5-flash"),
    session_secret=os.getenv("SESSION_SECRET", "super-secret-key-change-this"),
    cors_allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000"),
    session_max_age=int(os.getenv("SESSION_MAX_AGE", "3600")),
    session_same_site=os.getenv("SESSION_SAME_SITE", "lax"),
    session_https_only=parse_bool(os.getenv("SESSION_HTTPS_ONLY"), False),
    frontend_url=os.getenv("FRONTEND_URL", "http://localhost:3000"),
    oauth_callback_url=os.getenv("OAUTH_CALLBACK_URL", "http://localhost:8000/auth/google/callback"),
    oauth_post_login_redirect=os.getenv("OAUTH_POST_LOGIN_REDIRECT", "http://localhost:3000/chat"),
    rag_data_dir=os.getenv("RAG_DATA_DIR", str(Path(__file__).resolve().parent / "data")),
)
