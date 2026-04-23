# DOME-HUB

> Sovereign development environment, compute platform, and intelligence hub.

DOME-HUB is not a jail — it is a launchpad.

It protects sovereignty, IP, project integrity, memory, and data. Beyond protection it provides:

- **Unlimited virtual space** — structured repo management, isolated per-project environments, multi-language support
- **Full compute access** — CPU, GPU (Apple Metal/MPS), memory optimization, local AI inference
- **Massive dependency library** — Python, Node, Go, Rust, all AI/ML frameworks, math, data, and infra tools pre-installed and maintained
- **Brain management** — persistent vector memory (ChromaDB), episodic memory, RAG pipeline, knowledge bases, semantic search
- **Co-pilot support** — Kiro + Claude working in parallel, agent orchestration, multi-agent pipelines
- **Skills and tools** — 10 tools, 10 skills, 6 pre-built agents, streaming, tracing, task queue
- **Trinity Consortium integration** — FRACTAL E8-SSII-AGI, Mycelium Neural Mesh, trinity-unified-ai KB API
- **Build anything** — apps, platforms, websites, agents, models, APIs, pipelines, neural networks

---

## Who it's for

**Developers & engineers** — full-stack, backend, systems, ML, infra  
**Designers & creatives** — generative AI, creative tools, visual pipelines  
**Artists** — AI art, music, video, interactive media  
**Entrepreneurs** — build and ship products without cloud lock-in  
**Researchers** — local LLMs, quantum computing, data science  
**Anyone** who wants to build software, apps, websites, agents, models, or tools — privately, on their own machine

---

## What you get

One command installs and configures everything:

- **Full AI stack** — local LLMs (Ollama/MLX), Claude, OpenAI, LangChain, ChromaDB, RAG pipelines, agent framework
- **Model training** — PyTorch with Apple GPU (MPS), Transformers, fine-tuning ready
- **Quantum computing** — Qiskit, PennyLane, Cirq, QuTiP, PyQuil, Amazon Braket
- **Web & app dev** — Node 20, TypeScript, React-ready, FastAPI, PostgreSQL, Redis
- **Creative tools** — document generation (Word, PDF, PowerPoint, Excel), image pipelines
- **Data science** — NumPy, Pandas, SciPy, scikit-learn, Matplotlib, SymPy, Numba
- **Infra & cloud** — AWS CLI, Terraform, GitHub CLI, Docker
- **Security** — encrypted disk, private DNS, GPG signing, firewall, no telemetry
- **Your choice of AI assistant** — Kiro, Claude Code, Cursor, Copilot, Aider

Everything is isolated to your machine. Your data, your models, your code — never leaves unless you push it.

---

## Quick Start

```bash
# Clone
git clone https://github.com/gadikedoshim/DOME-HUB.git
cd DOME-HUB

# macOS (M1/M2/M3/M4)
bash scripts/sovereign-setup-mac.sh

# Windows
pwsh scripts/sovereign-setup-windows.ps1
```

That's it. The script handles everything — languages, databases, AI stack, security, shell config, and prompts you to pick your AI assistant at the end.

---

## Build anything

```bash
# Start a new project (creates isolated Python venv + Node)
newproject projects my-app
newproject agents my-agent
newproject platforms my-platform
newproject models my-model
newproject software my-tool

# Start the AI agent server
pnpm serve          # http://localhost:8000

# Start the async task worker
pnpm worker

# Re-index your knowledge base
pnpm ingest
```

---

## Customize everything

DOME-HUB is designed to be fully customized. Every piece is modular:

| What | Where | How |
|------|-------|-----|
| AI agents | `agents/` | Add new agents, tools, skills, memory backends |
| Knowledge bases | `kb/` | Drop in any `.md`, `.txt`, `.pdf` — auto-indexed into ChromaDB |
| Models | `models/` | Store fine-tunes, embeddings, weights locally |
| Databases | `db/` | SQLite, PostgreSQL, Redis, ChromaDB — all local |
| Scripts | `scripts/` | Add your own automation, hooks, workflows |
| Environment | `.env` | Switch providers, models, modes per project |
| Shell | `scripts/zshrc-dome.sh` | Add aliases, functions, env vars |
| Security | `scripts/harden.sh` | Adjust hardening rules to your needs |
| Projects | `projects/`, `platforms/`, `software/` | Fully isolated per-project environments |

---

## Stack

