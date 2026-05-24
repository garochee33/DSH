#!/usr/bin/env python3
"""
Ensure kb/language-landscape-<YEAR>.md exists for the calendar (or requested) year.

Copies from the latest existing landscape file and replaces that year's token in the
document so titles and section headers stay consistent. Safe to run repeatedly
(idempotent when the target file already exists).

Typical automation (Jan 1):
  cd "$DOME_ROOT" && source .venv/bin/activate && \\
    python3 scripts/rollover-language-landscape.py --ingest

Or use scripts/rollover-language-landscape.sh from cron or launchd.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

_YEAR_RE = re.compile(r"^language-landscape-(\d{4})\.md$")


def _dome_root() -> Path:
    return Path(
        os.environ.get("DOME_ROOT", Path(__file__).resolve().parent.parent)
    ).resolve()


def _kb_dir(root: Path) -> Path:
    return root / "kb"


def _discovered_years(kb: Path) -> list[int]:
    years: list[int] = []
    for p in kb.glob("language-landscape-*.md"):
        m = _YEAR_RE.match(p.name)
        if m:
            years.append(int(m.group(1)))
    return sorted(set(years))


def _template_source_year(target: int, existing: list[int]) -> int:
    """Use the newest file strictly before target; else max existing (rollover in one hop)."""
    before = [y for y in existing if y < target]
    if before:
        return max(before)
    return max(existing)


def _substitute_year(text: str, from_year: int, to_year: int) -> str:
    fy, ty = str(from_year), str(to_year)
    if fy == ty:
        return text
    return text.replace(fy, ty)


def _write_year_file(kb: Path, target: int, body: str) -> Path:
    out = kb / f"language-landscape-{target}.md"
    out.write_text(body, encoding="utf-8")
    return out


def _ingest_paths(root: Path, paths: list[Path]) -> None:
    sys.path.insert(0, str(root))
    from agents.core.rag import RAGPipeline

    rag = RAGPipeline(namespace="dome-kb")
    for p in paths:
        n = rag.ingest(str(p.resolve()))
        print(f"  ingest: {p.relative_to(root)} → {n} chunks")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create missing kb/language-landscape-<year>.md from the latest template."
    )
    parser.add_argument(
        "--year",
        type=int,
        metavar="Y",
        help="Target calendar year (default: current year)",
    )
    parser.add_argument(
        "--through",
        type=int,
        metavar="Y",
        help="Also create every missing year up to Y (inclusive), sequentially.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions only; do not write files or ingest.",
    )
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="After creating files, embed new/changed paths into ChromaDB dome-kb.",
    )
    args = parser.parse_args()

    root = _dome_root()
    kb = _kb_dir(root)
    if not kb.is_dir():
        print(f"error: kb directory not found: {kb}", file=sys.stderr)
        return 1

    existing = _discovered_years(kb)
    if not existing:
        print(
            "error: no language-landscape-*.md templates under kb/. "
            "Add at least one (e.g. language-landscape-2026.md).",
            file=sys.stderr,
        )
        return 1

    now_y = datetime.now().year
    primary = args.year if args.year is not None else now_y
    if args.through is not None and args.through < primary:
        print("error: --through must be >= --year (or default year)", file=sys.stderr)
        return 1

    hi = max(primary, args.through) if args.through is not None else primary
    lo = min(primary, args.through) if args.through is not None else primary

    mx_existing = max(existing)
    # If the span extends past the newest file, fill every missing year up to hi
    # (e.g. only 2026 on disk + --year 2028 → create 2027 then 2028).
    if hi > mx_existing:
        to_create = [y for y in range(mx_existing + 1, hi + 1) if y not in existing]
    else:
        to_create = [y for y in range(lo, hi + 1) if y not in existing]

    if not to_create:
        print(
            f"ok: kb/language-landscape-{primary}.md"
            + (f" through {hi}" if hi != primary else "")
            + " already satisfied — nothing to do."
        )
        return 0

    created: list[Path] = []
    working = list(existing)

    for target in sorted(to_create):
        if target in working:
            print(f"skip: language-landscape-{target}.md already exists")
            continue
        src_y = _template_source_year(target, working)
        src_path = kb / f"language-landscape-{src_y}.md"
        if args.dry_run:
            print(f"would create: language-landscape-{target}.md from {src_path.name}")
            working.append(target)
            working.sort()
            continue
        text = src_path.read_text(encoding="utf-8")
        new_body = _substitute_year(text, src_y, target)
        out = _write_year_file(kb, target, new_body)
        print(f"wrote: {out.relative_to(root)} (from language-landscape-{src_y}.md)")
        created.append(out)
        working.append(target)
        working.sort()

    if args.ingest and created and not args.dry_run:
        print("ingesting into dome-kb …")
        _ingest_paths(root, created)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
