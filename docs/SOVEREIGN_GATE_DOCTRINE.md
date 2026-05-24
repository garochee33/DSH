# Sovereign Gate Doctrine

**Version:** 1.0
**Created:** 2026-05-21
**Authority:** DOME-HUB Sovereign Node
**Enforcement:** MANDATORY for all agents, operators, and sessions

---

## Purpose

The Sovereign Gate is the single mandatory ceremony that must be executed:
- **AFTER** every session, workflow, major update, upgrade, or new development
- **BEFORE** any git commit, push, deployment, or agent handoff

No code leaves this node without passing the gate.

---

## Two-Layer Architecture

### Layer 1: Sovereign Gate (`scripts/sovereign-gate.sh`)

Fast verification (< 2 min). Blocks pushes if failed.

| Phase | What It Checks |
|-------|---------------|
| 1. Node Health | dome-check.sh (security, daemons, network, data) |
| 2. Git State | All repos clean, no uncommitted work |
| 3. Code Quality | TypeScript (all repos), Python imports, lint |
| 4. Secrets | Gitleaks scan across all repos |
| 5. Index Consistency | Critical .md files exist and are fresh |
| 6. LAVA Integrity | Compile-check if LAVA scripts changed |
| 7. Build Verification | pnpm build (pre-deploy/full mode only) |
| 8. KB & Data | SQLite present, ChromaDB populated |

**Invocation:**
```bash
pnpm gate                    # standard gate
pnpm gate -- --pre-deploy    # includes builds
pnpm gate -- --full          # everything
```

**Git Hook:** Wired as `.githooks/pre-push`. Blocks push on failure.
Override: `git push --no-verify` (use sparingly).

---

### Layer 2: Sovereign Audit Full (`scripts/sovereign-audit-full.sh`)

Comprehensive multi-agent orchestration (5–15 min). Runs the full doctrine.

**Step 1 — Audit, Analyze, Cross-Check, Verify, Test, Fix, Tune, Harden:**
- Security posture (firewall, FileVault, SIP, DNS, stealth)
- Git state across all 6+ repos
- TypeScript strict-mode verification
- Python syntax + import verification
- LAVA neuromorphic script compilation
- Gitleaks secret scanning
- Dependency vulnerability audit (pnpm audit)
- Data integrity (SQLite, ChromaDB, KB count)
- Index/doc freshness (staleness detection)
- Service port health (API, KB, Nexus, Ollama)

**Step 2 — Update, Sync, Wire, Harden, Optimize:**
- Dependency updates (pnpm update)
- KB re-ingestion (ingest.py)
- Skill registry sync (sync-dome-skills.py)
- Machine profile refresh (machine-probe.py)
- Stack optimization (optimize.sh)
- Git hooks wiring verification

**Step 3 — CTO Build Framework Validation:**
- Verify validation infrastructure (domain-matrix, run-index, evidence-roadmap)
- Count and report runs, reviews, evidence packets
- Check freshness of latest validation run and review
- Auto-file a CTO validation run for this audit session
- Produce version-bound evidence per Proof Doctrine (no inflated claims)

**Invocation:**
```bash
pnpm audit-full                    # full auto
pnpm audit-full -- --dry-run       # report only
pnpm audit-full -- --step1-only    # audit without updates
pnpm audit-full -- --step2-only    # updates without audit
```

**Output:**
- Markdown report: `logs/audits/AUDIT-{timestamp}.md`
- JSON for agents: `logs/audits/AUDIT-{timestamp}.json`

---

## When to Run What

| Trigger | Command | Layer |
|---------|---------|-------|
| End of coding session | `pnpm gate` | Gate |
| Before git push | Automatic (pre-push hook) | Gate |
| Before deployment | `pnpm gate -- --pre-deploy` | Gate |
| After major upgrade | `pnpm audit-full` | Full |
| New project/feature complete | `pnpm audit-full` | Full |
| Weekly maintenance | `pnpm audit-full` | Full |
| Agent handoff | `pnpm gate` + session log | Gate |
| Before release | `pnpm audit-full` then `pnpm gate -- --pre-deploy` | Both |

---

## Multi-Agent Protocol

When AI agents (Kiro, Claude, Codex, Cursor, Grok) operate on this codebase:

1. **Session Start:** Read this doctrine + `PROTOCOLS.md`
2. **During Work:** Follow LAVA Cross-Check Protocol if touching sims
3. **Session End:** Run `pnpm gate` — must pass before claiming "done"
4. **Major Changes:** Run `pnpm audit-full` — log results in session report
5. **Handoff:** Include gate verdict + any open warnings in handoff doc

### Agent Responsibilities (Step 2 Scope)

Every agent session that makes changes must verify these are updated:

| Category | Files/Systems |
|----------|--------------|
| Indexes | INDEX.md, AGENTS.md, kb/skills/INDEX.md, MANUAL.md |
| Docs | PROTOCOLS.md, ARCHITECTURE docs, FILE_TREE.md |
| Code | TypeScript types, Python imports, route registrations |
| Infra | Docker configs, deploy scripts, env examples |
| Data | DB schemas, KB collections, memory files |
| Skills | Skill registries, SKILL.md files, skill catalogs |
| Hooks | Git hooks, CI workflows, pre-commit checks |
| Ports | Service health, API endpoints, environment configs |

---

## Repos Under Governance

| Repo | Path | Primary Stack |
|------|------|---------------|
| DOME-HUB | `/` (root) | Python + TypeScript |
| Trinity Consortium | `home/projects/trinity-consortium` | TypeScript + Python + Docker |
| S3XYVERSE | `home/projects/s3xyverse/s3xyverse-next` | Next.js + TypeScript |
| DOME Console | `home/projects/dome-console` | Next.js + TypeScript |
| Paradise Estate | `home/projects/paradise-estate-mykonos` | Static + Research |
| Cabaret 33 | `home/projects/alchemmical-cabaret-33` | Static (Netlify) |

---

## Failure Handling

- **Gate BLOCKED:** Fix all ❌ items before pushing. Warnings are advisory.
- **Audit FAIL:** Review report, fix critical items, re-run.
- **Override:** `git push --no-verify` — only for emergencies. Document why.
- **Stale indexes:** Agent must update them before session close.

---

## File Locations

```
scripts/sovereign-gate.sh        # Fast gate (pre-push)
scripts/sovereign-audit-full.sh  # Full audit doctrine
.githooks/pre-push               # Git hook (wired via core.hooksPath)
docs/SOVEREIGN_GATE_DOCTRINE.md  # This document
logs/sovereign-gate-*.log        # Gate run logs
logs/audits/AUDIT-*.md           # Full audit reports
logs/audits/AUDIT-*.json         # Machine-readable results
```

---

*This doctrine is part of the DOME-HUB sovereign governance framework.*
*All agents operating on this node are bound by it.*

---

## Revision History

| Date | Change |
|------|--------|
| 2026-05-22 | Initial creation — 8-phase gate + 3-step full audit + CTO validation |
| 2026-05-22 | Fix: `stat` command compatibility (GNU coreutils vs macOS native) |
| 2026-05-23 | Gate verified 26/0 pass. Volatile files gitignored. All repos pushed. |
