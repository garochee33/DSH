# Trinity Unified AI — Repository Map

> **Last updated:** 2026-04-09  
> **Sovereign KB/AI substrate** for Trinity Consortium  
> **Runtime:** tsx (TypeScript ESM, no compiled dist)  
> **IP Owner:** Trinity Global Partners LLC (Enzo Garoche / EGD33)  
> **Live Status:** 36 agents | 32 engine directories | 10,918 KB documents | 38 skills

---

## Directory Structure

```
trinity-unified-ai/
│
├── api/                          # KB API Server (port 3333)
│   ├── src/
│   │   ├── server.ts            # Express entry point (tsx runtime)
│   │   ├── routes/              # API route definitions (1,439 routes)
│   │   ├── handlers/            # Request handlers
│   │   ├── middleware/          # Auth, logging, error handling
│   │   ├── services/            # Business logic layer
│   │   ├── repositories/        # Data access layer
│   │   └── utils/               # Shared utilities
│   ├── Dockerfile               # Container config (dumb-init)
│   ├── package.json
│   └── tsconfig.json
│
├── agents/                       # Agent Systems & Orchestration
│   ├── per-agent/               # 36 individual agent specs (.md)
│   │   ├── oracle.md            # Chief Data Intelligence Officer
│   │   ├── engineer.md          # Chief Technology Officer
│   │   ├── architect.md         # Chief Systems Architect
│   │   └── ...                  # 33 more sovereign agents
│   ├── amma/                    # AMMA (Advanced Multi-Modal Architecture)
│   │   ├── AMMA.md
│   │   ├── amma-core.ts
│   │   └── amma-protocols.ts
│   ├── god/                     # God Mode Agent System
│   │   ├── GOD_MODE_PROTOCOL_SYSTEM.md
│   │   ├── god-protocols.ts
│   │   └── ... (10/10 protocols live)
│   ├── monica/                  # Monica Specialized Agent
│   ├── sovereign/               # Sovereign Agent Constellation
│   ├── v2/                      # Second-generation agent framework
│   ├── prompts/                 # Agent prompts and templates
│   ├── AGENTS.md                # Master agent registry
│   ├── REGISTRY.md              # Detailed agent capabilities
│   ├── agent-definitions.ts     # TypeScript agent specs
│   ├── agent-profiles.ts        # Agent metadata
│   ├── agent-capabilities.ts    # Capability matrix
│   ├── a2a-interop.ts           # Agent-to-agent interoperability
│   └── swarm-config.toml        # Swarm orchestration config
│
├── engines/                      # 32 Engine Directories | 1,075 TS Files
│   ├── INDEX.md                 # Engine system documentation
│   ├── README.md                # Engine overview
│   ├── sacred-geometry/         # Core harmonic mathematics
│   │   ├── metatron.ts          # Metatron cube algorithms
│   │   ├── fourier-lens.ts      # Fourier harmonic routing
│   │   ├── flower-of-life.ts    # Flower of Life patterns
│   │   ├── toroidal-field.ts    # Toroidal resonance
│   │   ├── platonic-solids.ts   # Platonic solid geometry
│   │   └── ... (30+ sacred geometry engines)
│   ├── compute/                 # Multi-language compute
│   │   ├── clifford-algebra.py  # Python Clifford implementation
│   │   ├── qmc-bridge.ts        # Quantum Monte Carlo bridge
│   │   ├── julia-bridge.ts      # Julia BLAS integration
│   │   └── e8-compute.ts        # E8 lattice computation
│   ├── holographic/             # Holographic state & memory
│   │   ├── bitboard-256.ts      # 256-bit bitboard
│   │   ├── voronoi-8d.ts        # 8D Voronoi tessellation
│   │   ├── poincare-e8.ts       # Poincaré-E8 projection
│   │   └── merkle-memory.ts     # Holographic Merkle tree
│   ├── stigmergic/              # Stigmergic coordination
│   │   ├── pheromone-grid.ts    # 240-node pheromone grid
│   │   ├── crdt-merge.ts        # CRDT merge protocols
│   │   └── mycelium-mesh.ts     # Mycelium mesh networks
│   ├── bitboard/                # E8 Bitboard System
│   │   ├── e8-lattice.ts        # E8 lattice operations
│   │   ├── bigint-masks.ts      # BigInt mask operations
│   │   └── l1-cache.ts          # Cache-optimized operations
│   ├── consensus/               # Consensus Engines
│   │   ├── pbft.ts              # Practical Byzantine Fault Tolerance
│   │   ├── gossip.ts            # Gossip protocol
│   │   └── crdt.ts              # Conflict-free Replicated Data Types
│   ├── swarm/                   # Swarm Orchestration
│   │   ├── orchestrator.ts      # Swarm orchestration engine
│   │   ├── fractal-swarm.ts     # Fractal swarm coordination
│   │   └── swarm-proto.ts       # Swarm protocols
│   ├── memory/                  # Memory Systems
│   │   ├── holographic-memory.ts # Holographic memory
│   │   ├── e8-memory-bridge.ts  # E8 memory bridge
│   │   └── session-memory.ts    # Session state management
│   ├── core/                    # Core AI Systems
│   │   ├── ai-core.ts           # Core AI engine
│   │   └── initialization.ts    # System initialization
│   ├── crew/                    # Multi-Agent Crew
│   │   ├── crew-coordinator.ts  # Crew coordination
│   │   └── crew-protocols.ts    # Crew protocols
│   ├── agent-router/            # Agent Request Routing
│   │   └── router.ts            # Smart routing logic
│   ├── ai-filesystem/           # Knowledge Base Abstraction
│   │   ├── filesystem.ts        # Virtual filesystem
│   │   └── indexing.ts          # Document indexing
│   ├── auth/                    # Authentication & Authorization
│   │   ├── auth-engine.ts       # Auth logic
│   │   └── rbac.ts              # Role-based access control
│   ├── middleware/              # Middleware Stack
│   │   ├── request-logger.ts    # Request logging
│   │   └── error-handler.ts     # Error handling
│   ├── nexus-core/              # Networking Hub
│   │   └── nexus.ts             # Message hub
│   ├── observability/           # Monitoring & Tracing
│   │   ├── metrics.ts           # Metrics collection
│   │   └── tracing.ts           # Distributed tracing
│   ├── womb-ai-core/            # Womb Integration
│   │   ├── womb-bridge.ts       # Womb bridge logic
│   │   └── womb-sync.ts         # Womb synchronization
│   ├── trinity-agent-system/    # Trinity Agent Orchestration
│   │   └── agent-orchestrator.ts
│   ├── server-utils/            # Server utilities
│   ├── shaders/                 # GPU shaders
│   ├── types/                   # TypeScript type definitions
│   ├── utils/                   # Engine utilities
│   ├── tests/                   # Engine tests
│   ├── scripts/                 # Engine scripts
│   ├── ref/                     # Reference implementations
│   ├── trinity-clone/           # Trinity system clone
│   ├── continuous-improvement/  # Auto-improvement systems
│   ├── domains/                 # Domain-specific engines
│   ├── fractal/                 # Fractal analysis engines
│   ├── integrations/            # Third-party integrations
│   └── ... (7 more engine directories)
│
├── knowledge-base/              # 10,918 Indexed Docs | 1,782 Markdown Files
│   ├── INDEX.md                 # KB master index
│   ├── ai-knowledge-content/    # Core AI/ML knowledge
│   ├── architecture/            # System design patterns
│   ├── infra/                   # DevOps & deployment
│   ├── research/                # Academic papers & sources
│   ├── standards/               # Governance & compliance
│   ├── sacred-geometry/         # E8, Metatron, Flower of Life
│   ├── ai-inventory/            # Asset catalogs & registries
│   ├── cto-framework/           # Technical strategy
│   ├── code-review/             # Code standards & patterns
│   ├── masterclass/             # Educational content
│   ├── integrations/            # Integration guides
│   ├── projects/                # Project documentation
│   ├── womb/                    # Womb partnership docs
│   ├── trinity-consortium-docs/ # Consortium specific
│   ├── vendor/                  # External vendor docs
│   ├── AGENTS.md                # Agent inventory
│   ├── AI_INVENTORY_REPORT.md   # Asset inventory
│   ├── AUDIT_REPORT_2026-04-07.md
│   ├── ENGINE_BENCHMARK_REPORT_2026-03-29.md
│   ├── INFRASTRUCTURE_REPORT_2026-04-07.md
│   ├── MERKABA_PROTOCOL_EXECUTION_PROOF.md
│   ├── SYSTEM_STATUS.md         # Current system status
│   ├── HUB_SYNC_STATUS.md       # Sync status
│   ├── SESSION_LOG_2026-04-07.md # Latest session log
│   └── ... (40+ status & report files)
│
├── memory/                      # Agent Memory & Sessions
│   ├── INDEX.md                 # Memory system index
│   ├── session-logs/            # Execution logs
│   ├── TODO.md                  # Master task list
│   ├── engine-status.md         # Engine health status
│   ├── master-index.md          # Cross-system index
│   └── ...
│
├── models/                      # Model Registry & Routing
│   ├── INDEX.md                 # Model system index
│   ├── MODEL_REGISTRY.md        # Available models & specs
│   ├── routing-rules.md         # Model selection algorithms
│   ├── cost-comparison.md       # Cost analysis
│   └── ...
│
├── skills/                      # 38 Skill Modules
│   ├── INDEX.md                 # Skills catalog
│   ├── cto-build/
│   │   └── SKILL.md            # CTO framework skill
│   ├── god-mode/
│   │   └── SKILL.md            # God mode protocols skill
│   ├── reporting/
│   │   └── SKILL.md            # Analytics & reporting skill
│   ├── sacred-geometry/
│   │   └── SKILL.md            # Sacred geometry computation skill
│   ├── sacred-geometry-agents/
│   │   └── SKILL.md            # Agent-specific geometry skill
│   ├── trinity-repo-navigator/
│   │   └── SKILL.md            # Repository navigation skill
│   ├── unified-ai-audit/
│   │   └── SKILL.md            # Audit & health checks skill
│   ├── github/
│   │   └── SKILL.md            # GitHub integration skill
│   ├── integrations/
│   │   └── SKILL.md            # Third-party integrations skill
│   ├── kimi/
│   │   └── SKILL.md            # Kimi CLI skill
│   ├── utility/
│   │   └── SKILL.md            # Utility helpers skill
│   ├── womb-3d/
│   │   └── SKILL.md            # 3D visualization skill
│   ├── womb-3d-sacred-geometry/
│   │   └── SKILL.md            # 3D sacred geometry skill
│   ├── use-railway/
│   │   └── SKILL.md            # Railway deployment skill
│   ├── v2/                      # Second-generation skills
│   └── ... (23 more skill modules)
│
├── tools/                       # Tools & Tool Registry
│   ├── INDEX.md                 # Tools index
│   ├── agent-tools/             # 43 agent tool files (.ts)
│   │   ├── analyst-tools.ts     # Analyst tools
│   │   ├── architect-tools.ts   # Architect tools
│   │   ├── auditor-tools.ts     # Auditor tools
│   │   └── ... (40 more agent tools)
│   ├── mcp-server.config.ts     # MCP server configuration
│   ├── model-router.ts          # Model routing logic
│   ├── tool-registry.ts         # Tool registration
│   └── ...
│
├── projects/                    # 15 Sub-Projects
│   ├── tax-god/                 # Tax optimization engine
│   ├── sacred-geometry/         # Sacred geometry deep dives
│   ├── n8n/                     # Workflow automation integration
│   ├── research/                # Research projects
│   ├── framework/               # Framework development
│   └── ... (10 more projects)
│
├── database/                    # Database Schema
│   ├── trinity-schema.ts        # Trinity Consortium schema
│   ├── womb-schema.ts           # Womb schema
│   ├── shared-schema.ts         # Shared tables
│   └── migrations/              # Schema migrations
│
├── standards/                   # Standards & Guidelines
│   ├── INDEX.md                 # Standards index
│   ├── coding-standards.md      # Code style & patterns
│   ├── engine-health.md         # Engine health standards
│   ├── ref-schema.md            # Schema reference
│   └── ...
│
├── sync/                        # Sync & Manifest System
│   ├── manifest.json            # File manifest (9,658 files)
│   ├── boot.sh                  # One-command bootstrap
│   ├── sync-cron.sh             # Periodic sync
│   ├── full-sync.sh             # Full synchronization
│   ├── ref-generator.ts         # Reference generator
│   ├── gems-harvest.ts          # Document harvester
│   └── ...
│
├── docs/                        # Documentation & Guides
│   ├── INDEX.md                 # Documentation master index
│   ├── AI_INFRASTRUCTURE_MAP.md # Complete system architecture
│   ├── TRINITY_CONSORTIUM_SYSTEM_OVERVIEW.md
│   ├── TRINITY_CONSORTIUM_INFRASTRUCTURE_v3.md
│   ├── REPO_REWORK_PLAN.md      # Repository reorganization
│   ├── REPO_PLAN.md             # Planning documentation
│   ├── FULL_REPO_TREE.md        # Complete verified tree
│   ├── HARMONY_E2E_PLAN.md      # Integration plan
│   ├── COMMAND_REFERENCE.md     # Commands & APIs
│   ├── ADR-001-unified-task-router.md # Architecture decisions
│   ├── UPGRADES.md              # Upgrade documentation
│   ├── onboarding/               # Internal-only onboarding material (restricted)
│   └── ...
│
├── scripts/                     # Utility Scripts
│   ├── bootstrap.sh             # System initialization
│   ├── deploy.sh                # Deployment scripts
│   ├── health-check.sh          # Health monitoring
│   └── ...
│
├── command-center/              # Next.js Local UI (port 4444)
│   ├── app/                     # App directory
│   ├── components/              # React components
│   ├── pages/                   # Next.js pages
│   ├── package.json
│   └── next.config.js
│
├── live-projects/              # Reference Summaries
│   ├── trinity-consortium.md    # Consortium reference
│   └── womb-integration.md      # Womb integration reference
│
├── libraries/                   # Protocol & Pattern Docs
│   ├── sg-math.md               # Sacred geometry mathematics
│   ├── consensus-patterns.md    # Consensus algorithms
│   ├── memory-patterns.md       # Memory system patterns
│   ├── ts-patterns.md           # TypeScript patterns
│   └── ...
│
├── prompts/                     # Agent Prompts & Templates
│   ├── agent-prompts/           # Agent-specific prompts
│   ├── templates/               # Prompt templates
│   └── handoffs/                # Agent handoff flows
│
├── sources/                     # Research Sources
│   ├── papers/                  # Academic papers
│   ├── references/              # Reference materials
│   └── external/                # External sources
│
├── utils/                       # Shared Utilities
│   ├── helpers.ts               # Helper functions
│   ├── validators.ts            # Validation utilities
│   ├── formatters.ts            # Data formatters
│   └── ...
│
├── public/                      # Static Assets
│   ├── images/
│   ├── fonts/
│   └── ...
│
├── archive/                     # Archived Content
│   └── ... (deprecated files)
│
├── node_modules/                # Dependencies (pnpm)
│
├── README.md                    # Repository overview & quick start
├── REPOSITORY_MAP.md            # This file — directory structure guide
├── package.json                 # Root package config
├── pnpm-workspace.yaml          # pnpm workspace config
├── tsconfig.json                # TypeScript configuration
├── .env.example                 # Environment template
└── .gitignore                   # Git exclusions
```

