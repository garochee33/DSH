# TRINITY UNIFIED AI
## Sovereign Intelligence Layer | Knowledge Base | Multi-Agent Hub

> **Path:** `~/trinity-unified-ai/`
> **Updated:** 2026-04-09 (live-verified 19:12 UTC-4)
> **Mode:** FULL_MERKABA + GOD_MODE (10/10 protocols, score 100)
> **Database:** Local PostgreSQL (sovereign mode -- no Supabase dependency)
> **Package Manager:** pnpm

---

## Quick Start

```bash
# Authorized local machine only
touch ~/.trinity-sync-authorized

# Boot the full stack
bash ~/trinity-unified-ai/sync/boot.sh

# Or manually:
# Terminal 1 -- KB API (port 3333)
cd ~/trinity-unified-ai/api && pnpm start

# Terminal 2 -- Command Center UI (port 4444)
cd ~/trinity-unified-ai/command-center && npm run dev

# Required services
ollama serve                      # LLM inference (11434)
brew services start postgresql@17 # Local PG (5432)
brew services start redis         # Stigmergic engine (6379)
brew services start neo4j         # Knowledge graph (7474/7687)
```

---

## Bootstrap Access

Bootstrap and sync automation are restricted to owner-authorized local machines. Public clone, remote install, and third-party onboarding are revoked.

```bash
# Authorized local setup only
touch ~/.trinity-sync-authorized
bash spore.sh
```

---

## Verified Counts (2026-04-09)

| Asset | Count | Source |
|-------|-------|--------|
| Agents | 36 | `agents/per-agent/*.md` |
| Engine directories | 32 | `engines/*/` |
| Engine TypeScript files | 1,075 | `engines/**/*.ts` |
| Knowledge Base docs | 10,918 | `/api/stats` (live DB — verified 2026-04-09) |
| Knowledge Base markdown | 1,782 | `knowledge-base/**/*.md` |
| Skills (SKILL.md files) | 38 | `skills/**/SKILL.md` |
| Tool TypeScript files | 83 | `tools/**/*.ts` |
| Agent tool files | 43 | `tools/agent-tools/*.ts` |
| God Mode protocols | 10 | `/api/protocols/god-mode` |
| Ollama models loaded | 4 | devstral:latest, qwen2.5-coder:14b, qwen3.5:9b, nomic-embed-text:latest |

---

## Repo Structure

```
agents/          -- 36 agent specs (per-agent/*.md + registry + swarm-config)
api/             -- Express KB API (port 3333) + MCP server + ingest pipeline
command-center/  -- Next.js local UI (port 4444)
database/        -- Schema definitions (trinity-schema, womb-schema, shared)
engines/         -- 32 engine directories, 1,075 TS files (32 subdirs verified 2026-04-09)
  compute/       -- Python Clifford/QMC + Julia BLAS + TS bridge
  holographic/   -- 256-bit bitboard + 8D Voronoi + Poincare-E8
  stigmergic/    -- 240-node pheromone grid + CRDT merge
  bitboard/      -- E8 lattice, BigInt masks, L1-cache optimized
  sacred-geometry/ -- Metatron, Fourier, Fractal, Toroidal, etc.
  consensus/     -- PBFT, Gossip, CRDT engines
  swarm/         -- Orchestrator, fractal swarm
  memory/        -- Holographic Merkle memory + E8 bridge
  + 24 more...
knowledge-base/  -- 1,782 markdown docs (canonical KB, all frontmattered) | 10,918 indexed in DB
libraries/       -- Protocol docs (SG math, consensus, memory, TS patterns)
live-projects/   -- Reference summaries for consortium + womb
memory/          -- Session logs, TODO, master index, engine status
models/          -- Model registry + routing rules + cost comparison
projects/        -- 15 sub-projects (tax-god, sacred-geometry, n8n, etc.)
prompts/         -- Agent prompts, handoffs, templates
scripts/         -- Utility scripts
skills/          -- 38 skill modules (SKILL.md files verified 2026-04-09)
sources/         -- Research papers, external sources
standards/       -- Coding standards, engine health standard, ref schema
sync/            -- Sync scripts, ref generator, GEMS harvest
tools/           -- MCP server config, agent tools, model routing
utils/           -- Shared utilities
```

---

## Key API Endpoints (port 3333)

All routes require `x-hub-secret` header.

```
Health:       GET  /health
Search:       GET  /api/search?q=...&limit=5
Stats:        GET  /api/stats
Agents:       GET  /api/agents/list          POST /api/agents/execute
Engines:      GET  /api/engines              GET  /api/engines/topology
E8 Compute:   POST /api/e8-compute/qmc       GET  /api/e8-compute/status
Holographic:  POST /api/holographic/snapshot  GET  /api/holographic/status
Stigmergic:   POST /api/stigmergic/deposit   GET  /api/stigmergic/colony
Protocols:    GET  /api/protocols/god-mode
Orchestrate:  POST /api/orchestrate          GET  /api/orchestrate/status
Memory:       GET  /api/memory/status
Telemetry:    POST /api/telemetry            GET  /api/telemetry/recent
```

---

## Sovereign Mode (Local PostgreSQL)

The hub runs on local PostgreSQL -- no Supabase dependency. All data stays on-machine.

```
Database:  postgresql://localhost:5432/trinity
ORM:       postgres (via postgres npm package)
Shim:      db.ts re-exports pool from api/src/clients.js
Config:    config.ts provides env shims for engine imports
```

---

## 8-Entity Ecosystem

| Entity | Domain | Role |
|--------|--------|------|
| AKIOR | akior.com | Parent holding entity |
| Trinity Consortium | trinityconsortium.com | Sovereign AI platform + portal |
| E8-SSII | -- | Sacred geometry compute layer |
| Mesh | -- | Decentralized infrastructure network |
| The Womb | -- | Full-stack AI platform (monorepo) |
| Kommunity | kommunity.life | Decentralized DAO, dual-token (LIFE+HUB) |
| LaRive | -- | Real estate / hospitality vertical |
| A&I (Arts & Innovation) | -- | Creative + cultural vertical |

---

## Swarm Scripts

```bash
bash ~/trinity-unified-ai/sync/gems-harvest.sh       # Scan live repos for new assets
bash ~/trinity-unified-ai/sync/hub-remediation.sh     # AMMA + CTO-Auditor + Oracle
```

---

## Key Rules

- **Never modify** live repos (`~/projects/trinity-consortium`, `~/projects/the-womb/the-womb`)
- **Never delete** -- archive only after line-by-line diff
- **Never commit** `.env` files
- GitHub: `garochee33/trinity-unified-ai` (PRIVATE)
- API + UI bound to `127.0.0.1` only
