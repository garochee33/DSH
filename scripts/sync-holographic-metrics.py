#!/usr/bin/env python3
"""
Sync live metrics into HOLOGRAPHIC_FRACTAL_TREE_MAP between marker comments.
Run from update-tree-map.sh after fractalmap + FILE_TREE regeneration.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DOME_ROOT = Path(os.environ.get("DOME_ROOT", Path.home() / "DSH")).resolve()
TREE_MAP = DOME_ROOT / "logs" / "HOLOGRAPHIC_FRACTAL_TREE_MAP_2026-05-14.md"
FRACTALMAP = DOME_ROOT / ".fractalmap"
MARKER_START = "<!-- FRACTAL_STACK_SYNC_START -->"
MARKER_END = "<!-- FRACTAL_STACK_SYNC_END -->"


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


def parse_file_tree() -> tuple[int | None, int | None, str | None]:
    p = DOME_ROOT / "FILE_TREE.md"
    if not p.is_file():
        return None, None, None
    text = p.read_text(encoding="utf-8")
    m = re.search(r"Last run:\s*([^\n]+)", text)
    run = m.group(1).strip() if m else None
    m2 = re.search(r"(\d+)\s+dirs\s*·\s*(\d+)\s+files", text)
    if m2:
        return int(m2.group(1)), int(m2.group(2)), run
    return None, None, run


def load_manifest() -> dict | None:
    p = FRACTALMAP / "manifest.json"
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def count_scripts() -> int:
    scripts = DOME_ROOT / "scripts"
    n = 0
    for f in scripts.iterdir():
        if f.is_file() and f.suffix in {".sh", ".py", ".ps1"}:
            n += 1
    return n


def agents_stats() -> tuple[int, int]:
  files: list[Path] = []
  for ext in ("*.py", "*.ts"):
      files.extend(p for p in (DOME_ROOT / "agents").rglob(ext) if "__pycache__" not in p.parts)
  loc = 0
  for f in files:
      try:
          loc += sum(1 for _ in f.open(encoding="utf-8", errors="ignore"))
      except OSError:
          pass
  return len(files), loc


def l1_names(manifest: dict | None) -> list[str]:
    if not manifest:
        return []
    tiers = manifest.get("tiers", {})
    l1 = tiers.get("L1", [])
    return sorted(x.get("name", "") for x in l1 if x.get("name"))


def build_stack_block() -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M %Z")
    dirs, files, ft_run = parse_file_tree()
    manifest = load_manifest()
    script_n = count_scripts()
    agent_files, agent_loc = agents_stats()

    sha = branch = gen_at = "—"
    l1_count = tree_size_h = "—"
    l1_list = l1_names(manifest)
    if manifest:
        sha = (manifest.get("git_sha") or "—")[:12]
        branch = manifest.get("git_branch", "—")
        gen_at = manifest.get("generated_at", "—")
        l1_count = str(len(l1_list))
        tree = manifest.get("tiers", {}).get("tree", {})
        if tree.get("size"):
            tree_size_h = human_size(int(tree["size"]))

    lines = [
        "## FRACTALMAP STACK — Live Tier Sync",
        "",
        f"**Synced:** {now} · **Git:** `{sha}` on `{branch}` · **Fractalmap generated:** `{gen_at}`",
        "",
        "### Layer stack (bottom → top)",
        "",
        "```",
        "L4  HOLOGRAPHIC_FRACTAL_TREE_MAP  ← navigational E8 index (this file, sectors 0–7)",
        "L3  FILE_TREE.md                  ← depth-3 human tree + recursive dir/file counts",
        "L2  .fractalmap/L0.md             ← depth-2 overview + top-level file counts",
        "L1  .fractalmap/L1/*.md          ← per-subtree depth-4 maps (one per top-level dir)",
        "L0  .fractalmap/tree-full.txt     ← full repository tree dump",
        "M   .fractalmap/manifest.json    ← SHA-256 checksums + git SHA gate for auto-refresh",
        "```",
        "",
        "### Live metrics (auto-synced)",
        "",
        "| Tier | Artifact | Live value |",
        "|------|----------|------------|",
        f"| FILE_TREE | dirs · files | **{dirs or '—'}** · **{files or '—'}** |",
        f"| FILE_TREE | last run | `{ft_run or '—'}` |",
        f"| fractalmap | L1 subtree maps | **{l1_count}** maps |",
        f"| fractalmap | tree-full.txt | **{tree_size_h}** |",
        f"| fractalmap | git SHA (manifest) | `{sha}` |",
        f"| repo | scripts/ (sh+py+ps1) | **{script_n}** |",
        f"| repo | agents/ (.py+.ts) | **{agent_files}** files · **{agent_loc:,}** LOC |",
        "",
        "### L1 map index (fractalmap)",
        "",
    ]
    if l1_list:
        lines.append(", ".join(f"`{n}/`" for n in l1_list))
    else:
        lines.append("_No L1 maps — run `bash scripts/refresh-repo-maps.sh`_")
    lines.append("")
    lines.append("### Refresh commands")
    lines.append("")
    lines.append("```bash")
    lines.append("bash scripts/refresh-repo-maps.sh          # force full stack")
    lines.append("bash scripts/fractalmap-generate.sh dsh")
    lines.append("python3 scripts/generate-file-tree.py --repo dsh")
    lines.append("python3 scripts/sync-holographic-metrics.py  # metrics block only")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def sync_tree_map() -> bool:
    if not TREE_MAP.is_file():
        print(f"[holographic-sync] missing {TREE_MAP}", file=sys.stderr)
        return False

    content = TREE_MAP.read_text(encoding="utf-8")
    block = build_stack_block()
    wrapped = f"{MARKER_START}\n{block}{MARKER_END}"

    if MARKER_START in content and MARKER_END in content:
        pattern = re.compile(
            re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END),
            re.DOTALL,
        )
        content = pattern.sub(wrapped, content, count=1)
    else:
        # Insert after REPOSITORY COVERAGE MANIFEST section (before SYSTEM TOPOLOGY)
        anchor = "## SYSTEM TOPOLOGY — L0 (Root Zoom)"
        if anchor in content:
            content = content.replace(anchor, f"{wrapped}\n\n---\n\n{anchor}", 1)
        else:
            content = content.rstrip() + "\n\n---\n\n" + wrapped + "\n"

    now = datetime.now().strftime("%Y-%m-%d %H:%M %Z")
    content = re.sub(
        r"^\*\*Last Reconciliation:\*\*.*$",
        f"**Last Reconciliation:** {now} — fractal stack metrics sync (FILE_TREE + fractalmap manifest + repo counts)",
        content,
        count=1,
        flags=re.MULTILINE,
    )

    # Inline sector quick-stats
    manifest = load_manifest()
    l1_list = l1_names(manifest)
    dirs, files, _ = parse_file_tree()
    if dirs and files:
        content = re.sub(
            r" Live tree: \*\*[\d,]+ dirs · [\d,]+ files\*\* \(FILE_TREE\.md\)\.",
            "",
            content,
        )
        content = re.sub(
            r"(Complete inventory of `~/DSH/` \(24 directories \+ 19 root files\)\.)",
            rf"\1 Live tree: **{dirs:,} dirs · {files:,} files** (FILE_TREE.md).",
            content,
            count=1,
        )
    agent_files, agent_loc = agents_stats()
    content = re.sub(
        r"agents/\s+← AGENT ENGINE — \d+ source files, [\d,]+ LOC[^\n]*",
        f"agents/                            ← AGENT ENGINE — {agent_files} source files, {agent_loc:,} LOC (live)",
        content,
        count=1,
    )
    content = re.sub(
        r"scripts/ \(\d+ scripts\)",
        f"scripts/ ({count_scripts()} scripts)",
        content,
        count=1,
    )
    if l1_list:
        names = ", ".join(l1_list)
        content = re.sub(
            r"\*\*Fractalmap L1 maps \(\d+\):\*\*[^\n]+",
            f"**Fractalmap L1 maps ({len(l1_list)}):** {names} — live from manifest.json",
            content,
            count=1,
        )

    TREE_MAP.write_text(content, encoding="utf-8")
    print(f"[holographic-sync] updated {TREE_MAP}")
    return True


def main() -> int:
    return 0 if sync_tree_map() else 1


if __name__ == "__main__":
    sys.exit(main())
