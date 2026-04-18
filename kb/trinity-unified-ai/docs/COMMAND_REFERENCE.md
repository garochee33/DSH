# Trinity Unified AI — Complete Command Reference

> **Verified:** 2026-04-07 against live filesystem
> **Repo:** `~/trinity-unified-ai` (github.com/garochee33/trinity-unified-ai)
> **Total:** 34 runnable commands + 3 launchd services + 1 shell alias
> **NOTE:** This repo has NO `bin/` directory. The `trinity33` CLI lives only in `~/projects/trinity-consortium/bin/`.

---

## Quick Reference Table

| # | Command | Location | What It Does |
|---|---------|----------|--------------|
| 1 | `bash spore.sh` | root | Full machine bootstrap + E8 terraform |
| 2 | `bash sync/boot.sh` | sync/ | Health check + start API :3333 + CC :4444 |
| 3 | `./sync.sh` | sync/ | Push standards to Claude/Cursor/Codex/etc |
| 4 | `./full-sync.sh` | sync/ | 7-step bidirectional sync pipeline |
| 5 | `./pull-from-live.sh` | sync/ | Read-only mirror from consortium/womb |
| 6 | `./gems-harvest.sh` | sync/ | Scout swarm asset harvest |
| 7 | `./hub-remediation.sh` | sync/ | 3 AI audit agents (AMMA/CTO/ORACLE) |
| 8 | `./install.sh` | sync/ | Cross-AI standards installer |
| 9 | `./install-all.sh` | sync/ | Master v1+v2 installer |
| 10-23 | validation scripts | sync/scripts/ | 14 validation/automation scripts |
| 24-30 | `npm run *` | api/ | KB API server + ingest + seed |
| 31-33 | `npm run *` | command-center/ | Next.js dashboard |
| 34 | `npm test` | root | (stub) |

---

## 1. BOOTSTRAP

### spore.sh — E8 Mycelium Membrane Terraformer

```
File:       ~/trinity-unified-ai/spore.sh
Lines:      472
Quality:    ***** (production-grade, idempotent, adaptive to machine tier)
```

**Purpose:** Drop-and-go machine bootstrapper. Detects environment, installs everything, configures E8 lattice, starts all services.

**How to run:**
```bash
bash ~/trinity-unified-ai/spore.sh
```

**What it does (10 phases):**
1. Detect OS/arch/cores/RAM/GPU, assign machine tier (seed/scout/guardian/sovereign)
2. Clone/update trinity-unified-ai repo from GitHub
3. Install Node.js (via brew/fnm), pnpm, Ollama
4. Pull LLM models based on tier (qwen2.5-coder:14b, qwen3.5:9b, nomic-embed-text)
5. Generate machine-specific E8 lattice config (24-240 roots scaled by RAM/cores x phi)
6. Install API dependencies (`cd api && npm install`)
7. Create `api/.env` from template
8. Start KB API on :3333 (background)
9. Ingest KB docs to Supabase pgvector
10. Run full-sync.sh, optionally clone + start the-womb at :3000

**Prerequisites:** Authorized local machine, Git, internet access, 8+ GB RAM recommended

**Modifies:**
- Requires local authorization marker `~/.trinity-sync-authorized`
- Creates/updates `~/trinity-unified-ai/` (full repo)
- Creates `engines/machine-profile.json`
- Creates `api/.env`
- Installs Node.js, pnpm, Ollama if missing
- Pulls Ollama models (1-20GB depending on tier)
- Starts KB API process (:3333)
- Installs launchd auto-sync (macOS, 30-min interval)

**Keywords:** fresh machine, new setup, bootstrap, terraform, first install, onboarding

**Safe to re-run:** Yes (idempotent)

---

## 2. SYNC SCRIPTS (`~/trinity-unified-ai/sync/`)

### boot.sh — Full Merkaba Boot Sequence + Service Startup

```
File:       ~/trinity-unified-ai/sync/boot.sh
Lines:      221
Quality:    ****- (solid health checks, nice UX, missing graceful shutdown)
```

**Purpose:** System health check + start KB API and Command Center.

**How to run:**
```bash
bash ~/trinity-unified-ai/sync/boot.sh
```

