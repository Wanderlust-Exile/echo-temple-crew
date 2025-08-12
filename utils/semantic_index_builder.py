from crewai.tools import tool
import os
import json
from sentence_transformers import SentenceTransformer
import numpy as np

INDEX_FILE = "data/semantic_index.json"
MODEL = SentenceTransformer("all-MiniLM-L6-v2")

@tool("build_index_tool")
def build_index_tool():
    """Build or refresh the semantic search index."""
    if not os.path.exists("data"):
        print("[INDEX] No data directory found.")
        return "No data to index."

    entries = []
    for root, _, files in os.walk("data"):
        for file in files:
            if file.endswith(".txt") or file.endswith(".md") or file.endswith(".json"):
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    content = f.read()
                    entries.append({"file": file, "content": content})

    embeddings = MODEL.encode([e["content"] for e in entries])
    index_data = [{"file": e["file"], "embedding": emb.tolist()} for e, emb in zip(entries, embeddings)]

    os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=4)

    return f"Indexed {len(entries)} documents."