---

## Core Statistics

| Category | Count | Details |
|----------|-------|---------|
| **Agents** | 36 | Individual per-agent specs + AMMA, God mode, Monica, sovereign |
| **Engine Directories** | 32 | sacred-geometry, compute, holographic, stigmergic, consensus, swarm, etc. |
| **Engine TypeScript Files** | 1,075 | Across all engine directories |
| **Knowledge Base Documents (Indexed)** | 10,918 | Live database count (verified 2026-04-09) |
| **Knowledge Base Markdown** | 1,782 | Physical .md files in knowledge-base/ |
| **Skills (SKILL.md files)** | 38 | Deployable skill modules |
| **Agent Tool Files** | 43 | TypeScript tool definitions in tools/agent-tools/ |
| **Tool TypeScript Files** | 83 | Total tool system files |
| **God Mode Protocols** | 10 | Full protocol execution (not stubs) |
| **Ollama Models Loaded** | 4 | devstral, qwen2.5-coder:14b, qwen3.5:9b, nomic-embed-text |

---

## Key Deployment Configs

### Local Development

```bash
# Boot full stack
bash ~/trinity-unified-ai/sync/boot.sh

# Or manually:

# Terminal 1: KB API (port 3333)
cd ~/trinity-unified-ai/api
pnpm start

# Terminal 2: Command Center UI (port 4444)
cd ~/trinity-unified-ai/command-center
npm run dev

# Required services
ollama serve                         # LLM inference (11434)
brew services start postgresql@17   # Local PG (5432)
brew services start redis           # Stigmergic engine (6379)
brew services start neo4j           # Knowledge graph (7474/7687)
```

