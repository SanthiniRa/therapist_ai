import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# -----------------------------
# Load embedding model
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# Data storage
# -----------------------------
documents = []
embeddings = None
index = None

DATA_FILE = "data/knowledge.txt"


# -----------------------------
# Load knowledge from file
# -----------------------------
def load_documents():
    global documents

    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r") as f:
        text = f.read()

    # split into chunks (better than lines)
    documents = [text[i:i+300] for i in range(0, len(text), 300)]

    return documents


# -----------------------------
# Build FAISS index
# -----------------------------
def build_index():
    global embeddings, index

    if not documents:
        return

    embeddings = model.encode(documents)
    embeddings = np.array(embeddings).astype("float32")

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)


# -----------------------------
# Retrieve relevant context
# -----------------------------
def get_context(query: str, k=3):
    if index is None:
        return ""

    query_vec = model.encode([query])
    query_vec = np.array(query_vec).astype("float32")

    distances, indices = index.search(query_vec, k)

    results = [documents[i] for i in indices[0] if i < len(documents)]

    return "\n".join(results)


# -----------------------------
# Add knowledge dynamically
# -----------------------------
def add_knowledge(text: str):
    global documents

    # Save to file
    with open(DATA_FILE, "a") as f:
        f.write(text + "\n")

    documents.append(text)

    # Rebuild index
    build_index()

    return "Knowledge added successfully."


# -----------------------------
# Initialize system
# -----------------------------
def init_rag():
    load_documents()
    build_index()