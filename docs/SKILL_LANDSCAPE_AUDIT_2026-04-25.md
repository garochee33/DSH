# Skill Landscape Audit — 2026-04-25

> **Status:** Read-only audit. No changes executed in this document. Reconciliation actions are tracked separately in `~/.claude/plans/skill-landscape-execution-log-2026-04-25.md`.
>
> **Mirrored at:** `~/DSH/docs/SKILL_LANDSCAPE_AUDIT_2026-04-25.md` and `~/trinity-unified-ai/reports/SKILL_LANDSCAPE_AUDIT_2026-04-25.md`. Both files are byte-identical.

---

## §1 — Executive Summary

| Metric | Count |
|---|---|
| AI tool homes surveyed | 7 (`.claude`, `.codex`, `.cursor`, `.openclaw`, `.kiro`, `.unified-ai`, `.agents`) |
| Total SKILL.md files baselined | **619** (excluding `.codex/.tmp/` plugin cache of ~298 transient files) |
| Unique Trinity-ecosystem skill names | 41 |
| Tool-bundled / plugin orphans (intentional) | ~396 (Claude marketplace, Cursor IDE-native, OpenClaw bundled, Codex temp plugins) |
| Skills missing from their tree's INDEX.md | **~13** Trinity skills (see §6) |

### Top 5 priority issues

1. **`trinity-repo-navigator` has 5 different content versions** across 9 locations — biggest divergence. Some splits may be intentional (tier separation), others accidental.
2. **`use-railway` has 4 versions** across a standalone repo + main-tree + utility-nested + agents-tier — needs canonical-source decision.
3. **`dev-auditor` has 2 versions** — projects vs unified-ai-KB. Trivial to reconcile.
5. **No source-of-truth policy exists** — registries don't mark themselves as canonical vs mirror, so drift is silent and recurrent.

---

## §2 — Per-Registry Inventory

### A. User-level AI tool homes

#### `.claude` — `~/.claude`
- Skill mechanism: flat `skills/<name>/SKILL.md` (user-level) + plugin marketplace at `plugins/marketplaces/`
- Registry: none for user-level skills
- User-level skill count: **1** — `cto-build-framework-validator`
- Plugin marketplace skills: **26** (third-party plugins: hookify, mcp-server-dev, claude-md-management, plugin-dev, math-olympiad, session-report, discord, telegram, imessage, etc.)

#### `.codex` — `~/.codex`
- Skill mechanism: nested `skills/<package>/skills/<name>/SKILL.md` AND flat `skills/<name>/SKILL.md`
- Registry: `~/.codex/skills/INDEX.md`
- Agent registry: `~/.codex/AGENTS.md`
- Skill count: **284 active** (44 main + 38 vendor imports + 34 plugin cache + ~168 in `.tmp/`-excluded)
- Hook mechanism: `agents/openai.yaml` (per-skill) makes it invokable as `$skill-name`

#### `.cursor` — `~/.cursor`
- Skill mechanism: `skills/<category>/<name>/SKILL.md` + IDE-native `skills-cursor/<name>/SKILL.md`
- Registry: `~/.cursor/skills/INDEX.md` (synced to Codex INDEX)
- Skill count: **58** (39 main + 12 IDE-native + 7 nested)
- IDE-native (Cursor-only): `create-subagent`, `migrate-to-skills`, `shell`, `statusline`, `canvas`, `create-skill`, `create-rule`, `update-cursor-settings`, `update-cli-config`, `split-to-prs`, `create-hook`, `babysit`
- MCP config: `~/.cursor/mcp.json` (Asana, Gmail, Calendar, Trinity KB)

#### `.openclaw` — `~/.openclaw`
- Skill mechanism: `skills/<category>/<name>/SKILL.md` + bundled lib at `lib/node_modules/openclaw/skills/`
- Registry: `~/.openclaw/skills/INDEX.md` (synced)
- Skill count: **39 active** (60 bundled lib excluded — those are tool-shipped)
- MCP config: `~/.openclaw/mcp.json` (identical to Cursor)

#### `.kiro` — `~/.kiro`
- Skill mechanism: flat `skills/<name>/SKILL.md`
- Registry: none
- Skill count: **1** — `cto-build-framework-validator`
- Status: barely populated; mostly an empty Kiro install

#### `.unified-ai` — `~/.unified-ai`
- Skill mechanism: flat `skills/<name>/SKILL.md`
- Registry: `~/.unified-ai/ai-filesystem/INDEX.md`
- Master agent registry: `~/.unified-ai/AGENTS.md`

#### `.agents` — `~/.agents`
- Skill mechanism: flat `skills/<name>/SKILL.md`
- Registry: `.skill-lock.json` (lock file)
- Skill count: **1** — `find-skills`

### B. Project repos

#### `~/projects/AI_AGENTS/cto-build-framework`
- Path: `skills/`
- Skill count: **2** — `cto-build-framework-validator`, `dev-auditor`
- Role: **canonical source-of-truth for these 2 skills** (per session decision)

