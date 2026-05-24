# DOME-HUB Skill Registry

Canonical source: `kb/skills/*.md` (plus nested `kb/skills/<name>/SKILL.md` packages where present)  
Last updated: 2026-05-23 (sovereign gate doctrine, pnpm workspace, vault scripts)

Generated mirrors (run `python3 scripts/sync-dome-skills.py` after skill edits — **updates Codex trees only; does not overwrite this file**; use `python3 scripts/sync-dome-skills.py --check-only` to cross-validate this table vs `kb/skills/` without writing):
- `agents/Codex/skills/dome-hub/`
- `home/.codex/skills/dome-hub/`
- `home/.unified-ai/skills/dome-hub/`

Aggregated master index (Trinity): `home/projects/trinity-consortium/skills/MASTER_INDEX.md` (68 curated Trinity skill families + ~462 atomic SKILL.md in canonical pool `trinity-unified-ai/skills-library/skills/`; 7 effective filesystem tiers — Claude/Codex/Cursor/Kiro symlink to the canonical pool; 263 trigger keywords, BM25-recallable).

Quality report: `home/projects/trinity-consortium/skills/SKILL_QUALITY_AUDIT.md` (current: 9 Tier A · 38 Tier B · 0 Tier C · 0 Tier D · avg 72.6).

---

## Canonical index map (read this once — then drill)

| Index | Path | Role |
|-------|------|------|
| **DOME-HUB root** | `INDEX.md` | Full repo directory reference, scripts, `.fractalmap`, Trinity mirror table |
| **Master architecture** | `docs/DOME-HUB-ARCHITECTURE.md` | Full stack: compute layers, memory, Trinity mirror, Appendix A |
| **This file** | `kb/skills/INDEX.md` | Skill registry, sims, LAVA, Kiro, Trinity production skills, hooks, AGENTS coverage |
| **KB hub** | `kb/README.md` | KB layout, LAVA pointers, ingest |
| **Fractalmap skill** | `skills/fractalmap/SKILL.md` | Tiered maps; generator `scripts/fractalmap-generate.sh`; output `.fractalmap/` (`tree-full.txt` gitignored) |
| **Architecture audit** | `docs/architecture-audit-2026-05-12/INDEX.md` | 2026-05-12 CTO-style audit bundle |
| **TU-AI docs** | `kb/trinity-unified-ai/docs/INDEX.md` | KB API docs index (port 3333) |
| **TU-AI engines** | `kb/trinity-unified-ai/engines/INDEX.md` | Engine catalog (bitboard, Mandelbulb, mesh, …) |
| **TU-AI knowledge-base** | `kb/trinity-unified-ai/knowledge-base/INDEX.md` | Curated KB mirror slice + inventory docs |
| **Codex mirror** | `agents/Codex/skills/INDEX.md`, `agents/Codex/skills/dome-hub/INDEX.md` | Short mirror; **source of truth = this file** |
| **Cross-check policy** | `PROTOCOLS.md` § Cross-Check Protocol | Gates that require `INDEX.md` + `kb/skills/INDEX.md` in sync |
| **Sovereign Gate Doctrine** | `docs/SOVEREIGN_GATE_DOCTRINE.md` | Mandatory pre-push/deploy gate (8 phases) + full audit (834 lines) |
| **Public export (DSH) gaps** | `docs/PUBLIC_PROD_HARDENING.md` | P0 history purge, P1 identity/path audit, P2 governance — vs DOME-HUB tip reconciliation § |
| **Spore / mesh (Phase 2)** | `MANUAL.md` § Trinity § Phase 2, `spore.sh` | `pre-spore-verify.py` gate; lock/unlock; baseline `~/.trinity-spore/mycelium-mesh.sh` vs prod `scripts/mycelium-signal.sh` |
| **Agent context** | `AGENTS.md`, `MANUAL.md`, `CLAUDE.md` | Operator + agent runbooks (cross-check §16 in MANUAL) |

---

## Canonical Skill Docs (kb/skills/)

