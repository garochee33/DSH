# DOME-HUB

> Sovereign, local-first command center for AI development, software engineering, and compute.

DOME-HUB is the single root for all projects, platforms, agents, AI models, knowledge bases, and databases — running entirely on local hardware with no cloud dependencies. Built for privacy, security, and full data sovereignty.

---

## Owner
- **Gadi Kedoshim** (Gadi.K1989) — `gadi.k@greenergyfl.com`
- **Trinity Consortium** sovereign member — linked with Enzo Garoche (EGD33), founder of FRACTAL E8-SSII-AGI & trinity-unified-ai

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
├── agents/                  # AI agents
├── codebase/                # Shared libraries & core code
├── compute/                 # Infrastructure & compute configs
├── db/                      # Databases & data stores
│   └── dome.db              # SQLite — sessions, stack inventory
├── kb/                      # Knowledge bases
│   ├── developer-context.md # Trinity Consortium context
│   └── trinity-unified-ai/  # KB API for mycelium neural mesh
├── logs/                    # Session logs
├── models/                  # AI models & fine-tunes
├── platforms/               # Platforms & products
├── projects/                # Individual projects
├── scripts/                 # Automation & utility scripts
│   ├── sovereign-setup-mac.sh
│   ├── sovereign-setup-windows.ps1
│   ├── bootstrap.sh
│   ├── new-project.sh
│   ├── optimize.sh
│   ├── harden.sh
│   ├── audit.sh
│   └── zshrc-dome.sh
├── software/                # Software packages & tools
├── .venv/                   # Python 3.11.9 virtual environment
├── .vscode/                 # VS Code settings & extensions
├── .env.example             # Environment template
├── .eslintrc.json           # ESLint config
├── .gitignore
├── .nvmrc                   # Node version pin (20)
├── .prettierrc              # Prettier config
├── .python-version          # Python version pin (3.11)
├── INDEX.md                 # Full file & directory reference
├── MANUAL.md                # Usage guide
├── package.json             # Root Node/TS tooling
├── README.md
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

## New Project

```bash
newproject <category> <name>
# Example:
newproject agents my-agent
newproject projects my-app
```

Creates isolated Python venv + Node (pnpm) per project.

---

## Trinity Consortium

DOME-HUB is the local sovereign node for Trinity Consortium work.

- **trinity-unified-ai** — KB API for the Mycelium Neural Mesh (`kb/trinity-unified-ai/`)
- **FRACTAL E8-SSII-AGI** — core AGI architecture by Enzo Garoche (EGD33)
- **Mycelium Neural Mesh** — decentralized dimensional neural network

---

## Links
- GitHub: https://github.com/gadikedoshim/DOME-HUB
- Trinity Consortium: linked via `garochee33`
