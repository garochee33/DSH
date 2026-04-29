"""
Akashic Watcher — background daemon
Watches logs/, kb/, projects/, agents/ for new/changed files
and auto-ingests them as dimensional records.

Run: python3 akashic/watcher.py &
"""
from __future__ import annotations
import os
import sys
import time
import hashlib
from pathlib import Path

DOME_ROOT = Path(os.environ.get("DOME_ROOT", os.path.expanduser("~/DOME-HUB")))
sys.path.insert(0, str(DOME_ROOT))

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from akashic.record import write

WATCH_DIRS = ["logs", "kb", "agents"]
EXTENSIONS = {".md", ".txt", ".py", ".ts"}

# domain inference from path
DOMAIN_MAP = {
    "logs":    "meta",
    "kb":      "meta",
    "agents":  "agent",
    "projects":"build",
    "trinity": "trinity",
    "security":"security",
    "infra":   "infra",
}

_seen: dict[str, str] = {}  # path → content hash


def _infer_domain(path: Path) -> str:
    for part in path.parts:
        if part in DOMAIN_MAP:
            return DOMAIN_MAP[part]
    return "meta"


def _infer_depth(path: Path) -> str:
    name = path.stem.lower()
    if any(k in name for k in ("decision", "architecture", "design", "schema")):
        return "architecture"
    if any(k in name for k in ("axiom", "principle", "foundation")):
        return "axiom"
    if any(k in name for k in ("session", "log", "audit", "watch")):
        return "event"
    return "decision"


def _hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


def _ingest(path: Path):
    if path.suffix not in EXTENSIONS:
        return
    try:
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            return
        h = _hash(content)
        if _seen.get(str(path)) == h:
            return  # unchanged
        _seen[str(path)] = h

        entry_id = write(
            content=content[:2000],  # cap per entry
            domain=_infer_domain(path),
            depth=_infer_depth(path),
            node="system",
            tags=[path.suffix.lstrip("."), path.parent.name],
        )
        print(f"[akashic] ✦ {path.relative_to(DOME_ROOT)} → {entry_id[:8]}")
    except Exception as e:
        print(f"[akashic] ✗ {path.name}: {e}")


class AkashicHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            _ingest(Path(event.src_path))

    def on_created(self, event):
        if not event.is_directory:
            _ingest(Path(event.src_path))


def main():
    observer = Observer()
    for d in WATCH_DIRS:
        target = DOME_ROOT / d
        if target.exists():
            observer.schedule(AkashicHandler(), str(target), recursive=True)
            print(f"[akashic] watching {d}/")

    observer.start()
    print("[akashic] watcher active — dimensional field open")
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
