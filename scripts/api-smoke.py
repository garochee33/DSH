#!/usr/bin/env python3
"""FastAPI route wiring smoke checks (no network)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.api.server import app  # noqa: E402


def main() -> int:
    required = {
        ("POST", "/rag/query"),
        ("GET", "/rag/shortcuts"),
        ("POST", "/agents/{name}/run"),
        ("POST", "/agents/{name}/stream"),
        ("GET", "/health"),
    }
    present = set()
    for route in app.routes:
        methods = getattr(route, "methods", None)
        path = getattr(route, "path", None)
        if not methods or not path:
            continue
        for method in methods:
            present.add((method, path))
    missing = [item for item in required if item not in present]
    if missing:
        print("Missing routes:")
        for method, path in missing:
            print(f"- {method} {path}")
        return 1
    print("api-smoke: all required routes present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
