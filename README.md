# DOME-HUB

> Sovereign, local-first command center for AI development, software engineering, and compute.

DOME-HUB is the single root for all projects, platforms, agents, AI models, knowledge bases, and databases — running entirely on local hardware with no cloud dependencies. Built for privacy, security, and full data sovereignty.

---

## Node
- **Trinity Consortium** sovereign node
- Apple M3 Pro · local-first · fully sovereign

## Machine
- Apple M3 Pro · 12-core CPU · 18-core GPU · 18GB unified memory · macOS 26.3

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

---

## Structure

```
DOME-HUB/
├── agents/                  # AI agents (core, claude, api, workers, local)
├── codebase/                # Shared libraries & core code
├── compute/                 # Infrastructure & compute configs
├── db/                      # Databases & data stores
│   ├── dome.db              # SQLite — sessions, stack, agents, skills, tools
│   ├── episodic.db          # SQLite — episodic memory
│   └── chroma/              # ChromaDB vector store (dome-kb)
├── kb/                      # Knowledge bases
│   ├── developer-context.md # Trinity Consortium context
│   ├── kiro-skills.md       # Kiro CLI capability reference
│   ├── claude/              # Claude capability reference
│   └── trinity-unified-ai/  # KB API for mycelium neural mesh
├── logs/                    # Session and activity logs
├── models/                  # AI models & fine-tunes
├── platforms/               # Platforms & products
├── projects/                # Individual projects
├── scripts/                 # Automation & utility scripts
│   ├── sovereign-setup-mac.sh
│   ├── sovereign-setup-windows.ps1
│   ├── bootstrap.sh
│   ├── new-project.sh
│   ├── dome-check.sh        # Protocol enforcer
│   ├── dome-pm.sh           # Project manager
│   ├── dome-approve.sh      # Approval gate
│   ├── dome-sudo.sh         # Privileged command wrapper
│   ├── daemon-watch.sh      # Daemon watchdog
│   ├── ingest.py            # KB → ChromaDB ingest
│   ├── register-claude.py   # Register Claude in dome.db
│   ├── optimize.sh
│   ├── harden.sh
│   ├── audit.sh
│   ├── finish-security.sh
│   └── zshrc-dome.sh
├── software/                # Software packages & tools
├── src/                     # TypeScript source
├── .venv/                   # Python 3.11.9 virtual environment
├── .vscode/                 # VS Code settings & extensions
├── .env.example             # Environment template
├── eslint.config.js         # ESLint flat config (ESLint 9)
├── .gitignore
├── .nvmrc                   # Node version pin (20)
├── .prettierrc              # Prettier config
├── .python-version          # Python version pin (3.11)
├── CHANGELOG.md             # Change history
├── CLAUDE.md                # Claude agent context
├── INDEX.md                 # Full file & directory reference
├── MANUAL.md                # Usage guide
├── PROTOCOLS.md             # Core sovereignty protocols
├── package.json             # Root Node/TS tooling
└── tsconfig.json            # TypeScript config
```

---

## Stack

| Category | Tools |
|----------|-------|
| Languages | Python 3.11, Node 20, Go, Rust |
| AI/ML | PyTorch (MPS/GPU), OpenAI, Anthropic, LangChain, ChromaDB, Transformers |
| Math | NumPy, SciPy, Pandas, scikit-learn, SymPy, Numba |
| Databases | PostgreSQL 17, Redis 8, SQLite, ChromaDB |
| Infra | Terraform, AWS CLI, GitHub CLI, Docker |
| Editor | VS Code + 16 extensions |
| Security | FileVault, GPG, pass, dnscrypt-proxy, Firewall |
| Shell | zsh, Starship, zoxide, fzf, tmux, ripgrep |

---

## Security Posture

| Check | Status |
|-------|--------|
| FileVault (disk encryption) | ✅ |
| SIP (System Integrity Protection) | ✅ |
| Gatekeeper | ✅ |
| Firewall + Stealth mode | ✅ |
| Private DNS (dnscrypt-proxy) | ✅ |
| GPG key + pass secret store | ✅ |
| Git commit signing | ✅ |

---

## Scripts & Commands

### Shell Scripts

| Script | Command | Purpose |
|--------|---------|---------|
| `sovereign-setup-mac.sh` | `bash scripts/sovereign-setup-mac.sh` | Full sovereign setup for macOS M1/M2/M3/M4 |
| `sovereign-setup-windows.ps1` | `pwsh scripts/sovereign-setup-windows.ps1` | Full sovereign setup for Windows |
| `bootstrap.sh` | `bash scripts/bootstrap.sh` | Install all dependencies |
| `new-project.sh` | `newproject <cat> <name>` | Scaffold new project with venv + Node |
| `dome-check.sh` | `dome-check` / `pnpm check` | Protocol enforcer — security, code, git |
| `dome-pm.sh` | `dome-pm <cmd>` | Project manager (new, list, push-all…) |
| `dome-approve.sh` | `dome-approve <action> <desc>` | Approval gate for privileged actions |
| `dome-sudo.sh` | `dome-sudo <cmd>` | Privileged command wrapper |
| `daemon-watch.sh` | `bash scripts/daemon-watch.sh` | Remove unauthorized launch agents |
| `optimize.sh` | `sudo bash scripts/optimize.sh` | Hardware optimization |
| `harden.sh` | `sudo bash scripts/harden.sh` | Security hardening |
| `audit.sh` | `bash scripts/audit.sh` / `pnpm audit` | Security audit |
| `finish-security.sh` | `bash scripts/finish-security.sh` | Post-setup security finalization |
| `zshrc-dome.sh` | sourced by `~/.zshrc` | Shell environment & aliases |

### pnpm Scripts

| Command | Purpose |
|---------|---------|
| `pnpm check` | Full protocol check (`dome-check.sh`) |
| `pnpm sync` | Pull + ingest + commit + push |
| `pnpm ingest` | Populate ChromaDB from KB, logs, docs |
| `pnpm serve` | Start FastAPI agent server (port 8000) |
| `pnpm audit` | Run security audit |
| `pnpm lint` | ESLint TypeScript source |
| `pnpm lint:fix` | ESLint with auto-fix |
| `pnpm format` | Prettier format all files |
| `pnpm typecheck` | TypeScript type check |
| `pnpm worker` | Start async task worker |

---

```bash
newproject <category> <name>
# Example:
newproject agents my-agent
newproject projects my-app
```

Creates isolated Python venv + Node (pnpm) per project.

---

## AI Assistants

The setup script will prompt you to install one. You can also install manually:

| Assistant | Install |
|-----------|---------|
| **Kiro CLI** | `npm install -g kiro-cli` |
| **Claude Code** | `npm install -g @anthropic-ai/claude-code` |
| **Cursor** | `brew install --cask cursor` · [cursor.com](https://cursor.com) |
| **GitHub Copilot** | `gh extension install github/gh-copilot` |
| **Aider** | `pip install aider-chat` |

---

## Trinity Consortium

DOME-HUB is the local sovereign node for Trinity Consortium work.

- **trinity-unified-ai** — KB API for the Mycelium Neural Mesh (`kb/trinity-unified-ai/`)
- **FRACTAL E8-SSII-AGI** — core AGI architecture by Trinity Consortium
- **Mycelium Neural Mesh** — decentralized dimensional neural network

---

## Links
- GitHub: https://github.com/gadikedoshim/DOME-HUB
- Trinity Consortium: [member-only access]