- Multiple skill homes:
  - `skills/` — **39** (24 main + 15 v2 enterprise) — registry: `skills/INDEX.md`
  - `agents/skills/` — **8** — registry: `agents/skills/INDEX.md` (updated 2026-04-25 this session)
  - `.agents/skills/` — **7** legacy mirror — registry: `.agents/skills/INDEX.md`
  - `docs/skills/` — **4** documentation reference copies — no registry
  - `docs/hub/knowledge-base/cto-build/skills/` — **1** mirror

#### `~/trinity-unified-ai`
- Multiple skill homes:
  - `knowledge-base/cto-build/skills/` — **2** embedded copies
  - `knowledge-base/cto-build-framework/skills/` — **2** embedded copies

#### `~/DSH`
- Skill count: **16** — Enzo's personal sovereign env. Not a Trinity-ecosystem mirror.
- Path: `agents/`, plus skills under `kb/`, `akashic/`

#### `~/projects/use-railway`
- Standalone single-skill repo with `SKILL.md` at root
- SHA: `b0e97de9e2a5...` — matches `~/trinity-unified-ai/agents/skills/use-railway/SKILL.md` (one of 4 versions)

---

## §3 — Cross-Tool Skill-Name Index

(Trinity-ecosystem skills only; plugin-marketplace orphans listed in §5b)

| Skill | Locations | SHA distribution |
|---|---|---|
| **cto-build-framework-validator** | 12 locations across all tool homes + project mirrors | **1 SHA** (`711995260e54...`) — fully aligned this session |
| **design-architect** | .unified-ai/skills | 1 SHA |
| **find-skills** | .agents | 1 SHA — **ORPHAN** (tool-specific) |
| **gh-fix-ci** | same locations | 1 SHA |
| **god-mode** | 5+ locations across main + agents + .agents tiers | Tier-aligned: **3 SHAs by tier** |
| **notion-meeting-intelligence** | same | 1 SHA |
| **notion-research-documentation** | same | 1 SHA |
| **notion-spec-to-implementation** | same | 1 SHA |
| **react-component-architect** | same | 1 SHA |
| **refactoring-engineer** | same | 1 SHA |
| **security-auditor** | v2 mirrors | 1 SHA |
| **testing-strategist** | v2 mirrors | 1 SHA |
| **trinity-coding-standards** | kimi mirrors | 1 SHA |
| **trinity-repo-navigator** | 9 locations: main, kimi, agents, .agents, docs, unified-ai variants | **5 SHAs** ⚠️ |
| **trinity-womb-report** | reporting + agents + docs + KB locations | **2 SHAs by tier** |
| **use-railway** | standalone repo + main-tree + utility-nested + .agents + agents/unified-ai | **4 SHAs** ⚠️ |
| **verification-validation** | kimi mirrors | 1 SHA |
| **zero-trust-architecture** | v2 mirrors | 1 SHA |

---

## §4 — Divergence Map

### 4.1 — `dev-auditor` (2 SHAs)

| SHA12 | Locations |
|---|---|
| `4ecde623f0f5...` | `~/projects/AI_AGENTS/cto-build-framework/skills/dev-auditor/SKILL.md` (canonical source) |
| `8534779ea5b1...` | `trinity-unified-ai/knowledge-base/cto-build/skills/dev-auditor/SKILL.md` + `cto-build-framework/skills/dev-auditor/SKILL.md` |

**Reconciliation:** sync canonical AI_AGENTS version to all mirrors. (Previously the cto-build-framework-validator received this same treatment; dev-auditor was not. Pure parity gap.)

### 4.2 — `trinity-repo-navigator` (5 SHAs)

| SHA12 | Tier | Locations |
|---|---|---|
| `3c76ccf5a749...` | unified-ai main | `trinity-unified-ai/skills/trinity-repo-navigator/SKILL.md` |

**Reconciliation strategy:** treat as **tier-distinct canonicals**:
- kimi-tier: keep separate (already 1 SHA across mirrors)
- docs-tier: keep aligned with agents-tier mirror
- unified-ai main: align with consortium main

Expected post-reconciliation: 3-4 distinct tier SHAs, each internally consistent.

### 4.3 — `use-railway` (4 SHAs)

| SHA12 | Tier | Locations |
|---|---|---|
| `b0e97de9e2a5...` | standalone | `~/projects/use-railway/SKILL.md`, `trinity-unified-ai/agents/skills/use-railway/SKILL.md` |

**Reconciliation strategy:** standalone-repo is likely the original. Tier alignment:
- main-tree (already 1 SHA)
- utility-nested (already 1 SHA — this is a duplicate; recommend deprecating utility/ copy)
- agents-tier: align with standalone repo source
- .agents legacy: leave alone (Phase 6 will deprecate)


| SHA12 | Tier | Locations |
|---|---|---|

**Reconciliation strategy:**
- main-tree: 1 SHA already
- agents-tier: 1 SHA already (the one at `9b9396d030be...`)
- references: 1 SHA across all locations (intentional sub-skill, leave alone)
- .agents legacy: deprecate in Phase 6

---

## §5 — Orphan Map

### 5a — Trinity ecosystem orphans (3)