| Skill | Path | Description |
|-------|------|-------------|
| `algorithms` | `kb/skills/algorithms.md` | Algorithm design and analysis |
| `cognitive` | `kb/skills/cognitive.md` | Cognitive architecture patterns |
| `compute` | `kb/skills/compute.md` | Compute orchestration, QuantumDome, sim engines |
| `fractals` | `kb/skills/fractals.md` | Fractal geometry, Mandelbulb, E8 lattice |
| `frequency` | `kb/skills/frequency.md` | Frequency analysis, signal processing |
| `math` | `kb/skills/math.md` | Mathematical foundations |
| `sacred_geometry` | `kb/skills/sacred_geometry.md` | Sacred geometry engines |
| `skill-creator` | `kb/skills/skill-creator.md` | Meta-skill for creating new skills |
| `greenergyfl-finance` | `kb/skills/greenergyfl-finance/` | GreenEnergyFL finance skill (SKILL.md + evals/) |
| `visual-storytelling` | `kb/skills/visual-storytelling.md` | Visual-storytelling skill chain (architect + sexyverse-designer + ui-ux-pro-max), 8 motion-stack CSVs, hard rails, 5-act narrative model — added 2026-05-13 |

---

## Simulation Files (compute/)

| File | Description |
|------|-------------|
| `compute/sim_3x3x3.py` | 3×3×3 lattice — E8/Mandelbulb + NumPy Kuramoto using **K_OPTIMAL** (Loihi/LAVA calibration); no `lava` import in root `.venv` |
| `compute/sim_evolved.py` | Evolved simulation engine — adaptive parameter optimization |
| `compute/quantum_dome/` | QuantumDome framework (core, memory, pool, profiler, scheduler) |

---

## LAVA/Loihi 2 — Neuromorphic Compute Skills

Neuromorphic computing via Intel LAVA framework, targeting Loihi 2 hardware.

| Component | Location | Purpose |
|-----------|----------|---------|
| NumPy Kuramoto lattice | `compute/sim_3x3x3.py` | Same coupling constant as Loihi line; fast local sanity sim |
| Loihi2SimCfg + LIF SNN | `home/projects/trinity-consortium/python/lava/coherence_optimizer.py` | Spiking coherence optimizer (`lava-nc`, Python 3.10 sidecar) |
| LAVA bootstrap / probe | Trinity `scripts/lava-bootstrap.sh`, `scripts/lava-probe.py` (in mirror) | Sidecar venv + hardware probe |
| Architecture docs | `docs/DOME-HUB-ARCHITECTURE.md` §3 + Appendix A | DOME-HUB + Trinity mirror map |
| Trinity mesh + Loihi docs | `home/projects/trinity-consortium/docs/ARCHITECTURE-LOIHI2-MESH.md` | Production mesh architecture |
| Optical phase reference | `home/projects/trinity-consortium/docs/OPTICAL-PHASE-COMPUTATION.md` | Optical phase engine (session 2026-05-09) |

Session reference: `logs/session-2026-05-09-mandelbulb-optical-meninges-loihi.md`

---

## Kiro Agent Skills (home/.kiro/skills/)

| Skill | Path | Description |
|-------|------|-------------|
| `cto-build-framework-validator` | `home/.kiro/skills/cto-build-framework-validator/` | CTO Build Framework governance validation |
| `paradise-estate-mykonos` | `home/.kiro/skills/paradise-estate-mykonos/` | Paradise Estate Mykonos operations |
| `ui-ux-pro-max` | `home/.kiro/skills/ui-ux-pro-max/` | AI design intelligence — 85 styles, 161 palettes, 57 fonts, 99 UX rules, **19 stacks** incl. visual-storytelling (framer-motion / gsap / r3f / spline / video / web-audio / typography-motion). BM25 search. |
| `sexyverse-designer` | `home/.kiro/skills/sexyverse-designer/` | Frontend implementation agent (v1.2) — Framer Motion + GSAP + R3F + Spline + Web Audio + kinetic typography. Wired to all motion stacks. Added 2026-05-13. |
| `visual-storytelling-architect` | `home/.kiro/skills/visual-storytelling-architect/` | Narrative-arc planner (v1.0) for scroll-driven web — 5-act model, 3 rules of motion intent, stack-per-beat selection, a11y floor, pre-ship checklist. Sits *above* the implementation skills. Added 2026-05-13. |

Cross-tier mirrors: every kiro skill is also present at `home/projects/trinity-consortium/skills/`, `.agents/skills/`, `agents/skills/`, plus runtime tiers `.config/agents/skills`, `.claude/skills`, `.codex/skills`, `.cursor/skills`, `.openclaw/skills`, `.unified-ai/skills` per skill-tier-doctrine.

---

## Trinity Production Skills (home/projects/trinity-consortium/skills/)

Top-tier (≥80 audit score):

