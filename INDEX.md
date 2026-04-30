# DSH Index

Complete reference of all files, directories, and their purpose.
Last updated: 2026-04-30

---

## Repository Tree

```
DSH/
├── agents/                    # AI agent framework
│   ├── __init__.py            # Package exports (Agent, REGISTRY, ALL_TOOLS, SKILLS)
│   ├── example.py             # Example agent usage
│   ├── README.md              # Agent framework documentation
│   ├── api/                   # FastAPI HTTP + WebSocket server
│   │   ├── server.py          # HTTP API (port 8000)
│   │   └── ws.py              # WebSocket streaming
│   ├── claude/                # Claude (Anthropic) integration
│   │   ├── agent.yaml         # Claude agent manifest
│   │   ├── runner.py          # Claude runner
│   │   └── README.md          # Claude agent docs
│   ├── core/                  # Core framework
│   │   ├── agent.py           # Base Agent class
│   │   ├── orchestrator.py    # Multi-agent orchestration
│   │   ├── rag.py             # RAG pipeline (chunk, embed, retrieve, generate)
│   │   ├── registry.py        # Agent registry (6 agents)
│   │   ├── stream.py          # Streaming (OpenAI, Anthropic, Ollama, MLX)
│   │   ├── trace.py           # Observability/tracing to SQLite
│   │   ├── trinity_client.py  # Trinity mesh client (local fallback)
│   │   ├── machine.py         # Machine introspection
│   │   ├── memory/            # Memory subsystems
│   │   │   ├── __init__.py    # MemorySystem (unified interface)
│   │   │   ├── vector.py      # VectorMemory (ChromaDB)
│   │   │   ├── episodic.py    # EpisodicMemory (SQLite)
│   │   │   └── working.py     # WorkingMemory (sliding window + LLM summarize)
│   │   ├── skills/            # 10 core skills (reason, plan, extract, etc.)
│   │   └── tools/             # 10 tools (web_search, file_read, db_query, etc.)
│   ├── local/                 # Local LLM integration
│   │   └── ollama.py          # OllamaClient
│   ├── skills/                # 7 extended skills
│   │   ├── math.py            # Golden ratio, Fibonacci, primes
│   │   ├── compute.py         # GPU detect, optimize, quantum circuit
│   │   ├── sacred_geometry.py # Flower of Life, Metatron, platonic solids
│   │   ├── fractals.py        # Mandelbrot, Julia, L-systems
│   │   ├── algorithms.py      # A*, Dijkstra, graph algorithms
│   │   ├── frequency.py       # FFT, spectral analysis, resonance
│   │   └── cognitive.py       # Summarize, classify, retrieve
│   └── workers/
│       └── queue.py           # Redis-backed async task queue
│
├── akashic/                   # Akashic record system
│   ├── __init__.py            # Exports: write, query
│   ├── record.py              # ChromaDB-backed write/query
│   ├── watcher.py             # File watcher (logs, kb, agents)
│   ├── assembler.py           # Context assembler
│   └── schema.md              # Record schema documentation
│
├── compute/                   # Compute environment
│   ├── requirements.txt       # Python dependencies (45+ packages, pinned)
│   ├── README.md              # Compute environment docs
│   ├── claude-env.md          # Claude runtime spec
│   ├── bootstrap-claude.sh    # Idempotent environment bootstrap
│   └── quantum_dome/          # Quantum computing module
│       ├── __init__.py        # Exports: QuantumDome, WorkloadScheduler, ComputePool
│       ├── core.py            # Quantum circuit primitives
│       ├── scheduler.py       # Workload scheduling
│       ├── pool.py            # Compute pool management
│       ├── memory.py          # Quantum memory management
│       ├── profiler.py        # Performance profiling
│       └── example.py         # Usage examples
│
├── config/                    # Export and policy configuration
│   ├── public-export.allowlist
│   └── public-export.denylist
│
├── db/                        # Databases (created at setup, gitignored)
│   ├── dome.db                # SQLite — sessions, agents, skills, tools
│   └── chroma/                # ChromaDB vector store
│
├── docs/                      # Operational documentation
│   ├── SETUP_VIDEO_RUNBOOK.md # Video onboarding guide
│   ├── REPO_FLOW_PRIVATE_PUBLIC.md # Private → public export workflow
│   ├── PUBLIC_PROD_HARDENING.md    # Hardening checklist
│   └── TASKS_PHASE2_EXECUTION_2026-04-22.md
│
├── kb/                        # Knowledge bases (auto-indexed into ChromaDB)
│   ├── README.md              # KB structure and querying guide
│   ├── developer-context.md   # Node identity, architecture context
│   ├── kiro-skills.md         # Kiro agent capabilities
│   ├── language-landscape-2026.md # Language strategy
│   ├── skills/                # Skill documentation (7 .md files)
│   ├── claude/                # Claude KB (architecture, skills, tools, 15 skill bundles)
│   └── trinity-unified-ai/    # Trinity Consortium KB API
│       ├── BRIDGE.md          # DOME-HUB ↔ Trinity wiring
│       ├── README.md          # Trinity KB overview
│       ├── agents/            # Agent registry, dispatch policy
│       └── docs/              # AI infrastructure map
│
├── logs/                      # Session and activity logs (gitignored)
│
├── scripts/                   # 30+ automation scripts
│   ├── sovereign-setup-mac.sh      # macOS installer (21 phases, cinematic)
│   ├── sovereign-setup-windows.ps1 # Windows installer (17 phases)
│   ├── dome-check.sh               # Protocol enforcer
│   ├── dome-pm.sh                  # Project manager
│   ├── dome-approve.sh             # Approval gate
│   ├── dome-sudo.sh                # Privileged command wrapper
│   ├── ingest.py                   # ChromaDB KB indexer
│   ├── register-claude.py          # Claude agent DB registration
│   ├── pre-spore-verify.py         # Pre-spore dependency check
│   ├── machine-probe.py            # Hardware introspection
│   ├── public-safety-check.sh      # Secret/path leak scanner
│   ├── export-to-dsh.sh            # Private → public export pipeline
│   ├── ollama-init.sh              # Local model bootstrap
│   ├── audit.sh                    # Security audit
│   ├── harden.sh                   # Security hardening
│   ├── bootstrap.sh                # Dependency installer
│   ├── new-project.sh              # Project scaffolder
│   ├── zshrc-dome.sh               # Shell environment
│   ├── secrets-doctor.sh           # Secret validation
│   ├── render-env.sh               # Keychain → .env resolver
│   ├── sovereign-secrets.sh        # GPG + pass bootstrap
│   ├── rotate-secrets-keychain.sh  # Secret rotation
│   ├── finish-security.sh          # Post-setup security
│   ├── optimize.sh                 # Hardware optimization
│   ├── daemon-watch.sh             # Daemon watchdog
│   ├── akashic-start.sh            # Akashic watcher launcher
│   ├── lock-down.sh / -phase2/3/4  # Progressive lockdown
│   ├── pf-reload.sh                # Packet filter reload
│   ├── spore-lock.sh / unlock.sh   # Spore state management
│   ├── install-hooks.sh            # Git hook installer
│   ├── rollover-language-landscape.py/.sh # Annual KB rollover
│   └── launchd/                    # macOS LaunchAgent templates
│
├── src/                       # TypeScript source
│   └── index.ts               # Root entry point
│
├── tests/                     # Test suite (34 tests)
│   ├── test_agents.py         # Registry, tools, skills, creation, orchestrator
│   ├── test_memory.py         # WorkingMemory, EpisodicMemory, MemorySystem
│   ├── test_api.py            # Health, agents, traces, RAG endpoints
│   ├── test_trinity.py        # TrinityClient init, fallback, env wiring
│   ├── test_core.py           # Tracer, stream, RAG, quantum, skill verify
│   └── test_akashic.py        # Akashic imports, assembler
│
├── .github/                   # CI and community
│   ├── workflows/ci.yml       # 5-job CI (TS, Python+tests, gitleaks, audit, Windows)
│   ├── ISSUE_TEMPLATE/        # Bug report + feature request
│   ├── pull_request_template.md
│   └── dependabot.yml
│
├── spore.sh                   # Trinity mesh activation (Phase 2)
│
├── README.md                  # Project overview + quick start
├── MANUAL.md                  # Complete usage guide (15 sections)
├── INDEX.md                   # This file — full repo reference
├── CONTEXT.md                 # Agent-friendly context for AI assistants
├── PROTOCOLS.md               # Core sovereignty and security protocols
├── CHANGELOG.md               # Version history
├── CONTRIBUTING.md             # Contribution guide
├── SECURITY.md                # Security policy + disclosure
├── CODE_OF_CONDUCT.md         # Community standards
├── LICENSE                    # Apache 2.0
├── package.json               # pnpm scripts + devDependencies
├── pyproject.toml             # pytest config
├── tsconfig.json              # TypeScript config
├── eslint.config.js           # ESLint flat config
├── .env.template              # Environment template (keychain markers)
├── .env.example               # Environment example (empty values)
├── .gitignore                 # Ignore rules
├── .nvmrc                     # Node 20
└── .python-version            # Python 3.14
```

