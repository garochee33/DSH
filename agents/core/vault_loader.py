"""
DSH Vault Loader — ingest Obsidian "second brain" notes into ChromaDB.

Walks `brain/vault/**/*.md`, parses YAML frontmatter, embeds the body via the
existing VectorMemory backend, and upserts by relative path.

Index files (`REGISTRY-*.md`, `MASTER_INDEX-*.md`) under the Trinity layers
(`600-Engines/`, `700-Agents/`, `800-Skills/`) are ingested with metadata
override `type=registry`. Regular notes in those folders ingest normally and
keep whatever `type` their frontmatter declares.

Re-running is idempotent: ids are the POSIX relative path, so a second run
upserts in place instead of duplicating.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable

import yaml

from agents.core.memory.vector import VectorMemory, _get_embedder

DOME_ROOT = Path(os.environ.get("DOME_ROOT", Path.home() / "DSH"))
DEFAULT_VAULT_ROOT = DOME_ROOT / "brain" / "vault"
DEFAULT_COLLECTION = "vault_notes"

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.DOTALL)
_INDEX_NAME_RE = re.compile(r"^(REGISTRY-|MASTER_INDEX-)", re.IGNORECASE)
_TRINITY_LAYERS = ("600-Engines", "700-Agents", "800-Skills")


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split a markdown document into (frontmatter dict, body)."""
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    try:
        fm = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        fm = {}
    if not isinstance(fm, dict):
        fm = {}
    return fm, match.group(2)


def _flatten_scalar(value: Any) -> str | int | float | bool:
    """Chroma metadata only accepts flat scalars — coerce lists/dicts to str."""
    if isinstance(value, (str, int, float, bool)) or value is None:
        return "" if value is None else value
    if isinstance(value, (list, tuple)):
        return ", ".join(str(v) for v in value)
    return str(value)


def _build_metadata(
    fm: dict[str, Any], rel_path: str, is_registry: bool
) -> dict[str, Any]:
    """Project frontmatter onto a Chroma-safe flat metadata dict."""
    raw_type = fm.get("type")
    if is_registry:
        note_type = "registry"
    elif isinstance(raw_type, str) and raw_type.strip():
        note_type = raw_type.strip()
    else:
        # Folder-derived fallback so every vector has a usable type facet.
        top = rel_path.split("/", 1)[0]
        note_type = {
            "000-Inbox": "inbox",
            "100-Daily-Notes": "daily",
            "200-Projects": "project",
            "300-Areas": "area",
            "400-Resources": "resource",
            "500-Archive": "archive",
            "600-Engines": "engine",
            "700-Agents": "agent",
            "800-Skills": "skill",
            "900-Templates": "template",
        }.get(top, "note")

    meta: dict[str, Any] = {
        "path": rel_path,
        "title": _flatten_scalar(fm.get("title") or Path(rel_path).stem),
        "type": note_type,
        "tags": _flatten_scalar(fm.get("tags", [])),
        "links": _flatten_scalar(fm.get("links", [])),
        "created": _flatten_scalar(fm.get("created", "")),
        "status": _flatten_scalar(fm.get("status", "")),
        "source": _flatten_scalar(fm.get("source", "")),
        "tier": _flatten_scalar(fm.get("tier", "")),
    }
    return {k: v for k, v in meta.items() if v not in ("", None)}


def _iter_vault_files(vault_root: Path) -> Iterable[Path]:
    """Yield every .md file under the vault, skipping `.obsidian/` and dotfiles."""
    for path in vault_root.rglob("*.md"):
        if any(part.startswith(".") for part in path.relative_to(vault_root).parts):
            continue
        yield path


def _is_registry_index(rel_path: str) -> bool:
    """True if this is a REGISTRY-* / MASTER_INDEX-* file under a Trinity layer."""
    parts = rel_path.split("/")
    if len(parts) < 2 or parts[0] not in _TRINITY_LAYERS:
        return False
    return bool(_INDEX_NAME_RE.match(parts[-1]))


def ingest_vault(
    vault_root: Path | str = DEFAULT_VAULT_ROOT,
    collection: str = DEFAULT_COLLECTION,
) -> dict[str, int]:
    """Walk the vault, embed each note, and upsert by relative path.

    Returns a dict with counters: `{"ingested": N, "skipped": M, "registry": K}`.
    Idempotent: re-running upserts in place (id == POSIX relative path).
    """
    vault_root = Path(vault_root).expanduser().resolve()
    if not vault_root.exists():
        raise FileNotFoundError(f"vault root not found: {vault_root}")

    mem = VectorMemory(namespace=collection)
    embedder = _get_embedder()

    ids: list[str] = []
    docs: list[str] = []
    metas: list[dict[str, Any]] = []
    counters = {"ingested": 0, "skipped": 0, "registry": 0}

    for md_path in _iter_vault_files(vault_root):
        rel_path = md_path.relative_to(vault_root).as_posix()
        try:
            raw = md_path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"[vault_loader] skip {rel_path}: {exc}", file=sys.stderr)
            counters["skipped"] += 1
            continue

        fm, body = parse_frontmatter(raw)
        body = body.strip()
        if not body:
            counters["skipped"] += 1
            continue

        is_registry = _is_registry_index(rel_path)
        if is_registry:
            counters["registry"] += 1

        meta = _build_metadata(fm, rel_path, is_registry)
        ids.append(rel_path)
        docs.append(body)
        metas.append(meta)

    if not ids:
        print("[vault_loader] no notes found — nothing to ingest")
        return counters

    embeddings = embedder.encode(docs)
    if not isinstance(embeddings, list):
        embeddings = embeddings.tolist()

    # Upsert (vs add) so re-runs replace prior content for the same path.
    mem.collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=docs,
        metadatas=metas,
    )
    counters["ingested"] = len(ids)

    print(
        f"[vault_loader] ✓ upserted {counters['ingested']} notes "
        f"({counters['registry']} registry, {counters['skipped']} skipped) "
        f"into collection '{collection}' "
        f"(backend={VectorMemory.backend()}, total={mem.count()})"
    )
    return counters


if __name__ == "__main__":
    ingest_vault()