| Category | Tools |
|----------|-------|
| Languages | Python 3.11, Node 20, TypeScript, Go, Rust |
| Local AI | Ollama, MLX, mlx-lm (Apple Silicon native) |
| Cloud AI | Anthropic Claude, OpenAI (optional) |
| AI/ML | PyTorch (MPS/GPU), LangChain, ChromaDB, Transformers, sentence-transformers |
| Quantum | Qiskit, PennyLane, Cirq, QuTiP, PyQuil, Amazon Braket |
| Data | NumPy, Pandas, SciPy, scikit-learn, SymPy, Numba, Matplotlib |
| Databases | PostgreSQL 17, Redis 8, SQLite, ChromaDB |
| Web/API | FastAPI, uvicorn, httpx, requests, BeautifulSoup |
| Documents | python-docx, python-pptx, openpyxl, reportlab, pypdf |
| Infra | AWS CLI, Terraform, GitHub CLI, Docker |
| Editor | VS Code + 16 extensions |
| Security | FileVault, GPG, pass, dnscrypt-proxy, Firewall + Stealth |
| Shell | zsh, Starship, zoxide, fzf, tmux, ripgrep |

---

## AI Assistants

The setup script prompts you to pick one. Install manually anytime:

| Assistant | Install |
|-----------|---------|
| **Kiro CLI** | `npm install -g kiro-cli` |
| **Claude Code** | `npm install -g @anthropic-ai/claude-code` |
| **Cursor** | `brew install --cask cursor` · [cursor.com](https://cursor.com) |
| **GitHub Copilot** | `gh extension install github/gh-copilot` |
| **Aider** | `pip install aider-chat` |

---

## Security

DOME-HUB is hardened by default. Every setup runs:

| Check | Status |
|-------|--------|
| FileVault (disk encryption) | ✅ enabled |
| SIP (System Integrity Protection) | ✅ enabled |
| Gatekeeper | ✅ enabled |
| Firewall + Stealth mode | ✅ enabled |
| Private DNS (dnscrypt-proxy) | ✅ enabled |
| GPG key + pass secret store | ✅ configured |
| Git commit signing | ✅ enabled |
| Telemetry disabled | ✅ (Chrome, Siri, Spotlight, Crash Reporter) |
| Unauthorized daemons removed | ✅ auto-watched |

Run `pnpm check` anytime to verify and auto-fix your security posture.

---

## Commands

```bash
pnpm check      # full protocol check — security, code, git
pnpm sync       # pull + ingest + commit + push
pnpm ingest     # index KB into ChromaDB
pnpm serve      # start agent API server (port 8000)
pnpm worker     # start async task worker
pnpm audit      # security audit
pnpm lint       # lint TypeScript
pnpm format     # format all files
pnpm typecheck  # TypeScript type check
pnpm public:check       # safety gate for public export
pnpm public:export:dry  # build export set + diff preview (no writes)
pnpm public:export      # apply private -> public overlay sync
pnpm public:export:prune # strict mirror sync (deletes non-export files)
```

```bash
dome-check                        # protocol enforcer
dome-pm new <category> <name>     # new project
dome-pm list                      # list all projects
dome-pm push-all "message"        # push all repos
dome-approve <action> <desc>      # approval gate
```

Private/public repo flow: `docs/REPO_FLOW_PRIVATE_PUBLIC.md`

---

## Structure

```
DOME-HUB/
├── agents/          # AI agents — core, claude, api, workers, local
├── codebase/        # Shared libraries
├── compute/         # Compute configs & requirements
├── db/              # Databases (SQLite, ChromaDB)
├── kb/              # Knowledge bases (auto-indexed)
├── logs/            # Session & activity logs
├── models/          # Local AI models & fine-tunes
├── platforms/       # Platforms & products
├── projects/        # Individual projects
├── scripts/         # Automation & setup scripts
├── software/        # Software packages & tools
└── src/             # TypeScript source
```

---

## Trinity Consortium

DOME-HUB is the sovereign local node for Trinity Consortium work.

- **FRACTAL E8-SSII-AGI** — core AGI architecture
- **Mycelium Neural Mesh** — decentralized dimensional neural network
- **trinity-unified-ai** — KB API layer (`kb/trinity-unified-ai/`)

---

## Links

- GitHub: https://github.com/gadikedoshim/DOME-HUB
- Trinity Consortium: [member-only access]
