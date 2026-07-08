# DSH Skill Registry

Canonical source: `kb/skills/*.md` (plus nested `kb/skills/<name>/SKILL.md` packages where present)  
Last updated: 2026-05-23 (sovereign gate doctrine, pnpm workspace, vault scripts)

Generated mirrors (run `python3 scripts/sync-dome-skills.py` after skill edits — **updates Codex trees only; does not overwrite this file**; use `python3 scripts/sync-dome-skills.py --check-only` to cross-validate this table vs `kb/skills/` without writing):
- `agents/Codex/skills/dsh/`
- `home/.codex/skills/dsh/`
- `home/.unified-ai/skills/dsh/`



---

## Canonical index map (read this once — then drill)

| Index | Path | Role |
|-------|------|------|
| **DSH root** | `INDEX.md` | Full repo directory reference, scripts, `.fractalmap`, Trinity mirror table |
| **Master architecture** | `docs/DSH-ARCHITECTURE.md` | Full stack: compute layers, memory, Trinity mirror, Appendix A |
| **This file** | `kb/skills/INDEX.md` | Skill registry, sims, LAVA, Kiro, Trinity production skills, hooks, AGENTS coverage |
| **KB hub** | `kb/README.md` | KB layout, LAVA pointers, ingest |
| **Fractalmap skill** | `skills/fractalmap/SKILL.md` | Tiered maps; generator `scripts/fractalmap-generate.sh`; output `.fractalmap/` (`tree-full.txt` gitignored) |
| **Architecture audit** | `docs/architecture-audit-2026-05-12/INDEX.md` | 2026-05-12 CTO-style audit bundle |
| **TU-AI docs** | `kb/trinity-unified-ai/docs/INDEX.md` | KB API docs index (port 3333) |
| **TU-AI engines** | `kb/trinity-unified-ai/engines/INDEX.md` | Engine catalog (bitboard, Mandelbulb, mesh, …) |
| **TU-AI knowledge-base** | `kb/trinity-unified-ai/knowledge-base/INDEX.md` | Curated KB mirror slice + inventory docs |
| **Codex mirror** | `agents/Codex/skills/INDEX.md`, `agents/Codex/skills/dsh/INDEX.md` | Short mirror; **source of truth = this file** |
| **Cross-check policy** | `PROTOCOLS.md` § Cross-Check Protocol | Gates that require `INDEX.md` + `kb/skills/INDEX.md` in sync |
| **Sovereign Gate Doctrine** | `docs/SOVEREIGN_GATE_DOCTRINE.md` | Mandatory pre-push/deploy gate (8 phases) + full audit (834 lines) |
| **Public export (DSH) gaps** | `docs/PUBLIC_PROD_HARDENING.md` | P0 history purge, P1 identity/path audit, P2 governance — vs DSH tip reconciliation § |
| **Spore / mesh (Phase 2)** | `MANUAL.md` § Trinity § Phase 2, `spore.sh` | `pre-spore-verify.py` gate; lock/unlock; baseline `~/.trinity-spore/mycelium-mesh.sh` vs prod `scripts/mycelium-signal.sh` |
| **Agent context** | `AGENTS.md`, `MANUAL.md`, `CLAUDE.md` | Operator + agent runbooks (cross-check §16 in MANUAL) |

---

## Canonical Skill Docs (kb/skills/)

| Skill | Path | Description |
|-------|------|-------------|
| `algorithms` | `kb/skills/algorithms.md` | Algorithm design and analysis |
| `cognitive` | `kb/skills/cognitive.md` | Cognitive architecture patterns |
| `compute` | `kb/skills/compute.md` | Compute orchestration, QuantumDome, sim engines |
| `frequency` | `kb/skills/frequency.md` | Frequency analysis, signal processing |
| `math` | `kb/skills/math.md` | Mathematical foundations |
| `skill-creator` | `kb/skills/skill-creator.md` | Meta-skill for creating new skills |
| `greenergyfl-finance` | `kb/skills/greenergyfl-finance/` | GreenEnergyFL finance skill (SKILL.md + evals/) |
| `visual-storytelling` | `kb/skills/visual-storytelling.md` | Visual-storytelling skill chain (architect + sexyverse-designer + ui-ux-pro-max), 8 motion-stack CSVs, hard rails, 5-act narrative model — added 2026-05-13 |

---

## Simulation Files (compute/)