**What it does (10 phases):**
1. Fire Merkaba 3D visualizer (6s, cosmetic)
2. System check: Node, Python, Julia, Rust, Bun, Deno
3. Services: PostgreSQL, Redis, Neo4j, Ollama, IPFS
4. Ollama models inventory
5. E8 compute: verify 9 engine files exist
6. God Mode: verify protocols.ts (10 engines), 3 API route files
7. Consortium wiring: trinity-hub proxy, MerkabaEngineTab, CC tab
8. Supabase KB: doc count + agent count
9. **Start services:** kill existing, start KB API :3333 + Command Center :4444
10. Engine health: curl 4 status endpoints

**Prerequisites:** PostgreSQL, Ollama running; consortium at `~/projects/trinity-consortium`

**Modifies:** Kills existing API/CC processes, starts new ones. Logs to `/tmp/trinity-api.log`, `/tmp/trinity-ui.log`

**Keywords:** boot, startup, health check, morning startup, "are services running?"

---

### sync.sh — Push Standards to All AI Tools

```
File:       ~/trinity-unified-ai/sync/sync.sh
Lines:      206
Quality:    ***** (dry-run, targeted sync, logging, rsync --delete for skills)
```

**Purpose:** One-way broadcast FROM hub TO all AI tool configs.

**How to run:**
```bash
cd ~/trinity-unified-ai/sync
./sync.sh                          # sync everything to all tools
./sync.sh --target=claude          # sync only Claude configs
./sync.sh --dry-run                # preview what would change
./sync.sh --only=skills            # sync only skills/ folder
./sync.sh --dry-run --target=mcp   # dry-run MCP sync only
```

**Targets:** `claude`, `codex`, `cursor`, `openclaw`, `kiro`, `projects`, `mcp`, `all`
**Folders:** `skills`, `agents`, `standards`, `tools`, `all`

**What it syncs:**
- Claude -> `~/.claude/projects/` (standards, agents, mcp.json, skills/)
- Codex -> `~/.codex/` (agents, tools, skills)
- Cursor -> `~/.cursor/` (.cursorrules, mcp.json, skills/)
- OpenClaw -> `~/.openclaw/` (tools, skills/)
- Kiro -> each `~/projects/*/` (AGENTS.md)
- Projects -> each `~/projects/*/` (AGENTS.md + TRINITY_STANDARDS.md)
- MCP -> all tools' mcp.json

**Modifies:** Config files in tool directories. Logs to `sync/logs/sync-YYYY-MM-DD.log`

**Keywords:** push standards, update AI tools, sync configs, after editing standards

**Automated:** Every 6 hours via `com.trinity.sync.plist`

---

### full-sync.sh — Bidirectional 7-Step Sync Pipeline

```
File:       ~/trinity-unified-ai/sync/full-sync.sh
Lines:      254
Quality:    ***** (idempotent, dry-run, partial modes, error tracking, logged)
```

**Purpose:** Master sync pipeline. Bidirectional across 3 repos.

**How to run:**
```bash
cd ~/trinity-unified-ai/sync
./full-sync.sh                  # full 7-step cycle
./full-sync.sh --dry-run        # preview only
./full-sync.sh --pull-only      # steps 1-2 only (safe read)
./full-sync.sh --ingest-only    # steps 4-6 only (re-ingest KB)
```

**7 steps:**
1. **Git pull** all 3 repos (hub, consortium, womb)
2. **Vendor mirror** — rsync consortium + womb docs to `knowledge-base/vendor/`
3. **Push standards** — copy AGENTS.md + REGISTRY.md back to consortium + womb
4. **KB ingest** -> Supabase pgvector (embed all .md via Ollama nomic-embed-text)
5. **E8 Fractal Memory Sync** -> consortium's local Postgres (contentHash -> embedding -> E8 root -> bitboard -> HRR -> Merkle DAG)
6. **Agent memory + knowledge graph** refresh
7. **Commit + push** all 3 repos (auto-commit)

**Prerequisites:** All 3 repos cloned, Supabase configured, Ollama running with nomic-embed-text

**Modifies:** All 3 repos (git), Supabase tables, consortium Postgres. Logs to `sync/logs/full-sync-YYYY-MM-DD.log`

**Keywords:** full sync, KB update, E8 sync, ingest knowledge, update embeddings

**Automated:** Every 30 minutes via `com.trinity.full-sync.plist`

---

### pull-from-live.sh — Read-Only Mirror from Production Repos

```
File:       ~/trinity-unified-ai/sync/pull-from-live.sh
Lines:      210
Quality:    ***** (dry-run by default, conflict detection, source filtering)
```