| Skill | Sole location | Recommended disposition |
|---|---|---|
| `find-skills` | `~/.agents/skills/find-skills/SKILL.md` | Tool-specific to `.agents`. Document, don't promote. |
| `design-architect` | `~/.unified-ai/skills/design-architect/SKILL.md` | Single-location. Already in unified-ai INDEX. |

### 5b — Tool-bundled / plugin orphans (intentional, ~396)

These are NOT divergence problems — they are tool-shipped or third-party content. Listed here for completeness; **excluded from sync scope**.

| Tool | Count | Examples |
|---|---|---|
| `.claude` plugin marketplace | 26 | hookify, mcp-server-dev (3), claude-md-management, plugin-dev (7), discord (2), telegram (2), imessage (2), math-olympiad, session-report, skill-creator, frontend-design, etc. |
| `.cursor` IDE-native (`skills-cursor/`) | 12 | create-subagent, migrate-to-skills, shell, statusline, canvas, create-skill, create-rule, update-cursor-settings, update-cli-config, split-to-prs, create-hook, babysit |
| `.openclaw` bundled lib | 60 | ordercli, coding-agent, food-order, nano-pdf, gemini, clawhub, prose, blogwatcher, gifgrep, spotify-player, weather, oracle, 1password, etc. |
| `.codex` plugin cache (`.tmp/plugins/`) | ~298 | vercel, teams, google-calendar, outlook-calendar, life-science-research, hyperframes, hugging-face, expo, build-ios-apps, plugin-eval, superpowers, atlassian-rovo, etc. |
| `.codex` vendor imports | 38 | screenshot, doc, figma-*, playwright, security-threat-model, openai-docs, sentry, jupyter-notebook, notion-*, netlify-deploy, render-deploy, chatgpt-apps, linear, cloudflare-deploy, vercel-deploy, transcribe, speech, sora, yeet |

---

## §6 — Registry Coverage Gaps

Trinity-ecosystem skills present on disk but absent from their tree's INDEX.md / REGISTRY.md:

- `archive-manager`
- `kimi/trinity-repo-navigator` (kimi-tier variant)
- `utility/pdf`
- `utility/use-railway`
- `github/gh-fix-ci`
- `github/gh-address-comments`
- `integrations/notion/notion-meeting-intelligence`
- `integrations/notion/notion-research-documentation`
- `integrations/notion/notion-knowledge-capture`
- `integrations/notion/notion-spec-to-implementation`
- `v2/skills/deep-research`
- `v2/skills/knowledge-management`
- `v2/skills/zero-trust-architecture`

### `~/trinity-unified-ai/skills/INDEX.md` — same set missing
(unified-ai mirrors consortium tree; same gap list applies)

- `unified-ai`

### `~/.unified-ai/ai-filesystem/INDEX.md` is missing:
- `v2`

- 4 reference copies live there with no registry. Recommend adding a brief INDEX.md noting these are documentation-tier copies, not the canonical source.

---

## §7 — Recommendations

### P0 — Reconcile the 4 confirmed divergences (Phase 2 of execution plan)
- `dev-auditor`: sync canonical AI_AGENTS version to all mirrors (one-shot)
- `trinity-repo-navigator`: align main-tree, agents-tier, kimi-tier, docs-tier separately
- `use-railway`: align main-tree, utility-nested, agents-tier separately; standalone repo treated as canonical for agents-tier

### P1 — Establish source-of-truth policy (Phase 5 of execution plan)
Author `SKILL_REGISTRY_POLICY.md` at canonical locations + sync helper script.

### P2 — Close registry coverage gaps (Phase 3 of execution plan)
Add the ~13 missing INDEX entries listed in §6.

### P3 — Install `cto-build-framework-validator` at 5 missing locations (Phase 4)
- `.unified-ai/skills/`
- `trinity-unified-ai/agents/skills/`
- (one more if surfaced)

### P4 — Deprecate `.agents/skills/` legacy directory (Phase 6)
Mark deprecated in INDEX.md banner + per-skill SKILL.md notes. Don't delete.

### P5 — Plugin / IDE-native / bundled skills
**Accept as out-of-scope.** Tool-shipped content is not for ecosystem sync.

### P6 — Future drift prevention

---

## Appendix A — File-counts cheat sheet

```
AI_AGENTS/cto-build-framework: 2 SKILL.md
trinity-unified-ai:          113 SKILL.md
DSH:                     16 SKILL.md
.codex (active, no tmp):     284 SKILL.md
.cursor:                      58 SKILL.md
.openclaw:                    39 SKILL.md
.claude:                      27 SKILL.md
.kiro:                         1 SKILL.md
.unified-ai:                   8 SKILL.md
.agents:                       1 SKILL.md
─────────────────────────────────
TOTAL:                       619 SKILL.md baselined
+ ~298 .codex .tmp/ plugin cache (excluded — transient)
```

## Appendix B — Reconciliation execution log

The fix-actions for divergences and orphans are recorded in:
**`~/.claude/plans/skill-landscape-execution-log-2026-04-25.md`**

Each phase has a timestamped entry with prep, actions, verification output, decisions, and outcome.

---

**End of audit.**
