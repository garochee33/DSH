# Trinity Three-Platform Doctrine

**Status:** v1.0 — established 2026-05-19
**Authority:** $OPERATOR (Enzo Garoche) · sole [admin-tier]
**Supersedes:** the implicit "all-in-one" model previously assumed
**Scope:** governs every working session across the three canonical Trinity platforms
**Read order at boot:** `~/.claude/CLAUDE.md` → this file → per-repo CLAUDE.md/AGENTS.md

---

## 0. Why this doc exists

Three production-shape codebases coexist on this sovereign node — and previously had no written division of labor. The result was duplicated capabilities (e.g. `~/DOME-HUB/skills/` shadowing `trinity-unified-ai/skills-library/`), unclear ownership of cross-cutting concerns (auth, KB ingest, mesh telemetry), and multi-agent stomping when terminals didn't know which platform owned what. This doctrine fixes that. **Every agent that touches any of these three repos must respect these boundaries.**

---

## 1. The three platforms — one-line identity

| Platform | Identity | Default port | Deploy target |
|---|---|---|---|
| **trinity-consortium** | Production + multi-tenant ops + project hub + command center | `:5055` local, `:443` prod | [cloud-provider] at `[production-domain]` |
| **trinity-unified-ai** | Intelligence backbone — KB API, 461-skill canon, agent swarm, KB ingest | `:3333` local | Local-first; future federation possible |
| **DOME-HUB** + **dome-console** | Sovereign local machine control center + local hub GUI | `:4747` (dome-console) | Localhost-only on this M5 Pro (48 GB, 40+ TOPS NE) |

**Mental model:** consortium is the *body* (lives in production, serves the public). TU-AI is the *mind* (knowledge + intelligence, callable by any platform). DOME-HUB is the *home* (the sovereign machine where the operator lives, where local-only concerns are owned).

---

## 2. trinity-consortium — Production hub + command center

**Repo:** `projects/trinity-consortium`
**Remote:** `[private-repo]` (private)
**Stack:** Express + Drizzle ORM + tsx@4.22 on Node 24 · Next.js 16 + React 19 + Tailwind v4 frontend · PostgreSQL + pgvector (177 tables) · Redis · Docker Compose · Caddy
**Production:** [cloud-provider], served from `[production-domain]` (Cloudflare Full SSL, Origin certs)
**Local dev:** `pnpm dev` from repo root → server at `127.0.0.1:5055`

### 2.1 What consortium uniquely owns (canonical — never duplicate elsewhere)

**Production identity & multi-tenancy:**
- Auth + JWT issuance + tier verification (`server/auth/middleware.ts`, `auth.service.ts`, `tier-constants.ts`)
- Member tier ladder L1/L2/L3 (CONFIDENTIAL/RESTRICTED/CLASSIFIED) + Admin tier ladder A1/A2/A3/A4 (TEAM/INVESTOR/PARTNER/DEV-OWNER)
- Founder gate (`FOUNDER_USERNAME = '$OPERATOR'`, single A4) at `server/domains/auth/auth.service.ts:38-50`
- Workspace + ACL multi-tenancy (`enforceTenantOnScopedRoutes`)
- Stripe webhook handling + billing events + idempotency via Redis pub/sub
- Member onboarding grants ($20–$30 per tier; A4 unlimited)

**Public/multi-tenant compute:**
- AMMA production self-heal (`server/domains/ai/amma.routes.ts`, `ai/amma-self-heal.ts`, `ai/amma-system-metrics.ts`)
- Bees + Hive orchestrator with integrity guard (any edit under `server/ai/bees/` requires `BEE_INTEGRITY_BOOTSTRAPPED_BY=$OPERATOR pnpm exec tsx scripts/trinity-bees-integrity-bootstrap.ts` to re-authorize)
- Mandelbulb GPU dispatcher + sacred geometry engines (E8 lattice, Metatron, Merkaba, Flower of Life, φ-scaling)
- Production sub-domain stack: 69 route domains, ~400–500 endpoints across ai/auth/vault/admin/womb/knowledge/compute/enterprise

**Production-only routes never to be mirrored in dome-console:**
- `/api/auth/*` — login, signup, tier verification, JWT refresh
- `/api/settings/*` — env config (A4-only write)
- `/api/cost/*`, `/api/spend/*`, `/api/tiers/*` — billing & cost governance
- `/api/admin/members`, `/api/admin/workspaces`, `/api/admin/acl/*`
- Anything requiring `requireAdminTier(3+)`