**Purpose:** Safe read-only rsync from live repos into hub. Never touches live repos.

**How to run:**
```bash
cd ~/trinity-unified-ai/sync
./pull-from-live.sh                          # dry-run (DEFAULT)
./pull-from-live.sh --apply                  # actually copy files
./pull-from-live.sh --apply --source=consortium  # consortium only
./pull-from-live.sh --source=womb            # dry-run womb only
```

**What it copies:**
- Consortium `server/ai/` -> hub `engines/ai-filesystem/`
- Consortium `shared/schema.ts` -> hub `database/trinity-schema/`
- Womb `packages/ai-core/src/` -> hub `engines/womb-ai-core/`
- Womb `server/ai/` -> hub `engines/womb-server-ai/`
- Womb `shared/schema.ts` -> hub `database/womb-schema/`

**Modifies (only with --apply):** Hub `engines/` and `database/` dirs. No git ops.

**Keywords:** pull from prod, mirror code, after major consortium changes

---

### gems-harvest.sh — Triangle 1 Scout Swarm

```
File:       ~/trinity-unified-ai/sync/gems-harvest.sh
Lines:      224
Quality:    ****- (skip-if-exists, report generation, no --apply guard)
```

**Purpose:** Extract high-value AI assets from live repos. Three scouts.

**How to run:**
```bash
cd ~/trinity-unified-ai/sync
./gems-harvest.sh              # live harvest
./gems-harvest.sh --dry-run    # preview only
```

**Scouts:**
- **SCOUT-A (Consortium):** agent-router, bridges, modes, skills (god-mode, trinity-repo-navigator, use-railway), KB docs, agent prompts
- **SCOUT-B (Womb):** trinity-agent-system (e8-bitboard, e8-lattice, sacred-geometry), shaders, unified-ai-audit skill
- **SCOUT-C (Report):** Generates `memory/GEMS_HARVEST_REPORT.md`

**Modifies:** Creates dirs in hub `engines/`, `skills/`, `knowledge-base/`. Skips existing files.

**Keywords:** harvest assets, populate hub, after major new features in consortium/womb

---

### hub-remediation.sh — Triangle 2 (AMMA + CTO-AUDITOR + ORACLE)

```
File:       ~/trinity-unified-ai/sync/hub-remediation.sh
Lines:      260
Quality:    ****- (3 AI agents, graceful Ollama fallback to static analysis)
```

**Purpose:** Run 3 AI audit agents against the hub. Produces gap analysis + health scores.

**How to run:**
```bash
cd ~/trinity-unified-ai/sync
./hub-remediation.sh               # full AI + static analysis
./hub-remediation.sh --dry-run     # static analysis only (no Ollama)
```

**Agents:**
- **AMMA** (qwen2.5-coder:14b): Code health, broken refs, orphaned files -> `memory/AMMA_AUDIT_REPORT.md`
- **CTO-AUDITOR** (qwen2.5-coder:14b): API routes, tables, MCP tools, cross-refs -> `memory/CTO_WIRING_REPORT.md`
- **ORACLE** (qwen3.5:9b): KB docs, agents, engines, skills inventory -> `memory/ORACLE_SCAN_REPORT.md`

**Prerequisites:** Ollama running with qwen2.5-coder:14b + qwen3.5:9b (degrades gracefully)

**Modifies:** 3 report files in `memory/` (analysis only, no code changes)

**Keywords:** hub audit, gap analysis, health check, "what's broken?"

---

### install.sh — Cross-AI Standards Installer (v1 Base)

```
File:       ~/trinity-unified-ai/sync/install.sh
Lines:      343
Quality:    ***-- (interactive prompts, overwrites CLAUDE.md without diff)
```

**Purpose:** Install Trinity AI Standards configs to Kimi, Claude, Cursor, VS Code/Copilot.

**How to run:**
```bash
cd ~/trinity-unified-ai/sync
./install.sh                     # interactive (prompts for each tool)
./install.sh --all               # install all without prompting
./install.sh --claude --cursor   # specific tools only
./install.sh --help              # show options
```

**Flags:** `--all`, `--kimi`, `--claude`, `--cursor`, `--vscode`, `--help`

**WARNING:** Overwrites existing CLAUDE.md, .cursorrules, VS Code settings in all project dirs with template versions. Use `sync.sh` for incremental updates instead.

**Modifies:** `~/.claude/`, `~/.cursor/`, `~/.vscode/`, `~/projects/*/`, `~/TRINITY_STANDARDS.md`

