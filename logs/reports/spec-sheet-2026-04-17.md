# DOME-HUB — Technical Specification Sheet
**Version:** 1.0.0  
**Date:** 2026-04-17  
**Node:** gadikedoshim/DOME-HUB

---

## Hardware

| Component | Spec |
|-----------|------|
| Chip | Apple M3 Pro |
| Memory | 18 GB Unified Memory |
| OS | macOS 26.3 |
| Architecture | ARM64 (Apple Silicon) |

---

## Language Runtimes

| Language | Version | Manager |
|----------|---------|---------|
| Python | 3.11.9 | pyenv |
| Node.js | 20.20.2 | nvm |
| Go | 1.26.2 | homebrew |
| Rust | 1.94.1 | rustup |
| TypeScript | 6.0 | pnpm |

---

## Databases

| Database | Version | Port | Backend | Purpose |
|----------|---------|------|---------|---------|
| PostgreSQL | 17.9 | 5432 | local | Relational data |
| Redis | 8.6.2 | 6379 | local | Task queue, cache |
| SQLite | 3.51 | — | file | Episodic memory, traces |
| ChromaDB | 1.5.8 | 8001 | local | Vector memory, KB, Akashic |

---

## AI / ML Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| PyTorch | 2.11.0 | Tensor compute, MPS GPU |
| Transformers | 5.5.4 | Model loading, inference |
| sentence-transformers | 5.4.1 | Embeddings (all-MiniLM-L6-v2) |
| MLX | 0.31.1 | Apple Silicon native inference |
| mlx-lm | 0.31.2 | MLX language model runner |
| Ollama | 0.6.1 | Local LLM server |
| LangChain | — | Agent/chain framework |
| ChromaDB | 1.5.8 | Vector store |
| Anthropic SDK | 0.96.0 | Claude API |
| OpenAI SDK | 2.32.0 | OpenAI API |

---

## Quantum Computing Stack

| Framework | Version | Backend |
|-----------|---------|---------|
| Qiskit | 2.3.0 | IBM Quantum / Aer simulator |
| Qiskit Aer | 0.17.2 | Local quantum simulation |
| PennyLane | 0.44.1 | Quantum ML, variational circuits |
| Cirq | 1.6.1 | Google quantum framework |
| QuTiP | 5.2.3 | Quantum toolbox |
| PyQuil | 4.17.0 | Rigetti quantum |
| Amazon Braket SDK | 1.100.0 | AWS quantum |

---

## Web / API Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| FastAPI | 0.136.0 | HTTP API server |
| uvicorn | 0.44.0 | ASGI server |
| WebSockets | 16.0 | Real-time streaming |
| httpx | 0.28.1 | Async HTTP client |
| pydantic | 2.13.1 | Data validation |

---

## Agent System

| Module | Path | Purpose |
|--------|------|---------|
| Base Agent | agents/core/agent.py | Tool dispatch, memory, streaming |
| Orchestrator | agents/core/orchestrator.py | Multi-agent coordination |
| Registry | agents/core/registry.py | Agent factory + dome orchestrator |
| RAG Pipeline | agents/core/rag.py | Chunk → embed → retrieve → generate |
| Stream | agents/core/stream.py | Multi-provider LLM streaming |
| Trace | agents/core/trace.py | Observability → SQLite |
| Vector Memory | agents/core/memory/vector.py | ChromaDB semantic memory |
| Episodic Memory | agents/core/memory/episodic.py | SQLite session facts |
| Working Memory | agents/core/memory/working.py | Sliding window + summarize |
| HTTP Server | agents/api/server.py | FastAPI port 8000 |
| WebSocket | agents/api/ws.py | Real-time streaming |
| Task Queue | agents/workers/queue.py | Redis async tasks |
| Local LLM | agents/local/ollama.py | Ollama integration |
| Claude Runner | agents/claude/runner.py | Claude agent runner |

---

## Pre-Spore Skills

