import os
import re
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# -----------------------------
# Load embedding model
# -----------------------------
model = SentenceTransformer("all-mpnet-base-v2")

# -----------------------------
# Data storage
# -----------------------------
documents = []
sources = []
embeddings = None
index = None

from backend.config import settings

DATA_DIR = settings.rag_data_dir
DEFAULT_SOURCE = "Internal knowledge"


# -----------------------------
# Text chunking helpers
# -----------------------------
def chunk_text(text, max_length=300, overlap=50):
    text = text.replace("\n", " ").strip()
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = []
    current_len = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if current_len + len(sentence) + 1 <= max_length:
            current.append(sentence)
            current_len += len(sentence) + 1
            continue

        if current:
            chunks.append(" ".join(current).strip())
            if overlap > 0:
                tail = " ".join(current)[-overlap:]
                current = [tail]
                current_len = len(tail)
            else:
                current = []
                current_len = 0

        current.append(sentence)
        current_len = len(sentence) + 1

    if current:
        chunks.append(" ".join(current).strip())

    return [chunk for chunk in chunks if chunk]


def source_label(filename):
    key = os.path.splitext(os.path.basename(filename))[0].lower()
    if "nhs" in key:
        return "NHS"
    if "wiki" in key or "wikipedia" in key:
        return "Wikipedia"
    if "therapy" in key:
        return "Therapy knowledge"
    return DEFAULT_SOURCE


# -----------------------------
# Load knowledge from files
# -----------------------------
def load_documents():
    global documents, sources

    documents = []
    sources = []

    if not os.path.isdir(DATA_DIR):
        return []

    for filename in sorted(os.listdir(DATA_DIR)):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.isfile(filepath):
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read().strip()

        if not text:
            continue

        label = source_label(filename)
        for chunk in chunk_text(text):
            documents.append(chunk)
            sources.append(label)

    return documents


# -----------------------------
# Build FAISS index
# -----------------------------
def build_index():
    global embeddings, index

    if not documents:
        index = None
        embeddings = None
        return

    embeddings = model.encode(documents)
    embeddings = np.array(embeddings).astype("float32")

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)


# -----------------------------
# Retrieve relevant context
# -----------------------------
def get_context(query: str, k=3):
    if index is None or not documents:
        return ""

    query_vec = model.encode([query])
    query_vec = np.array(query_vec).astype("float32")

    distances, indices = index.search(query_vec, min(k, len(documents)))
    parts = []
    for distance, idx in zip(distances[0], indices[0]):
        if idx < 0 or idx >= len(documents):
            continue
        parts.append(f"[Source: {sources[idx]}] {documents[idx]} (score={distance:.4f})")

    return "\n\n".join(parts)


# -----------------------------
# Add knowledge dynamically
# -----------------------------
def add_knowledge(text: str, filename: str = "knowledge.txt"):
    global documents, sources

    if not os.path.isdir(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)

    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(text.strip() + "\n")

    label = source_label(filename)
    for chunk in chunk_text(text):
        documents.append(chunk)
        sources.append(label)

    build_index()
    return "Knowledge added successfully."


# -----------------------------
# Initialize system
# -----------------------------
def init_rag():
    load_documents()
    build_index()