**Keywords:** initial setup, install standards, configure AI tools, onboarding

---

### install-all.sh — Master Installer (v1 + v2 Enhanced)

```
File:       ~/trinity-unified-ai/sync/install-all.sh
Lines:      179
Quality:    ***-- (orchestrator, v2 may not exist, appends to .zshrc)
```

**Purpose:** Run both v1 and v2 installers, create global config.

**How to run:**
```bash
cd ~/trinity-unified-ai/sync
./install-all.sh
```

**What it does:**
1. Runs `install.sh --all` (v1)
2. Runs `v2/install-v2.sh` (v2, warns if missing)
3. Creates `~/.trinity/config.json`
4. Adds `~/.local/bin` to PATH in `~/.zshrc`

**Keywords:** complete setup, full install, v1+v2

---

## 3. VALIDATION SCRIPTS (`~/trinity-unified-ai/sync/scripts/`)

### install-cron.sh — LaunchD Agent Manager

```
File:       ~/trinity-unified-ai/sync/scripts/install-cron.sh
Lines:      155
Quality:    ****- (install/uninstall/status, proper launchctl bootstrap)
```

**How to run:**
```bash
cd ~/trinity-unified-ai/sync/scripts
./install-cron.sh              # install all launchd agents
./install-cron.sh --uninstall  # unload + remove
./install-cron.sh --status     # check loaded status + recent logs
```

**Manages 3 launchd agents:**
- `com.trinity.sync.plist` — `sync.sh` every 6 hours
- `com.trinity.full-sync.plist` — `full-sync.sh` every 30 minutes
- `com.trinity.ref-sync.plist` — `daily-ref-sync.sh` at 3:00 AM

**Prerequisites:** macOS only (launchctl)

**Keywords:** schedule, automate, cron, mycelium-mesh, launchd

---

### run-ref-generation.sh — Master .ref.md Generator

```
File:       ~/trinity-unified-ai/sync/scripts/run-ref-generation.sh
Lines:      238
Quality:    ****- (processes 11 source dirs, generates manifest.json)
```

**How to run:**
```bash
cd ~/trinity-unified-ai/sync/scripts
./run-ref-generation.sh
```

**Processes 11 consortium directories, generates .ref.md summaries:**
1. `server/ai/engines/` -> `engines/ref/engines/`
2. `server/ai/swarm/` -> `engines/ref/swarm/`
3. `server/ai/consensus/` -> `engines/ref/consensus/`
4. `server/ai/crew/` -> `engines/ref/crew/`
5. `server/ai/bitboard/` -> `engines/ref/bitboard/`
6. `server/ai/continuous-improvement/` -> `engines/ref/continuous-improvement/`
7. `server/ai/sentinel/` -> `engines/ref/sentinel/`
8. `server/ai/monica/` -> `engines/ref/monica/`
9. `server/ai/*-tools.ts` -> `engines/ref/tools/`
10. `server/ai/*.ts` -> `engines/ref/core/`
11. `shared/schema.ts` -> `engines/ref/database/`

**Modifies:** Creates 288+ .ref.md files + `sync/manifest.json`

**Keywords:** generate docs, index codebase, reference summaries

---

### daily-ref-sync.sh — Overnight .ref.md Regeneration

```
File:       ~/trinity-unified-ai/sync/scripts/daily-ref-sync.sh
Lines:      129
Quality:    ****- (hash comparison, auto-commit, dry-run support)
```

**How to run:**
```bash
./daily-ref-sync.sh            # live run
./daily-ref-sync.sh --dry-run  # preview
```

**Automated:** Daily at 3:00 AM via launchd

**Keywords:** overnight sync, scheduled ref update

---

### generate-ref-summaries.sh — Single-Dir .ref.md Generator

```
File:       ~/trinity-unified-ai/sync/scripts/generate-ref-summaries.sh
Lines:      108
Quality:    ***-- (regex-based TS extraction, fragile with complex files)
```

**How to run:**
```bash
./generate-ref-summaries.sh <source_dir> <dest_dir> <type> [manifest_path]
```

**Keywords:** generate reference, extract metadata, TypeScript introspection

---

### Remaining Validation Scripts