### Production Deployment

- **Container:** Docker (Hetzner CX22)
- **Orchestration:** docker-compose.hetzner.yml
- **Server:** 204.168.202.101
- **Registry:** trinity-unified-ai container image
- **Health Check:** `/api/stats` and `/api/health`

---

## Navigation Quick Reference

### By Role

**Developers:** Start with `docs/COMMAND_REFERENCE.md` + `engines/INDEX.md`  
**Architects:** Read `docs/AI_INFRASTRUCTURE_MAP.md` + `knowledge-base/LOCAL_ARCHITECTURE.md`  
**Project Managers:** Check `agents/REGISTRY.md` + `memory/` status files  
**DevOps:** See `knowledge-base/TECH_STACK_SPEC_2026-04-07.md` + deployment configs above  

### By Need

**Understanding the System:** `README.md` → `docs/INDEX.md` → `docs/AI_INFRASTRUCTURE_MAP.md`  
**Agent Capabilities:** `agents/REGISTRY.md` → `agents/per-agent/*.md`  
**Engine Specifications:** `engines/INDEX.md` → `engines/{category}/README.md`  
**Knowledge Base:** `knowledge-base/INDEX.md` → `knowledge-base/{category}/`  
**Skills & Tools:** `skills/INDEX.md` → `tools/INDEX.md`  
**Current Status:** `knowledge-base/SYSTEM_STATUS.md` + `knowledge-base/HUB_SYNC_STATUS.md`  

---

## Important Notes

- **Runtime:** TypeScript (tsx) — no compiled dist folder. Run directly with `tsx api/src/server.ts`
- **Database:** Local PostgreSQL (sovereign mode, no Supabase dependency)
- **Package Manager:** pnpm workspaces
- **IP:** All code is proprietary to Trinity Global Partners LLC
- **NCNDA:** Development governed by signed non-compete non-disclosure agreement
- **Last Verified:** 2026-04-09 — all counts cross-validated against filesystem

---

## See Also

- **[README.md](./README.md)** — Quick start and overview
- **[docs/INDEX.md](./docs/INDEX.md)** — Documentation master index
- **[agents/REGISTRY.md](./agents/REGISTRY.md)** — Complete agent listing
- **[engines/INDEX.md](./engines/INDEX.md)** — Engine system documentation
- **[knowledge-base/INDEX.md](./knowledge-base/INDEX.md)** — Knowledge base index

---

**Trinity Unified AI**  
**Last Updated:** 2026-04-09  
**IP Owner:** Trinity Global Partners LLC (Enzo Garoche / EGD33)
