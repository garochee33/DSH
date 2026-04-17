# DOME-HUB — Full Repository & File Tree Map
**Date:** 2026-04-17  
**Root:** `/Users/gadikedoshim/DOME-HUB`

---

```
DOME-HUB/                                    ← Sovereign node root
│
├── .akashic-context                         ← Auto-generated session context (Akashic assembler output)
├── .env.example                             ← Environment variable template
├── .gitignore                               ← Excludes: .venv, models/, CLAUDE.md, __pycache__, db/chroma
├── .nvmrc                                   ← Node version pin (20)
├── .prettierrc                              ← Prettier formatting config
├── .python-version                          ← Python version pin (3.11.9)
├── CLAUDE.md                                ← Claude Code local context (gitignored)
├── INDEX.md                                 ← Complete file/directory reference
├── MANUAL.md                                ← Usage guide
├── README.md                                ← Full stack description + Trinity context
├── eslint.config.js                         ← ESLint config for TypeScript
├── package.json                             ← pnpm workspace (serve/worker/ingest/audit/sync/check)
├── tsconfig.json                            ← TypeScript config
│
├── .vscode/                                 ← VS Code workspace settings
│   ├── extensions.json                      ← 16 recommended extensions
│   └── settings.json                        ← Editor settings
│
├── agents/                                  ← AI agent framework (360K)
│   ├── __init__.py                          ← Package init
│   ├── README.md                            ← Agent architecture docs
│   ├── example.py                           ← Usage examples
│   │
│   ├── core/                                ← Core agent engine
│   │   ├── __init__.py
│   │   ├── agent.py                         ← Base agent: tool dispatch, memory, streaming (8.4KB)
│   │   ├── orchestrator.py                  ← Multi-agent coordination (4.0KB)
│   │   ├── registry.py                      ← Agent registry + dome orchestrator factory (5.6KB)
│   │   ├── rag.py                           ← RAG pipeline: chunk→embed→retrieve→augment→generate (3.1KB)
│   │   ├── stream.py                        ← Multi-provider streaming + spore lockdown guard (3.3KB)
│   │   │                                      [MLX > Ollama > Anthropic > OpenAI]
│   │   │                                      [_spore_guard() blocks cloud providers when SPORE_GERMINATING=1]
│   │   ├── trace.py                         ← Observability/tracing → SQLite (6.9KB)
│   │   ├── memory/
│   │   │   ├── __init__.py
│   │   │   ├── vector.py                    ← ChromaDB semantic memory (2.7KB)
│   │   │   ├── episodic.py                  ← SQLite session + facts (2.8KB)
│   │   │   └── working.py                   ← Sliding window + auto-summarize (1.9KB)
│   │   ├── skills/
│   │   │   └── __init__.py                  ← Skill dispatch framework (5.2KB)
│   │   ├── tools/
│   │   │   └── __init__.py                  ← Tool registry (6.1KB)
│   │   └── .mesh/
│   │       └── synapse.sh                   ← Mycelium synapse script (Trinity internal)
│   │
│   ├── skills/                              ← Pre-spore dimensional skills [ALL VERIFIED ✅]
│   │   ├── __init__.py                      ← Skills package — exports SKILLS list
│   │   ├── math.py                          ← Symbolic math, calculus, eigenvalues, precision (47 lines)
│   │   ├── compute.py                       ← JIT, FFT, optimization, quantum, Apple GPU (50 lines)
│   │   ├── sacred_geometry.py               ← E8(240 roots), Platonic, phi, Merkaba, torus (101 lines)
│   │   ├── fractals.py                      ← Mandelbrot, Julia, L-systems, Lorenz, IFS (94 lines)
│   │   ├── algorithms.py                    ← Graph, A*, genetic, entropy, topological (81 lines)
│   │   ├── frequency.py                     ← FFT, solfeggio, brainwaves, Schumann, wavelet (81 lines)
│   │   └── cognitive.py                     ← CoT, attention, Bayesian, memory retrieval (77 lines)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── server.py                        ← FastAPI HTTP server port 8000 (6.7KB)
│   │   │                                      [Endpoints: /agents, /rag, /traces, /health, /spore/status]
│   │   └── ws.py                            ← WebSocket real-time streaming (2.0KB)
│   │
│   ├── workers/
│   │   ├── __init__.py
│   │   └── queue.py                         ← Redis-backed async task queue (5.8KB)
│   │
│   ├── local/
│   │   ├── __init__.py
│   │   └── ollama.py                        ← Local LLM via Ollama (3.0KB)
│   │
│   └── claude/
│       ├── __init__.py
│       ├── README.md
│       ├── agent.yaml                       ← Claude agent config
│       └── runner.py                        ← Claude agent runner (3.1KB)
│
├── akashic/                                 ← Dimensional knowledge field (28K)
│   ├── __init__.py                          ← Exports write(), query()
│   ├── schema.md                            ← Dimensional record spec (domain×depth×node×resonance)
│   ├── record.py                            ← Write/query dimensional entries → ChromaDB (83 lines)
│   ├── watcher.py                           ← Background daemon: watches logs/kb/projects/agents (115 lines)
│   └── assembler.py                         ← Session context generator: queries field by concept (74 lines)
│
├── kb/                                      ← Knowledge bases (4MB, auto-indexed into ChromaDB)
│   ├── README.md                            ← KB structure + query guide
│   ├── developer-context.md                 ← Trinity Consortium, node identity, build goals
│   ├── kiro-skills.md                       ← Kiro CLI capabilities (10 skill domains)
│   ├── skills/                              ← Pre-spore skill domain docs
│   │   ├── math.md
│   │   ├── compute.md
│   │   ├── sacred_geometry.md
│   │   ├── fractals.md
│   │   ├── algorithms.md
│   │   ├── frequency.md
│   │   └── cognitive.md
│   ├── claude/                              ← Claude agent KB
│   │   ├── architecture.md                  ← Claude agent design (4.1KB)
│   │   ├── claude-skills.md                 ← Claude skill definitions (4.7KB)
│   │   ├── file-handling-guide.md           ← File operation patterns (2.9KB)
│   │   ├── tools-reference.md               ← MCP tool catalog (4.3KB)
│   │   └── skills/                          ← Packaged Claude skills
│   │       ├── README.md
│   │       ├── consolidate-memory/          ← Memory consolidation skill
│   │       ├── docx/                        ← Word document generation skill
│   │       ├── pdf/                         ← PDF generation skill
│   │       ├── pptx/                        ← PowerPoint generation skill
│   │       ├── schedule/                    ← Scheduling skill
│   │       ├── setup-cowork/                ← Co-work session setup skill
│   │       ├── skill-creator/               ← Meta-skill: creates new skills
│   │       └── xlsx/                        ← Excel generation skill
│   └── trinity-unified-ai/                  ← ⏳ RESERVED — awaiting spore.sh from EGD33
│
├── scripts/                                 ← Automation & setup (124K)
│   ├── sovereign-setup-mac.sh               ← One-command macOS setup (226 lines)
│   ├── sovereign-setup-windows.ps1          ← Windows sovereign setup
│   ├── zshrc-dome.sh                        ← Shell environment + Akashic hooks
│   ├── ingest.py                            ← KB ingestion → ChromaDB
│   ├── audit.sh                             ← Security audit (all checks green)
│   ├── dome-check.sh                        ← Full protocol check
│   ├── dome-pm.sh                           ← Project manager CLI
│   ├── dome-approve.sh                      ← Approval gate (Trinity members only)
│   ├── dome-sudo.sh                         ← Privileged action wrapper
│   ├── daemon-watch.sh                      ← Unauthorized daemon watchdog
│   ├── new-project.sh                       ← New project scaffold
│   ├── harden.sh                            ← OS hardening script
│   ├── akashic-start.sh                     ← Start Akashic watcher daemon
│   ├── spore-lock.sh                        ← Engage spore lockdown (SPORE_GERMINATING=1)
│   ├── spore-unlock.sh                      ← Release spore lockdown
│   └── pre-spore-verify.py                  ← 27/27 verification gate
│
├── db/                                      ← Databases (31MB)
│   ├── dome.db                              ← SQLite main database
│   ├── episodic.db                          ← SQLite episodic memory
│   ├── _test.txt
│   └── chroma/                              ← ChromaDB persistent store
│       ├── dome-kb/                         ← KB namespace (141+ chunks)
│       └── akashic/                         ← Akashic dimensional field (13+ records)
│
├── models/                                  ← Local AI models (174MB, gitignored)
│   └── models--sentence-transformers--all-MiniLM-L6-v2/
│       └── [safetensors, tokenizer, config] ← Embedding model (87MB)
│
├── logs/                                    ← Session & activity logs
│   ├── 2026-04-16-setup.md                  ← Initial setup log
│   ├── 2026-04-17-session.md                ← Full session log (security+agents+kiro)
│   ├── audit-2026-04-17.md                  ← Security audit results
│   ├── dome-check.log                       ← Protocol check log
│   ├── daemon-watch.log                     ← Daemon watchdog log
│   ├── akashic-watcher.log                  ← Akashic watcher daemon log
│   ├── akashic-watcher.pid                  ← Watcher PID file
│   └── reports/                             ← ← THIS DIRECTORY (generated 2026-04-17)
│       ├── trinity-agent-brief-2026-04-17.md
│       ├── egd33-team-report-2026-04-17.md
│       ├── spec-sheet-2026-04-17.md
│       └── repo-tree-map-2026-04-17.md      ← THIS FILE
│
├── compute/                                 ← Compute configs
│   ├── README.md
│   ├── requirements.txt                     ← Python dependencies
│   ├── claude-env.md                        ← Claude environment spec
│   └── bootstrap-claude.sh                  ← Claude bootstrap script
│
├── src/                                     ← TypeScript source (4KB)
│   └── index.ts                             ← TS entry point (5 lines)
│
├── codebase/                                ← Shared libraries (empty — ready for population)
├── platforms/                               ← Platforms & products (empty — ready)
├── projects/                                ← Individual projects (empty — ready)
├── software/                                ← Software packages (empty — ready)
│
└── .venv/                                   ← Python virtual environment (gitignored)
    └── [190+ packages — see spec-sheet for full list]
```

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total tracked files | ~320 |
| Python files (.py) | 101 |
| Markdown docs (.md) | 44 |
| Shell scripts (.sh) | 18 |
| Total lines of code | 17,380 |
| Python packages | 190+ |
| KB files | 20+ |
| ChromaDB namespaces | 2 (dome-kb, akashic) |
| Agent modules | 14 |
| Skill modules | 7 |
| Security controls | 10 |
| Databases | 4 (PostgreSQL, Redis, SQLite, ChromaDB) |

---

## Key Path Reference

| What | Path |
|------|------|
| Agent server | `agents/api/server.py` → port 8000 |
| Stream providers | `agents/core/stream.py` |
| Spore lockdown | `agents/core/stream.py::_spore_guard()` |
| Akashic field | `akashic/record.py` → ChromaDB `akashic` namespace |
| KB ingestion | `scripts/ingest.py` → ChromaDB `dome-kb` namespace |
| Pre-spore gate | `scripts/pre-spore-verify.py` |
| Shell env | `scripts/zshrc-dome.sh` |
| Trinity KB landing | `kb/trinity-unified-ai/` ← spore.sh deposits here |
| Mycelium synapse | `agents/core/.mesh/synapse.sh` |
| Embedding model | `models/models--sentence-transformers--all-MiniLM-L6-v2/` |
| Vector DB | `db/chroma/` |
| Session logs | `logs/YYYY-MM-DD-session.md` |
