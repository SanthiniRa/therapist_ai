from pathlib import Path

import pytest

import backend.rag_faiss as rag_faiss


def test_chunk_text_creates_chunks_from_long_text():
    text = "Hello world. This is a simple test. Another sentence follows."
    chunks = rag_faiss.chunk_text(text, max_length=30, overlap=10)

    assert len(chunks) >= 2
    assert any("Hello world." in chunk for chunk in chunks)


def test_rag_loads_text_files_and_returns_source_labels(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    (data_dir / "knowledge.txt").write_text("This is internal knowledge about therapy.")
    (data_dir / "nhs_mental_health.txt").write_text("NHS guidance recommends breathing exercises for anxiety.")

    monkeypatch.setattr(rag_faiss, "DATA_DIR", str(data_dir))
    rag_faiss.init_rag()

    result = rag_faiss.get_context("anxiety", k=2)

    assert "Source: NHS" in result or "Source: Internal knowledge" in result
    assert "anxiety" in result.lower()
