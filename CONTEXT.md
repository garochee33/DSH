# DSH — Agent Context

> For AI assistants working in this repo. Humans: see README.md and MANUAL.md.

## What is DSH

DSH (Dome Sovereign Hub) is a sovereign development environment installer.
One command sets up a hardened, local-first AI stack with quantum computing,
agent framework, and security posture — on any Mac or Windows machine.

DSH is also the prerequisite for `spore.sh` → Trinity Consortium mesh access.

## Quick Reference

| Item | Detail |
|------|--------|
| Languages | Python 3.14, Node 20, TypeScript, Go, Rust |
| AI Stack | Ollama (devstral), MLX, Claude, LangChain, ChromaDB |
| Databases | PostgreSQL 18, Redis, SQLite, ChromaDB |
| Agents | 6 pre-built (researcher, coder, analyst, planner, kb_agent, local) |
| Tools | 10 (web_search, web_fetch, shell_run, file_read/write/list, code_run, db_query/write, kb_search) |
| Skills | 10 core + 7 extended (math, compute, sacred_geometry, fractals, algorithms, frequency, cognitive) |
| API | FastAPI on port 8000 (`pnpm serve`) |
| Tests | `pnpm test` — 34 pytest tests |

## Key Entry Points

- `scripts/sovereign-setup-mac.sh` — macOS installer (21 phases, cinematic mode)
- `scripts/sovereign-setup-windows.ps1` — Windows installer (17 phases)
- `agents/core/registry.py` — agent registry (6 agents)
- `agents/core/agent.py` — base Agent class
- `agents/api/server.py` — FastAPI HTTP server
- `agents/core/trinity_client.py` — Trinity mesh client (local fallback)
- `scripts/dome-check.sh` — protocol enforcer
- `spore.sh` — Trinity mesh activation (requires DSH setup first)

## Commands

```bash
pnpm check      # protocol check
pnpm test       # run 34 tests
pnpm serve      # start API server
pnpm ingest     # index KB into ChromaDB
pnpm lint       # ESLint
pnpm typecheck  # tsc --noEmit
```

## Environment

- `DOME_ROOT` — repo root (auto-detected or `$HOME/DSH`)
- `DOME_PROVIDER` — `local` | `claude` | `mixed` (default: mixed)
- `DOME_LOCAL_MODEL` — Ollama model (default: devstral:latest)
- `.env` created from `.env.example` at setup time

## Rules for Agents

1. Never commit secrets or API keys
2. Run `pnpm test` after code changes
3. Use `DOME_ROOT` env var for paths — never hardcode absolute paths
4. All Python files must pass `py_compile`
5. All TypeScript must pass `tsc --noEmit`
6. Check `scripts/public-safety-check.sh --strict-paths` before any public-facing change
