# Skill Registry Policy

> **Status:** Active doctrine for the Trinity skill ecosystem.
> **Established:** 2026-04-25 (after the [Skill Landscape Audit](https://internal/SKILL_LANDSCAPE_AUDIT_2026-04-25.md))
> **Mirrored at:** `~/projects/AI_AGENTS/cto-build-framework/skills/SKILL_REGISTRY_POLICY.md`, `~/projects/trinity-consortium/skills/SKILL_REGISTRY_POLICY.md`, `~/trinity-unified-ai/skills/SKILL_REGISTRY_POLICY.md`, `~/DOME-HUB/docs/SKILL_REGISTRY_POLICY.md` (byte-identical)

---

## 1. Why this policy exists

Skills sprawled across 11 registries with **619 SKILL.md files** baselined on 2026-04-25. The same skill name appeared in up to 9 locations with up to 6 distinct content versions. Without a written policy, drift was silent and recurrent. This document fixes the source-of-truth pattern, the mirror direction, and the tier conventions.

## 2. Source of truth per skill family

| Skill family | Canonical source repo | Examples |
|---|---|---|
| **Framework-owned** (CTO Build Framework skills) | `~/projects/AI_AGENTS/cto-build-framework/skills/` | `cto-build-framework-validator`, `dev-auditor` |
| **Trinity ecosystem** | `~/projects/trinity-consortium/skills/` | `trinity-repo-navigator`, `god-mode`, `sacred-geometry`, `sacred-geometry-agents`, `kb-architecture`, `unified-ai-audit`, `trinity-womb-report`, `womb-3d`, `womb-3d-sacred-geometry`, `archive-manager` |
| **v2 enterprise skills** | `~/projects/trinity-consortium/skills/v2/skills/` | `ai-cost-optimizer`, `api-gateway-designer`, `ci-cd-architect`, etc. (15 skills) |
| **kimi-tier** specialized | `~/projects/trinity-consortium/skills/kimi/` | `trinity-coding-standards`, `verification-validation`, `end-to-end-wiring` |
| **Standalone single-skill repos** | The repo itself | `~/projects/use-railway/SKILL.md` |
| **Tool-bundled / IDE-native** (out of scope) | The tool's own bundle | `.cursor/skills-cursor/`, `.openclaw/lib/node_modules/openclaw/skills/`, `.claude/plugins/marketplaces/` |
| **Codex-evolved** (intentionally diverges from canonical) | `~/.codex/skills/<name>/` | Codex variants typically add frontmatter + `agents/openai.yaml` hook |

## 3. Tier conventions

Skills can legitimately exist in multiple **tiers**. Each tier maintains its own canonical content. Cross-tier sync is forbidden without explicit user direction.

| Tier | Path pattern | Purpose |
|---|---|---|
| **main-tree** | `<repo>/skills/<name>/` | Primary canonical; widest mirror set |
| **agents-tier** | `<repo>/agents/skills/<name>/` | Agent-execution-layer variant; may differ from main-tree |
| **kimi-tier** | `<repo>/skills/kimi/<name>/` | Tuned for Kimi agents |
| **codex-tier** | `~/.codex/skills/<name>/` | Codex variant with `agents/openai.yaml` invocation hook |
| **utility-nested** | `<repo>/skills/utility/<name>/` | Often a duplicate of main-tree; deprecation candidate |
| **docs-tier** | `<repo>/docs/skills/<name>/` or `docs/hub/knowledge-base/.../skills/<name>/` | Documentation reference copy |
| **standalone-repo** | `~/projects/<skill-name>/SKILL.md` | Single-skill repo (e.g., `use-railway`) |
| **`.agents/skills/`** legacy | `<repo>/.agents/skills/<name>/` | Deprecated; do not mirror to; will be marked in Phase 6 |
| **vendor mirror** | `<repo>/knowledge-base/vendor/<source-repo>/.../skills/<name>/` | Vendored snapshot from another repo; sync from canonical periodically |

## 4. Mirror direction

- Canonical → tool homes (`.codex`, `.cursor`, `.openclaw`, `.claude`, `.kiro`, `.unified-ai`)
- Canonical → project mirrors (`trinity-consortium/skills/...`, `trinity-unified-ai/skills/...`)
- Canonical → DOME-HUB tiers (`DOME-HUB/agents/skills/...`, `DOME-HUB/home/.unified-ai/skills/...`, etc.)
- **Never reverse direction** — if a mirror has newer content, raise it to user before promoting

## 5. When to add a new skill

1. Create the SKILL.md in the **canonical source repo** for its family (per §2)
2. Register it in the canonical INDEX.md
3. Mirror to relevant tool homes (`.codex` always; others as needed)
4. If Codex-tier is needed, add `agents/openai.yaml` hook
5. Run `~/projects/trinity-consortium/scripts/sync-skills.sh` to verify parity

## 6. When to mirror an existing skill

A new mirror is added only when:
- A new tool home is being adopted (e.g., a fresh Claude/Cursor install)
- A new tier convention is being established
- A user explicitly asks for it

Adding a mirror without intent creates drift surface area. Don't.

## 7. Deprecation policy

- **Mark, don't delete.** Add a banner to the INDEX.md and a header note to each SKILL.md.
- Keep deprecated content on disk for at least one full cycle (typically until the next quarter's audit).
- Only after an explicit user "OK to delete" do deprecated paths come off disk.

## 8. Tool-specific exceptions (out of scope for sync)

These are **never** mirrored to from canonical Trinity sources:

- **Claude plugin marketplace** (`~/.claude/plugins/marketplaces/`) — third-party plugins
- **Cursor IDE-native** (`~/.cursor/skills-cursor/`) — IDE-specific skills (12 skills: `create-subagent`, `migrate-to-skills`, `shell`, `statusline`, etc.)
- **OpenClaw bundled lib** (`~/.openclaw/lib/node_modules/openclaw/skills/`) — tool-shipped skills
- **Codex temp plugin cache** (`~/.codex/.tmp/plugins/`) — transient
- **Codex vendor imports** (`~/.codex/skills/utility/...`, vendor figma/playwright/sora/etc.) — third-party-curated skills

## 9. Sync helper script

Use `~/projects/trinity-consortium/scripts/sync-skills.sh`:

```
# Default — dry-run audit only, no changes
./scripts/sync-skills.sh

# Apply — sync mirrors to canonical within each tier
./scripts/sync-skills.sh --apply
```

The script:
- Discovers every Trinity skill in §2 canonical paths
- Checks each known mirror for SHA parity within tier
- Reports drift with paths + SHAs
- With `--apply`, copies canonical → mirror (never deletes; never reverses direction)

## 10. Audit cadence

Run a fresh audit (`SKILL_LANDSCAPE_AUDIT_<YYYY-MM-DD>.md`) when:
- More than 30 days have passed since the last audit
- A new tool home is added to the ecosystem
- A repo merge or major refactor touches skill paths
- Drift is detected by `sync-skills.sh` that can't be explained by tier separation

## 11. Halt conditions

If during a sync operation:
- A skill has 3+ tier-distinct canonicals AND tier intent is unclear → **halt + ask**
- A mirror has newer mtime than canonical → **halt + ask** (potential reverse-promotion)
- A live repo has uncommitted changes in skill paths → **halt + show user**
- An INDEX.md row references a path that doesn't exist → **note, don't fix without confirmation**

## 12. References

- Audit: `~/DOME-HUB/docs/SKILL_LANDSCAPE_AUDIT_2026-04-25.md` (also at `~/trinity-unified-ai/reports/`)
- Execution log: `~/.claude/plans/skill-landscape-execution-log-2026-04-25.md`
- Plan: `~/.claude/plans/audit-the-wider-zesty-ripple.md`
- Sync script: `~/projects/trinity-consortium/scripts/sync-skills.sh`
