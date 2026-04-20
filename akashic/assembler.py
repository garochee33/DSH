"""
Akashic Assembler — session context generator
Queries the dimensional field and writes .akashic-context
for the current session. Run on every new terminal.

Run: python3 akashic/assembler.py [optional: concept]
"""
from __future__ import annotations
import sys
import os
from pathlib import Path
from datetime import datetime, timezone

DOME_ROOT = Path(os.environ.get("DOME_ROOT") or Path(__file__).resolve().parents[1])
sys.path.insert(0, str(DOME_ROOT))

from akashic.record import query

OUTPUT = DOME_ROOT / ".akashic-context"


def _cwd_concept() -> str:
    """Infer session concept from current working directory."""
    cwd = Path(os.getcwd())
    skip = {"Users", "/", os.environ.get("USER", "")}
    for p in reversed(cwd.parts):
        if p not in skip:
            return p
    return "DOME-HUB sovereign node"


def assemble(concept: str | None = None) -> str:
    concept = concept or _cwd_concept()

    sections = []

    # Pull architecture-level records first (foundational)
    arch = query(concept, depth="architecture", n=3)
    if arch:
        sections.append("## Architecture")
        for r in arch:
            sections.append(f"[{r['domain']}] {r['content'][:300]}")

    # Pull recent decisions
    decisions = query(concept, depth="decision", n=3)
    if decisions:
        sections.append("\n## Decisions")
        for r in decisions:
            sections.append(f"[{r['domain']}] {r['content'][:300]}")

    # Pull recent events
    events = query(concept, depth="event", n=2)
    if events:
        sections.append("\n## Recent Events")
        for r in events:
            sections.append(f"[{r['domain']}] {r['content'][:200]}")

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    header = f"# Akashic Context — {concept}\nAssembled: {timestamp}\n"
    body = "\n".join(sections) if sections else "No records found in the field yet."

    return f"{header}\n{body}"


def main():
    concept = sys.argv[1] if len(sys.argv) > 1 else None
    context = assemble(concept)
    OUTPUT.write_text(context, encoding="utf-8")
    print(f"[akashic] context assembled → {OUTPUT}")
    print(f"\n{context[:500]}...")


if __name__ == "__main__":
    main()
