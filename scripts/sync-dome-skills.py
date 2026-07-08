#!/usr/bin/env python3
"""Sync canonical DSH skill docs into agent-specific SKILL.md mirrors.

Discovers:
  - Top-level ``kb/skills/*.md`` (excluding INDEX.md)
  - Directory packages ``kb/skills/<name>/SKILL.md`` when no sibling ``<name>.md`` exists

When both ``foo.md`` and ``foo/SKILL.md`` exist, the top-level ``.md`` wins (canonical doc).
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "kb" / "skills"
CANONICAL_INDEX = SOURCE_DIR / "INDEX.md"
TARGET_ROOTS = [
    ROOT / "agents" / "Codex" / "skills" / "dsh",
    ROOT / "home" / ".codex" / "skills" / "dsh",
    ROOT / "home" / ".unified-ai" / "skills" / "dsh",
]

DESCRIPTIONS = {
    "algorithms": "Algorithm design and analysis skill for DSH; use when working on optimization, data structures, or computational procedures.",
    "cognitive": "Cognitive systems skill for reasoning, memory, and agent behavior; use when designing agent workflows or mental-model tooling.",
    "compute": "High-performance numerical and quantum compute skill for scientific workloads; use when working on numeric algorithms, simulation, or acceleration.",
    "fractals": "Fractal geometry and self-similarity skill; use when working on recursive geometric or visual systems.",
    "frequency": "Frequency-domain and signal-processing skill; use when working on Fourier, spectral, or resonance analysis.",
    "math": "General mathematical methods skill for symbolic and numerical work; use when solving equations or deriving relationships.",
    "skill-creator": "Skill authoring and optimization skill; use when creating, improving, testing, or packaging skills for DSH agents.",
    "visual-storytelling": "Visual storytelling skill chain for DSH; use for narrative motion, scroll-driven UX, and stack-aware implementation rails.",
    "greenergyfl-finance": "GreenEnergyFL financial advisor skill; use for invoices, cash flow, bills, and job finances for the contracting business.",
}


@dataclass(frozen=True)
class SkillSource:
    name: str
    source_path: Path  # .md file, or package directory containing SKILL.md
    target_name: str
    is_package: bool


def discover_skills() -> list[SkillSource]:
    """Collect skill sources. Prefer ``<name>.md`` over ``<name>/SKILL.md`` when both exist."""
    by_md: dict[str, Path] = {}
    for path in sorted(SOURCE_DIR.glob("*.md")):
        if path.name.upper() == "INDEX.MD":
            continue
        by_md[path.stem] = path

    by_dir: dict[str, Path] = {}
    for path in sorted(SOURCE_DIR.iterdir()):
        if not path.is_dir():
            continue
        if path.name.startswith((".", "_")) or path.name == "__pycache__":
            continue
        skid = path / "SKILL.md"
        if skid.is_file():
            by_dir[path.name] = path

    names = sorted(set(by_md) | set(by_dir))
    out: list[SkillSource] = []
    for name in names:
        if name in by_md:
            out.append(
                SkillSource(
                    name=name,
                    source_path=by_md[name],
                    target_name=name,
                    is_package=False,
                )
            )
        else:
            out.append(
                SkillSource(
                    name=name,
                    source_path=by_dir[name],
                    target_name=name,
                    is_package=True,
                )
            )
    return out


def _canonical_skill_section(text: str) -> str:
    marker = "## Canonical Skill Docs"
    idx = text.find(marker)
    if idx < 0:
        raise ValueError(f"Missing `{marker}` section in {CANONICAL_INDEX}")
    rest = text[idx + len(marker) :]
    lines = rest.splitlines()
    buf: list[str] = []
    for line in lines:
        if line.startswith("## ") and "Canonical Skill Docs" not in line:
            break
        buf.append(line)
    return "\n".join(buf)


def parse_canonical_index_table() -> list[tuple[str, str]]:
    """Return (skill_name, path_literal) from the Canonical Skill Docs table."""
    text = CANONICAL_INDEX.read_text(encoding="utf-8")
    section = _canonical_skill_section(text)
    rows: list[tuple[str, str]] = []
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p]
        if len(parts) < 2:
            continue
        if parts[0].lower() == "skill" and "path" in parts[1].lower():
            continue
        if set(parts[0]) <= set("-: "):
            continue
        m1 = re.match(r"`([^`]+)`", parts[0])
        m2 = re.match(r"`([^`]+)`", parts[1])
        if m1 and m2:
            rows.append((m1.group(1), m2.group(1)))
    return rows


def expected_index_path(skill: SkillSource) -> Path:
    if skill.is_package:
        return Path("kb") / "skills" / skill.name
    return Path("kb") / "skills" / f"{skill.name}.md"


def validate_canonical_index(skills: list[SkillSource]) -> list[str]:
    """Cross-check ``kb/skills/INDEX.md`` Canonical Skill Docs table vs disk and discovery."""
    errors: list[str] = []
    try:
        index_rows = parse_canonical_index_table()
    except (OSError, ValueError) as e:
        return [str(e)]

    index_map = {name: path_lit for name, path_lit in index_rows}
    discovered = {s.name: s for s in skills}

    for name, path_lit in index_rows:
        rel = Path(path_lit.strip().rstrip("/"))
        abs_path = ROOT / rel
        if path_lit.strip().endswith(".md"):
            if not abs_path.is_file():
                errors.append(f"INDEX lists `{path_lit}` but file is missing: {abs_path}")
        else:
            if not (abs_path / "SKILL.md").is_file():
                errors.append(f"INDEX lists `{path_lit}` but package or SKILL.md missing: {abs_path / 'SKILL.md'}")

    index_names = set(index_map)
    disc_names = set(discovered)
    for name in sorted(index_names - disc_names):
        errors.append(
            f"INDEX lists skill `{name}` but discover_skills() did not emit it "
            f"(missing source or layout not covered by sync rules)."
        )
    for name in sorted(disc_names - index_names):
        errors.append(
            f"Discovered skill `{name}` ({discovered[name].source_path.relative_to(ROOT)}) "
            f"is missing from Canonical Skill Docs table in {CANONICAL_INDEX}"
        )

    for skill in skills:
        if skill.name not in index_map:
            continue
        lit = index_map[skill.name]
        rel_index = Path(lit.strip().rstrip("/"))
        rel_expected = expected_index_path(skill)
        if rel_index != rel_expected:
            hint = "directory package" if skill.is_package else "single `.md` file"
            errors.append(
                f"Skill `{skill.name}` ({hint}): INDEX path `{lit}` normalizes to `{rel_index.as_posix()}` "
                f"but discovery expects `{rel_expected.as_posix()}`."
            )

    return errors


def sync_skill(skill: SkillSource) -> list[Path]:
    created: list[Path] = []
    for root in TARGET_ROOTS:
        target_dir = root / skill.target_name
        if skill.is_package:
            if target_dir.exists():
                shutil.rmtree(target_dir)
            shutil.copytree(skill.source_path, target_dir)
            created.append(target_dir / "SKILL.md")
            continue

        content = skill.source_path.read_text(encoding="utf-8")
        description = DESCRIPTIONS.get(
            skill.name, f"DSH skill for {skill.name}. Use when working in the `{skill.name}` domain."
        )
        wrapped = (
            f"---\n"
            f"name: {skill.name}\n"
            f"description: {description}\n"
            f"---\n\n"
            f"{content.lstrip()}"
        )
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / "SKILL.md"
        target_file.write_text(wrapped, encoding="utf-8")
        created.append(target_file)
    return created


def write_index(skills: list[SkillSource]) -> None:
    """Write short mirror INDEX files only. Do **not** overwrite `kb/skills/INDEX.md`."""
    entries = "\n".join(
        f"- `{skill.name}` → `{skill.source_path.relative_to(ROOT).as_posix()}`"
        + (" (package)" if skill.is_package else "")
        for skill in skills
    )
    mirror_lines = "\n".join(f"- `{root.relative_to(ROOT).as_posix()}`" for root in TARGET_ROOTS)
    mirror_index = (
        "# DSH Skill Mirror\n\n"
        "**Canonical registry (do not overwrite):** `kb/skills/INDEX.md`\n\n"
        "Auto-synced from `kb/skills/*.md` and directory packages (`kb/skills/<name>/SKILL.md` "
        "when no `<name>.md`) by `scripts/sync-dome-skills.py`.\n\n"
        "Generated mirrors:\n"
        f"{mirror_lines}\n\n"
        "Skills:\n"
        f"{entries}\n"
    )
    for root in TARGET_ROOTS:
        (root / "INDEX.md").write_text(mirror_index, encoding="utf-8")
        if root.name == "dsh" and root.parent.name == "skills":
            parent_index = root.parent / "INDEX.md"
            parent_index.write_text(mirror_index, encoding="utf-8")


def warn_mirror_orphans(skills: list[SkillSource]) -> list[str]:
    """Children under mirror roots that are not known skills (excluding INDEX.md)."""
    allowed = {s.target_name for s in skills}
    warnings: list[str] = []
    for root in TARGET_ROOTS:
        if not root.is_dir():
            continue
        for child in root.iterdir():
            if child.name == "INDEX.md":
                continue
            if child.is_dir() and child.name not in allowed:
                warnings.append(f"Orphan mirror directory (not in sync set): {child.relative_to(ROOT)}")
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Validate kb/skills/INDEX.md vs disk + discovery only; do not write mirrors.",
    )
    args = parser.parse_args()

    if not SOURCE_DIR.exists():
        print(f"Missing source directory: {SOURCE_DIR}", file=sys.stderr)
        return 1

    skills = discover_skills()
    if not skills:
        print("No skills discovered", file=sys.stderr)
        return 1

    v_errs = validate_canonical_index(skills)
    for e in v_errs:
        print(e, file=sys.stderr)

    if args.check_only:
        if v_errs:
            print(f"Cross-check failed ({len(v_errs)} issue(s)).", file=sys.stderr)
            return 1
        print(f"OK: {len(skills)} skills discovered; INDEX table matches.")
        return 0

    if v_errs:
        print("Aborting sync: fix INDEX ↔ kb/skills cross-check errors above.", file=sys.stderr)
        return 1

    for root in TARGET_ROOTS:
        root.mkdir(parents=True, exist_ok=True)

    for skill in skills:
        sync_skill(skill)

    write_index(skills)

    orphans = warn_mirror_orphans(skills)
    for w in orphans:
        print(w, file=sys.stderr)

    print(f"Synced {len(skills)} skills into {len(TARGET_ROOTS)} mirror roots.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
