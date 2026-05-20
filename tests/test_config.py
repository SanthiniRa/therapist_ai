import os

from backend.config import Settings


def test_settings_api_key_falls_back_to_genai(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setenv("GENAI_API_KEY", "genai-key")

    settings = Settings()

    assert settings.api_key == "genai-key"


def test_settings_cors_allow_origins_parses_comma_list(monkeypatch):
    monkeypatch.setenv("CORS_ALLOW_ORIGINS", "http://localhost:3000, http://example.com")
    settings = Settings()

    assert settings.cors_allow_origins == ["http://localhost:3000", "http://example.com"]


def test_settings_uses_default_model_name():
    settings = Settings()

    assert settings.model_name == "models/gemini-2.5-flash"
