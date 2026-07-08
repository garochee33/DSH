# AGENT GUARDRAILS — Trinity Consortium Codebase
# Last updated: 2026-05-04 by Kiro CLI
# This file MUST be read by any agent (Kiro, Codex, Claude, Cursor, or other)
# before making changes to any Trinity repo.

## Golden Rule
**Never fix something that breaks something else.**
Every change must be cross-checked against all affected systems before commit.

## Pre-Change Checklist
Before modifying ANY file, the agent MUST:

1. **Read this file** and the repo's CONTEXT.md / README.md
2. **Check git status** — know what's dirty, what branch you're on
3. **Run the build** — `npx tsc --noEmit` for TS, `python3 -m py_compile` for Python
4. **Run tests** — `python3 -m pytest tests/ -q` for DSH, relevant tests for others
6. **Identify blast radius** — which containers, services, or users are affected?

## Post-Change Checklist
After modifying ANY file, the agent MUST:

1. **TypeScript check** — `npx tsc --noEmit` must pass (ignore pre-existing client errors)
2. **Python check** — `python3 -m py_compile` on changed .py files
3. **Run tests** — all existing tests must still pass
4. **Safety check** (DSH only) — `bash scripts/public-safety-check.sh --strict-paths`
5. **No personal paths** — grep for `/Users/`, usernames, API keys before commit
6. **Verify production** after deploy — health endpoint, container status, log check

## Repo Rules

### DSH — PUBLIC REPO
- **Branch:** main
- **Status:** SHIPPED — do not touch unless critical fix
- **Tests:** 33 passing, 1 skipped
- **CI:** 5 jobs (TS lint, Python+tests, gitleaks, dep audit, Windows)
- **Safety:** `bash scripts/public-safety-check.sh --strict-paths` must pass
- **No personal paths, no secrets, no DSH references**

### DSH (~/DSH) — PRIVATE REPO
- **Branch:** master
- **home/ is gitignored** — contains nested repos (DSH, trinity-unified-ai)
- **kiro-cli stays in package.json** (removed only from DSH public)

- **Branch:** main
- **Deploy:** rsync + docker compose (NOT git pull — server git is broken)
- **TS check:** `npx tsc --noEmit` — ignore client/ errors from other agents
- **Server changes require rebuild:** `docker compose --env-file .env.hetzner -f docker-compose.hetzner.yml up -d --build app`
- **Another agent may be working here** — check dirty files before touching

### trinity-unified-ai — KB API
- **Branch:** master
- **KB API Dockerfile:** `api/Dockerfile` — uses `--no-frozen-lockfile`
- **Changes require:** rsync to server + rebuild kb-api container

## Production Deployment

> **Phase 2 (Trinity Mesh):** Production deployment, mesh peer connectivity, and
> infrastructure access require a Trinity Consortium subscription. Run `spore.sh`
> with valid `SPORE_TOKEN` and `USER_ID` to connect your node to the E8 Mycelium

### Critical Metrics to Monitor
- SpectralMonitor CRITICALs: should be ≤1 (initial tick)
- Health endpoint: must return `{"status":"ok"}`
- All 7 containers must be healthy/running

## Known Issues (Do NOT Re-Fix)
These are known states, not bugs:

1. **Mandelbulb coherence 0.22** — correct (escapeIter/maxIter ratio)
2. **Julia routes = 1 after restart** — cold start, repopulates with traffic
3. **Fractal fragments = 1** — ingest pipeline needs work, not a code bug
4. **KB API `clifford` module missing** — non-critical, E8 prewarm skipped
5. **SpectralMonitor 1 CRITICAL on startup** — initial tick before sync detection
6. **Mesh handshake 401 with JWT** — by design, uses HMAC not JWT
7. **BOUNDARY_LOW "mismatch"** — FALSE FINDING, both CPU/GPU use 0.2

## GPG Signing
- Disabled globally: `git config --global commit.gpgsign false`
- Use: `git -c commit.gpgsign=false commit -m "msg"`
- Key 3549CD92A76B79A8 exists but pinentry-mac fails in non-interactive shells

## File Sensitivity
- `.env`, `.env.hetzner`, `.env.local` — NEVER commit, NEVER echo values
- `certs/` — TLS certificates, never commit
- `config.json` in `~/.trinity-spore/` — contains spore token, chmod 600
