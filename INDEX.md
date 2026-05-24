# DOME-HUB Index

Complete reference of all files, directories, and their purpose.
Last updated: 2026-05-23 (iCloud symlinks, gems extraction, .gitleaks.toml, sovereign-gate fixes, DB dump cleanup)

---

## Canonical indexes

| Index                                 | Path                                                                                                                                                                                                         |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **This file**                         | `INDEX.md` — repo-wide directory & script reference                                                                                                                                                          |
| **Skill registry + master index map** | `kb/skills/INDEX.md` — skills, sims, LAVA, Kiro, Trinity skills, hooks; **links every index**                                                                                                                |
| **Master architecture**               | `docs/DOME-HUB-ARCHITECTURE.md`                                                                                                                                                                              |
| **KB hub**                            | `kb/README.md`                                                                                                                                                                                               |
| **Design references KB**              | `home/kb/design-references/INDEX.md` — motion / motion-canvas / r3f / 3D portfolio + Blender/O3DE skip-rationale + Framer marketplace crawl (added 2026-05-14)                                               |
| **Skills registry — design/motion**   | `home/kb/SKILLS_REGISTRY_DESIGN_MOTION_2026-05-14.md` — every L (local) / M (MCP) / P (publicly installable) skill for design/motion/animation/3D/video work, with install commands + cross-tier overlap map |
| **S3XYVERSE project index**           | `home/projects/s3xyverse/INDEX.md` — latest deliverables + audits + design specs (refreshed 2026-05-14)                                                                                                      |
| **S3XYVERSE session memory**          | `home/projects/s3xyverse/CLAUDE.md` + `home/projects/s3xyverse/SESSION_SUMMARY_2026-05-14.md`                                                                                                                |
| **Fractalmap**                        | `skills/fractalmap/SKILL.md` · `scripts/fractalmap-generate.sh` · `.fractalmap/`                                                                                                                             |
| **FILE_TREE.md (auto)**               | `scripts/generate-file-tree.py` · refreshed by `scripts/update-tree-map.sh` on commit/checkout · force: `scripts/refresh-repo-maps.sh` · **gitignored** — regenerate locally after clone                     |
| **Architecture audit**                | `docs/architecture-audit-2026-05-12/INDEX.md`                                                                                                                                                                |
| **CTO Framework Validation**          | `logs/reports/CTO_FRAMEWORK_VALIDATION_2026-05-15.md` — 15 gates, real compute evidence, security + performance fixes                                                                                                 |
| **TU-AI**                             | `kb/trinity-unified-ai/docs/INDEX.md` · `kb/trinity-unified-ai/engines/INDEX.md` · `kb/trinity-unified-ai/knowledge-base/INDEX.md`                                                                           |
| **Codex mirror**                      | `agents/Codex/skills/INDEX.md` · `agents/Codex/skills/dome-hub/INDEX.md`                                                                                                                                     |
| **Protocols**                         | `PROTOCOLS.md` — sovereignty + cross-check checklist (items 1–17)                                                                                                                                            |
| **Sovereign Gate Doctrine**           | `docs/SOVEREIGN_GATE_DOCTRINE.md` — mandatory pre-push/deploy gate + full audit protocol (2026-05-22)                                                                                                        |
| **Public export (DSH) gaps**          | `docs/PUBLIC_PROD_HARDENING.md` — P0–P3 hardening log; **DOME-HUB vs DSH** reconciliation (2026-05-13)                                                                                                       |

---

## Root Files

