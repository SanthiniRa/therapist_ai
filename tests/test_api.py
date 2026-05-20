import importlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


def import_main_with_env(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-client-secret")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key")
    monkeypatch.setenv("CORS_ALLOW_ORIGINS", "http://localhost:3000")
    monkeypatch.setenv("OAUTH_CALLBACK_URL", "http://localhost:8000/auth/google/callback")
    monkeypatch.setenv("OAUTH_POST_LOGIN_REDIRECT", "http://localhost:3000/chat")
    monkeypatch.setenv("RAG_DATA_DIR", str(Path(__file__).resolve().parents[1] / "backend" / "data"))

    main = importlib.import_module("backend.main")
    importlib.reload(main)
    return main


def test_health_endpoint(monkeypatch):
    main = import_main_with_env(monkeypatch)
    monkeypatch.setattr(main, "load_memory", lambda: None)
    monkeypatch.setattr(main, "init_rag", lambda: None)

    with TestClient(main.app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Therapist AI is healthy"}


def test_chat_requires_auth(monkeypatch):
    main = import_main_with_env(monkeypatch)
    monkeypatch.setattr(main, "load_memory", lambda: None)
    monkeypatch.setattr(main, "init_rag", lambda: None)

    with TestClient(main.app) as client:
        response = client.post("/chat", json={"message": "Hello"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_user_endpoint_returns_none_without_session(monkeypatch):
    main = import_main_with_env(monkeypatch)
    monkeypatch.setattr(main, "load_memory", lambda: None)
    monkeypatch.setattr(main, "init_rag", lambda: None)

    with TestClient(main.app) as client:
        response = client.get("/user")

    assert response.status_code == 200
    assert response.json() == {"user": None}