**Projects served by the platform (live under consortium's umbrella):**
- s3xyverse (Druya's project, Trinity-hosted; deployed to dedicated Hetzner at `s3xyverse.com`)
- Paradise-Estate-Mykonos (client project)
- Any future commercial property the platform serves

### 2.2 Things consortium currently owns that should be reconsidered

**Dev-tools domain** (`server/domains/dev-tools/dev-tools.routes.ts`):
- `/api/dev/fs/*`, `/api/dev/git/*`, `/api/dev/github/*`, `/api/dev/shell/*`
- These are *local-workspace tooling*, not production concerns. They power the Trinity Dev-Portal but fundamentally belong on a sovereign node.
- **Recommendation:** keep the API on consortium (it's deployed, multi-user), but dome-console *consumes* these via HTTP with workspace scoping, doesn't reimplement them.
- **DOME-HUB-local alternative:** dome-console can also expose its own thin shell of these capabilities for *its own machine* (no remote workspace dimension).

**`compute/crypto/`** (post-quantum: ML-KEM-1024, ML-DSA-87): currently only used by `agents/skills/pqc_mesh_auth.py` in DOME-HUB. Candidate for promotion to a shared lib in trinity-unified-ai (so all nodes use the same primitives).

**`agents/core/trinity_client.py`** (HTTP bridge from DOME-HUB → consortium mesh): candidate for promotion to a published SDK (`@trinity-consortium/mesh-client`) so any node — not just DOME-HUB — can join the mesh with one import.

### 2.3 Anti-patterns (do not do these on consortium)

- ❌ Adding local-only sovereign hardening controls to consortium routes (firewall toggles, FileVault state) — that's DOME-HUB territory.
- ❌ Hosting skill definitions or KB ingest in consortium — those live in TU-AI.
- ❌ Adding `localhost`-only diagnostic endpoints — they don't make sense in production.
- ❌ Editing files under `server/ai/bees/` without re-running the integrity bootstrap.
- ❌ Mixing dome-console code into consortium (kept as separate inner repo).

---

## 3. trinity-unified-ai — Intelligence backbone

**Repo:** `trinity-unified-ai` (canonical path)
**Stack:** Express.js (KB API) + PostgreSQL + pgvector + Ollama (local, 11434) + Redis + Neo4j (graph)
**HTTP surface:** Express KB API on `:3333` (local), auth via dual-mode JWT (from consortium) + `x-hub-secret` header
**Routes:** ~1,439 across skill invoke, search, agent list/execute, E8 compute, holographic/stigmergic state, stats, protocols, orchestration, memory, telemetry

### 3.1 What TU-AI uniquely owns (canonical — single source of truth)

**The 461-skill canonical library** (`skills-library/skills/`):
- 461 versioned skills with `skill.yaml` manifests conforming to `trinity.skill.schema.json`
- 31 categories (agent-meta 154, backend 68, deployment 48, ai-ml 40, bioinformatics 37, …)
- Quality: 98% strong (9 A-tier, 38 B-tier, avg 72.6)
- **Master index:** `skills-library/MASTER_INDEX.md` + `skills.index.json` (machine-readable)
- **All agent runtimes symlink here:** `~/.kiro/skills`, `~/.claude/skills`, `~/.codex/skills`, `~/.cursor/skills` all point back to TU-AI's `skills-library/skills/`. This is the *only* canonical location.

**The skill-recall hook:**
- Source: `skills-library/hooks/skill-recall.sh`
- Triggered by `UserPromptSubmit` in every CLI agent
- Reads `skills.index.json`, matches trigger phrases + skill names, surfaces top-8 skills per prompt
- **No agent reimplements skill matching.** Either call the hook or call TU-AI's `/api/skills/search?q=...` endpoint.

**KB ingest pipeline** (`api/src/ingest.ts`):
- Globs markdown + SKILL.md + agent specs + standards + engine docs (lines 14-24 in ingest.ts)
- Chunks via semantic splits on `## `, embeds via `nomic-embed-text` (768-dim)
- Stores in PostgreSQL pgvector
- **Current corpus:** 10,918 indexed docs (verified 2026-04-09)

**Agent constellation** (`agents/per-agent/`):
- 36 sovereign agent specs (Oracle/CDIO, Engineer/CTO, Architect, Monica, AMMA core, God Mode 13/13)
- Agent-to-agent interop (`agents/a2a-interop.ts`)
- Swarm orchestration config (`agents/swarm-config.toml`)
- These definitions are canonical; consortium and DOME-HUB reference them, never redefine.

**Mathematical substrate** (`engines/`, 32 directories, 1,075 TS files):
- Sacred geometry: Metatron, Fourier Lens, Flower of Life, Toroidal
- Compute: Clifford algebra, QMC, Julia bridge
- Holographic: 256-bit bitboard, 8D Voronoi, Poincaré-E8
- Consensus: PBFT, Gossip, CRDT
- Swarm: Orchestrator, fractal-swarm
- Memory: Holographic Merkle + E8 bridge

### 3.2 Public API surface (call these from consortium / dome-console)

| Endpoint | Purpose | Auth |
|---|---|---|
| `GET /health` | Liveness | none |
| `GET /api/search?q=<query>&limit=N` | General KB search | x-hub-secret |
| `GET /api/skills/search?q=<query>` | Semantic skill search | x-hub-secret |
| `POST /api/skills/invoke` | Execute named skill | x-hub-secret + JWT |
| `GET /api/agents/list` | List agents | x-hub-secret |
| `POST /api/agents/execute` | Submit task to swarm | x-hub-secret + JWT |
| `GET /api/stats` | Doc count, engine status | x-hub-secret |
| `GET /api/memory/status` | Recall state, sessions | x-hub-secret |
| `GET /api/protocols/god-mode` | List active 13 God-Mode protocols | x-hub-secret |
| `GET /api/e8-compute/qmc` | E8 quantum Monte Carlo | x-hub-secret |
| `GET /api/holographic/snapshot` | Current holographic memory state | x-hub-secret |
| `POST /api/stigmergic/deposit` | Deposit pheromone trace | x-hub-secret |

### 3.3 Anti-patterns (do not do these on TU-AI)

- ❌ Hosting auth, billing, or tenant management — that's consortium.
- ❌ Holding personal/PII data — TU-AI is a knowledge backbone, not a CRM.
- ❌ Local-machine controls (launchd, FileVault, firewall) — that's DOME-HUB.
- ❌ Storing skill definitions outside `skills-library/skills/` — anything in `skills/` (note: trailing `s/`, not `-library/`) is **deprecated** per REPOSITORY_MAP.md:L190-221.
- ❌ Direct writes to ChromaDB/pgvector by external callers — must go through `api/src/ingest.ts`.

---

## 4. DOME-HUB — Sovereign local machine + dome-console GUI

**Repo:** `~/DOME-HUB` (private, `[private-repo]`)
**Identity:** This M5 Pro (48 GB, 40+ TOPS NE) is one sovereign node in the Trinity mesh. DOME-HUB is portable to any Apple Silicon machine.
**Inner repos** (excluded from outer `.gitignore` via `/home/`):
- `projects/dome-console` (the GUI, `[private-repo]`, private)
- `projects/trinity-consortium` (production platform)
- `DSH` (the public sovereign foundation, `garochee33/DSH`)
- `trinity-unified-ai` (TU-AI canonical location)

### 4.1 What DOME-HUB uniquely owns (canonical — never duplicate elsewhere)

**Local-machine control (only this node knows the answer):**
- launchd plists in `~/Library/LaunchAgents/com.{dome,trinity,akashic}.*` — currently 4 active:
  - `com.dome.whispercpp.8082` (Whisper.cpp ASR server, PID running ~95h)
  - `com.dome.akashic-watcher` (filesystem → ChromaDB ingester)
  - `com.dome.mycelium-signal` (mesh peer heartbeat)
  - `com.trinity.consortium.server` (the production server *also runs locally* for dev)
- Local services: Ollama (`:11434`), MLX bridge (`:8101`, configured but not currently running), PostgreSQL (`:5432`), Redis (`:6379`), MariaDB (`:3306`/`:33306`), Neo4j (`:7474`/`:7687`), FastAPI agents (`:8001`)
- Local sovereign hardening: FileVault, SIP, Gatekeeper, firewall, dnscrypt-proxy, GPG, pass, Keychain
- Disk / filesystem health, archive tiers (Dual-Archive Protocol: Hot=local+iCloud, Cold=iCloud-only)
- Cross-agent runtime state: `~/.claude/projects/`, `~/.codex/`, `~/.kiro/sessions/`, `~/.cursor/projects/`

**The agent runners + local intelligence:**
- 7 runner adapters under `agents/` — claude, codex, cursor, kiro, kimi, trinity (HTTP bridge), local (Ollama/MLX direct)
- 15-agent registry (`agents/core/registry.py`) — researcher, coder, analyst, planner, kb_agent, local, security, devops, creative, mesh, akashic, healer, monitor, concierge, orchestrator
- 13 skill-agents under `agents/skills/` — algorithms, cognitive, compute, fractals, frequency, math, sacred_geometry, plus 2026-05 additions: neuromorphic_sync, stigmergic_routing, pqc_mesh_auth
- Voice pipeline (`agents/voice/`): VAD → ASR → TTS, Whisper.cpp + Apple NE
- API layer (`agents/api/`): WebSocket server with HMAC-SHA256 token auth

**Local compute layer (this machine's specific physics):**
- `compute/sim_evolved.py` — Kuramoto 3D + MPS FFT (26-neighbor Moore topology, K=2.663)
- `compute/sim_3x3x3.py` — baseline lattice
- `compute/amma_monitor.py` — local AMMA quad-sensor coherence → golden-needle / mitosis recovery
- `compute/quantum_dome/` — Apple MPS profiler + scheduler (4 GB RAM budget)
- `compute/resonance_layer.py` — 7 paradigm upgrades (persistent homology, optical phase, dimensional folding, Fourier lens zoom, cymatics routing, quantum resonance addressing, alchemy codex)
- `compute/crypto/` — ML-KEM-1024 / ML-DSA-87 (NIST FIPS 203/204) — *candidate for promotion to TU-AI shared lib*

**Local memory layer:**
- `db/dome.db` — SQLite registry: sessions, traces, agents, skills, tools, stack inventory, contacts ([N] — owned by dome-console CRM)
- `db/episodic.db` — episodic memory (currently 0 episodes, 0 sessions, 17 facts — placeholder for episodic engine)
- `db/chroma/` — Akashic ChromaDB (~50 MB, 7 collections, 267+ documents)
- `db/.akashic-seen.json` — watcher dedup (now properly gitignored as of 2026-05-19 commit chain)
- `~/.trinity-spore/mempalace.db` — E8-indexed memory palace (Trinity mesh state)
- `~/.trinity-spore/` (entire dir, ~594 MB) — peer identity, handshake, lattice binding, mesh logs
- `memory/sessions/2026-*/` — 79 consolidated session narratives (executive summaries)
- `memory/facts/`, `memory/decisions/` — fact base + decision journal
- `brain/` (added 2026-05-19, commit `98c8f98`) — *reference layer*, not duplicate storage. `engines/*.ref` are 17 text pointers to actual engines in trinity-unified-ai. `state/dome.ref` points at `db/dome.db`. Catalog, not copy.
- `~/.claude/projects/-Users-<user>/memory/` — Claude auto-memory (separate from `memory/` by design; raw turn-by-turn vs. executive narratives)

**Local KB layer (NOT canonical — defers to TU-AI):**
- `kb/skills/` — *local subset* (264 files, 67 unique). For local-only references. **Canonical skill source is TU-AI's `skills-library/skills/`** (461 skills).
- `kb/trinity-unified-ai/` — landing zone for Trinity seed deposit
- `kb/claude/`, `kb/developer-context.md`, `kb/language-landscape-2026.md`

**The Mycelium mesh signal (this node's link to Trinity):**
- `~/DOME-HUB/scripts/mycelium-signal.sh` — production-grade signal with HMAC-SHA256 auth, retry/backoff, rate-limit awareness, log rotation
- Heartbeat cadences: 60s compute, 120s mesh peer, 300s memory sync
- launchd-managed via `~/Library/LaunchAgents/com.dome.mycelium-signal.plist`
- Frequency pulse formula (geometric, post-2026-05-12): `node_hz = 432 × φ^((root_index % 8) / 8)`
- **Current node identity** (verified 2026-05-19 from `~/.trinity-spore/config.json` + `mesh/peer-id.txt`):
  - peerId: `node:dsh-cb821cf4f461`
  - E8 root: **33** (NOT 84 — peer identity changed since 2026-04-26 spore re-bootstrap; older memory was stale)
  - Resonance: **465.37 Hz** (= 432 × φ^(33/8/8); NOT 549.51 Hz — that was for root 84)
  - Active roots: 240 (full lattice coverage)
  - Tier: sovereign
  - **Note:** lattice-binding.txt is currently missing — E2EE binding not yet completed at this peer identity. 401 errors observed in mycelium-signal.log between 05:33–14:37 today (2026-05-19) indicate either HUB_API_SECRET mismatch or server-side peer registration drift. Heartbeats post-14:37 are succeeding.

**Sovereign hardening (script-level enforcement):**
- `scripts/audit.sh` — verification: FileVault, SIP, Gatekeeper, firewall, SMB, screen lock, FV key on standby, IR receiver, Siri, Spotlight web, AirPlay receiver, crash reporter, Chrome privacy, Terminal secure keyboard
- `scripts/harden.sh` — enforcement of all the above
- `scripts/lock-down.sh` (+ phase 2/3/4 variants) — incremental lockdown
- `scripts/sovereign-secrets.sh`, `rotate-secrets-keychain.sh`, `secrets-doctor.sh` — Keychain + GPG secret lifecycle
- `~/.password-store/` — pass + GPG (fingerprint `2041FECCC6929FBA27D61DB93549CD92A76B79A8`)

**Protocol & governance scripts (DOME-HUB-only authority):**
- `scripts/dome-check.sh` — protocol enforcer (firewall, FileVault, git, imports, TS, DB integrity)
- `scripts/dome-pm.sh` — project manager (new, list, status, push-all, pull-all, publish, env)
- `scripts/dome-approve.sh`, `dome-sudo.sh` — approval gates for privileged actions
- `scripts/daemon-watch.sh` — authorized daemon inventory tracker

**Structural / observability:**
- `.fractalmap/` — gitignored (local-only, hook-refreshed); per-repo L0/L1/L2 tier maps + manifest.json (SHA-256 Merkle root)
- `scripts/fractalmap-generate.sh` — tiered repo map generator
- `scripts/sync-holographic-metrics.py` — syncs into `logs/HOLOGRAPHIC_FRACTAL_TREE_MAP_2026-05-14.md`
- `scripts/update-tree-map.sh` — post-commit hook that runs fractalmap regen + holographic sync
- `scripts/frequency-pulse.py` — E8 harmonic pulse (PQC-signed)

### 4.2 dome-console — the local GUI surface

**Repo:** `projects/dome-console` (private inner repo)
**Stack:** Next.js 16.2.6 + React 19.2.4 + TypeScript 5 + Tailwind v4 + shadcn/ui (Base UI) + Sonner (toast) + Recharts + `@tanstack/react-virtual` + `better-sqlite3` + Zod
**Data:** raw SQL on shared `~/DOME-HUB/db/dome.db` (no ORM, parameterized queries)
**Binding:** `127.0.0.1:3737` — no auth (sovereign by isolation)
**Current live surfaces:**
- `/` System Dashboard (CPU, RAM, disk, DB sizes, agent counts, Ollama, contacts, 24h load chart, 5s refresh)
- `/crm` Contact list ([N] contacts, virtualized, search by name/phone/email, tag/note badges)
- `/crm/[id]` Contact detail (tags, notes, 6-type interaction logging)
- `/api/metrics` (GET) — system metrics endpoint
- Server actions for CRM mutations (addTag, removeTag, addNote, deleteNote, logInteraction)

**Disabled stubs in sidebar (`app-sidebar.tsx`):**
`/agents`, `/knowledge`, `/database`, `/models`, `/mesh`, `/logs`

**Extensibility:** 6/10 — clear data/component/route layering, reusable primitives (`MetricTile`, virtualized list), server-actions pattern, easy to add new tables to `lib/db.ts:ensureSchema()`. Each tab still requires bespoke wiring.

**Existing primitives reusable for expansion:**
- `MetricTile` — sparkline + value + hint (use for agent runner status, model memory, mesh latency)
- `useVirtualizer` pattern — apply to any large 1D list (repo grid, signal log tail)
- Server-action shape — Zod validate → DB mutate → `revalidatePath` → Sonner toast

---

## 5. Division-of-labor matrix

Use this when deciding where to put a new capability.

| Capability | Owned by | Notes |
|---|---|---|
| Auth, JWT, sessions | **consortium** | Single source of truth for identity |
| Billing, Stripe, cost governance | **consortium** | Production-only |
| Member/admin tier ladder + $OPERATOR enforcement | **consortium** | `tier-constants.ts` is canonical |
| AMMA production self-heal | **consortium** | Multi-tenant healing |
| Bees + Hive orchestrator | **consortium** | Integrity guard required |
| Mandelbulb GPU dispatch | **consortium** | Production fractal compute |
| Public-facing endpoints (member portal, marketing) | **consortium** | [production-domain] |
| s3xyverse, paradise-estate, client projects | **consortium** | Served by the platform |
| Dev-tools API (`/api/dev/*`) | **consortium** (but dome-console may shell *its own* version locally) | Wrap, don't replicate |
| **Skill canonical library (461)** | **TU-AI** | `skills-library/skills/` is single source |
| Skill recall hook | **TU-AI** | `skills-library/hooks/skill-recall.sh` |
| Skill search + invoke API | **TU-AI** | `/api/skills/search`, `/api/skills/invoke` |
| KB ingest pipeline | **TU-AI** | `api/src/ingest.ts` only writer to pgvector |
| 36 sovereign agent specs | **TU-AI** | `agents/per-agent/` canonical |
| 32 engine directories (sacred geometry, holographic, consensus, swarm, memory) | **TU-AI** | Mathematical substrate |
| E8 / holographic / stigmergic compute APIs | **TU-AI** | `/api/e8-compute/*`, `/api/holographic/*` |
| Post-quantum crypto primitives | **DOME-HUB today → TU-AI candidate** | Currently `compute/crypto/`; promote for federation |
| Trinity HTTP client SDK | **DOME-HUB today → TU-AI candidate** | `agents/core/trinity_client.py` → `@trinity-consortium/mesh-client` |
| **launchd plists, local service control** | **DOME-HUB** | Only this node knows |
| **Sovereign hardening (FileVault/firewall/GPG/pass/Keychain)** | **DOME-HUB** | Local-machine-specific |
| **Mycelium signal (this node's heartbeat)** | **DOME-HUB** | Owns the signal; consortium owns the endpoint it calls |
| **Akashic local ChromaDB** | **DOME-HUB** | Local 267-doc record; ingest via `akashic/watcher.py` |
| **Personal memory (`memory/`, `~/.claude/memory/`)** | **DOME-HUB** | Operator's private context |
| **Local agent runners (claude/codex/kiro/cursor/kimi/trinity/local)** | **DOME-HUB** | The 7 adapters |
| **15-agent registry + 13 skill-agents** | **DOME-HUB** | `agents/core/`, `agents/skills/` |
| **Voice pipeline (Whisper.cpp + ASR + TTS)** | **DOME-HUB** | Local-only |
| **Local compute layer (Kuramoto, MPS, resonance_layer)** | **DOME-HUB** | This M5 Pro's specific physics |
| **dome.db SQLite (sessions, traces, registry, CRM)** | **DOME-HUB** (via dome-console for CRM tables) | Shared local DB |
| **Fractalmap (.fractalmap/ + scripts)** | **DOME-HUB** | Local-machine generated |
| **Dual-Archive Protocol enforcement** | **DOME-HUB** | Hot/Cold archive tiers |
| **CTO Build Framework validation** | **DOME-HUB** (with consortium-validator integration) | Local pre-commit gates |

---

## 6. Data-flow doctrine — what syncs between platforms

**Skill flow:** TU-AI's `skills-library/skills/` is the *only* canonical source. All other agent runtimes (`~/.kiro/skills`, `~/.claude/skills`, `~/.codex/skills`, `~/.cursor/skills`) **symlink** back. The skill-recall hook reads TU-AI's `skills.index.json`. No reverse mirroring.

**KB flow:** Markdown files anywhere in the known globs feed TU-AI's `api/src/ingest.ts`, which chunks/embeds/stores into pgvector. Other platforms *call* `/api/search`; they don't write to the KB directly.

**Auth flow:** consortium issues JWTs. TU-AI accepts them (dual-mode JWT + `x-hub-secret`). DOME-HUB / dome-console can present the JWT to call either platform.

**Mesh flow:** DOME-HUB → mycelium-signal.sh → POST `https://[production-domain]/api/mesh/peer/{handshake,heartbeat,merkaba/signal}` with HMAC-SHA256. consortium owns the endpoint + peer registry; DOME-HUB owns the signal.

**Cost/billing flow:** consortium-owned. Other platforms never need to know.

**Project repo flow:** Each "project" lives in its own repo (s3xyverse-next, etc.). consortium serves them. DOME-HUB hosts them under `home/projects/` (firmlinked from `~/projects/`) for local dev.

**dome-console call flow:**
```
dome-console (Next.js, :3737)
  ├── reads     ~/DOME-HUB/db/dome.db          (shared SQLite — local)
  ├── reads     ~/DOME-HUB/db/chroma/          (Akashic local — local)
  ├── reads     ~/DOME-HUB/memory/*            (filesystem — local)
  ├── reads     ~/.trinity-spore/*             (mesh state — local)
  ├── runs      launchctl, lsof, ps            (machine introspection — local)
  ├── calls     :3333/api/skills/search        (TU-AI — local-network HTTP)
  ├── calls     :3333/api/search               (TU-AI KB)
  ├── calls     :5055 or :443/api/auth/me      (consortium identity)
  └── calls     :5055 or :443/api/dev/git/...  (consortium dev-tools, scoped)
```

---

## 7. Sovereignty boundaries — what never leaves DOME-HUB

These are inviolable:

- **Personal memory** — `memory/`, `~/.claude/projects/-Users-<user>/memory/`, `~/.password-store/`, Keychain entries
- **PII** — dome-console's [N] contacts. Never mirrored out, never reachable from network.
- **Quantum internals** — `compute/sim_evolved.py` (Kuramoto K=2.663 internals), Mandelbulb fingerprints, MB-01→MB-10 vectors
- **AMMA soul-layer** — the φ-Mandelbulb frequency super-engine logic itself (production AMMA exposes scores only, not algorithm)
- **Dev keys** — `MESH_PEER_SECRET`, `HUB_API_SECRET`, GPG private key, Keychain secrets
- **Local launchd plists** — owned by this user account, not exported
- **Trinity-licensable IP carried in `agents/core/`** — per IP-LEDGER-MASTER doctrine

**Exception layer (DSH — public mirror):** `DSH/` is the *sovereign foundation* that's deliberately public (Apache 2.0). The `scripts/export-to-dsh.sh` pipeline sanitizes DOME-HUB → DSH using `config/public-export.{allowlist,denylist}`. Mirror **direction is one-way only** (DOME-HUB → DSH). Never mirror DSH content back into DOME-HUB personal layers.

---

## 8. Identity & governance — $OPERATOR / A4 / tier ladder

**Operator identity (this machine):**
- Username: `$OPERATOR`
- Real name: Enzo Garoche
- Primary email: `<redacted-email>`
- Aliases: `<redacted-email>`, `<redacted-email>`, `<redacted-email>`
- Member tier: **[member-tier]**
- Admin tier: **[admin-tier]** — sole holder, never delegated
- Company: Trinity Global Partners LLC (Trinity Consortium)

**Authority by tier (canonical at `trinity-consortium/shared/tier-constants.ts:168-184`):**

| Resource | L1 | L2 | L3 | A1 | A2 | A3 | A4 |
|---|---|---|---|---|---|---|---|
| Public landing | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| INTERNAL docs | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| CONFIDENTIAL docs |  | ✓ | ✓ |  | ✓ | ✓ | ✓ |
| STRICTLY_CONFIDENTIAL |  |  | ✓ |  |  | ✓ | ✓ |
| TECHNICAL_RESTRICTED (system IP) |  |  |  |  |  | ✓ | ✓ |
| Settings/env writes |  |  |  |  |  |  | ✓ |
| Shell exec via `/api/dev/shell` |  |  |  |  |  |  | ✓ |
| MESH_PEER_SECRET rotation |  |  |  |  |  |  | ✓ |
| Credential revocation |  |  |  |  |  |  | ✓ |

**Trust ladder for `/api/dev/*`:**
- Read fs/git: M1+
- Write fs / git push: A3+
- Shell exec: A4 only

**Founder gate enforcement points:**
- `auth.service.ts:1184` — founder identity gate
- `tier-constants.ts:ADMIN_OWNER_USERNAME = '$OPERATOR'`
- Defense-in-depth gaps surfaced 2026-04-26 (DB CHECK constraint, JWT-sign-time validation) — *not yet applied*. Tracked in memory.

**dome-console identity model:**
- Local-only on `127.0.0.1:3737`, no auth needed (sovereign by isolation)
- For consortium API calls: dome-console holds a JWT in local config (rotated per session) + `x-hub-secret`
- For privileged ops (start/stop services, rotate secrets): require **Touch ID biometric** confirmation + audit log entry to `~/.trinity-spore/logs/dome-console-actions.log`

---

## 9. dome-console expansion roadmap

### 9.1 Phasing principle

**Cheapest reuse first.** Each panel must reuse existing primitives (`MetricTile`, virtualized list, server-actions pattern) before warranting new infrastructure. No panel goes live without (a) a defined data source, (b) safe-by-default read-only mode, and (c) an audit-log entry for any state-changing action.

### 9.2 Phase A — capabilities already implied by current data (smallest delta)

**A1. Models Manager** (`/models`)
- Data: existing Ollama probe in `/api/metrics` + a thin `lib/ollama.ts` wrapper around `ollama list`
- UI: one `MetricTile` per loaded model (size, last-used, inference latency), modal for `ollama pull`
- LOC: ~200
- Why first: data already captured, zero new external dependencies

**A2. Agent Status Panel** (`/agents`)
- Data: existing `agents` table in `dome.db` + new `lib/agents.ts` (read-only queries)
- UI: 7 runner cards (claude/codex/cursor/kiro/kimi/trinity/local) + 15 core registry rows, last-run timestamps from `traces`
- Optional: `/api/agents/live` endpoint polling `~/.claude/projects/`, `~/.kiro/sessions/` mtimes for "active right now" indicator
- LOC: ~350

**A3. 5-Repo Git Grid** (`/repos`)
- Data: `git -C <path> status --short` + `git log -1 --format=%H:%ai` per repo
- UI: 5 cards (DOME-HUB / DSH / trinity-consortium / trinity-unified-ai / dome-console itself), uncommitted-count badge, **stomp-warning indicator** (if another agent's commit landed since the local working tree diverged)
- Why critical: *directly addresses the multi-agent stomp problem* we hit today (a sibling agent's `git commit --amend` orphaned a local commit; UI surfaces this in real time)
- LOC: ~400

### 9.3 Phase B — local control surfaces (new shell-out helpers)

**B1. Service / launchd Control Panel** (`/services`)
- Data: parse `~/Library/LaunchAgents/com.{dome,trinity}.*` plists + `launchctl list` + `lsof -iTCP -sTCP:LISTEN`
- UI: service grid with port / PID / uptime / restart policy + per-row [Start] [Stop] [Restart] [Tail Log]
- Safety: **green** for status reads, **amber** (confirm) for start/restart, **red** (Touch ID re-auth + audit) for unload/kill
- LOC: ~600

**B2. Mycelium Mesh Card** (`/mesh`)
- Data: tail `~/.trinity-spore/logs/mycelium-signal.log` + read `~/.trinity-spore/config.json` + call `/api/mesh/peer/status/:peerId` with HMAC
- UI: peer identity card (peerId, E8 root, resonance Hz, status), last-heartbeat indicator, heartbeat timeline graph (60s window), lattice-binding status, "Initiate handshake" button
- Special: shows the 401 error trace from today so operator can debug HUB_API_SECRET alignment
- LOC: ~500

### 9.4 Phase C — memory / knowledge surfaces (largest data integration)

**C1. Unified Memory Browser** (`/memory`)
- Five-tab layout:
  - **Episodic** — full-text + date range over `memory/sessions/2026-*/` + `db/episodic.db:facts`
  - **Akashic** — vector search over `db/chroma/` with domain + depth filters (call `akashic/record.py:query()`)
  - **Brain Registry** — tree view of `brain/REGISTRY.md` + `brain/engines/*.ref` → click → jumps to source in TU-AI
  - **Skills** — hierarchical browser, *delegates queries to TU-AI's `/api/skills/search`*, never reads local files
  - **Trinity Loci** — spatial layout of `~/.trinity-spore/mempalace.db` (palaces, rooms, loci, associations)
- LOC: ~1,300

**C2. KB Search** (`/knowledge`)
- Data: pure pass-through to TU-AI `/api/search` — dome-console does not store its own embeddings
- UI: search box, result cards with snippet + source link, filter by category
- LOC: ~250

### 9.5 Phase D — sovereign + identity surfaces

**D1. Hardening Compliance Grid** (`/hardening`)
- Data: on-demand exec of `audit.sh` checks (cached 5 min), no secrets ever stored
- UI: 14-control grid (FileVault / SIP / Gatekeeper / firewall / SMB / screen-lock / FV-standby / IR / Siri / Spotlight / AirPlay / crash-reporter / Chrome / Terminal-secure-keyboard), per-row [Verify], one-click [Harden All] (requires Touch ID)
- LOC: ~400

**D2. Identity Badge + Audit Trail** (`/identity`)
- Data: JWT inspector (claims, expiry, signature), call `/api/auth/me`, recent approval actions from `~/.trinity-spore/logs/dome-console-actions.log`
- UI: badge card with tier ladder visualization + recent privileged action feed
- LOC: ~250

**D3. Doctrine Board** (`/doctrines`)
- Data: filesystem scan of `docs/` + `projects/trinity-consortium/docs/` for canonical doctrines (8 listed in §11 below + this file)
- UI: card per doctrine with title, date, status (Active/Superseded/WIP), last-modified, link
- Companion: Recent Audits feed (mtime-sorted from `logs/reports/` + `home/trinity-unified-ai/reports/`)
- Companion: Contradiction Scanner — surfaces the 5 items in §10 below
- LOC: ~500

### 9.6 Phase E — observability + maps

**E1. Fractalmap Navigator** (`/fractalmap`)
- Data: read `.fractalmap/L0.md` + `L1/*.md` per registered repo (`config/fractalmap-repos.yaml`)
- UI: φ-zoom navigator across 5 canonical repos, manual [Refresh] trigger
- LOC: ~300

**E2. Compute Monitor** (`/compute`)
- Data: read `compute/sim_evolved.py` state (Kuramoto convergence, K-value), `compute/amma_monitor.py` coherence reading, `resonance_layer.py` Betti numbers
- UI: live coherence meter + AMMA state (frequency-tune / golden-needle / mitosis), topology drift alert
- LOC: ~400

### 9.7 Total expansion estimate

| Phase | Panels | LOC | Risk | Order |
|---|---|---|---|---|
| A | Models, Agents, Repos | ~950 | low | first |
| B | Services, Mesh | ~1,100 | medium (privileged ops) | second |
| C | Memory, KB | ~1,550 | medium (TU-AI integration) | third |
| D | Hardening, Identity, Doctrine | ~1,150 | high (touches secrets surface) | fourth |
| E | Fractalmap, Compute | ~700 | low | last |

**Total:** ~5,450 LOC on top of current ~4,293. Roughly **doubles** the codebase size — manageable in 6–8 focused sessions.

### 9.8 What dome-console MUST NOT do (anti-patterns)

- ❌ Duplicate auth, billing, tier enforcement — always call consortium
- ❌ Reimplement skill matching or KB ingest — always call TU-AI
- ❌ Provide a GUI for `dome-check`, `dome-approve`, `dome-sudo`, `audit.sh`, `harden.sh` *triggers* — keep these CLI-first; surface their *output*
- ❌ Allow Keychain secret value reads (only "present? yes/no" indicators)
- ❌ Allow one-click `git push` / `git reset --hard` / `launchctl unload` / `pf reload` without explicit confirmation + audit
- ❌ Cache JWT in localStorage / IndexedDB — keep in `httpOnly` cookie only
- ❌ Expose port 3737 beyond `127.0.0.1` (sovereign-by-isolation is the only auth model)
- ❌ Mix CRM tables with infra tables in the same data layer (already correctly separated: `contacts/*` are app-owned, `agents/skills/tools/traces/sessions/stack` are infra)

---

## 10. Open contradictions surfaced by deep-dive (must address)

1. **IP-removal — ✅ RESOLVED 2026-05-19** — the-womb codebase consolidation is complete; Trinity IP signature removal closed by $OPERATOR. Treat any older "4/8 FAIL" audit as superseded. Do not reopen this item without an explicit new finding.
2. **`trinity-dev-console` path refs — ✅ FALSE POSITIVE** — re-verified 2026-05-19: `trinity-consortium/CLAUDE.md:103` already marks the path as **DECOMMISSIONED**. Doc is correct.
3. **Old locked server `<REDACTED-IP>` — ✅ FALSE POSITIVE** — re-verified 2026-05-19: `trinity-consortium/CLAUDE.md:40,376` already documents the April 15 lockout as historical context (LOCKED OUT). Doc is correct.
4. **TU-AI path mismatch — ✅ RESOLVED 2026-05-19** — verified that `~/trinity-unified-ai` IS a real symlink to the canonical location. Docs using either path resolve to the same files. The nested form remains canonical for new docs; the symlink is a valid alias. No mass-rewrite needed.
5. **5 CTO bugs from 2026-04-27 — ✅ RESOLVED 2026-05-19** — re-probed each: (A) devstral 14 GB is now pulled in Ollama; (B) no `node tsx` process running from overlay path; (C) migration journal moved from `drizzle/` to `migrations/meta/_journal.json` (system reorganized, not broken); (D) `dist/` mtime is today 15:07 (fresh, not 17 days stale); (E) mesh-signal heartbeats green at 19:53Z. All 5 closed.
6. **`data/chromadb/` — ✅ DOCUMENTED 2026-05-19** — collection name is `dome-kb` with 5 embeddings (mtime 2026-05-17). Zero code references in DOME-HUB or trinity-consortium — writer is a manual/experimental ingest, not a production pipeline. Path is now gitignored (commit chain 2026-05-19). Treat as sibling experimental store; canonical Akashic remains `db/chroma/`. Owner may archive when convenient.
7. **trinity-consortium hive-orchestrator integrity drift — ✅ RESOLVED 2026-05-19** — `control-plane-hashes.json` re-blessed at 00:59 today. No current diff. Owner already ran the bootstrap ritual.
8. **Mycelium lattice-binding — ✅ FALSE POSITIVE** — re-verified 2026-05-19: binding exists at `~/.trinity-spore/mesh/lattice-binding.txt` (65 bytes, May 3). The deep-dive checked the wrong path. 401s between 05:33–14:37 today were a transient HUB_API_SECRET window; post-14:37 heartbeats green.

---

## 11. Companion doctrines currently in force

These should be respected jointly with this one:

| File | Purpose |
|---|---|
| `docs/SKILL_REGISTRY_POLICY.md` (2026-04-25) | 9-tier skill convention, canonical→mirror direction |
| `docs/architecture-audit-2026-05-12/INDEX.md` (2026-05-15) | 8-system audit + drift punch list |
| `docs/DOME-HUB-ARCHITECTURE.md` (2026-05-15) | 80 KB master architecture spec |
| `docs/PUBLIC_PROD_HARDENING.md` (2026-05-14) | DSH public mirror hardening boundaries |
| `docs/DSH_PUBLIC_PHASE1_BOUNDARY.md` (2026-05-14) | What's safe to public vs private |
| `docs/SKILL_LANDSCAPE_AUDIT_2026-04-25.md` (2026-04-25) | Skill landscape audit (619 SKILL.md baseline) |
| `docs/MQM_PARADIGM_UPGRADE_SPEC.md` (2026-05-18) | Mycelium Quantum Mesh — 7 paradigm upgrades |
| `home/projects/trinity-consortium/CLAUDE.md` | Trinity IP ownership + NCNDA breach status doctrine |
| Memory entry `feedback_dual_archive_protocol.md` | Hot/Cold archive tiers, per-repo schema |
| Memory entry `project_skill_landscape_consolidation_2026_04_25.md` | 8-phase consolidation final state |
| Memory entry `feedback_skill_tier_doctrine.md` | Same skill in multiple tiers is legitimate; sync within tier only |
| Memory entry `feedback_trinity_vocabulary.md` | Mycelium Signal not daemon, spore not bootstrap, etc. |
| Memory entry `feedback_egd33_owner_authority.md` | $OPERATOR sets tier/policy; API auto-detect is default not authority |

---

## 12. Multi-agent coordination doctrine

This sovereign node runs Claude Code (this), Codex CLI, Kiro CLI, Cursor, and the trinity-unified-ai swarm concurrently. Other agents edit files between any two of your tool calls.

**Rules every agent must follow:**

1. **Verify against git, not memory.** Memory files are point-in-time snapshots; the codebase changes. Before recommending a file/function/flag, grep for it.
2. **Don't `git commit --amend` in a shared working tree.** Today we observed an amend by another agent silently swallowing a sibling commit. Always create new commits.
3. **Stash + branch for non-trivial work in shared repos.** When working in DOME-HUB master or trinity-consortium main, prefer a topic branch so amend-races don't orphan your commits.
4. **Read fractalmap (`bash ~/DOME-HUB/skills/fractalmap/invoke.sh repo=<name> zoom=L0`) before deep dives** — it auto-regens if stale, so you get current state without scanning the whole tree.
5. **When in doubt about another agent's WIP, hold.** Better to leave files uncommitted for the owner than to bundle in-progress work under your authorship.
6. **dome-console's `/repos` panel surfaces stomp-warning indicators** (once Phase A3 ships) — check it before committing in a shared repo.

---

## 13. Verification commands

```bash
# Doctrine present
ls -la ~/DOME-HUB/docs/PLATFORM_DOCTRINE.md

# Three platforms reachable
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3737              # dome-console (expect 200)
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3333/health       # trinity-unified-ai (expect 200)
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:5055/api/health   # trinity-consortium local (expect 200)
curl -s -o /dev/null -w '%{http_code}\n' https://[production-domain]/api/health  # consortium prod (expect 200)

# Mycelium signal alive
launchctl list | grep com.dome.mycelium-signal
tail -5 ~/.trinity-spore/logs/mycelium-signal.log

# Akashic watcher alive
launchctl list | grep com.dome.akashic-watcher

# 5-repo git state
for r in $DOME_ROOT $DOME_ROOT/DSH $DOME_ROOT/projects/trinity-consortium $DOME_ROOT/trinity-unified-ai $DOME_ROOT/projects/dome-console; do
  printf '%-60s ' "$r"; (cd "$r" && git status --short | wc -l | xargs printf '%s files dirty\n')
done

# Skill canon (TU-AI is single source)
ls $DOME_ROOT/trinity-unified-ai/skills-library/skills/ | wc -l        # expect ~461

# Hardening spot-check
fdesetup status; csrutil status; /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# Operator identity
echo "$OPERATOR → A4 (DEV-OWNER) → sole holder"
```

---

## 14. Change log

- **2026-05-19** — v1.0 doctrine established by $OPERATOR after 8-agent parallel deep-dive analysis. Supersedes implicit prior assumptions. dome-console expansion roadmap defined (5 phases, ~5,450 LOC delta).
