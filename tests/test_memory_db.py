from pathlib import Path

import pytest

from backend import memory


def test_memory_db_roundtrip(tmp_path, monkeypatch):
    db_file = tmp_path / "memory.db"
    json_file = tmp_path / "memory.json"

    monkeypatch.setattr(memory, "DB_PATH", db_file)
    monkeypatch.setattr(memory, "JSON_PATH", json_file)

    memory.init_db()

    memory.add_message("user1", "user", "hello")
    memory.add_message("user1", "assistant", "hi there")

    conversation = memory.get_conversation("user1")
    assert len(conversation) == 2
    assert conversation[0]["role"] == "user"
    assert conversation[1]["content"] == "hi there"

    session = memory.get_session("user1")
    assert session["mood"] == "neutral"

    memory.update_session("user1", "mood", "happy")
    assert memory.get_session("user1")["mood"] == "happy"

    profile = memory.get_profile("user1")
    assert profile["issues"] == []
    memory.update_profile("user1", "I feel anxious")
    assert "anxiety" in memory.get_profile("user1")["issues"]


def test_trim_conversation_keeps_last_20(tmp_path, monkeypatch):
    db_file = tmp_path / "memory.db"
    json_file = tmp_path / "memory.json"

    monkeypatch.setattr(memory, "DB_PATH", db_file)
    monkeypatch.setattr(memory, "JSON_PATH", json_file)

    memory.init_db()

    for i in range(25):
        memory.add_message("user2", "user", f"message {i}")

    conversation = memory.get_conversation("user2")
    assert len(conversation) == 20
    assert conversation[0]["content"] == "message 5"
    assert conversation[-1]["content"] == "message 24"
