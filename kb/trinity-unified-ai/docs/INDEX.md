# Trinity Unified AI — Documentation Index

> Last updated: 2026-04-16  
> KB API: port 3333 | Runtime: tsx (TypeScript ESM, no compiled dist)  
> IP Owner: Trinity Global Partners LLC (Enzo Garoche / EGD33)  
> Live verified: 36 agents, 32 engine directories, 10,918 KB documents  
> **2026-04-16 Alchemist Battle:** `phi-recall.ts` created, `agent-kernel.ts` patched, `POST /api/memory/phi-recall` added, alchemist agent registered

---

## Quick Navigation

| Category | Path | Description |
|----------|------|-------------|
| **API Reference** | [../api/](../api/) | KB API server (port 3333), routes, authentication, orchestration |
| **Knowledge Base** | [../knowledge-base/](../knowledge-base/) | 10,918 indexed documents, 1,782 markdown files, vector search, embeddings |
| **Engines** | [../engines/](../engines/) | 32 engine directories, 1,075 TypeScript files — sacred geometry, compute, consensus |
| **Agents** | [../agents/](../agents/) | 36 agent specs, AMMA system, Monica, God mode, sovereign agents, swarm config |
| **Skills** | [../skills/](../skills/) | 38 skill modules (SKILL.md files) — cto-build, reporting, sacred-geometry, womb-3d |
| **Models** | [../models/](../models/) | Model registry, routing rules, cost comparison |
| **Memory** | [../memory/](../memory/) | Session logs, execution tracking, master index, engine status |
| **Tools** | [../tools/](../tools/) | MCP server config, 43 agent tool files, model routing |
| **Projects** | [../projects/](../projects/) | 15 sub-projects, reference implementations |
| **Standards** | [../standards/](../standards/) | Coding standards, engine health standard, schema reference |
| **Scripts** | [../scripts/](../scripts/) | Utility and automation scripts |
| **Reports** | [../reports/](../reports/) | Audit reports, performance benchmarks, security assessments |

---

## Architecture Documentation

### Foundational Maps & Specs

- **[AI_INFRASTRUCTURE_MAP.md](./AI_INFRASTRUCTURE_MAP.md)** — Complete system architecture, 55+ agents, 432 tools, 170 skills, consensus protocols
- **[TRINITY_CONSORTIUM_SYSTEM_OVERVIEW.md](./TRINITY_CONSORTIUM_SYSTEM_OVERVIEW.md)** — System-wide architecture overview
- **[TRINITY_CONSORTIUM_INFRASTRUCTURE_v3.md](./TRINITY_CONSORTIUM_TRINITY_UNIFIED_AI_INFRASTRUCTURE_v3.md)** — Detailed infrastructure specification
- **[LOCAL_ARCHITECTURE.md](../knowledge-base/LOCAL_ARCHITECTURE.md)** — Local deployment architecture
- **[TECH_STACK_SPEC_2026-04-07.md](../knowledge-base/TECH_STACK_SPEC_2026-04-07.md)** — Complete technology stack specification

### Planning & Migration

- **[REPO_REWORK_PLAN.md](./REPO_REWORK_PLAN.md)** — Repository reorganization strategy
- **[REPO_PLAN.md](./REPO_PLAN.md)** — Directory structure and module planning
- **[FULL_REPO_TREE.md](./FULL_REPO_TREE.md)** — Complete verified repository tree
- **[HARMONY_E2E_PLAN.md](./HARMONY_E2E_PLAN.md)** — End-to-end integration plan
- **[TRINITY_WOMB_UPGRADE_PLAN.md](../knowledge-base/TRINITY_WOMB_UPGRADE_PLAN.md)** — Womb integration roadmap

### Engineering & Implementation

