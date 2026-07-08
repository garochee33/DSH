## Summary

<!-- 1–3 bullet points: what this PR changes and why -->

## Linked issue

Closes #

## Type

- [ ] feat — new capability
- [ ] fix — bug fix
- [ ] security — security hardening
- [ ] docs — documentation only
- [ ] refactor — internal cleanup, no behavior change
- [ ] test — tests only
- [ ] chore — deps, build, CI, release

## Checklist

- [ ] Branch name follows `<type>/<short-description>`
- [ ] `pnpm lint` passes
- [ ] `pnpm typecheck` passes
- [ ] `python3 scripts/pre-spore-verify.py` passes (27/27)
- [ ] `bash scripts/audit.sh` returns green
- [ ] `bash scripts/dome-check.sh` returns green
- [ ] Docs updated (`README`, `MANUAL`, `INDEX`, or relevant `kb/`)
- [ ] Tests added/updated if applicable
- [ ] No secrets, credentials, or machine-identifying data committed
- [ ] No new large binaries (>50 MB) — use git-lfs if weights are involved
- [ ] Git history is clean (squash WIP commits)

## Sovereignty impact

- [ ] Preserves `DOME_PROVIDER=local` air-gapped mode
- [ ] No new mandatory cloud API dependency
- [ ] No new telemetry / phone-home
- [ ] No closed-source runtime component

## Test plan

<!-- What exactly did you run to confirm this works? -->