| Module | Path | Domain | Depth |
|--------|------|--------|-------|
| math | agents/skills/math.py | build | axiom |
| compute | agents/skills/compute.py | build | axiom |
| sacred_geometry | agents/skills/sacred_geometry.py | trinity | axiom |
| fractals | agents/skills/fractals.py | trinity | axiom |
| algorithms | agents/skills/algorithms.py | build | axiom |
| frequency | agents/skills/frequency.py | trinity | axiom |
| cognitive | agents/skills/cognitive.py | agent | axiom |

---

## Akashic System

| Component | Path | Purpose |
|-----------|------|---------|
| Schema | akashic/schema.md | Dimensional record spec |
| Record | akashic/record.py | Write/query dimensional entries |
| Watcher | akashic/watcher.py | Background file watcher daemon |
| Assembler | akashic/assembler.py | Session context generator |
| DB Namespace | db/chroma/ (akashic) | ChromaDB vector store |

**Dimensions:** domain × depth × node × resonance × timestamp  
**Retrieval:** Semantic (vector similarity), not linear (timestamp)

---

## Knowledge Base

| Path | Contents |
|------|---------|
| kb/developer-context.md | Trinity Consortium, node identity, architecture |
| kb/kiro-skills.md | Kiro CLI capabilities |
| kb/README.md | KB structure and query guide |
| kb/skills/ | 7 skill domain docs |
| kb/claude/ | Claude agent KB (architecture, skills, tools, file-handling) |
| kb/claude/skills/ | Packaged Claude skills (docx, pdf, pptx, xlsx, etc.) |
| kb/trinity-unified-ai/ | ⏳ Reserved — awaiting spore.sh |

**ChromaDB namespace:** dome-kb | **Chunks indexed:** 141+

---

## Security Controls

| Control | Implementation |
|---------|---------------|
| Disk encryption | FileVault (macOS native) |
| System integrity | SIP enabled |
| App verification | Gatekeeper enabled |
| Network | Firewall + Stealth mode |
| DNS | dnscrypt-proxy (127.0.0.1) |
| Secrets | GPG key 1EAB79C5C7DCA719 + pass store |
| Git | Commit signing enabled |
| Telemetry | Blocked in /etc/hosts + system prefs |
| Daemons | Watchdog — auto-removes unauthorized agents |
| Access | Approval gate — Trinity members only |
| Spore lockdown | SPORE_GERMINATING=1 → blocks Anthropic/OpenAI |

---

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | /agents/{name}/run | Run agent |
| POST | /agents/{name}/stream | Stream agent response |
| GET | /agents | List agents |
| GET | /agents/{name}/memory | Get agent memory |
| DELETE | /agents/{name}/memory | Clear agent memory |
| POST | /rag/ingest | Ingest text to vector store |
| POST | /rag/query | Query vector store |
| GET | /traces | Get observability traces |
| GET | /health | Stack health check |
| GET | /spore/status | Spore status (allowed during lockdown) |

---

## CLI Commands

```bash
pnpm serve      # FastAPI server — port 8000
pnpm worker     # Redis task worker
pnpm ingest     # Re-index KB into ChromaDB
pnpm check      # Full protocol check
pnpm sync       # pull + ingest + commit + push
pnpm audit      # Security audit
pnpm lint       # ESLint TypeScript
pnpm format     # Prettier
pnpm typecheck  # TypeScript check

source scripts/spore-lock.sh       # Engage air-gap lockdown
source scripts/spore-unlock.sh     # Release lockdown
python3 scripts/pre-spore-verify.py  # 27/27 verification gate
bash scripts/akashic-start.sh      # Start Akashic watcher daemon
akashic-query [concept]            # Query dimensional field
```

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| DOME_ROOT | /Users/gadikedoshim/DOME-HUB |
| DOME_PROVIDER | mixed (local \| claude \| mixed) |
| DOME_LOCAL_MODEL | llama3.1:8b |
| SPORE_GERMINATING | 1 = lockdown active |
| SENTENCE_TRANSFORMERS_HOME | models/ |
| HF_HOME | models/hf |
| TORCH_HOME | models/torch |