| Script | Lines | Quality | How to Run | What It Does |
|--------|-------|---------|-----------|--------------|
| `full-validation.sh` | 85 | ****- | `bash full-validation.sh` | Runs ALL: static + unit + integration + e2e + security |
| `static-check.sh` | 90 | ***-- | `bash static-check.sh` | TypeScript typecheck + ESLint |
| `unit-test.sh` | 58 | ***-- | `bash unit-test.sh` | Run vitest/jest if configured |
| `integration-test.sh` | 116 | ***-- | `bash integration-test.sh` | API integration tests (needs services) |
| `e2e-validate.sh` | 119 | ***-- | `bash e2e-validate.sh` | End-to-end validation |
| `security-audit.sh` | 95 | ***-- | `bash security-audit.sh` | SAST scan, secret detection |
| `performance-report.sh` | 45 | **--- | `bash performance-report.sh` | Build time, bundle size metrics |
| `migration-helper.sh` | 54 | **--- | `bash migration-helper.sh` | DB migration helpers |
| `pre-commit.sh` | 41 | ***-- | `bash pre-commit.sh` | Runs static-check + unit-test |
| `add-frontmatter.sh` | 40 | ***-- | `bash add-frontmatter.sh <file>` | Add YAML frontmatter to .md |

---

## 4. LAUNCHD SCHEDULED SERVICES

| Plist | Script | Frequency | Logs |
|-------|--------|-----------|------|
| `com.trinity.sync.plist` | `sync.sh` | Every 6 hours | `sync/logs/launchd-sync.log` |
| `com.trinity.full-sync.plist` | `full-sync.sh` | Every 30 minutes | `sync/logs/launchd-full-sync.log` |
| `com.trinity.ref-sync.plist` | `daily-ref-sync.sh` | Daily at 3:00 AM | `sync/logs/launchd-ref-sync.log` |

**Install:** `bash sync/scripts/install-cron.sh`
**Uninstall:** `bash sync/scripts/install-cron.sh --uninstall`
**Status:** `bash sync/scripts/install-cron.sh --status`

---

## 5. KB API SERVER (`~/trinity-unified-ai/api/`)

API Source: 2,570 LOC (12 core files) + 2,376 LOC (17 route files) = **4,946 LOC**

### npm run dev — Start KB API Dev Server

```
File:       ~/trinity-unified-ai/api/src/server.ts (237 LOC)
Command:    cd ~/trinity-unified-ai/api && npm run dev
Actual:     NODE_PATH=./node_modules tsx watch src/server.ts
Port:       3333
Quality:    ****- (hot reload, 17 route files, protocols wired)
```

**Routes served (17 files, ~46 endpoints):**

| Route | File | LOC | Description |
|-------|------|-----|-------------|
| `/api/search` | search.ts | 22 | Semantic search |
| `/api/chat` | chat.ts | 478 | AI chat with KB context |
| `/api/agents` | agents.ts | 140 | Agent registry CRUD |
| `/api/agent` | agent.ts | 26 | Single agent ops |
| `/api/orchestrate` | orchestrate.ts | 29 | Basic orchestration |
| `/api/orchestration` | orchestration.ts | 159 | Full orchestration engine |
| `/api/dispatch` | dispatch.ts | 38 | Task dispatch queue |
| `/api/session` | session.ts | 21 | Session management |
| `/api/e8-compute` | e8-compute.ts | 190 | E8 lattice compute |
| `/api/holographic` | holographic.ts | 246 | Holographic bitboard ops |
| `/api/stigmergic` | stigmergic.ts | 225 | Pheromone grid + CRDT |
| `/api/protocols` | protocols.ts | 48 | God Mode protocol endpoints |
| `/api/engine` | engine.ts | 127 | Engine health + status |
| `/api/settings` | settings.ts | 287 | Runtime settings CRUD |
| `/api/stats` | stats.ts | 120 | Telemetry + metrics |
| `/api/telemetry` | telemetry.ts | 50 | System telemetry |
| `/api/tax-god` | tax-god.ts | 170 | Tax God domain |
| `/health` | server.ts | — | Health check |

**Core modules:**

| File | LOC | Description |
|------|-----|-------------|
| `protocols.ts` | 668 | 10 real God Mode engines |
| `agent-kernel.ts` | 483 | Real agent execution (MAX_ITERATIONS=50, $100/day limit) |
| `task-dispatch.ts` | 303 | Task queue + dispatch |
| `server.ts` | 237 | Express app + routes |
| `real-orchestrator.ts` | 210 | Production orchestrator |
| `orchestration-engine.ts` | 148 | Orchestration with protocols |
| `ingest.ts` | 156 | KB -> Supabase pgvector |
| `e8-memory-bridge.ts` | 144 | E8 lattice memory bridge |
| `seed-agents.ts` | 70 | Agent seeder |
| `ensure-tables.ts` | 59 | Auto-create tables |
| `clients.ts` | 49 | Supabase + Ollama clients |
| `search.ts` | 43 | Semantic search |

