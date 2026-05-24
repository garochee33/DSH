"""
DOME-HUB Vector Memory — ChromaDB-backed persistent semantic memory

Embedding backend priority:
  1. CoreML via ONNX Runtime (Apple Silicon Neural Engine)
  2. sentence-transformers (CPU fallback)
"""

from __future__ import annotations
import os, uuid, time
from pathlib import Path
import chromadb
from chromadb.config import Settings

DOME_ROOT = Path(os.environ.get("DOME_ROOT", Path.home() / "DOME-HUB"))
_MODELS_DIR = Path(os.environ.get("SENTENCE_TRANSFORMERS_HOME", DOME_ROOT / "models"))
_ONNX_MODEL = DOME_ROOT / "models" / "embeddings" / "model_quantized.onnx"
_embedder = None
_backend = "unknown"


def _get_embedder():
    global _embedder, _backend
    if _embedder is not None:
        return _embedder

    # Try CoreML via ONNX Runtime first (routes to Neural Engine on Apple Silicon)
    if _ONNX_MODEL.exists():
        try:
            import onnxruntime as ort
            providers = ["CoreMLExecutionProvider", "CPUExecutionProvider"]
            sess = ort.InferenceSession(str(_ONNX_MODEL), providers=providers)
            active = sess.get_providers()
            _backend = "coreml" if "CoreMLExecutionProvider" in active else "cpu-onnx"
            _embedder = _ONNXEmbedder(sess)
            print(f"[VectorMemory] ✓ Loaded ONNX embeddings via {_backend} (Neural Engine)" if _backend == "coreml" else "[VectorMemory] ✓ Loaded ONNX embeddings via CPU")
            return _embedder
        except Exception as e:
            print(f"[VectorMemory] ONNX/CoreML unavailable ({e}), falling back to sentence-transformers")

    # Fallback: sentence-transformers on CPU
    from sentence_transformers import SentenceTransformer
    _embedder = SentenceTransformer("all-MiniLM-L6-v2", cache_folder=str(_MODELS_DIR))
    _backend = "sentence-transformers"
    print("[VectorMemory] ✓ Loaded sentence-transformers (CPU)")
    return _embedder


class _ONNXEmbedder:
    """Minimal ONNX Runtime embedder matching sentence-transformers .encode() API."""

    def __init__(self, session):
        self._sess = session
        self._tokenizer = None

    def _get_tokenizer(self):
        if self._tokenizer is None:
            from tokenizers import Tokenizer
            tok_path = DOME_ROOT / "models" / "embeddings" / "tokenizer.json"
            self._tokenizer = Tokenizer.from_file(str(tok_path))
            self._tokenizer.enable_truncation(max_length=256)
            self._tokenizer.enable_padding(length=256)
        return self._tokenizer

    def encode(self, texts, **_):
        import numpy as np
        tok = self._get_tokenizer()
        if isinstance(texts, str):
            texts = [texts]
        encoded = tok.encode_batch(texts)
        ids = np.array([e.ids for e in encoded], dtype=np.int64)
        mask = np.array([e.attention_mask for e in encoded], dtype=np.int64)
        tids = np.zeros_like(ids)
        out = self._sess.run(None, {"input_ids": ids, "attention_mask": mask, "token_type_ids": tids})
        hidden = out[0]  # (batch, seq, dim)
        # Mean pooling with attention mask
        mask_exp = mask[:, :, np.newaxis].astype(np.float32)
        pooled = (hidden * mask_exp).sum(axis=1) / mask_exp.sum(axis=1).clip(min=1e-9)
        # L2 normalize
        norms = np.linalg.norm(pooled, axis=1, keepdims=True).clip(min=1e-9)
        return (pooled / norms).tolist()


class VectorMemory:
    """Persistent semantic memory backed by ChromaDB."""

    _embed_cache: dict = {}  # LRU embedding cache (query → embedding), max 256 entries

    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
        self.client = chromadb.PersistentClient(
            path=str(DOME_ROOT / "db" / "chroma"),
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=namespace, metadata={"hnsw:space": "cosine"}
        )

    @staticmethod
    def backend() -> str:
        """Return active embedding backend name."""
        _get_embedder()
        return _backend

    def store(self, text: str, metadata: dict | None = None) -> str:
        """Store text with optional metadata. Returns memory ID."""
        mid = str(uuid.uuid4())
        emb = _get_embedder().encode([text])
        if not isinstance(emb, list):
            emb = emb.tolist()
        self.collection.add(
            ids=[mid],
            embeddings=emb,
            documents=[text],
            metadatas=[{**(metadata or {}), "ts": time.time()}],
        )
        return mid

    def store_batch(self, texts: list[str], metadatas: list[dict] | None = None) -> list[str]:
        """Store multiple texts in one embedding call. 10× faster than repeated store()."""
        if not texts:
            return []
        mids = [str(uuid.uuid4()) for _ in texts]
        emb = _get_embedder().encode(texts)
        if not isinstance(emb, list):
            emb = emb.tolist()
        ts = time.time()
        metas = [
            {**(metadatas[i] if metadatas and i < len(metadatas) else {}), "ts": ts}
            for i in range(len(texts))
        ]
        self.collection.add(ids=mids, embeddings=emb, documents=texts, metadatas=metas)
        return mids

    def search(
        self, query: str, top_k: int = 5, where: dict | None = None
    ) -> list[dict]:
        """Semantic search. Returns ranked results with scores. Caches embeddings."""
        if query in VectorMemory._embed_cache:
            emb = VectorMemory._embed_cache[query]
        else:
            emb = _get_embedder().encode([query])
            if not isinstance(emb, list):
                emb = emb.tolist()
            # LRU eviction at 256 entries
            if len(VectorMemory._embed_cache) >= 256:
                VectorMemory._embed_cache.pop(next(iter(VectorMemory._embed_cache)))
            VectorMemory._embed_cache[query] = emb
        kwargs = {
            "query_embeddings": emb,
            "n_results": min(top_k, self.collection.count() or 1),
        }
        if where:
            kwargs["where"] = where
        results = self.collection.query(**kwargs)
        out = []
        for i, doc in enumerate(results["documents"][0]):
            out.append(
                {
                    "id": results["ids"][0][i],
                    "text": doc,
                    "score": 1 - results["distances"][0][i],
                    "metadata": results["metadatas"][0][i],
                }
            )
        return out

    def delete(self, memory_id: str):
        self.collection.delete(ids=[memory_id])

    def count(self) -> int:
        return self.collection.count()

    def clear(self):
        self.client.delete_collection(self.namespace)
        self.collection = self.client.get_or_create_collection(self.namespace)