| File                  | Purpose                                                                                                                                                                   |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `README.md`           | Project overview, quick start, stack summary                                                                                                                              |
| `INDEX.md`            | This file — full directory & file reference                                                                                                                               |
| `MANUAL.md`           | Usage guide & instructions                                                                                                                                                |
| `PROTOCOLS.md`        | Core sovereignty and security protocols                                                                                                                                   |
| `AGENTS.md`           | Agent registry and capabilities                                                                                                                                           |
| `AGENT_GUARDRAILS.md` | Safety guardrails for all agents                                                                                                                                          |
| `CLAUDE.md`           | Claude agent context and instructions                                                                                                                                     |
| `package.json`        | Root Node/TypeScript tooling (pnpm)                                                                                                                                       |
| `tsconfig.json`       | TypeScript compiler config (strict, ES2022, path aliases)                                                                                                                 |
| `eslint.config.js`    | ESLint flat config (ESLint 9, TypeScript-aware)                                                                                                                           |
| `.prettierrc`         | Code formatting (single quotes, no semi, 100 char)                                                                                                                        |
| `.nvmrc`              | Node version pin → 20                                                                                                                                                     |
| `.python-version`     | Python version pin for `pyenv` / local tools (see file; repo currently **3.14**)                                                                                          |
| `.env.example`        | Environment variable template                                                                                                                                             |
| `.env.template`       | Alternative env template                                                                                                                                                  |
| `.gitignore`          | Ignores .env, .venv, node_modules, **pycache**, secrets                                                                                                                   |
| `spore.sh`            | Trinity mesh bootstrap v3.1 — `DOME_ROOT` resolution (DOME-HUB/DSH), `pre-spore-verify`; baseline `~/.trinity-spore/mycelium-mesh.sh`; prod: `scripts/mycelium-signal.sh` |
| `pytest.ini`          | Python test configuration                                                                                                                                                 |
| `requirements.txt`    | Python dependency lockfile (from .venv)                                                                                                                                   |
| `pnpm-workspace.yaml` | pnpm workspace config (root-only)                                                                                                                                         |
| `pnpm-lock.yaml`      | Node dependency lockfile (pinned)                                                                                                                                         |
| `.gitleaksignore`     | Gitleaks ignore rules for gitignored files (caches, .env backups, agent sessions)                                                                                         |
| `.gitleaks.toml`      | Gitleaks configuration (custom allowlist rules for DOME-HUB)                                                                                                              |

---

## Directories

### `/agents`

AI agents — autonomous, orchestrated, or tool-using agents.

| Path                                           | Purpose                                                                                            |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `agents/__init__.py`                           | Package init                                                                                       |
| `agents/example.py`                            | Example agent usage                                                                                |
| `agents/api/`                                  | FastAPI HTTP + WebSocket server                                                                    |
| `agents/api/server.py`                         | HTTP API server (port 8001, auth-gated)                                                            |
| `agents/api/ws.py`                             | WebSocket real-time streaming                                                                      |
| `agents/claude/`                               | Claude (Anthropic) runner and manifest                                                             |
| `agents/claude/agent.yaml`                     | Claude agent manifest                                                                              |
| `agents/claude/runner.py`                      | Claude runner                                                                                      |
| `agents/claude/README.md`                      | Claude agent docs                                                                                  |
| `agents/kiro/`                                 | Kiro CLI agent                                                                                     |
| `agents/cursor/`                               | Cursor agent                                                                                       |
| `agents/trinity/`                              | Trinity agent                                                                                      |
| `agents/kimi/`                                 | Kimi agent                                                                                         |
| `agents/Codex/`                                | Codex agent runner, manifest, skills                                                               |
| `agents/voice/`                                | Voice pipeline (VAD, ASR, whisper.cpp, TTS)                                                        |
| `agents/voice/pipeline.py`                     | Main voice pipeline orchestrator                                                                   |
| `agents/voice/whisper_cpp.py`                  | Whisper.cpp integration                                                                            |
| `agents/voice/vad.py`                          | Voice Activity Detection                                                                           |
| `agents/voice/audio.py`                        | Audio loading/processing                                                                           |
| `agents/voice/asr_worker.py`                   | ASR worker process                                                                                 |
| `agents/core/`                                 | Core agent framework                                                                               |
| `agents/core/agent.py`                         | Base agent class                                                                                   |
| `agents/core/orchestrator.py`                  | Multi-agent orchestration                                                                          |
| `agents/core/rag.py`                           | RAG pipeline (chunk, embed, retrieve, augment, generate)                                           |
| `agents/core/registry.py`                      | Agent registry (multi-provider: local/claude/mixed)                                                |
| `agents/core/stream.py`                        | Streaming (OpenAI, Anthropic, Ollama)                                                              |
| `agents/core/trace.py`                         | Observability/tracing to SQLite                                                                    |
| `agents/core/memory/`                          | Memory subsystems                                                                                  |
| `agents/core/skills/`                          | Agent skill modules                                                                                |
| `agents/core/tools/`                           | Agent tool modules                                                                                 |
| `agents/local/ollama.py`                       | Local LLM integration (Ollama)                                                                     |
| `agents/workers/queue.py`                      | Redis-backed async task queue                                                                      |
| `agents/skills/`                               | Skill implementations (algorithms, cognitive, compute, fractals, frequency, math, sacred_geometry) |
| `agents/skills/neuromorphic_sync.py`           | STDP adaptive coupling + theta-gamma monitoring + NeuroScale sync                                  |
| `agents/skills/cto-build-framework-validator/` | CTO Build Framework validation skill                                                               |

