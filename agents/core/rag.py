"""
DOME-HUB RAG Pipeline — ingest, retrieve, augment, generate
"""
from __future__ import annotations
import re
from pathlib import Path
from typing import Callable

from agents.core.memory.vector import VectorMemory

SUPPORTED_EXTS = {".md", ".txt", ".py", ".ts"}


def chunk_text(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping character-level chunks."""
    chunks, start = [], 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start += size - overlap
    return [c for c in chunks if c.strip()]


def _load_source(source: str) -> str:
    """Load text from a file path or URL."""
    if source.startswith("http://") or source.startswith("https://"):
        import urllib.request
        with urllib.request.urlopen(source) as r:
            raw = r.read().decode("utf-8", errors="replace")
        # strip HTML tags for web pages
        return re.sub(r"<[^>]+>", " ", raw)
    path = Path(source)
    if path.suffix not in SUPPORTED_EXTS:
        raise ValueError(f"Unsupported file type: {path.suffix}. Supported: {SUPPORTED_EXTS}")
    return path.read_text(encoding="utf-8")


class RAGPipeline:
    def __init__(
        self,
        namespace: str = "rag",
        llm_fn: Callable[[list[dict]], str] | None = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ):
        """
        llm_fn: callable(messages: list[dict]) -> str
                messages follow OpenAI chat format [{role, content}, ...]
        """
        self.memory = VectorMemory(namespace=namespace)
        self.llm_fn = llm_fn
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def ingest(self, source: str) -> int:
        """Load source, chunk, and store in vector memory. Returns chunk count."""
        text = _load_source(source)
        chunks = chunk_text(text, self.chunk_size, self.chunk_overlap)
        for i, chunk in enumerate(chunks):
            self.memory.store(chunk, metadata={"source": source, "chunk": i})
        return len(chunks)

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """Retrieve top_k semantically relevant chunks."""
        return self.memory.search(query, top_k=top_k)

    def augment(self, query: str, context: list[dict]) -> str:
        """Build an augmented prompt from query + retrieved context."""
        ctx_text = "\n\n---\n\n".join(r["text"] for r in context)
        return (
            f"Use the following context to answer the question.\n\n"
            f"Context:\n{ctx_text}\n\n"
            f"Question: {query}"
        )

    def generate(self, query: str, top_k: int = 5) -> str:
        """Full RAG loop: retrieve → augment → generate."""
        if not self.llm_fn:
            raise RuntimeError("llm_fn is required for generate()")
        context = self.retrieve(query, top_k=top_k)
        prompt = self.augment(query, context)
        return self.llm_fn([{"role": "user", "content": prompt}])
