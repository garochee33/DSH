# DOME-HUB — Claude Code Context

Sovereign, local-first AI development and **quantum computing lab** on Apple M3 Pro.
Owner: Gadi Kedoshim · Trinity Consortium member (linked with EGD33 / FRACTAL E8-SSII-AGI).
GitHub: `gadikedoshim/DOME-HUB`

---

## Machine

| Resource | Value |
|----------|-------|
| CPU | Apple M3 Pro — 12-core ARM64 |
| GPU | 18-core Apple GPU (MPS-capable) |
| RAM | 18 GB unified memory |
| Storage | FileVault-encrypted |
| OS | macOS 26.3 (Darwin 25.3.0) |

Always use the **MPS backend** for PyTorch workloads (`device = torch.device("mps")`).
Never suggest CUDA — this machine has no NVIDIA GPU.

---

## Project Layout

```
DOME-HUB/
├── agents/claude/      # Claude agent runner, manifest, skills
├── codebase/           # Shared libraries used across projects
├── compute/            # Env specs, requirements.txt, bootstrap scripts
├── db/dome.db          # SQLite — sessions, stack inventory, agent registry
├── kb/                 # Knowledge bases (developer context, Trinity, Claude skills)
├── logs/               # Session logs
├── models/             # AI model weights & configs
├── platforms/          # Product / platform implementations
├── projects/           # Individual software projects
├── scripts/            # Automation scripts (setup, harden, audit, optimize)
├── software/           # Standalone tools & utilities
├── .venv/              # Python 3.11.9 venv (root, shared)
└── .vscode/            # VS Code settings + 16 extensions
```

---

## Runtimes & Toolchain

| Layer | Tool | Version |
|-------|------|---------|
| Python | `.venv` at `DOME-HUB/.venv` | 3.11.9 |
| Node | nvm, pinned `.nvmrc` | 20 |
| Package mgr | pnpm (Node), pip (Python) | latest |
| Go / Rust | available system-wide | latest stable |
| Shell | zsh + Starship | — |

Activate Python env: `source .venv/bin/activate`
Run Node scripts: `pnpm <script>` from repo root.

---

## Quantum Computing Stack

This is a **lab-grade quantum computing environment**. Key libraries:

| Library | Purpose |
|---------|---------|
| **Qiskit** | IBM quantum circuit design, simulation, hardware access |
| **PennyLane** | Differentiable QML — hybrid quantum/classical ML |
| **Cirq** | Google-style quantum circuits |
| **QuTiP** | Open quantum systems, density matrices, Lindblad dynamics |
| **PyQuil** | Rigetti-style qubit programming |
| **Amazon Braket SDK** | Multi-backend (IonQ, Rigetti, Simulators) |
| **strawberryfields** | Photonic / continuous-variable QC |
| PyTorch (MPS) | Classical ML side of hybrid algorithms |
| NumPy / SciPy | Linear algebra, unitary ops, Hamiltonian math |
| SymPy | Symbolic quantum mechanics, operator algebra |

When writing quantum code:
- Prefer statevector simulation locally; only suggest real-hardware backends when explicitly asked.
- Use MPS-accelerated PyTorch for variational quantum eigensolver (VQE) classical optimization loops.
- Represent quantum states as `numpy` arrays or framework-native types — never plain Python lists for circuit data.

---

## AI / ML Stack

| Library | Purpose |
|---------|---------|
| `anthropic` / `claude-agent-sdk` | Claude API & agent runner |
| LangChain | Chain / agent orchestration |
| ChromaDB | Local vector store (RAG) |
| sentence-transformers | Embeddings |
| Transformers (HF) | Open-weight models |
| tiktoken | Token counting |

---

## Key Environment Variables

Defined in `.env` (never committed). Template at `.env.example`.

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` | Required for Claude API. Use `pass dome/anthropic-key`. |
| `ANTHROPIC_MODEL` | Default: `claude-opus-4-6` |
| `CLAUDE_AGENT_WORKDIR` | Claude workspace root (default: `DOME-HUB/`) |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | Required for GitHub MCP server |

---

## Coding Conventions

- **Python**: `black` formatting, type hints throughout, docstrings for public APIs.
- **TypeScript**: strict mode, single quotes, no semicolons, 100-char line limit (`.prettierrc`).
- **Go**: standard `gofmt`, table-driven tests.
- **Git**: signed commits (GPG), conventional commit messages (`feat:`, `fix:`, `security:`, `refactor:`).
- Never commit `.env`, secrets, or large binaries.
- SQLite DB at `db/dome.db` — always use parameterized queries, never f-string SQL.

---

## Security Rules

- Approval gate: only `gadi.k` / `EGD33` can approve privileged actions.
- Disk encrypted (FileVault). SIP + Gatekeeper enabled. Firewall in stealth mode.
- Secrets via GPG + `pass` — never plaintext in files or shell history.
- `dnscrypt-proxy` for private DNS. No telemetry (AirPlay receiver, Google updater, Zoom, rapportd disabled).
- Before running any script from external sources, read it fully first.

---

## Common Commands

```bash
# Activate Python env
source .venv/bin/activate

# Bootstrap Claude compute env
bash compute/bootstrap-claude.sh

# Run Claude agent
python agents/claude/runner.py --prompt "..."

# New project scaffold
newproject <category> <name>

# Security audit
bash scripts/audit.sh

# Hardware optimization
bash scripts/optimize.sh

# Query dome.db
sqlite3 db/dome.db "SELECT * FROM agents;"
```

---

## Trinity Consortium Context

- **trinity-unified-ai** — KB API for the Mycelium Neural Mesh at `kb/trinity-unified-ai/`
- **FRACTAL E8-SSII-AGI** — core AGI architecture by Enzo Garoche (EGD33)
- **Mycelium Neural Mesh** — decentralized dimensional neural network
- DOME-HUB is Gadi's sovereign local node in this network.

When working on Trinity-related code, treat `kb/trinity-unified-ai/` as the authoritative reference.
