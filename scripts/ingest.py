#!/usr/bin/env python3
"""
DSH KB Ingest Script
Populates vector memory from all KB, logs, docs, and agent code
Run: python3 scripts/ingest.py
"""
import sys
import os

from pathlib import Path

DOME_ROOT = Path(os.environ.get("DOME_ROOT", Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(DOME_ROOT))

from agents.core.rag import RAGPipeline

SOURCES = [
    DOME_ROOT / "kb",
    DOME_ROOT / "logs",
    DOME_ROOT / "docs",
    DOME_ROOT / "brain",
    DOME_ROOT / "memory",
    DOME_ROOT / "README.md",
    DOME_ROOT / "INDEX.md",
    DOME_ROOT / "MANUAL.md",
    DOME_ROOT / "agents/core",
]

# .json intentionally omitted — RAGPipeline._load_source rejects unknown suffixes,
# so including .json here just produced "Unsupported file type" warnings for every config.
EXTENSIONS = {".md", ".txt", ".py", ".ts"}

def main():
    print(f"[ingest] starting, DOME_ROOT={DOME_ROOT}", flush=True)
    rag = RAGPipeline(namespace="dome-kb")
    print(f"[ingest] RAGPipeline ready (namespace=dome-kb)", flush=True)
    total = 0

    for source in SOURCES:
        print(f"[ingest] scanning: {source.relative_to(DOME_ROOT) if source.is_relative_to(DOME_ROOT) else source}", flush=True)
        source = Path(source)
        if not source.exists():
            print(f"  skip (not found): {source}", flush=True)
            continue

        files = [source] if source.is_file() else [
            f for f in source.rglob("*")
            if f.is_file() and f.suffix in EXTENSIONS
            and ".venv" not in str(f)
            and "__pycache__" not in str(f)
        ]

        for f in files:
            try:
                count = rag.ingest(str(f))
                print(f"  ✓ {f.relative_to(DOME_ROOT)} → {count} chunks", flush=True)
                total += count
            except Exception as e:
                print(f"  ✗ {f.name}: {e}", flush=True)

    print(f"\n✅ KB populated: {total} chunks indexed", flush=True)
    print(f"   Namespace: dome-kb", flush=True)
    print(f"   DB: {DOME_ROOT}/db/chroma", flush=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print(f"\n❌ ingest crashed: {type(e).__name__}: {e}", flush=True)
        traceback.print_exc()
        sys.exit(1)
