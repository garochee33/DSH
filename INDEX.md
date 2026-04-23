# DOME-HUB Index

Complete reference of all files, directories, and their purpose.
Last updated: 2026-04-17

---

## Root Files

| File | Purpose |
|------|---------|
| `README.md` | Project overview, quick start, stack summary |
| `INDEX.md` | This file — full directory & file reference |
| `MANUAL.md` | Usage guide & instructions |
| `PROTOCOLS.md` | Core sovereignty and security protocols |
| `CLAUDE.md` | Claude agent context and instructions |
| `package.json` | Root Node/TypeScript tooling (pnpm) |
| `pnpm-lock.yaml` | pnpm lockfile |
| `tsconfig.json` | TypeScript compiler config (strict, ES2022, path aliases) |
| `eslint.config.js` | ESLint flat config (ESLint 9, TypeScript-aware) |
| `.prettierrc` | Code formatting (single quotes, no semi, 100 char) |
| `.nvmrc` | Node version pin → 20 |
| `.python-version` | Python version pin → 3.11 |
| `.env.example` | Environment variable template |
| `.gitignore` | Ignores .env, .venv, node_modules, __pycache__, secrets |

---

## Directories

### `/agents`
AI agents — autonomous, orchestrated, or tool-using agents.

| Path | Purpose |
|------|---------|
| `agents/__init__.py` | Package init |
| `agents/example.py` | Example agent usage |
| `agents/api/` | FastAPI HTTP + WebSocket server |
| `agents/api/server.py` | HTTP API server (port 8000) |
| `agents/api/ws.py` | WebSocket real-time streaming |
| `agents/claude/` | Claude (Anthropic) runner and manifest |
| `agents/claude/agent.yaml` | Claude agent manifest |
| `agents/claude/runner.py` | Claude runner |
| `agents/claude/README.md` | Claude agent docs |
| `agents/core/` | Core agent framework |
| `agents/core/agent.py` | Base agent class |
| `agents/core/orchestrator.py` | Multi-agent orchestration |
| `agents/core/rag.py` | RAG pipeline (chunk, embed, retrieve, augment, generate) |
| `agents/core/registry.py` | Agent registry |
| `agents/core/stream.py` | Streaming (OpenAI, Anthropic, Ollama) |
| `agents/core/trace.py` | Observability/tracing to SQLite |
| `agents/core/memory/` | Memory subsystems |
| `agents/core/skills/` | Agent skill modules |
| `agents/core/tools/` | Agent tool modules |
| `agents/local/ollama.py` | Local LLM integration (Ollama) |
| `agents/workers/queue.py` | Redis-backed async task queue |

### `/codebase`
Shared libraries, utilities, and core code used across projects.

### `/compute`
Infrastructure configs, compute specs, deployment manifests.

| Path | Purpose |
|------|---------|
| `compute/README.md` | Compute environment docs |
| `compute/claude-env.md` | Claude runtime spec |
| `compute/requirements.txt` | Shared Python deps (pinned) |
| `compute/bootstrap-claude.sh` | Idempotent environment bootstrap |

### `/db`
Local databases and data stores.

| Path | Purpose |
|------|---------|
| `db/dome.db` | SQLite — sessions, stack, agents, skills, tools |
| `db/episodic.db` | SQLite — episodic memory (session facts) |
| `db/chroma/` | ChromaDB vector store (dome-kb, 141 chunks) |

### `/kb`
Knowledge bases.

| Path | Purpose |
|------|---------|
| `kb/developer-context.md` | Trinity Consortium identity and architecture context |
| `kb/kiro-skills.md` | Kiro CLI agent capability reference |
| `kb/claude/architecture.md` | Claude ↔ DOME-HUB architecture diagram |
| `kb/claude/claude-skills.md` | Claude skills catalog |
| `kb/claude/tools-reference.md` | Claude full tool catalog |
| `kb/claude/file-handling-guide.md` | Path rules and artifact guidance |
| `kb/claude/skills/` | Local mirror of live SKILL.md bundles |
| `kb/trinity-unified-ai/` | KB API for the Mycelium Neural Mesh (FRACTAL E8-SSII-AGI) |

### `/logs`
Session and activity logs.

| Path | Purpose |
|------|---------|
| `logs/2026-04-16-setup.md` | Initial DOME-HUB setup session log |
| `logs/2026-04-17-session.md` | Full system hardening + agent stack upgrade session |
| `logs/audit-2026-04-17.md` | Full audit report (security, Python, TypeScript, structure) |
| `logs/daemon-watch.log` | Daemon watchdog output log |
| `logs/dome-check.log` | Protocol check output log |

### `/models`
AI models, fine-tunes, weights, and model configs.
- `models/embeddings/` — local embedding models

### `/platforms`
Platform and product implementations.

### `/projects`
Individual software projects.

### `/scripts`
Automation, security, and utility scripts.

| Script | Purpose |
|--------|---------|
| `sovereign-setup-mac.sh` | Full sovereign setup for macOS M1/M2/M3/M4 |
| `sovereign-setup-windows.ps1` | Full sovereign setup for Windows |
| `bootstrap.sh` | Install all dependencies |
| `new-project.sh` | Scaffold new project with venv + Node |
| `optimize.sh` | Hardware optimization (CPU/GPU/memory tuning) |
| `harden.sh` | Security hardening (firewall, privacy, telemetry) |
| `audit.sh` | Security audit |
| `finish-security.sh` | Post-setup security finalization |
| `zshrc-dome.sh` | Shell environment (sourced by ~/.zshrc) |
| `dome-check.sh` | Protocol enforcer — runs all checks, auto-fixes |
| `dome-pm.sh` | Project manager (new, list, status, push-all, pull-all) |
| `dome-approve.sh` | Approval gate for privileged actions |
| `dome-sudo.sh` | Privileged command wrapper (requires approval) |
| `daemon-watch.sh` | Daemon watchdog — removes unauthorized launch agents |
| `ingest.py` | Populate ChromaDB vector store from KB, logs, docs |
| `rollover-language-landscape.py` | Create next `kb/language-landscape-<year>.md` from latest + optional ingest |
| `rollover-language-landscape.sh` | Wrapper: venv + rollover + ingest (cron / launchd) |
| `register-claude.py` | Populate dome.db with Claude agent + skills + tools |
| `public-safety-check.sh` | Public export gate for secrets, key signatures, and path leaks |
| `export-to-dsh.sh` | Allowlist/denylist-driven DOME-HUB -> DSH export pipeline |

### `/software`
Software packages, tools, and standalone utilities.

### `/src`
TypeScript source files.

| Path | Purpose |
|------|---------|
| `src/index.ts` | Root TypeScript entry point |

### `/.venv`
Python 3.11.9 virtual environment (root).
- All AI/ML libs installed here
- Activate: `source .venv/bin/activate`

### `/.vscode`
VS Code settings.

| Path | Purpose |
|------|---------|
| `.vscode/settings.json` | Format on save, Python/TS/Go defaults |
| `.vscode/extensions.json` | 16 recommended extensions |

---

## Key Paths

| Resource | Path |
|----------|------|
| Root | `~/DOME-HUB` |
| Python venv | `~/DOME-HUB/.venv` |
| SQLite DB | `~/DOME-HUB/db/dome.db` |
| Episodic DB | `~/DOME-HUB/db/episodic.db` |
| Vector Store | `~/DOME-HUB/db/chroma` |
| Trinity KB | `~/DOME-HUB/kb/trinity-unified-ai` |
| API Server | `http://127.0.0.1:8000` |
| GitHub | `https://github.com/gadikedoshim/DOME-HUB` |