| File | Description |
|------|-------------|
| `compute/sim_3x3x3.py` | 3×3×3 lattice — E8/Mandelbulb + NumPy Kuramoto using **K_OPTIMAL** (Loihi/LAVA calibration); no `lava` import in root `.venv` |
| `compute/quantum_dome/` | QuantumDome framework (core, memory, pool, profiler, scheduler) |

---

## LAVA/Loihi 2 — Neuromorphic Compute Skills

Neuromorphic computing via Intel LAVA framework, targeting Loihi 2 hardware.

| Component | Location | Purpose |
|-----------|----------|---------|
| NumPy Kuramoto lattice | `compute/sim_3x3x3.py` | Same coupling constant as Loihi line; fast local sanity sim |
| LAVA bootstrap / probe | Trinity `scripts/lava-bootstrap.sh`, `scripts/lava-probe.py` (in mirror) | Sidecar venv + hardware probe |
| Architecture docs | `docs/DSH-ARCHITECTURE.md` §3 + Appendix A | DSH + Trinity mirror map |

Session reference: `logs/session-2026-05-09-mandelbulb-optical-meninges-loihi.md`

---

## Kiro Agent Skills (home/.kiro/skills/)

| Skill | Path | Description |
|-------|------|-------------|
| `cto-build-framework-validator` | `home/.kiro/skills/cto-build-framework-validator/` | CTO Build Framework governance validation |
| `ui-ux-pro-max` | `home/.kiro/skills/ui-ux-pro-max/` | AI design intelligence — 85 styles, 161 palettes, 57 fonts, 99 UX rules, **19 stacks** incl. visual-storytelling (framer-motion / gsap / r3f / spline / video / web-audio / typography-motion). BM25 search. |
| `sexyverse-designer` | `home/.kiro/skills/sexyverse-designer/` | Frontend implementation agent (v1.2) — Framer Motion + GSAP + R3F + Spline + Web Audio + kinetic typography. Wired to all motion stacks. Added 2026-05-13. |
| `visual-storytelling-architect` | `home/.kiro/skills/visual-storytelling-architect/` | Narrative-arc planner (v1.0) for scroll-driven web — 5-act model, 3 rules of motion intent, stack-per-beat selection, a11y floor, pre-ship checklist. Sits *above* the implementation skills. Added 2026-05-13. |


---


Top-tier (≥80 audit score):

| Skill | Score | Description |
|-------|------:|-------------|
| `sexyverse-designer` | 90 | (See kiro entry above) |
| `end-to-end-wiring` | 89 | Service integration + connectivity verification |
| `ui-ux-pro-max` | 85 | (See kiro entry above) |
| `visual-storytelling-architect` | 80 | (See kiro entry above) |
| `nextlevelbuilder-ecosystem` | 80 | GoClaw gateway (66 MCP tools) + AgentBrain KB + SkillX marketplace |

Plus `claude-code-builtins/` — Trinity wrapper that documents the 10 Claude Code CLI runtime built-ins (update-config, simplify, schedule, loop, claude-api, keybindings-help, fewer-permission-prompts, init, review, security-review) so cross-platform agents can delegate via `claude --headless`.

Full inventory: see MASTER_INDEX.md.

---


| Script | Purpose |
|--------|---------|
| `skill-quality-audit.py` | Score every canonical SKILL.md 0-100 (PyYAML-backed, handles multi-line `description: >` + `triggers:` lists). Output to `SKILL_QUALITY_AUDIT.md`. |
| `skill-batch-patch.py` | Idempotent: adds missing `version` / `status` / `updated` frontmatter fields. |
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
| DSH (root) | ✓ |
| trinity-unified-ai | ✓ |
| mycelium-e8 | ✓ |
| AI_AGENTS/Sacred-Geometry-Space | ✓ |
| AI_AGENTS/cto-build-framework | ✓ |
| AI_AGENTS/tax-god-copilot | ✓ |
| AI_AGENTS/agent_swarm_runner | ✓ |
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

---

## Workstation Utility Skills (agents/skills/ — added 2026-05-24)

File generation, automation, security, and research skills that turn DSH into a full sovereign workstation.

### File Generation

