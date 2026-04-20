#!/usr/bin/env python3
"""
DOME-HUB KB Ingest Script
Populates vector memory from all KB, logs, docs, and agent code
Run: python3 scripts/ingest.py
"""
import os, sys
from pathlib import Path

DOME_ROOT = Path(os.environ.get("DOME_ROOT") or Path(__file__).resolve().parents[1])
sys.path.insert(0, str(DOME_ROOT))

from agents.core.rag import RAGPipeline

SOURCES = [
    DOME_ROOT / "kb",
    DOME_ROOT / "logs",
    DOME_ROOT / "README.md",
    DOME_ROOT / "INDEX.md",
    DOME_ROOT / "MANUAL.md",
    DOME_ROOT / "agents/core",
]

EXTENSIONS = {".md", ".txt", ".py", ".ts", ".json"}

def main():
    rag = RAGPipeline(namespace="dome-kb")
    total = 0

    for source in SOURCES:
        source = Path(source)
        if not source.exists():
            print(f"  skip (not found): {source}")
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
                print(f"  ✓ {f.relative_to(DOME_ROOT)} → {count} chunks")
                total += count
            except Exception as e:
                print(f"  ✗ {f.name}: {e}")

    print(f"\n✅ KB populated: {total} chunks indexed")
    print(f"   Namespace: dome-kb")
    print(f"   DB: {DOME_ROOT}/db/chroma")

if __name__ == "__main__":
    main()
