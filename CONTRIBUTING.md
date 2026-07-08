# Contributing to DSH

DSH (Dome Sovereign Hub) is a sovereign, local-first development environment.
Contributions that strengthen sovereignty, harden security, or broaden local-
first tooling are welcome.

Contributions that introduce mandatory cloud dependencies, tracking,
telemetry, or proprietary lock-ins will not be merged.

## Before you contribute

Read:
- `README.md` — what DSH is for
- `PROTOCOLS.md` — the sovereignty and security contract
- `SECURITY.md` — security posture + reporting
- `docs/PUBLIC_PROD_HARDENING.md` — what's still pending

## How to propose changes

### 1. Open an issue first

For non-trivial changes, open an issue to discuss the approach before
writing code. This prevents wasted effort if the direction is off.

### 2. Fork + branch

Work in a feature branch named `<type>/<short-description>`, where `<type>`
is one of:

- `feat/` — new capability
- `fix/` — bug fix
- `security/` — security hardening
- `docs/` — documentation
- `refactor/` — internal cleanup, no behavior change
- `test/` — tests only
- `chore/` — dependencies, build, CI, release

### 3. Local checks

Before opening a PR, run:

```bash
cd "$DOME_ROOT"   # e.g. ~/DSH
source .venv/bin/activate

# Python + TypeScript lint
pnpm lint
pnpm typecheck

# Skill + dep verification
python3 scripts/pre-spore-verify.py

# Full protocol + security check
bash scripts/dome-check.sh
bash scripts/audit.sh
```

All five must pass. CI will re-run them on your PR.

### 4. Commit message format

Use Conventional Commits. Examples:

- `feat(agents): add sovereign-audit skill`
- `fix(scripts): portable DOME_ROOT in audit.sh`
- `security(mesh): verify peer signature before handshake`
- `docs(manual): add Ollama troubleshooting section`
- `chore(deps): bump chromadb to 0.5.5`

If your change affects behavior, include a `BREAKING CHANGE:` footer.

Signed commits (GPG) are preferred — see `SECURITY.md` for the hardening
checklist.

### 5. Pull request checklist

In your PR description, confirm:

- [ ] Linked to an issue (if non-trivial)
- [ ] Branch name follows `<type>/<description>` convention
- [ ] All local checks pass (`pnpm lint`, `typecheck`, `pre-spore-verify`,
      `dome-check`, `audit`)
- [ ] New dependencies are justified (no cloud lock-in; prefer local-first)
- [ ] Docs updated (`README`, `MANUAL`, `INDEX`, or relevant `kb/`)
- [ ] Tests added/updated if applicable
- [ ] No secrets, credentials, or machine-identifying data committed
- [ ] Git history is clean (squash WIP commits; no `.DS_Store`, no large
      binaries)

## What we won't merge

- Anything that adds required telemetry or "phone-home" behavior
- Anything that hardcodes a cloud-provider secret
- Anything that breaks `DOME_PROVIDER=local` air-gapped mode
- Anything under 100 MB that bloats `.git` history (git-lfs welcome for
  weights / binaries)
- Style-only changes that ignore the existing conventions

## Code of conduct

See `CODE_OF_CONDUCT.md`. In short: be technical, be direct, be sovereign.
Disagreements are welcome on merits; ad-hominem is not.

## Releases

DSH uses semantic versioning (`v0.x.y` until `v1.0.0`).

- Patch releases: bug fixes, docs
- Minor releases: new capabilities, new skills, new engines
- Major releases: breaking changes to API, CLI, or setup contract

Release notes live in `CHANGELOG.md` and as GitHub Releases.

Thank you for contributing to sovereign, local-first development.
