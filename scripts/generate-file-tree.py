#!/usr/bin/env python3
"""
Generate FILE_TREE.md — human-readable depth-limited tree + recursive file/dir counts.

Used by scripts/update-tree-map.sh on git commit and session end.
Excludes align with scripts/fractalmap-generate.sh (+ repo .fractalmapignore).
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DOME_ROOT = Path(os.environ.get("DOME_ROOT", Path.home() / "DSH")).resolve()
REGISTRY = DOME_ROOT / "config" / "fractalmap-repos.yaml"

DEFAULT_EXCLUDE_PARTS = [
    "node_modules",
    ".git",
    ".venv",
    "venv",
    ".venv-coreml",
    "__pycache__",
    "dist",
    "build",
    ".next",
    ".turbo",
    ".cache",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".DS_Store",
    ".fractalmap",
    "deps",
    "coverage",
    "htmlcov",
    "out",
    ".output",
    "storybook-static",
    "playwright-report",
    ".pnpm-store",
    ".parcel-cache",
    ".vite",
    ".gradle",
    "Pods",
    "bower_components",
]


def load_registry() -> dict[str, Path]:
    """Parse fractalmap-repos.yaml without PyYAML (simple line parser)."""
    repos: dict[str, Path] = {}
    if not REGISTRY.is_file():
        return {"dsh": DOME_ROOT}
    current_name: str | None = None
    for line in REGISTRY.read_text(encoding="utf-8").splitlines():
        m_name = re.match(r"^\s*-\s*name:\s*(\S+)", line)
        if m_name:
            current_name = m_name.group(1)
            continue
        m_path = re.match(r"^\s*path:\s*(.+)", line)
        if m_path and current_name:
            repos[current_name] = Path(m_path.group(1).strip()).expanduser()
            current_name = None
    return repos or {"dsh": DOME_ROOT}


def build_tree_exclude_pattern(repo_path: Path) -> str:
    parts = list(DEFAULT_EXCLUDE_PARTS)
    ignore_file = repo_path / ".fractalmapignore"
    if ignore_file.is_file():
        for line in ignore_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts.append(line)
    # tree -I uses | as OR of basename patterns
    return "|".join(dict.fromkeys(parts))


def should_skip(name: str, exclude_basenames: set[str]) -> bool:
    return name in exclude_basenames


def count_entries(repo_path: Path, exclude_basenames: set[str]) -> tuple[int, int]:
    """Recursive file/dir counts with directory-name excludes (prune)."""
    dir_count = 0
    file_count = 0
    for root, dirs, files in os.walk(repo_path, topdown=True):
        dirs[:] = [d for d in dirs if not should_skip(d, exclude_basenames)]
        rel = Path(root).relative_to(repo_path)
        if rel != Path(".") and should_skip(rel.name, exclude_basenames):
            continue
        dir_count += len(dirs)
        file_count += len(files)
    return dir_count, file_count


def run_tree(repo_path: Path, depth: int, exclude_pattern: str) -> str:
    repo_path = repo_path.resolve()
    display_root = repo_path.name if repo_path.name else str(repo_path)
    try:
        proc = subprocess.run(
            ["tree", "-a", f"-L{depth}", "-I", exclude_pattern, str(repo_path)],
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            lines = proc.stdout.strip().splitlines()
            # Normalize root label to repo name for consistency
            if lines:
                lines[0] = f"{display_root}/"
            return "\n".join(lines)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return _fallback_tree(repo_path, depth, set(exclude_pattern.split("|")))


def _fallback_tree(repo_path: Path, depth: int, exclude: set[str]) -> str:
    lines = [f"{repo_path.name}/"]

    def walk(path: Path, prefix: str, level: int) -> None:
        if level > depth:
            return
        try:
            entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except OSError:
            return
        entries = [e for e in entries if not should_skip(e.name, exclude)]
        for i, entry in enumerate(entries):
            last = i == len(entries) - 1
            branch = "└── " if last else "├── "
            lines.append(f"{prefix}{branch}{entry.name}{'/' if entry.is_dir() else ''}")
            if entry.is_dir() and level < depth:
                extension = "    " if last else "│   "
                walk(entry, prefix + extension, level + 1)

    walk(repo_path, "", 1)
    return "\n".join(lines)


def generate_file_tree(
    repo_path: Path,
    *,
    depth: int = 3,
    output: Path | None = None,
) -> Path:
    repo_path = repo_path.resolve()
    if not repo_path.is_dir():
        raise FileNotFoundError(f"Repo path not found: {repo_path}")

    output = output or repo_path / "FILE_TREE.md"
    exclude_pattern = build_tree_exclude_pattern(repo_path)
    exclude_basenames = set(exclude_pattern.split("|"))
    dir_count, file_count = count_entries(repo_path, exclude_basenames)
    tree_body = run_tree(repo_path, depth, exclude_pattern)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rel_path = f"~/{repo_path.relative_to(Path.home())}" if repo_path.is_relative_to(Path.home()) else str(repo_path)

    content = f"""# {repo_path.name} — File Tree Map

> Auto-generated by `scripts/generate-file-tree.py`. Last run: {generated}.
> Path: `{rel_path}` · {dir_count} dirs · {file_count} files (skipping {len(exclude_basenames)} exclude patterns)
> Depth: {depth}

```
{tree_body}
```
"""
    output.write_text(content, encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate FILE_TREE.md for DSH repos.")
    parser.add_argument("--repo", default="dsh", help="Registry name (fractalmap-repos.yaml)")
    parser.add_argument("--path", type=Path, help="Override repo path")
    parser.add_argument("--depth", type=int, default=3, help="Tree display depth (default: 3)")
    parser.add_argument("--all", action="store_true", help="Generate for every registered repo")
    parser.add_argument("--list", action="store_true", help="List registered repos")
    args = parser.parse_args()

    registry = load_registry()

    if args.list:
        for name, path in registry.items():
            print(f"{name}\t{path}")
        return 0

    targets: list[tuple[str, Path]] = []
    if args.all:
        targets = list(registry.items())
    elif args.path:
        targets = [(args.path.name, args.path.expanduser())]
    else:
        path = registry.get(args.repo)
        if not path:
            print(f"Unknown repo: {args.repo}", file=sys.stderr)
            return 1
        targets = [(args.repo, path)]

    for name, path in targets:
        if not path.is_dir():
            print(f"[file-tree] SKIP {name}: missing {path}", file=sys.stderr)
            continue
        out = generate_file_tree(path, depth=args.depth)
        print(f"[file-tree] {name} → {out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
