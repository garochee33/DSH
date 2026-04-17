# DOME-HUB — Claude Code Context

Sovereign, local-first AI development and **quantum computing lab** on Apple M3 Pro.
Trinity Consortium sovereign node.
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

## LLM Provider Architecture — Multi-Provider, Local-First

Sovereignty means no single vendor owns this stack. Provider hierarchy:

| Priority | Provider | When to use |
|----------|----------|-------------|
| 1 | **Apple MLX** (`mlx-*` models) | Fastest local, fully air-gapped, M3 Pro native |
| 2 | **Ollama** (`llama3.1`, `mistral`, `phi3`, `qwen2.5-coder`, etc.) | Local, air-gapped, sovereign |
| 3 | **Anthropic Claude** (`claude-*`) | Cloud, but no OpenAI dependency — for tasks needing strong reasoning |
| 4 | **OpenAI** (`gpt-*`) | Last resort only — not sovereign, avoid for sensitive work |

**Control via env vars:**
- `DOME_PROVIDER=local` → force all agents to Ollama (air-gapped mode)
- `DOME_PROVIDER=claude` → all agents use Anthropic API
- `DOME_PROVIDER=mixed` → per-agent optimal (default)
- `DOME_LOCAL_MODEL=llama3.1:8b` → default local model

**Recommended Ollama models for this machine (18GB unified memory):**
- `llama3.1:8b` — general purpose (fast, fits easily)
- `qwen2.5-coder:14b` — code (fits in 18GB)
- `phi3:medium` — lightweight, fast
- `mistral:7b` — strong general reasoning
- `nomic-embed-text` — local embeddings (alternative to sentence-transformers)

Pull models: `ollama pull llama3.1:8b`

**Agent → provider mapping (DOME_PROVIDER=mixed):**
- `kb_agent` → always local (KB data never leaves machine)
- `analyst` → local (data sovereignty)
- `coder` → local (IP stays on device)
- `researcher` → Claude (needs web, cloud acceptable)
- `planner` → local or Claude depending on complexity
- `local` → always Ollama, always air-gapped

---

## Key Environment Variables

Defined in `.env` (never committed). Template at `.env.example`.

| Variable | Purpose |
|----------|---------|
| `DOME_PROVIDER` | `local` / `claude` / `mixed` — controls agent provider strategy |
| `DOME_LOCAL_MODEL` | Default Ollama model (default: `llama3.1:8b`) |
| `ANTHROPIC_API_KEY` | Claude API — use `pass dome/anthropic-key` |
| `ANTHROPIC_MODEL` | Override Claude model (default: `claude-opus-4-6`) |
| `CLAUDE_AGENT_WORKDIR` | Claude workspace root (default: `DOME-HUB/`) |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | GitHub MCP server |

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

- Approval gate: only authorized Trinity Consortium members can approve privileged actions.
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

## Trinity Consortium — The Infrastructure

Trinity Consortium is not a component of DOME-HUB. It IS the infrastructure that DOME-HUB
exists inside. DOME-HUB is Gadi's **sovereign node** in the Trinity network.

**Network architecture:**
- **FRACTAL E8-SSII-AGI** — AGI system by Trinity Consortium. Core intelligence of the network.
- **Mycelium Neural Mesh** — decentralized inter-node network, dimensional, biological-inspired.
  All sovereign member nodes connect through this mesh.
- **trinity-unified-ai** — KB API layer for the Mycelium network. `kb/trinity-unified-ai/`
  is the landing zone for Trinity's seed deposit.
- **spore.sh** — Trinity's initialization/seed script. Activates this node on the mesh.

**Approved principals:** Trinity Consortium members only (defined in operational security config).

**Current state:** Foundation built. Awaiting `spore.sh` and trinity-unified-ai KB spec
to activate the Mycelium connection for this node.

When working on any Trinity-related code:
- Treat `kb/trinity-unified-ai/` as authoritative once seeded
- All Trinity work operates under the decentralized sovereignty principle — no single vendor owns it
- Inter-node communication protocol is defined by Trinity Consortium spec
