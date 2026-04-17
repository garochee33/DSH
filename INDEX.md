# DOME-HUB Index

Complete reference of all files, directories, and their purpose.

---

## Root Files

| File | Purpose |
|------|---------|
| `README.md` | Project overview, quick start, stack summary |
| `INDEX.md` | This file — full directory & file reference |
| `MANUAL.md` | Usage guide & instructions |
| `package.json` | Root Node/TypeScript tooling (pnpm) |
| `tsconfig.json` | TypeScript compiler config (strict, ES2022, path aliases) |
| `.eslintrc.json` | ESLint rules (TypeScript-aware) |
| `.prettierrc` | Code formatting (single quotes, no semi, 100 char) |
| `.nvmrc` | Node version pin → 20 |
| `.python-version` | Python version pin → 3.11 |
| `.env.example` | Environment variable template |
| `.gitignore` | Ignores .env, .venv, node_modules, __pycache__ |

---

## Directories

### `/agents`
AI agents — autonomous, orchestrated, or tool-using agents.

### `/codebase`
Shared libraries, utilities, and core code used across projects.

### `/compute`
Infrastructure configs, compute specs, deployment manifests.

### `/db`
Local databases and data stores.
- `dome.db` — SQLite database
  - `sessions` table — session logs with timestamps and tags
  - `stack` table — installed tools, versions, and status

### `/kb`
Knowledge bases.
- `developer-context.md` — Trinity Consortium identity and architecture context
- `trinity-unified-ai/` — KB API for the Mycelium Neural Mesh (FRACTAL E8-SSII-AGI)

### `/logs`
Session and activity logs.
- `2026-04-16-setup.md` — Initial DOME-HUB setup session log

### `/models`
AI models, fine-tunes, weights, and model configs.

### `/platforms`
Platform and product implementations.

### `/projects`
Individual software projects.

### `/software`
Software packages, tools, and standalone utilities.

### `/.venv`
Python 3.11.9 virtual environment (root).
- All AI/ML libs installed here
- Activate: `source .venv/bin/activate`

### `/.vscode`
VS Code settings.
- `settings.json` — format on save, Python/TS/Go defaults
- `extensions.json` — 16 recommended extensions

---

## Scripts (`/scripts`)

| Script | Purpose |
|--------|---------|
| `sovereign-setup-mac.sh` | Full sovereign setup for macOS M1/M2/M3/M4 |
| `sovereign-setup-windows.ps1` | Full sovereign setup for Windows |
| `bootstrap.sh` | Install all dependencies |
| `new-project.sh` | Scaffold new project with venv + Node |
| `optimize.sh` | Hardware optimization (CPU/GPU/memory tuning) |
| `harden.sh` | Security hardening (firewall, privacy, telemetry) |
| `audit.sh` | Security audit |
| `zshrc-dome.sh` | Shell environment (sourced by ~/.zshrc) |

---

## Key Paths

| Resource | Path |
|----------|------|
| Root | `/Users/gadikedoshim/DOME-HUB` |
| Python venv | `/Users/gadikedoshim/DOME-HUB/.venv` |
| SQLite DB | `/Users/gadikedoshim/DOME-HUB/db/dome.db` |
| Trinity KB | `/Users/gadikedoshim/DOME-HUB/kb/trinity-unified-ai` |
| GitHub | `https://github.com/gadikedoshim/DOME-HUB` |