| Skill | Path | Description |
|-------|------|-------------|
| `docx` | `agents/skills/docx/SKILL.md` | Create/edit Word documents via python-docx |
| `pdf` | `agents/skills/pdf/SKILL.md` | Create/read PDFs via reportlab + pdfplumber |
| `pptx` | `agents/skills/pptx/SKILL.md` | Create/edit PowerPoint presentations |
| `xlsx` | `agents/skills/xlsx/SKILL.md` | Create/edit Excel spreadsheets via openpyxl |
| `pandoc` | `agents/skills/pandoc/SKILL.md` | Universal document conversion (md↔docx↔html↔pdf↔epub↔pptx) |
| `latex-tectonic` | `agents/skills/latex-tectonic/SKILL.md` | Compile LaTeX/TeX with Tectonic |
| `imagegen` | `agents/skills/imagegen/SKILL.md` | AI image generation via OpenAI API |
| `speech` | `agents/skills/speech/SKILL.md` | Text-to-speech via OpenAI Audio API |
| `transcribe` | `agents/skills/transcribe/SKILL.md` | Audio-to-text transcription with diarization |
| `jupyter-notebook` | `agents/skills/jupyter-notebook/SKILL.md` | Scaffold/edit Jupyter notebooks (.ipynb) |

### Automation & DevOps

| Skill | Path | Description |
|-------|------|-------------|
| `playwright` | `agents/skills/playwright/SKILL.md` | Browser automation (navigation, forms, screenshots, data extraction) |
| `screenshot` | `agents/skills/screenshot/SKILL.md` | OS-level desktop/window screen capture |
| `github` | `agents/skills/github/SKILL.md` | GitHub repo management (PRs, issues, Actions, releases) |
| `ci-cd-architect` | `agents/skills/ci-cd-architect/SKILL.md` | CI/CD pipeline design, GitHub Actions, deployment automation |

### Security

| Skill | Path | Description |
|-------|------|-------------|
| `security-threat-model` | `agents/skills/security-threat-model/SKILL.md` | Repository-grounded threat modeling |
| `security-best-practices` | `agents/skills/security-best-practices/SKILL.md` | Language-specific secure coding review |

### Research & Meta

| Skill | Path | Description |
|-------|------|-------------|
| `deep-research` | `agents/skills/deep-research/SKILL.md` | Deep multi-source research synthesis |
| `skill-generator-engine` | `agents/skills/skill-generator-engine/SKILL.md` | Autonomous skill creation engine |

**Dependency installer:** `scripts/install-format-deps.sh` (cross-platform macOS/Linux)

---

## Developer Productivity Skills (agents/skills/ — added 2026-05-25)

Full-stack development, infrastructure, quality engineering, and monetization skills.

### Frameworks & Full-Stack

| Skill | Path | Description |
|-------|------|-------------|
| `nextjs` | `agents/skills/nextjs/SKILL.md` | Next.js App Router — SSR, Server Components, routing, deployment |
| `fastapi` | `agents/skills/fastapi/SKILL.md` | Python API development with Pydantic models |
| `ai-sdk` | `agents/skills/ai-sdk/SKILL.md` | Vercel AI SDK — chat, streaming, tool calling, any LLM |
| `react-best-practices` | `agents/skills/react-best-practices/SKILL.md` | React/Next.js performance optimization |
| `shadcn` | `agents/skills/shadcn/SKILL.md` | Component library — CLI, theming, Tailwind CSS |

### Data & Infrastructure

| Skill | Path | Description |
|-------|------|-------------|
| `database-optimizer` | `agents/skills/database-optimizer/SKILL.md` | PostgreSQL + Drizzle ORM query tuning, indexing |
| `neon-postgres` | `agents/skills/neon-postgres/SKILL.md` | Serverless Postgres (Neon) |
| `migration-specialist` | `agents/skills/migration-specialist/SKILL.md` | Schema evolution, zero-downtime deploys |
| `cloudflare-deploy` | `agents/skills/cloudflare-deploy/SKILL.md` | Deploy Workers, Pages, KV, D1, R2 |
| `api-gateway-designer` | `agents/skills/api-gateway-designer/SKILL.md` | REST/GraphQL/WebSocket endpoint design |

### Engineering Quality

| Skill | Path | Description |
|-------|------|-------------|
| `testing-strategist` | `agents/skills/testing-strategist/SKILL.md` | Unit/integration/E2E test strategy |
| `refactoring-engineer` | `agents/skills/refactoring-engineer/SKILL.md` | Technical debt reduction, modernization |
| `performance-tuner` | `agents/skills/performance-tuner/SKILL.md` | Profiling, caching, bundle optimization |
| `dependency-manager` | `agents/skills/dependency-manager/SKILL.md` | Vulnerability scanning, license compliance |
| `documentation-generator` | `agents/skills/documentation-generator/SKILL.md` | Auto-generate API docs, READMEs |

### Monetization

| Skill | Path | Description |
|-------|------|-------------|
| `stripe-best-practices` | `agents/skills/stripe-best-practices/SKILL.md` | Payments, subscriptions, Connect platforms |
