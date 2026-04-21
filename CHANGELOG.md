# Changelog

All notable changes to DSH (Dome Sovereign Hub) will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
DSH uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Full sovereign lockdown suite (`scripts/lock-down.sh`, `-phase2`, `-phase3`,
  `-phase4`, `scripts/pf-reload.sh`) — kills phone-home daemons, pins DNS to
  dnscrypt-proxy, configures pf anchor for known telemetry endpoints.
- Secrets pipeline: `scripts/sovereign-secrets.sh` (GPG + pass bootstrap),
  `scripts/render-env.sh` (resolve `.env.template` from Keychain or pass).
- `.env.template` with `{{keychain:SERVICE}}` and `{{pass:dome/KEY}}` markers.
- Pre-loaded Trinity Consortium KB (15 architecture docs in
  `kb/trinity-unified-ai/`) so `spore.sh` activation is mesh-connect only,
  not a fresh KB fetch.
- Full Apache-2.0 LICENSE with Trinity Consortium scope notes.
- Public governance: `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`.
- CI pipeline: `pnpm lint` + `typecheck`, Python syntax + `pre-spore-verify`,
  gitleaks, dependency audit.
- Dependabot for npm + pip + github-actions.
- Issue and PR templates with sovereignty-impact checklist.

### Changed
- All scripts (`scripts/*.sh`, `akashic/*.py`, `agents/example.py`) now derive
  `$DOME_ROOT` portably via `pathlib.Path(__file__)` or `BASH_SOURCE`, with
  `$DOME_ROOT` env var override.
- `README.md` / `MANUAL.md` / `INDEX.md` / `kb/` / `compute/` rebadged from
  `gadikedoshim/DOME-HUB` references to `garochee33/DSH`; personal paths
  replaced with `$DOME_ROOT` or `~/DSH` defaults.
- `scripts/dome-check.sh` — macOS Keychain fallback for secrets, GPG signing
  optional (not auto-enabled), auto-commit/push removed (was destructive).
- `psql -U gadikedoshim` → `psql -U "$USER"` in MANUAL.

### Removed
- Unused npm deps: `latest` (typosquat-adjacent) and `kiro-cli` (is an
  optional global install per README, should not be a project dep).
- Private state from public snapshot: machine-local `CLAUDE.md`, session
  logs (`logs/*.md`, `logs/reports/`), `google drive/` sync folder
  (≈616 MB, 15 large binaries).
- 698 MB of large binaries purged from git history via `git filter-repo`.

### Security
- First cut of threat model in `SECURITY.md` with private disclosure path.
- Pre-commit secret-scan check via gitleaks in CI.
- `scripts/dome-check.sh` auto-remove of unauthorized LaunchAgents.
- Dependency audits wired into CI (pnpm audit + pip-audit, non-blocking).

---

## [0.0.1] — 2026-04-17

### Added
- Initial DOME-HUB / DSH foundation build.
- Python 3.11 venv with AI/ML stack (anthropic, LangChain, ChromaDB,
  sentence-transformers, PyTorch-MPS, Transformers).
- Quantum-computing stack (Qiskit, PennyLane, Cirq, QuTiP, PyQuil,
  Amazon Braket SDK).
- Local inference via MLX + Ollama.
- Agent framework in `agents/core/` (agent, orchestrator, RAG pipeline,
  registry, streaming, tracing) + memory subsystems (vector, episodic,
  working).
- 7 skill modules in `agents/skills/` — math, compute, sacred_geometry,
  fractals, algorithms, frequency, cognitive.
- Akashic dimensional-record system (`akashic/record.py`, `assembler.py`,
  `watcher.py`) with ChromaDB-backed namespace.
- FastAPI agent server (`agents/api/server.py`, port 8000) + WebSocket
  streaming (`agents/api/ws.py`).
- Redis-backed async task queue (`agents/workers/queue.py`).
- Setup scripts: `sovereign-setup-mac.sh`, `sovereign-setup-windows.ps1`.
- Security scripts: `harden.sh`, `audit.sh`, `daemon-watch.sh`, `optimize.sh`.
- Project manager: `dome-pm.sh` (new / list / status / push-all / publish).
- Approval gate: `dome-approve.sh`, `dome-sudo.sh`.
- `PROTOCOLS.md` — core sovereignty and security protocols.
- `spore.sh` v3.0 — Trinity mesh activation (E8 lattice, Mandelbulb,
  bitboard, MERKABA signal, A.M.M.A. relay, Loihi-2 bridge).

[Unreleased]: https://github.com/garochee33/DSH/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/garochee33/DSH/releases/tag/v0.0.1
