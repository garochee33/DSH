# DSH — Codex Context

Sovereign, local-first AI development and **quantum computing lab** for any Apple Silicon Mac.
Public foundation for Trinity Consortium sovereign nodes.
GitHub: `garochee33/DSH`

> This file is the Codex-flavored mirror of `CLAUDE.md`. Both should stay aligned. Read whichever your agent loads.

---

## Machine — reference target

DSH is designed for any modern Apple Silicon Mac (M1 / M2 / M3 / M4). It auto-detects your CPU, GPU, Neural Engine, and unified memory; the snippets below show a typical reference machine.

| Resource | Typical value |
|----------|---------------|
| CPU | Apple Silicon (8–12 P-cores) |
| GPU | Apple integrated GPU (MPS-capable) |
| RAM | 16 GB+ unified memory recommended |
| Storage | FileVault-encrypted recommended |
| OS | macOS 14+ (Sonoma or later) |

Always use the **MPS backend** for PyTorch workloads (`device = torch.device("mps")`).
Never suggest CUDA — Apple Silicon has no NVIDIA GPU.

---

## Project Layout

```
DSH/
├── agents/             # Agent runners (Claude, Codex, Kiro, Cursor), manifests, skills
├── codebase/           # Shared libraries used across projects
├── compute/            # Env specs, requirements.txt, bootstrap scripts
├── db/                 # SQLite — sessions, stack inventory, agent registry
├── kb/                 # Knowledge bases (developer context, skills)
├── logs/               # Session logs
├── models/             # AI model weights & configs
├── scripts/            # Automation (setup, harden, audit, optimize)
├── dsh-console/        # Localhost sovereign-node control panel (Next.js)
├── .venv/              # Python venv (root, shared)
└── .vscode/            # VS Code settings
```

---

## Runtimes & Toolchain

| Layer | Tool | Version |
|-------|------|---------|
| Python | `.venv` at `DSH/.venv` | per `.python-version` |
| Node | nvm, pinned `.nvmrc` | 20 |
| Package mgr | pnpm (Node), pip (Python) | latest |
| Go / Rust | available system-wide | latest stable |
| Shell | zsh + Starship | — |

Activate Python env: `source .venv/bin/activate`
Run Node scripts: `pnpm <script>` from repo root.

---

## Quantum Computing Stack

DSH ships a lab-grade quantum environment. Key libraries:

| Library | Purpose |
|---------|---------|
| **Qiskit** | IBM quantum circuit design, simulation, hardware access |
| **PennyLane** | Differentiable QML — hybrid quantum/classical ML |
| **Cirq** | Google-style quantum circuits |
| **QuTiP** | Open quantum systems, density matrices, Lindblad dynamics |
| **PyQuil** | Rigetti-style qubit programming |
| **Amazon Braket SDK** | Multi-backend (IonQ, Rigetti, simulators) |
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
| 1 | **Apple MLX** (`mlx-*` models) | Fastest local, fully air-gapped, Apple Silicon native |
| 2 | **Ollama** (`llama3.1`, `mistral`, `phi3`, `qwen2.5-coder`, etc.) | Local, air-gapped, sovereign |
| 3 | **Anthropic Claude** (`claude-*`) | Cloud, but no OpenAI dependency — for tasks needing strong reasoning |
| 4 | **OpenAI** (`gpt-*`) | Last resort only — not sovereign, avoid for sensitive work |

**Control via env vars:**
- `DOME_PROVIDER=local` → force all agents to Ollama (air-gapped mode)
- `DOME_PROVIDER=claude` → all agents use Anthropic API
- `DOME_PROVIDER=mixed` → per-agent optimal (default)
- `DOME_LOCAL_MODEL=llama3.1:8b` → default local model

**Recommended Ollama models (16–24 GB unified memory target):**
- `llama3.1:8b` — general purpose (fast, fits easily)
- `qwen2.5-coder:14b` — code (needs 16 GB+)
- `phi3:medium` — lightweight, fast
- `mistral:7b` — strong general reasoning
- `nomic-embed-text` — local embeddings

Pull models: `ollama pull llama3.1:8b`

**Agent → provider mapping (`DOME_PROVIDER=mixed`):**
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
| `ANTHROPIC_MODEL` | Override Claude model |
| `CLAUDE_AGENT_WORKDIR` | Claude agent workspace root (default: `DSH/`) |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | GitHub MCP server |

Trinity-mesh variables (Phase 2; subscription + `spore.sh` required) live commented in `.env.example` — see `docs/DSH_PUBLIC_PHASE1_BOUNDARY.md`.

---

## Coding Conventions

- **Python**: `black` formatting, type hints throughout, docstrings for public APIs.
- **TypeScript**: strict mode, single quotes, no semicolons, 100-char line limit (`.prettierrc`).
- **Go**: standard `gofmt`, table-driven tests.
- **Git**: conventional commit messages (`feat:`, `fix:`, `security:`, `refactor:`).
- Never commit `.env`, secrets, or large binaries.
- SQLite — always use parameterized queries, never f-string SQL.

---

## Security Rules

- Disk encrypted (FileVault) recommended. SIP + Gatekeeper enabled. Firewall in stealth mode.
- Secrets via GPG + `pass` — never plaintext in files or shell history.
- `dnscrypt-proxy` for private DNS recommended.
- Before running any script from external sources, read it fully first.

---

## Common Commands

```bash
# Activate Python env
source .venv/bin/activate

# Bootstrap compute env
bash compute/bootstrap.sh

# Run an agent
python agents/claude/runner.py --prompt "..."   # or codex / kiro / cursor

# Security audit
bash scripts/audit.sh

# Hardware optimization
bash scripts/optimize.sh

# Query the local sqlite db
sqlite3 db/dome.db "SELECT * FROM agents;"

# Launch the localhost dashboard (Next.js)
cd dsh-console && pnpm install && pnpm dev
# → http://127.0.0.1:4747
```

---

## Trinity Consortium Mesh (Phase 2 — optional)

Trinity Consortium is the optional decentralized infrastructure that DSH nodes
can join after Phase 1 setup is complete. It is NOT required to run DSH locally.

**Network architecture (Phase 2):**
- **FRACTAL E8-SSII-AGI** — AGI system by Trinity Consortium. Core intelligence of the network.
- **Mycelium Neural Mesh** — decentralized inter-node network. Sovereign nodes connect via mesh.
- **trinity-unified-ai** — KB API layer for the Mycelium network. `kb/trinity-unified-ai/` is the landing zone for the Trinity seed deposit (Phase 2).
- **spore.sh** — Trinity's initialization/seed script. Activates a DSH node on the mesh.

**Current state of public DSH:** Phase 1 foundation only. The Trinity stack is governed by
its own (proprietary) terms — see the proprietary notice in `LICENSE` and the boundary doc
`docs/DSH_PUBLIC_PHASE1_BOUNDARY.md`.

When working on Trinity-related code (Phase 2 operators only):
- Treat `kb/trinity-unified-ai/` as authoritative once seeded
- All Trinity work operates under the decentralized sovereignty principle — no single vendor owns it
- Inter-node communication protocol is defined by Trinity Consortium spec