- **[COMMAND_REFERENCE.md](./COMMAND_REFERENCE.md)** — Complete command and API reference
- **[ADR-001-unified-task-router.md](./ADR-001-unified-task-router.md)** — Architecture Decision Record: Task routing
- **[UPGRADES.md](./UPGRADES.md)** — System upgrade documentation
- **Internal onboarding** — restricted to owner-controlled distribution, not stored in the public doc index

### Status & Reporting

- **[HUB_SYNC_STATUS.md](../knowledge-base/HUB_SYNC_STATUS.md)** — Current sync and health status
- **[SYSTEM_STATUS.md](../knowledge-base/SYSTEM_STATUS.md)** — Overall system operational status
- **[SESSION_LOG_2026-04-07.md](../knowledge-base/SESSION_LOG_2026-04-07.md)** — Latest session execution log

---

## Knowledge Base Structure

The Knowledge Base (`knowledge-base/`) contains 1,782 markdown files organized into 18 core categories:

### Knowledge Categories

| Category | Path | Purpose |
|----------|------|---------|
| **AI Knowledge Content** | `ai-knowledge-content/` | Core AI/ML algorithms, patterns, frameworks |
| **Architecture** | `architecture/` | System design, micro-services, integration patterns |
| **Infrastructure** | `infra/` | DevOps, deployment, monitoring, observability |
| **Research** | `research/` | Academic papers, external sources, references |
| **Standards** | `standards/` | Governance, compliance, quality standards |
| **Sacred Geometry** | `sacred-geometry/` | E8 lattice, Metatron cube, Flower of Life, harmonic math |
| **AI Inventory** | `ai-inventory/` | Asset catalogs, tool registries, capability lists |
| **CTO Framework** | `cto-framework/` | Technical strategy, architectural decisions, frameworks |
| **Code Review** | `code-review/` | Code standards, review patterns, best practices |
| **Masterclass** | `masterclass/` | Educational content, tutorials, deep dives |
| **Integrations** | `integrations/` | Third-party service integration guides |
| **Projects** | `projects/` | Project-specific documentation |
| **Womb** | `womb/` | The Womb integration, licensing, partnerships |
| **Trinity Consortium** | `trinity-consortium-docs/` | Consortium-specific documentation |
| **Vendor** | `vendor/` | External vendor documentation |
| **And 3 more...** | — | See full index at `knowledge-base/INDEX.md` |

**Total: 1,782 markdown files | 10,918 indexed documents in database**

---

## Engine System

The Engines (`engines/`) contains 32 specialized directories covering sacred geometry, compute, and AI infrastructure:

### Engine Categories (32 total)

- **sacred-geometry** — Core harmonic mathematics (Metatron, Fourier, Fractal, Toroidal, Platonic solids)
- **compute** — Python Clifford algebra, Julia BLAS, TypeScript bridge
- **holographic** — 256-bit bitboard, 8D Voronoi, Poincaré-E8 lattice projection
- **stigmergic** — 240-node pheromone grid, CRDT merge protocols
- **bitboard** — E8 lattice, BigInt masks, L1-cache optimization
- **consensus** — PBFT, Gossip, CRDT engines
- **swarm** — Orchestration, fractal swarm coordination
- **memory** — Holographic Merkle memory, E8 bridge
- **phi-recall** — `engines/phi-recall.ts` — φ-weighted memory recall across fractal fabric (added 2026-04-16) ← NEW
- **core** — Foundational AI core systems
- **crew** — Multi-agent crew coordination
- **agent-router** — Agent request routing
- **ai-filesystem** — Knowledge base filesystem abstraction
- **auth** — Authentication & authorization
- **middleware** — API and request middleware
- **nexus-core** — Core networking hub
- **observability** — Monitoring and tracing
- **womb-ai-core** — Womb integration core
- **trinity-agent-system** — Trinity agent orchestration
- **And 14 more specialized engines...**

**Total: 32 engine directories | 1,075 TypeScript files | ~62 engines**

See detailed specs at `engines/INDEX.md` and `engines/README.md`

---

## Agent System

The Agents (`agents/`) contains specifications for 36 sovereign agents organized in multiple subsystems:

### Agent Subsystems

- **per-agent/** — Individual agent specifications (36 files)
- **amma/** — AMMA agent system (Advanced Multi-Modal Architecture)
- **god/** — God mode agent protocols (10/10 protocols live)
- **monica/** — Monica specialized agent
- **sovereign/** — Sovereign agent constellation
- **v2/** — Second-generation agent framework
- **prompts/** — Agent prompts and templates

### Agent Registries & Config

- **AGENTS.md** — Master agent registry
- **REGISTRY.md** — Detailed agent capabilities registry
- **agent-definitions.ts** — TypeScript agent definitions
- **agent-profiles.ts** — Agent profiles and metadata
- **agent-capabilities.ts** — Capability matrix
- **a2a-interop.ts** — Agent-to-agent interoperability
- **swarm-config.toml** — Swarm coordination configuration

See `agents/REGISTRY.md` for full agent listing with titles, capabilities, and cost metrics.

---

## Skills System

The Skills (`skills/`) contains 38 skill modules organized by function:

- **cto-build** — CTO framework and architectural skills
- **god-mode** — God mode protocol skills
- **reporting** — Analytics and reporting skills
- **sacred-geometry** — Sacred geometry computation skills
- **sacred-geometry-agents** — Agent-specific geometry skills
- **trinity-repo-navigator** — Repository navigation
- **unified-ai-audit** — Audit and health checks
- **github** — GitHub integration
- **integrations** — Third-party service skills
- **kimi** — Kimi Code CLI skills
- **utility** — Utility and helper skills
- **womb-3d** — 3D visualization for Womb
- **womb-3d-sacred-geometry** — 3D sacred geometry
- **use-railway** — Railway deployment skills
- **And 23 more skill modules...**

Each skill is defined as a SKILL.md file. See `skills/INDEX.md` for complete registry.

---

## Model System

The Models (`models/`) provides LLM and model routing:

- **MODEL_REGISTRY.md** — Complete model availability and specs
- **routing-rules.md** — Model selection algorithms and routing logic
- **cost-comparison.md** — Cost analysis and comparison

---

## Quick References

### Essential Commands

```bash
# Boot the full stack
bash sync/boot.sh

# Start KB API (port 3333)
cd api && pnpm start

# Start Command Center UI (port 4444)
cd command-center && npm run dev

# View live API stats
curl http://localhost:3333/api/stats
```

### Key Files by Role

**For Developers:**
- `COMMAND_REFERENCE.md` — All commands and APIs
- `engines/INDEX.md` — Engine documentation
- `engines/phi-recall.ts` — φ-weighted memory recall (added 2026-04-16)
- `api/routes/memory.routes.ts` — `POST /api/memory/phi-recall` endpoint (added 2026-04-16)
- `standards/` — Coding standards

**For Architects:**
- `AI_INFRASTRUCTURE_MAP.md` — System overview
- `knowledge-base/LOCAL_ARCHITECTURE.md` — Deployment architecture
- `knowledge-base/TECH_STACK_SPEC_2026-04-07.md` — Full tech stack

**For Project Managers:**
- `agents/REGISTRY.md` — Agent capabilities
- `projects/` — Sub-project documentation
- `memory/` — Status and logs

---

## See Also

- **[README.md](../README.md)** — Repository overview and quick start
- **[knowledge-base/INDEX.md](../knowledge-base/INDEX.md)** — Knowledge base master index
- **[agents/REGISTRY.md](../agents/REGISTRY.md)** — Complete agent registry
- **[engines/INDEX.md](../engines/INDEX.md)** — Engine system documentation
- **[skills/INDEX.md](../skills/INDEX.md)** — Skills catalog

---

**Repository:** Trinity Unified AI  
**Updated:** 2026-04-09  
**Verified:** All counts cross-validated against filesystem  
**IP:** Trinity Global Partners LLC (Enzo Garoche / EGD33)
