# Changelog

All notable changes to DSH (Dome Sovereign Hub) will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
DSH uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- **18 workstation utility skills** — file generation (docx, pdf, pptx, xlsx, pandoc, latex-tectonic, imagegen, speech, transcribe, jupyter-notebook), automation (playwright, screenshot, github, ci-cd-architect), security (security-threat-model, security-best-practices), research (deep-research, skill-generator-engine)
- **16 developer productivity skills** — frameworks (nextjs, fastapi, ai-sdk, react-best-practices, shadcn), data/infra (database-optimizer, neon-postgres, migration-specialist, cloudflare-deploy, api-gateway-designer), quality (testing-strategist, refactoring-engineer, performance-tuner, dependency-manager, documentation-generator), monetization (stripe-best-practices)
- `scripts/install-format-deps.sh` — cross-platform dependency installer for all workstation skills
- Windows setup: workstation format deps (pandoc, miktex, ffmpeg, python-docx, playwright)

### Changed
- **Node 20 → 22 LTS** across entire stack: CI, .nvmrc, engines, docs, setup script
- **GitHub Actions** bumped to v6: checkout, setup-node, setup-python, pnpm/action-setup
- `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` added to CI workflow env
- `compute/requirements.txt` deps bumped: sentence-transformers >=5.4.1, anthropic >=0.97.0, python-docx >=1.2.0, pypdf >=6.10.2, pyquil >=4.16.2, eslint ^10.4.0, @types/node ^25.9.1
- `dsh-console/package.json` @types/node ^20 → ^22

### Added
- `.gitleaks.toml` — custom secret scanning (11 rules: API keys, JWTs, connection strings, Hetzner tokens, SPORE tokens, hardcoded IPs)
- `scripts/backup-projects-to-icloud.sh` — automated iCloud backup for local projects (cron every 4h)
- `dsh-console/` entry added to INDEX.md repository tree
- GitHub branch protection on main: required status checks (TS lint, Python verify, Gitleaks), linear history, strict mode

### Fixed
- **Windows setup script** — bash heredoc→PowerShell pipe, venv path handling, graceful fallbacks for missing scripts, Python 3.11→3.14, postgresql17→postgresql
- CI `deps-audit` job cache path error (removed unused `cache: pnpm`)
- Stale `kb/trinity-unified-ai/` phantom reference in INDEX.md → corrected to `kb/claude`
- All stale Python 3.11 references updated to 3.14 (registry.py, architecture.md, requirements.txt)
- `pnpm-lock.yaml` sync issue (Dependabot merge resolved)

### Security
- `.gitignore` hardened: blocks `akashic/books/` (653MB), all binary formats, `uv.lock`
- GitHub repo: squash-only merges, auto-merge enabled, wiki/projects disabled
- Dependabot security updates + vulnerability alerts enabled
- `home/.kiro/memory/MEMORY.md` removed from DSH tracking (contained server IP)

### Merged PRs
- #8 pyquil >=4.16.2
- #9 pypdf >=6.10.2
- #10 sentence-transformers >=5.4.1
- #11 anthropic >=0.97.0
- #12 python-docx >=1.2.0
- #24 eslint ^10.4.0
- #25 @types/node ^25.9.1

### Previously Added (pre-2026-05-23)
- DSH prerequisite check in `spore.sh` — now verifies `.env`, `agents/`, `kb/`
  exist before mesh activation; runs `pre-spore-verify.py` automatically.
- `TRINITY_JWT` added to `.env.template` and `.env.example` for JWT-based
  Trinity API auth alongside `HUB_API_SECRET`.
- Missing Python deps added to `compute/requirements.txt`: fastapi, uvicorn,
  langchain, transformers, sqlalchemy, psycopg2-binary, redis, numba,
  networkx, psutil, matplotlib, scikit-learn, statsmodels.
- Shell tools (jq, yq, tree, htop, curl, wget) now documented in README Stack table.