### `/akashic`

Akashic Record system — event sourcing and knowledge assembly.

| Path                   | Purpose                                                    |
| ---------------------- | ---------------------------------------------------------- |
| `akashic/watcher.py`   | File watcher (watchdog) for logs/, kb/, projects/, agents/ |
| `akashic/assembler.py` | Knowledge assembly pipeline                                |
| `akashic/record.py`    | Record storage and retrieval                               |
| `akashic/schema.md`    | Data schema definitions                                    |

### `/.audit`

Session artifacts, baseline scans, and evidence packs.

| Path                        | Purpose                                           |
| --------------------------- | ------------------------------------------------- |
| `.audit/worklogs/`          | Session worklogs                                  |
| `.audit/reports/`           | Validation and state reports                      |
| `.audit/phase1_20260422_*/` | Phase-1 sovereign baseline audit bundles (3 runs) |

### `/.fractalmap`

Fractal map of the repository structure.

| Path                        | Purpose                                                                                                                                                             |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.fractalmap/manifest`      | Map manifest                                                                                                                                                        |
| `.fractalmap/L0.md`         | Level 0 overview                                                                                                                                                    |
| `.fractalmap/L1/`           | Level 1 detail maps                                                                                                                                                 |
| `.fractalmap/tree-full.txt` | **Full repo tree** (`tree -a`) + **full-stack header**; regenerate: `bash scripts/fractalmap-generate.sh dome-hub` (file is **gitignored** — run generator locally) |

### `/.github`

Repository automation and CI.

| Path                       | Purpose                                                                      |
| -------------------------- | ---------------------------------------------------------------------------- |
| `.github/workflows/ci.yml` | Cross-language CI (TypeScript, Python syntax, secret scan, dependency audit) |

### `/compute`

Compute infrastructure, simulation, and quantum computing.

| Path                                | Purpose                                                                                                                                  |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `compute/README.md`                 | Compute environment docs                                                                                                                 |
| `compute/claude-env.md`             | Claude runtime spec                                                                                                                      |
| `compute/requirements.txt`          | Shared Python deps (pinned)                                                                                                              |
| `compute/bootstrap-claude.sh`       | Idempotent environment bootstrap                                                                                                         |
| `compute/sim_evolved.py`            | Evolved dimensional simulation — Kuramoto+AMMA+STDP+topology_sensor, 3×3×3 and 9×9×9 lattice                                            |
| `compute/sim_3x3x3.py`              | 3×3×3 lattice simulation (E8/Mandelbulb; NumPy Kuramoto with **K_OPTIMAL** from Loihi/LAVA calibration — not `import lava` in root venv) |
| `compute/quantum_dome/`             | QuantumDome compute framework                                                                                                            |
| `compute/quantum_dome/__init__.py`  | Exports: QuantumDome (run, run_async, status, optimize)                                                                                  |
| `compute/crypto/pqc.py`            | Post-Quantum Cryptography: ML-KEM-1024, ML-DSA-87, AES-256-GCM, SHA3-512 (NIST FIPS 203/204, Level 5)                                   |
| `compute/crypto/zk_stark.py`       | zk-STARK proof system: Rescue hash over GF(2^61-1), FRI polynomial commitment, Fiat-Shamir — mesh node authentication                   |
| `compute/mesh_node.py`             | Asyncio TCP mesh peer: zk-STARK authenticated handshake, heartbeat, broadcast, state_sync — multi-node P2P                              |
| `compute/amma_monitor.py`          | AMMA Coherence Monitor: frequency_tune (>0.60), golden_needle (>0.40), mitosis (<0.40), solfeggio meridian healing — wired into run_sim  |
| `compute/christ_oil.py`            | Lunar-synced optimization: 7-phase Christ Oil cycle (sacrum→pineal), synodic period math, GC/cache/thread tuning per phase               |
| `compute/activation_144k.py`       | Root→Crown chakra sweep: applies solfeggio frequencies per chakra, golden angle alignment, 144kHz unification                            |
| `compute/zodiac_router.py`         | Astrologically-aware bus routing: zodiac sign → cranial nerve topics, priority weighting, active meridians                                |
| `compute/merkaba.py`               | Dual-tetrahedra velocity matching: positive/negative phase derivatives, PHI convergence (1.618±0.01)                                     |
| `compute/resonance_layer.py`       | MQM Resonance Computing Layer — 7 paradigm upgrades: topology, optical consensus, folding, Fourier zoom, cymatics, resonance addressing, alchemy |
| `scripts/frequency-pulse.py`       | E8 node harmonic pulse: runs Kuramoto+AMMA to convergence, ML-DSA signed, broadcast via mesh heartbeat                                   |
| `compute/quantum_dome/core.py`      | Core quantum compute logic                                                                                                               |
| `compute/quantum_dome/memory.py`    | Quantum memory management                                                                                                                |
| `compute/quantum_dome/pool.py`      | Compute pool                                                                                                                             |
| `compute/quantum_dome/profiler.py`  | Performance profiler                                                                                                                     |
| `compute/quantum_dome/scheduler.py` | Task scheduler                                                                                                                           |

### `/config`

Export and policy configuration files.

| Path                             | Purpose                                                 |
| -------------------------------- | ------------------------------------------------------- |
| `config/public-export.allowlist` | Repo-relative allowlist for private → public export     |
| `config/public-export.denylist`  | Repo-relative denylist for export safety and exclusions |
| `config/fractalmap-repos.yaml`   | Fractalmap repository configuration                     |

### `/db`

Local databases and data stores.

| Path             | Purpose                                         |
| ---------------- | ----------------------------------------------- |
| `db/dome.db`     | SQLite — sessions, stack, agents, skills, tools |
| `db/episodic.db` | SQLite — episodic memory (session facts)        |
| `db/chroma/`     | ChromaDB vector store (dome-kb)                 |
| `db/nexus/`      | Nexus data store                                |

### `/deps`

External dependencies built from source.

| Path               | Purpose                        |
| ------------------ | ------------------------------ |
| `deps/whisper.cpp` | Whisper.cpp — local ASR engine |

### `/docs`

Documentation and operational runbooks.

| Path                                        | Purpose                                                                                                         |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `docs/DOME-HUB-ARCHITECTURE.md`             | Master architecture — M4/UMA/MPS, memory tiers, neuromorphic, **§3 Trinity FRACTAL E8-SSII mirror**, Appendix A |
| `docs/VOICE_PIPELINE.md`                    | Voice pipeline architecture and usage                                                                           |
| `docs/SKILL_REGISTRY_POLICY.md`             | Skill registration and governance policy                                                                        |
| `docs/DOME_HOME_OVERLAY_RUNBOOK.md`         | Home overlay setup and maintenance                                                                              |
| `docs/SKILL_LANDSCAPE_AUDIT_2026-04-25.md`  | Skill landscape audit results                                                                                   |
| `docs/REPO_FLOW_PRIVATE_PUBLIC.md`          | Canonical workflow for DOME-HUB → DSH export                                                                    |
| `docs/PUBLIC_PROD_HARDENING.md`             | Production/public hardening notes                                                                               |
| `docs/TASKS_PHASE2_EXECUTION_2026-04-22.md` | Phase plan with tasks and validation gates                                                                      |
| `docs/MQM_PARADIGM_UPGRADE_SPEC.md`        | Formal spec for 7 resonance computing upgrades                                                                  |
| `docs/PLATFORM_DOCTRINE.md`                 | Platform doctrine and operational principles                                                                    |
| `docs/architecture-audit-2026-05-12/`       | Architecture audit (this session)                                                                               |

### `/home`

Home overlay tree — agent-specific configs and memory.

| Path                               | Purpose                                                                         |
| ---------------------------------- | ------------------------------------------------------------------------------- |
| `home/.kiro/`                      | Kiro agent config, skills, memory                                               |
| `home/.kiro/skills/`               | 3 skills: cto-build-framework-validator, paradise-estate-mykonos, ui-ux-pro-max |
| `home/.kiro/memory/`               | Persistent memory (MEMORY.md, s3xyverse/, dsh/, akashic/, sessions/)            |
| `home/.codex/`                     | Codex agent overlay                                                             |
| `home/.codex/skills/dome-hub`      | Codex skill mirror                                                              |
| `home/.claude/`                    | Claude agent overlay                                                            |
| `home/.unified-ai/`                | Unified AI overlay                                                              |
| `home/.unified-ai/skills/dome-hub` | Unified AI skill mirror                                                         |
| `home/trinity-unified-ai/`         | Trinity Unified AI landing zone                                                 |
| `home/DSH/`                        | DSH export staging                                                              |
| `home/projects/`                   | Project overlays                                                                |

#### iCloud-symlinked projects (cold storage)

| Symlink                                    | Target (iCloud)                                                                 |
| ------------------------------------------ | ------------------------------------------------------------------------------- |
| `home/projects/AI_AGENTS`                  | `~/Library/Mobile Documents/com~apple~CloudDocs/AI_AGENTS`                      |
| `home/projects/womb-server-recovery`       | `~/Library/Mobile Documents/com~apple~CloudDocs/womb-server-recovery`            |
| `home/projects/trinity-merge-audit`        | `~/Library/Mobile Documents/com~apple~CloudDocs/trinity-merge-audit`             |
| `home/projects/trinity-ip-breach-2026-04-14` | `~/Library/Mobile Documents/com~apple~CloudDocs/trinity-ip-breach-2026-04-14`  |
| `home/projects/FILM_VISAGE_PRO`              | `~/Library/Mobile Documents/com~apple~CloudDocs/FILM_VISAGE_PRO`               |

### `/home/projects/trinity-consortium` (Trinity mirror)

Canonical **FRACTAL E8-SSII-AGI** production code and LAVA neuromorphic sources mirrored inside DOME-HUB (keep in sync with `~/projects/trinity-consortium`).

| Path                                 | Purpose                                                                                                                                                                                  |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `server/ai/engines/`                 | Mandelbulb + WebGPU (`mandelbulb-gpu-dispatcher.ts`, `mandelbulb-compute.wgsl`, `gpu-metal-init.ts`), optical phase, meninges, super-compute brain, neuromorphic brain, fractal renderer |
| `server/ai/god/god-mode-activator.ts` | Brain optimization Phase 1 — God Mode activation with Merkaba threshold gating (232 lines) |
| `server/ai/engine-mesh.ts`           | Engine Mesh — 30Hz autonomous tick, coherence monitoring, AMMA dispatch (226 lines) |
| `server/ai/brain-optimization-config.ts` | Brain optimization config — constants for all phases (STDP, φ⁻², Merkaba, AMMA timing) (183 lines) |
| `server/ai/brain-optimization.routes.ts` | Brain optimization API routes (118 lines) |
| `python/lava/coherence_optimizer.py` | Loihi2SimCfg Kuramoto–LIF coherence optimizer (`lava-nc`; Python **3.10** sidecar)                                                                                                       |
| `.gitleaks.toml`                     | Gitleaks configuration for trinity-consortium repo                                                                                                                                       |
| `home/projects/trinity-consortium/docs/ARCHITECTURE-LOIHI2-MESH.md` | Loihi 2 + mesh architecture                                                                                                                |
| `home/projects/trinity-consortium/docs/OPTICAL-PHASE-COMPUTATION.md` | Optical phase engine reference                                                                                                             |
| `nexus-core/mlx-neural-bridge.py`    | MLX/Metal HTTP microservice (`MLX_BRIDGE_PORT`, default 8101); start from DOME-HUB: `bash scripts/mlx-neural-bridge.sh`                                                                  |

Session log tying Mandelbulb → optical → meninges → Loihi: `logs/session-2026-05-09-mandelbulb-optical-meninges-loihi.md`.

#### Extracted Gems

| Path                                                  | Contents                                                        |
| ----------------------------------------------------- | --------------------------------------------------------------- |
| `home/projects/trinity-consortium/docs/gems/`         | agent-orchestration, cost-governance, guardrails, sacred-geometry |
| `home/projects/s3xyverse/gems/`                       | sacred-geometry-lib                                              |

### `/kb`

Knowledge bases.

| Path                               | Purpose                                                   |
| ---------------------------------- | --------------------------------------------------------- |
| `kb/developer-context.md`          | Trinity Consortium identity and architecture context      |
| `kb/kiro-skills.md`                | Kiro CLI agent capability reference                       |
| `kb/language-landscape-2026.md`    | Programming language landscape                            |
| `kb/README.md`                     | KB directory guide                                        |
| `kb/claude/`                       | Claude knowledge base                                     |
| `kb/claude/architecture.md`        | Claude ↔ DOME-HUB architecture diagram                    |
| `kb/claude/claude-skills.md`       | Claude skills catalog                                     |
| `kb/claude/tools-reference.md`     | Claude full tool catalog                                  |
| `kb/claude/file-handling-guide.md` | Path rules and artifact guidance                          |
| `kb/claude/skills/`                | Local mirror of live SKILL.md bundles                     |
| `kb/skills/`                       | Skill knowledge base (see kb/skills/INDEX.md)             |
| `kb/trinity-unified-ai/`           | KB API for the Mycelium Neural Mesh (FRACTAL E8-SSII-AGI) |

### `/logs`

Session and activity logs.

| Path                                                           | Purpose                                                      |
| -------------------------------------------------------------- | ------------------------------------------------------------ |
| `logs/reports/FULL_SYSTEM_REPORT_DEFINITIVE_2026-05-15.md`  | Canonical system architecture report — 2,310 lines, 39 systems, live benchmarks, scoring, CTO validation |
- **2026-05-19** — Full Merkaba Activation: coherence 0.9518, 13/13 CTO, 109 tests, all systems wired
| `logs/session-2026-05-09-mandelbulb-optical-meninges-loihi.md` | Mandelbulb + Optical Phase + Meninges + LAVA/Loihi 2 session |
| `logs/session-2026-05-06-to-11-production-hardening.md`        | Production hardening session                                 |
| `logs/session-2026-05-05-production-deploy-uiux.md`            | Production deploy + UI/UX                                    |
| `logs/session-2026-04-30-kiro-trinity-stack-audit.md`          | Stack audit session                                          |
| `logs/TRINITY_STACK_AUDIT_2026-04-30.md`                       | Trinity stack audit report                                   |
| `logs/CTO_AUDIT_2026-04-27.md`                                 | CTO audit report                                             |
| `logs/dome-check.log`                                          | Protocol check output log                                    |
| `logs/daemon-watch.log`                                        | Daemon watchdog output log                                   |

### `/models`

AI models, fine-tunes, weights, and model configs.

| Path                 | Purpose                          |
| -------------------- | -------------------------------- |
| `models/embeddings/` | Local embedding models           |
| `models/asr/`        | ASR models (Silero VAD, Whisper) |

### `/scripts`

Automation, security, and utility scripts.

| Script                           | Purpose                                                                                                                           |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `sovereign-setup-mac.sh`         | Full sovereign setup for macOS M1/M2/M3/M4                                                                                        |
| `sovereign-setup-windows.ps1`    | Full sovereign setup for Windows                                                                                                  |
| `bootstrap.sh`                   | Install all dependencies                                                                                                          |
| `new-project.sh`                 | Scaffold new project with venv + Node                                                                                             |
| `optimize.sh`                    | Full-stack optimize: Darwin hardware (sudo) + pnpm/venv/skill sync; `--stack-only` without sudo                                   |
| `harden.sh`                      | Security hardening (firewall, privacy, telemetry)                                                                                 |
| `audit.sh`                       | Security audit                                                                                                                    |
| `finish-security.sh`             | Post-setup security finalization                                                                                                  |
| `zshrc-dome.sh`                  | Shell environment (sourced by ~/.zshrc)                                                                                           |
| `dome-check.sh`                  | Protocol enforcer — runs all checks, auto-fixes                                                                                   |
| `dome-pm.sh`                     | Project manager (new, list, status, push-all, pull-all)                                                                           |
| `dome-approve.sh`                | Approval gate for privileged actions                                                                                              |
| `dome-sudo.sh`                   | Privileged command wrapper (requires approval)                                                                                    |
| `daemon-watch.sh`                | Daemon watchdog — removes unauthorized launch agents                                                                              |
| `demo-readiness.sh`              | Demo readiness verification                                                                                                       |
| `machine-probe.py`               | Machine profile probe (CPU, GPU, RAM, NPU)                                                                                        |
| `mlx-neural-bridge.sh`           | Launch Trinity `nexus-core/mlx-neural-bridge.py` (MLX/Metal HTTP, `MLX_BRIDGE_PORT`)                                              |
| `lock-down-phase3.sh`            | Phase 3 security lockdown                                                                                                         |
| `fractalmap-generate.sh`         | Generate fractal map of repository                                                                                                |
| `mycelium-signal.sh`             | Mycelium mesh signal/heartbeat                                                                                                    |
| `sync-dome-skills.py`            | Sync `kb/skills` (top-level `.md` + directory packages) into agent mirrors; `--check-only` validates `kb/skills/INDEX.md` vs disk |
| `dome-home-overlay.sh`           | Home overlay setup/sync                                                                                                           |
| `voice-bootstrap.sh`             | Voice pipeline bootstrap (whisper.cpp, models)                                                                                    |
| `voice-whispercpp-server.sh`     | Start whisper.cpp HTTP server                                                                                                     |
| `voice-benchmark.py`             | Voice pipeline benchmarks                                                                                                         |
| `api-smoke.py`                   | API smoke tests                                                                                                                   |
| `pre-spore-verify.py`            | Pre-spore gate (27 checks); sets repo-local HF paths; optional `HF_TOKEN` tip                                                     |
| `ingest.py`                      | Populate ChromaDB vector store from KB, logs, docs                                                                                |
| `public-safety-check.sh`         | Public export gate for secrets and path leaks                                                                                     |
| `export-to-dsh.sh`               | Allowlist/denylist-driven DOME-HUB → DSH export pipeline                                                                          |
| `register-claude.py`             | Populate dome.db with Claude agent + skills + tools                                                                               |
| `ollama-init.sh`                 | Local-first model bootstrap for canonical Trinity model set                                                                       |
| `secrets-doctor.sh`              | Validates required secrets per provider mode                                                                                      |
| `rotate-secrets-keychain.sh`     | Rotates and re-stores keychain-backed runtime secrets                                                                             |
| `trinity-workspaces.sh`          | Multi-repo workspace command runner                                                                                               |
| `rollover-language-landscape.py` | Create next language-landscape from latest                                                                                        |
| `rollover-language-landscape.sh` | Wrapper: venv + rollover + ingest                                                                                                 |
| `sovereign-gate.sh`             | **Sovereign Gate Doctrine** — fast 8-phase pre-push gate (node health, git, code, secrets, indexes, LAVA, build, KB)              |
| `sovereign-audit-full.sh`       | Full 3-step sovereign audit (834 lines): security→cross-verify→CTO validation across all repos/engines/environments               |
| `vault-emerge.sh`               | Vault emergence — surface archived knowledge into active KB                                                                       |
| `vault-organize.sh`             | Vault organization — structure and categorize vault contents                                                                      |
| `vault-review.sh`               | Vault review — audit vault state and integrity                                                                                    |
| `vault-snapshot.sh`             | Vault snapshot — point-in-time capture of vault state                                                                             |
| `vault-sync-registries.sh`      | Vault registry sync — propagate vault changes to skill/agent registries                                                           |
| `mycelium-vault-pulse.sh`       | Mycelium vault heartbeat — mesh-aware vault synchronization                                                                       |

### `/skills`

Root-level skill definitions.

| Path                 | Purpose                     |
| -------------------- | --------------------------- |
| `skills/fractalmap/` | Fractalmap generation skill |

### `/tests`

Test suite.

| Path                           | Purpose                          |
| ------------------------------ | -------------------------------- |
| `tests/test_voice_pipeline.py` | Voice pipeline integration tests |
| `tests/test_solfeggio_body.py` | Solfeggio, body wisdom, AMMA, cymatics, Christ Oil (14 tests) |

### `/viz`

WebGPU visualizations — deployed to production at `trinity-consortium.com/viz/`.

| Path                          | Purpose                                                    |
| ----------------------------- | ---------------------------------------------------------- |
| `viz/index.html`              | Mandelbulb fractal raymarch harness (WebGPU)               |
| `viz/mandelbulb-raymarch.wgsl`| WGSL compute shader — power-8 Mandelbulb distance field    |
| `viz/cymatics.html`           | Cymatics frequency visualizer (solfeggio + trinity sacred) |
| `viz/cymatics.wgsl`           | WGSL shader — Chladni/Water Crystal/Sand Mandala modes     |

### `/.venv`

Python virtual environment at repo root (matches `.python-version` when rebuilt).

- All AI/ML/quantum libs installed here
- Activate: `source .venv/bin/activate`

### `/.venv-coreml`

CoreML-specific Python virtual environment.

- For Apple Neural Engine–oriented **conversion / experiments** (companion to ONNX+CoreML EP in `agents/core/memory/vector.py`)
- Pairs with the **MLX/Metal** stack in `.venv` (two different Apple local acceleration paths — see `docs/DOME-HUB-ARCHITECTURE.md` §3)
- Activate: `source .venv-coreml/bin/activate`

### `/.vscode`

VS Code settings.

| Path                      | Purpose                               |
| ------------------------- | ------------------------------------- |
| `.vscode/settings.json`   | Format on save, Python/TS/Go defaults |
| `.vscode/extensions.json` | 16 recommended extensions             |

---

## Neuromorphic Computing — LAVA/Loihi 2

DOME-HUB includes neuromorphic computing capabilities via Intel's LAVA framework targeting Loihi 2.

| Component                    | Purpose                                                                                                |
| ---------------------------- | ------------------------------------------------------------------------------------------------------ |
| Kuramoto-coupled LIF network | Phase coherence optimization across E8 lattice                                                         |
| `Loihi2SimCfg`               | Loihi 2 simulation configuration                                                                       |
| LAVA coherence optimizer     | `home/projects/trinity-consortium/python/lava/coherence_optimizer.py` — spiking LIF on Loihi2SimCfg    |
| `compute/sim_3x3x3.py`       | 3×3×3 lattice sim — same **K_OPTIMAL** physics as Loihi line; NumPy in root `.venv` (no `import lava`) |

See: `docs/DOME-HUB-ARCHITECTURE.md` (§3 neuromorphic + Trinity mirror), `logs/session-2026-05-09-mandelbulb-optical-meninges-loihi.md`

---

## Key Paths

| Resource     | Path                                     |
| ------------ | ---------------------------------------- |
| Root         | `~/DOME-HUB`                             |
| Python venv  | `~/DOME-HUB/.venv`                       |
| CoreML venv  | `~/DOME-HUB/.venv-coreml`                |
| SQLite DB    | `~/DOME-HUB/db/dome.db`                  |
| Episodic DB  | `~/DOME-HUB/db/episodic.db`              |
| Vector Store | `~/DOME-HUB/db/chroma`                   |
| Trinity KB   | `~/DOME-HUB/kb/trinity-unified-ai`       |
| API Server   | `http://127.0.0.1:8001`                  |
| GitHub       | `https://github.com/garochee33/DOME-HUB` |