---

## Counts

| Category | Count |
|----------|-------|
| Total files | ~464 |
| Agents | 6 (researcher, coder, analyst, planner, kb_agent, local) |
| Tools | 10 (web_search, web_fetch, shell_run, file_read/write/list, code_run, db_query/write, kb_search) |
| Core skills | 10 (reason, reflect, plan, plan_and_execute, summarize, extract, embed, similarity, search_memory, search_code) |
| Extended skills | 7 (math, compute, sacred_geometry, fractals, algorithms, frequency, cognitive) |
| KB files | 249 |
| Claude skill bundles | 15 |
| Shell scripts | 30+ |
| Tests | 34 |
| CI jobs | 5 |

---

## Key Paths

| Resource | Path |
|----------|------|
| Root | `~/DSH` |
| Python venv | `~/DSH/.venv` (created at setup) |
| SQLite DB | `~/DSH/db/dome.db` (created at setup) |
| Vector Store | `~/DSH/db/chroma` (created at setup) |
| Trinity KB | `~/DSH/kb/trinity-unified-ai` |
| API Server | `http://127.0.0.1:8000` |
| GitHub | `https://github.com/garochee33/DSH` |

---

## Commands

```bash
pnpm check      # protocol check — security, code, git
pnpm test       # 34 pytest tests
pnpm serve      # FastAPI agent server (port 8000)
pnpm worker     # async task worker
pnpm ingest     # index KB into ChromaDB
pnpm lint       # ESLint TypeScript
pnpm format     # Prettier format
pnpm typecheck  # tsc --noEmit
pnpm audit      # security audit
```