**Required env vars:** `PORT=3333`, `OLLAMA_BASE_URL`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
**Optional:** `OPENAI_API_KEY` (fallback embeddings), `DATABASE_URL` (E8 memory bridge)

---

### npm run ingest — Embed KB Docs to Supabase

```
Command:    cd ~/trinity-unified-ai/api && npm run ingest
Dry-run:    cd ~/trinity-unified-ai/api && npm run ingest:dry
Quality:    ****- (idempotent via content hash, Ollama-first embeddings)
```

Scans `knowledge-base/**/*.md`, embeds via Ollama nomic-embed-text (768D), upserts to Supabase `knowledge_docs` table.

---

### npm run seed-agents — Populate Agent Registry

```
Command:    cd ~/trinity-unified-ai/api && npm run seed-agents
Quality:    ***-- (simple upsert from per-agent .md files)
```

Reads `agents/per-agent/*.md` (30 files), parses frontmatter, upserts to Supabase `agents` table.

---

### npm run setup — Full KB Setup

```
Command:    cd ~/trinity-unified-ai/api && npm run setup
Actual:     npm run seed-agents && npm run ingest
```

Convenience wrapper: seeds agents then ingests KB.

---

### npm run build / npm start — Production

```
Build:      cd ~/trinity-unified-ai/api && npm run build   (tsc -> dist/)
Start:      cd ~/trinity-unified-ai/api && npm start        (node dist/api/src/server.js)
```

---

## 6. COMMAND CENTER UI (`~/trinity-unified-ai/command-center/`)

```
Stack:      Next.js 15.5.14, React 18, TailwindCSS
Port:       4444 (localhost only)
Pages:      11
```

### npm run dev — Start Command Center

```
Command:    cd ~/trinity-unified-ai/command-center && npm run dev
Actual:     next dev -p 4444 -H 127.0.0.1
```

**Pages:**
- `/` — Dashboard home
- `/agents` — Agent registry view
- `/chat` — AI chat interface
- `/health` — System health dashboard
- `/kb` — Knowledge base browser
- `/logs` — Execution logs
- `/orchestrate` — Orchestration control
- `/protocols` — God Mode protocols
- `/settings` — Settings management
- `/swarm` — Swarm visualization
- `/sync` — Sync status

### npm run build / npm start — Production

```
Build:      cd ~/trinity-unified-ai/command-center && npm run build
Start:      cd ~/trinity-unified-ai/command-center && npm start   (next start -p 4444)
```

---

## 7. ROOT PACKAGE.JSON

```
Command:    cd ~/trinity-unified-ai && npm test
Actual:     echo "Error: no test specified" && exit 1
```

Stub only. No build/dev scripts at root level.

---

## 8. SHELL ALIAS

```bash
cd-unified    # -> cd ~/trinity-unified-ai
```

Defined in `~/.zshrc`.

---

## Recommended Execution Order

### First-Time Setup
```bash
bash ~/trinity-unified-ai/spore.sh                    # One-time bootstrap
bash ~/trinity-unified-ai/sync/scripts/install-cron.sh # Schedule automation
```

### Daily Startup
```bash
bash ~/trinity-unified-ai/sync/boot.sh                # Health check + start services
```

### Manual Sync
```bash
cd ~/trinity-unified-ai/sync
./full-sync.sh --pull-only     # Safe: pull only, no push
./full-sync.sh                 # Full bidirectional sync
```

### After Major Changes
```bash
cd ~/trinity-unified-ai/sync
./pull-from-live.sh --apply    # Mirror latest from production
./gems-harvest.sh              # Extract new assets
./hub-remediation.sh           # Audit hub health
./sync.sh                      # Push updated standards to AI tools
```

---

## Quality Scoring Legend

| Rating | Meaning |
|--------|---------|
| `*****` | Production-grade: error handling, idempotent, dry-run, logging |
| `****-` | Solid: good structure, minor gaps |
| `***--` | Functional: works but fragile |
| `**---` | Minimal: placeholder-level, needs hardening |
| `*----` | Stub: exists but not production-ready |
