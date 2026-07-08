"""
DSH Vault Writer — agents → vault.

Writes well-formed Obsidian notes into the allowed PARA folders, with strict
frontmatter, deterministic slug rules, and conflict-safe filenames. The
Trinity layers (`600-Engines/`, `700-Agents/`, `800-Skills/`) and system
folders (`900-Templates/`, `.obsidian/`) are sync-managed — writes to them are
refused so agents never trample the registry-derived notes.
"""

from __future__ import annotations

import datetime as _dt
import os
import re
from pathlib import Path
from typing import Any, Iterable

DOME_ROOT = Path(os.environ.get("DOME_ROOT", Path.home() / "DSH"))
DEFAULT_VAULT_ROOT = DOME_ROOT / "brain" / "vault"

ALLOWED_FOLDERS: frozenset[str] = frozenset(
    {
        "000-Inbox",
        "100-Daily-Notes",
        "200-Projects",
        "300-Areas",
        "400-Resources",
        "500-Archive",
    }
)
FORBIDDEN_FOLDERS: frozenset[str] = frozenset(
    {"600-Engines", "700-Agents", "800-Skills", "900-Templates", ".obsidian"}
)

_SLUG_NON_ALNUM = re.compile(r"[^a-z0-9]+")
_SLUG_COLLAPSE = re.compile(r"[-_]{2,}")


def slugify(title: str) -> str:
    """Lowercase, alphanumeric + `-`, collapse repeats. Never empty."""
    s = _SLUG_NON_ALNUM.sub("-", title.strip().lower())
    s = _SLUG_COLLAPSE.sub("-", s).strip("-_")
    return s or "untitled"


def _resolve_filename(folder_path: Path, slug: str) -> Path:
    """Pick `<slug>.md`, or `<slug>-2.md`, `<slug>-3.md` if it already exists."""
    candidate = folder_path / f"{slug}.md"
    if not candidate.exists():
        return candidate
    n = 2
    while True:
        candidate = folder_path / f"{slug}-{n}.md"
        if not candidate.exists():
            return candidate
        n += 1


def _yaml_scalar(value: Any) -> str:
    """Render a scalar safely for YAML frontmatter (quote when ambiguous)."""
    if value is None:
        return '""'
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value)
    # Always quote strings — the vault's existing frontmatter convention.
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _yaml_list(values: Iterable[Any]) -> str:
    items = [_yaml_scalar(v).strip('"') for v in values]
    if not items:
        return "[]"
    return "[" + ", ".join(items) + "]"


def _format_frontmatter(fm: dict[str, Any]) -> str:
    """Serialize frontmatter using vault conventions (tags as flow list)."""
    lines = ["---"]
    for key, value in fm.items():
        if key == "tags":
            lines.append(f"{key}: {_yaml_list(value)}")
        elif isinstance(value, list):
            lines.append(f"{key}: {_yaml_list(value)}")
        else:
            lines.append(f"{key}: {_yaml_scalar(value)}")
    lines.append("---")
    return "\n".join(lines)


def write_note(
    folder: str,
    title: str,
    body: str,
    *,
    links: list[str] | None = None,
    tags: list[str] | None = None,
    status: str = "active",
    extra_frontmatter: dict[str, Any] | None = None,
    vault_root: Path | str = DEFAULT_VAULT_ROOT,
) -> Path:
    """Write a frontmattered markdown note into an allowed PARA folder.

    Args:
        folder: One of ALLOWED_FOLDERS. Trinity layers + templates are refused.
        title: Human title; also becomes the slug source.
        body: Markdown body (frontmatter is prepended automatically).
        links: Wiki-links list; defaults to `["[[Map of Content]]"]`.
        tags: Frontmatter tags; defaults to `[f"type/{folder-derived}"]`.
        status: Frontmatter `status` field.
        extra_frontmatter: Extra top-level keys merged into frontmatter.
        vault_root: Override for tests.

    Returns:
        Absolute Path of the file written.

    Raises:
        ValueError: folder not in ALLOWED_FOLDERS.
    """
    if folder in FORBIDDEN_FOLDERS:
        raise ValueError(
            f"folder '{folder}' is sync-managed and write-protected "
            f"(forbidden: {sorted(FORBIDDEN_FOLDERS)})"
        )
    if folder not in ALLOWED_FOLDERS:
        raise ValueError(
            f"folder '{folder}' not in allow-list "
            f"(allowed: {sorted(ALLOWED_FOLDERS)})"
        )

    vault_root = Path(vault_root).expanduser().resolve()
    folder_path = vault_root / folder
    folder_path.mkdir(parents=True, exist_ok=True)

    slug = slugify(title)
    target = _resolve_filename(folder_path, slug)

    today = _dt.date.today().isoformat()
    type_tag = {
        "000-Inbox": "type/inbox",
        "100-Daily-Notes": "type/daily",
        "200-Projects": "type/project",
        "300-Areas": "type/area",
        "400-Resources": "type/resource",
        "500-Archive": "type/archive",
    }[folder]

    fm: dict[str, Any] = {
        "title": title,
        "created": today,
        "tags": tags if tags is not None else [type_tag, f"status/{status}"],
        "links": (links if links is not None else ["[[Map of Content]]"]),
        "status": status,
    }
    if extra_frontmatter:
        for k, v in extra_frontmatter.items():
            if k not in fm:
                fm[k] = v
            else:
                # Allow overrides for non-load-bearing fields only.
                if k in {"status", "tags", "links"}:
                    fm[k] = v

    # Render `links` as a single quoted scalar when it's a single wiki-link
    # (matches the existing vault convention seen across engines/agents/skills).
    if isinstance(fm["links"], list) and len(fm["links"]) == 1:
        fm["links"] = fm["links"][0]

    content = _format_frontmatter(fm) + "\n\n" + body.strip() + "\n"
    target.write_text(content, encoding="utf-8")
    return target


def _smoke_test() -> None:
    """Self-check: write → verify → delete a single note in 400-Resources."""
    title = "Vault Writer Smoke Test"
    body = "This file was written by `vault_writer._smoke_test`. Safe to delete."
    path = write_note(
        "400-Resources",
        title,
        body,
        tags=["type/resource", "status/smoke-test"],
    )
    assert path.exists(), f"file not created: {path}"
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), "missing frontmatter opener"
    assert "title:" in text and title in text, "title not embedded"
    assert "Map of Content" in text, "default link missing"

    # Folder allow-list enforcement
    try:
        write_note("600-Engines", "Should Fail", "x")
    except ValueError:
        pass
    else:
        path.unlink(missing_ok=True)
        raise AssertionError("forbidden folder 600-Engines was not rejected")

    path.unlink(missing_ok=True)
    print(f"[vault_writer] ✓ smoke test PASS ({path.name} written, verified, deleted)")


if __name__ == "__main__":
    _smoke_test()
