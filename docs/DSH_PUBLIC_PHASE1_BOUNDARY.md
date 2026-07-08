# DSH (public) — Phase 1 vs Phase 2 boundary

**Phase 1 — default public `garochee33/DSH` checkout**

- **Purpose:** sovereign local lab (Ollama/MLX, agents API, Chroma ingest, compute sims) **without** shipping Trinity Consortium production topology, proprietary KB mirrors, mesh credentials, or internal architecture audits.
- **What the export excludes** (see `config/public-export.denylist` and `PREFIX:` rules in `scripts/export-to-dsh.sh`):
  - Entire **`kb/trinity-unified-ai/`** tree (TU-AI KB API docs, engine catalogs, knowledge-base slice).
  - **`kb/developer-context.md`** (member-node / Trinity infrastructure narrative).
  - **`docs/architecture-audit-2026-05-12/`** (internal CTO-style audit; may cite paths and production posture).
  - **`docs/DSH-ARCHITECTURE.md`** (full internal architecture reference).
  - **`agents/trinity/`** adapter (consortium-specific surface; Phase 2 opt-in only).
- **Secrets:** real `.env` never ships — only `.env.example` / `.env.template`. Trinity mesh variables are **commented** in those templates (Phase 2); Phase 1 leaves code defaults (local placeholders). Run `pnpm public:check` before any public push.
- **Git:** `.gitignore` must keep `.env`, `db/`, `models/`, `agents/core/.mesh/`, logs, keys, and machine-local overlays out of git. Curated `AGENTS.md` in the public tree **should** be committed (not gitignored).

**Phase 2 — Trinity unified stack (opt-in + subscription)**

- Obtain **tier / subscription** credentials from Trinity (per your commercial / member program — not documented in this public repo).
- Set **`SPORE_TOKEN`**, **`USER_ID`**, and mesh-related secrets per operator runbook (private `MANUAL.md` / Trinity onboarding — not in default DSH export).
- Run **`spore.sh`** from the repo root after **`python3 scripts/pre-spore-verify.py`** passes. That script may switch from DSH-local mode to mesh-connected mode when real tokens are present.
- **Production mesh peer** (HMAC, retries): use private `scripts/mycelium-signal.sh` when operating a bound node (vendored in full DSH; not required for Phase 1 reading).

**Verification**

```bash
pnpm public:check   # stages allowlist − denylist; blocks prod IPv4 literals in that slice
bash scripts/export-to-dsh.sh   # dry-run; inspect diff before --apply
```

**Policy owner:** tighten `config/public-export.denylist` whenever a new path would leak Trinity IP, production API hosts, internal DB layouts, or subscription-only tooling into the public tree.