| Skill | Score | Description |
|-------|------:|-------------|
| `trinity-site-forge` | **98** | Sovereign brand-to-site pipeline — Firecrawl + NanoBanana2 (Gemini Image) + Claude Code + s3xyverse-next stack + Hetzner deploy. CLI at `cli.ts`. Added 2026-05-13. |
| `sexyverse-designer` | 90 | (See kiro entry above) |
| `end-to-end-wiring` | 89 | Service integration + connectivity verification |
| `ui-ux-pro-max` | 85 | (See kiro entry above) |
| `womb-3d-sacred-geometry` | 85 | God-mode 3D sacred geometry + GLSL shaders + E8 lattice |
| `visual-storytelling-architect` | 80 | (See kiro entry above) |
| `nextlevelbuilder-ecosystem` | 80 | GoClaw gateway (66 MCP tools) + AgentBrain KB + SkillX marketplace |

Plus `claude-code-builtins/` — Trinity wrapper that documents the 10 Claude Code CLI runtime built-ins (update-config, simplify, schedule, loop, claude-api, keybindings-help, fewer-permission-prompts, init, review, security-review) so cross-platform agents can delegate via `claude --headless`.

Full inventory: see MASTER_INDEX.md.

---

## Audit + Maintenance Scripts (home/projects/trinity-consortium/scripts/)

| Script | Purpose |
|--------|---------|
| `skill-quality-audit.py` | Score every canonical SKILL.md 0-100 (PyYAML-backed, handles multi-line `description: >` + `triggers:` lists). Output to `SKILL_QUALITY_AUDIT.md`. |
| `skill-batch-patch.py` | Idempotent: adds missing `version` / `status` / `updated` frontmatter fields. |
| `generate-file-tree.py` | Auto-generate FILE_TREE.md across all 13 major projects (depth 3, skips node_modules/.git/etc.). |
| `generate-skill-specs.ts` | Regenerate `server/ai/swarm/skill-specs.json` from the production skills-library. |

---

## Claude Code Hooks (~/.claude/hooks/)

Wired in `~/.claude/settings.json`. Coverage:

| Hook | Event | Purpose |
|------|-------|---------|
| `trinity-skill-recall.sh` | UserPromptSubmit | Surface matching skills from MASTER_INDEX inverted index on every prompt |
| `trinity-block-dangerous-bash.sh` | PreToolUse Bash | Block 6 destructive patterns (docker compose --build, force-push main, cert deletion, rm -rf /, etc.) |
| `trinity-block-write-paths.sh` | PreToolUse Edit/Write/NotebookEdit | Block writes to the-womb/, /opt/trinity/certs/, legal evidence files, .env files |
| `trinity-project-guardrails.sh` | PostToolUse Edit/Write | Surface BRAND.md hard rails + Tesla TM check + 12-project-specific context |
| `trinity-skill-sync-reminder.sh` | PostToolUse Edit/Write | Remind on SKILL.md and stack CSV edits: INDEX.md update + tier mirror + skill-specs.json regen + production swarm registration |

---

## AGENTS.md Coverage (10 of 13 major repos)

| Repo | AGENTS.md |
|------|-----------|
| DOME-HUB (root) | ✓ |
| trinity-consortium | ✓ |
| trinity-unified-ai | ✓ |
| s3xyverse-next | ✓ |
| s3xyverse-app | ✓ |
| paradise-estate-mykonos | ✓ |
| mycelium-e8 | ✓ |
| AI_AGENTS/Sacred-Geometry-Space | ✓ |
| AI_AGENTS/cto-build-framework | ✓ |
| AI_AGENTS/tax-god-copilot | ✓ |
| AI_AGENTS/agent_swarm_runner | ✓ |
| alchemmical-cabaret-33 | ✓ |
| dome-console | ✓ |

FILE_TREE.md auto-generated at every project root via `generate-file-tree.py`.

---

## Agent Skill Implementations (agents/skills/)

| Skill | File | Description |
|-------|------|-------------|
| `algorithms` | `agents/skills/algorithms.py` | Algorithm skill implementation |
| `cognitive` | `agents/skills/cognitive.py` | Cognitive skill implementation |
| `compute` | `agents/skills/compute.py` | Compute skill implementation |
| `fractals` | `agents/skills/fractals.py` | Fractals skill implementation |
| `frequency` | `agents/skills/frequency.py` | Frequency skill implementation |
| `math` | `agents/skills/math.py` | Math skill implementation |
| `sacred_geometry` | `agents/skills/sacred_geometry.py` | Sacred geometry skill implementation |
