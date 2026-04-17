"""
DOME-HUB Vector Memory — ChromaDB-backed persistent semantic memory
"""
from __future__ import annotations
import uuid, time
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

DOME_ROOT = Path.home() / "DOME-HUB"
_embedder = None

def _get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


class VectorMemory:
    """Persistent semantic memory backed by ChromaDB."""

    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
        self.client = chromadb.PersistentClient(
            path=str(DOME_ROOT / "db" / "chroma"),
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=namespace,
            metadata={"hnsw:space": "cosine"}
        )

    def store(self, text: str, metadata: dict | None = None) -> str:
        """Store text with optional metadata. Returns memory ID."""
        mid = str(uuid.uuid4())
        emb = _get_embedder().encode([text]).tolist()
        self.collection.add(
            ids=[mid],
            embeddings=emb,
            documents=[text],
            metadatas=[{**(metadata or {}), "ts": time.time()}]
        )
        return mid

    def search(self, query: str, top_k: int = 5, where: dict | None = None) -> list[dict]:
        """Semantic search. Returns ranked results with scores."""
        emb = _get_embedder().encode([query]).tolist()
        kwargs = {"query_embeddings": emb, "n_results": min(top_k, self.collection.count() or 1)}
        if where:
            kwargs["where"] = where
        results = self.collection.query(**kwargs)
        out = []
        for i, doc in enumerate(results["documents"][0]):
            out.append({
                "id": results["ids"][0][i],
                "text": doc,
                "score": 1 - results["distances"][0][i],
                "metadata": results["metadatas"][0][i],
            })
        return out

    def delete(self, memory_id: str):
        self.collection.delete(ids=[memory_id])

    def count(self) -> int:
        return self.collection.count()

    def clear(self):
        self.client.delete_collection(self.namespace)
        self.collection = self.client.get_or_create_collection(self.namespace)
