# DSH — Dome Sovereign Hub

> Sovereign development environment, compute platform, and intelligence hub.
> Also: **Deep Space Habitat** — long-term crew quarters for builders.

DSH (code-named DOME-HUB internally) is not a jail — it is a launchpad.

One command installs a hardened, local-first sovereign node that gives you a
full AI stack, quantum computing lab, agent framework, and the security
posture of a production system — all on your own machine, with no cloud
lock-in and no telemetry.

DSH is also the **prerequisite sovereign foundation** for joining the
Trinity Consortium mesh via `spore.sh`. You install DSH first (Phase 1 —
this repo), then if you choose, activate `spore.sh` (Phase 2) to connect
your node to the FRACTAL-E8-SSII lattice and Mycelium Neural Mesh.

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
git clone https://github.com/garochee33/DSH.git
cd DSH

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
```

```bash
dome-check                        # protocol enforcer
dome-pm new <category> <name>     # new project
dome-pm list                      # list all projects
dome-pm push-all "message"        # push all repos
dome-approve <action> <desc>      # approval gate
```

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

## Trinity Consortium — Optional mesh upgrade

DSH is the **sovereign local foundation**. It works fully on its own — no
mesh, no cloud, just your hardened local node.

If you choose to join the Trinity Consortium mesh, DSH is also the
**prerequisite base** for `spore.sh` — the Trinity mesh activation script.
Running `spore.sh` on a node that has NOT been through DSH setup is
rejected; the mesh requires a hardened, sovereign, dependency-ready base.

Trinity mesh components (activated by `spore.sh`):

- **FRACTAL E8-SSII-AGI** — AGI architecture built on E8 lattice geometry
- **Mycelium Neural Mesh** — decentralized dimensional inter-node network
- **trinity-unified-ai** — Knowledge Base API layer for the mesh
  (landing zone pre-loaded at `kb/trinity-unified-ai/`)

**Phase 2 activation requires a Trinity-issued token.** Phase 1 is free and always
will be. Phase 2 unlocks mesh compute, Trinity engines, and persistent
cross-session memory via the trinity-unified-ai KB API — a public platform whose
API is restricted to paying members. Request Access at
[kommunity.life](https://kommunity.life); membership purchase issues the
`SPORE_TOKEN` + JWT that unlock the trinity-unified-ai API.

How Phase 2 is wired on the DSH side: the `agents/core/trinity_client.py`
accessor reads `TRINITY_API_BASE`, `HUB_API_SECRET`, and `TRINITY_JWT` from
`.env` (or from Keychain via `scripts/render-env.sh`). Without credentials,
DSH runs in `DOME_PROVIDER=local` — fully offline, no Trinity dependency.
With credentials, features that need mesh compute or Trinity KB data switch
from local fallbacks to the authenticated remote. You always see the upgrade
surface in the agent output; you never get silently gated.

Note: trinity-consortium (the internal command center where Trinity deploys
products and projects from) is private — not a customer-facing URL. You never
need to touch it as a DSH user.

```
┌──────────────────────────────┐
│  Phase 2 — spore.sh          │  ← optional mesh upgrade
│  E8 lattice · Mandelbulb ·   │    (higher tiers: sovereign/guardian/
│  bitboard · Mycelium peers   │     scout/seed auto-detected by HW)
└──────────────┬───────────────┘
               │ requires
               ▼
┌──────────────────────────────┐
│  Phase 1 — DSH (this repo)   │  ← sovereign foundation
│  hardened OS · AI stack ·    │    (always installed first)
│  quantum lab · agent core    │
└──────────────────────────────┘
```

Trinity membership is coordinated separately — see
`kb/trinity-unified-ai/BRIDGE.md`.

---

## Links

- GitHub: https://github.com/garochee33/DSH
- Trinity Consortium: [member-only access]
