# DOME-HUB Phase 2 Tasks (Execution Tracker)

- Owner: Enzo + active agents
- Updated: 2026-04-22
- Context: post Phase-1 audit + cross-repo stabilization

## Current State

- `DOME-HUB` is functioning as the private canonical local environment.
- `DSH` remains protected as public mirror with denylist safeguards.
- `trinity-consortium` and `trinity-unified-ai` both contain active concurrent workstreams.

## Must-Do Next (P0)

- [ ] Run unified-ai full tests on local machine with required services running (Redis, Postgres, Ollama).
- [ ] Resolve any runtime test failures not attributable to environment restrictions.
- [ ] Commit scoped updates only (no broad `git add -A`) in each repo.
- [ ] Push all scoped commits and verify remote branch heads.

## Stabilization (P1)

- [ ] Decide canonical DB client contract in `trinity-unified-ai` (`drizzle` vs raw `pg.Pool`) and align engine usage.
- [ ] Promote `scripts/trinity-workspaces.sh` + `trinity4()` docs into public-facing operational guide.
- [ ] Add a reproducible smoke script that validates all 4 terminal workspaces quickly.

## Governance / Documentation (P1)

- [ ] Keep `.audit/worklogs/chat_session_2026-04-22_codex.md` as single source of this session history.
- [ ] Keep `.audit/reports/cross_validation_state_2026-04-22.md` up to date after each major validation run.
- [ ] Update `INDEX.md` whenever new scripts/reports are added to root-level operations.

## Release Safety Checks

Run before each public/private sync or push wave:

```bash
cd ~/DOME-HUB
pnpm typecheck
pnpm public:check
pnpm public:export:dry
bash scripts/public-safety-check.sh --source . --strict-paths
```