### Fixed
- All scripts now default to `$HOME/DSH` (was `$HOME/DSH`): zshrc-dome,
  audit, daemon-watch, dome-approve, render-env, secrets-doctor,
  rotate-secrets-keychain, sovereign-secrets, export-to-dsh, finish-security,
  rollover-language-landscape, launchd plist.
- `agents/core/memory/episodic.py` and `agents/workers/queue.py` now respect
  `DOME_ROOT` env var (was hardcoded `~/DSH`).
- `agents/api/server.py` memory endpoint: `agent.memory` → `agent.mem.context()`.
- `agents/core/agent.py` `clear_memory()`: `.messages.clear()` → `.clear()`.
- `agents/core/memory/working.py` `llm_fn` type: `str` → `list[dict]` to match
  `Agent._call_llm` signature.
- DB schema in `sovereign-setup-mac.sh` now matches `register-claude.py`
  (agents table: name UNIQUE, vendor, version, surface, role, kb_path, entrypoint).
- Python version aligned across all files: README, CI, requirements comment → 3.14.
- PostgreSQL version aligned: README, MANUAL → 18 (matches setup script).
- CI workflow: actions/checkout@v4, setup-python@v5, Python 3.14, step labels fixed.
- PROTOCOLS.md: `master` → `main`.
- README Structure section: `DSH/` → `DSH/`, removed non-existent dirs
  (codebase/, models/, platforms/, projects/, software/), added actual dirs.
- Docker removed from README claims (not installed by setup script).
- `kiro-cli` and `latest` removed from package.json dependencies.
- All user-facing DSH references → DSH in MANUAL.md, INDEX.md, README.md.
- INDEX.md: removed stale refs to .audit/, /codebase, /models, /platforms,
  /projects, /software, phase1_sovereign_baseline_audit.sh. Key Paths → ~/DSH.
- kb/README.md: added missing skills/ subtree, paths → ~/DSH.
- Skill doc mismatches fixed: cognitive.md (max_chars), algorithms.md (astar),
- akashic/watcher.py: removed stale `projects` from WATCH_DIRS.
- BRIDGE.md: added JWT auth pattern, paths → ~/DSH.

### Removed
- All personal paths (`/Users/<user>/`) from every
  tracked file: .env.example, AI_INFRASTRUCTURE_MAP.md, AGENTS.md, REGISTRY.md,
  PUBLIC_PROD_HARDENING.md, CHANGELOG.md, kiro-skills.md.
- Hardcoded personal identity from finish-security.sh (GPG name → $USER),
  dome-approve.sh (usernames → $USER).
- `db/_test.txt` and `logs/akashic-watcher.log` removed from git tracking.

### Security
- `public-safety-check.sh --strict-paths` passes clean: zero secrets, zero
  personal paths, zero credential patterns in any tracked file.
- CTO Build Framework validation: 40/42 checks PASS across 6 domains.

## [Unreleased] (previous)

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
  private DSH references to `garochee33/DSH`; personal paths
  replaced with `$DOME_ROOT` or `~/DSH` defaults.
- `scripts/dome-check.sh` — macOS Keychain fallback for secrets, GPG signing
  optional (not auto-enabled), auto-commit/push removed (was destructive).
- `psql -U <username>` → `psql -U "$USER"` in MANUAL.

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
- Initial DSH / DSH foundation build.
- Python 3.11 venv with AI/ML stack (anthropic, LangChain, ChromaDB,
  sentence-transformers, PyTorch-MPS, Transformers).
- Quantum-computing stack (Qiskit, PennyLane, Cirq, QuTiP, PyQuil,
  Amazon Braket SDK).
- Local inference via MLX + Ollama.
- Agent framework in `agents/core/` (agent, orchestrator, RAG pipeline,
  registry, streaming, tracing) + memory subsystems (vector, episodic,
  working).
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
  bitboard, MERKABA signal, A.M.M.A. relay, Loihi-2 bridge).

[Unreleased]: https://github.com/garochee33/DSH/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/garochee33/DSH/releases/tag/v0.0.1
