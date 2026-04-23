"""
Akashic Record — dimensional entry writer
Stores structured records into ChromaDB with domain/depth/node metadata.
"""
from __future__ import annotations
import os, uuid
from datetime import datetime, timezone
from typing import Literal

import chromadb
from chromadb.utils import embedding_functions

DOME_ROOT = os.environ.get("DOME_ROOT", os.path.expanduser("~/DOME-HUB"))
CHROMA_PATH = f"{DOME_ROOT}/db/chroma"
NAMESPACE = "akashic"
_MODEL_NAME = "all-MiniLM-L6-v2"
# Pin cache inside DOME-HUB via env var (set in zshrc-dome.sh)
os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", f"{DOME_ROOT}/models")

Domain = Literal["security", "agent", "build", "trinity", "infra", "creative", "meta"]
Depth  = Literal["event", "decision", "architecture", "axiom"]


def _collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=_MODEL_NAME
    )
    return client.get_or_create_collection(NAMESPACE, embedding_function=ef)


def write(
    content: str,
    domain: Domain,
    depth: Depth,
    node: str = "system",
    tags: list[str] | None = None,
    resonance: list[str] | None = None,
) -> str:
    """Write a dimensional record. Returns the entry id."""
    entry_id = str(uuid.uuid4())
    col = _collection()
    col.add(
        ids=[entry_id],
        documents=[content],
        metadatas=[{
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "domain": domain,
            "depth": depth,
            "node": node,
            "tags": ",".join(tags or []),
            "resonance": ",".join(resonance or []),
        }],
    )
    return entry_id


def query(
    concept: str,
    domain: Domain | None = None,
    depth: Depth | None = None,
    n: int = 5,
) -> list[dict]:
    """Retrieve records by resonance — dimensional, not linear."""
    col = _collection()
    where: dict = {}
    if domain:
        where["domain"] = domain
    if depth:
        where["depth"] = depth

    results = col.query(
        query_texts=[concept],
        n_results=n,
        where=where if where else None,
        include=["documents", "metadatas", "distances"],
    )

    records = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        records.append({"content": doc, "resonance_score": 1 - dist, **meta})
    return records
