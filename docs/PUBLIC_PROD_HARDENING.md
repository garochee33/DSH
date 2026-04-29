# DSH — Public Prod Hardening Log

**Status:** blocking public push to `garochee33/DSH`
**Generated:** 2026-04-18
**Source of truth:** this file — update as items are resolved.

This log catalogs every gap between DSH's current state and "safe to publish."
Items are ranked by how hard they block publishability.

---

## Severity key

| Level | Meaning |
|-------|---------|
| `P0` | Push to GitHub fails until resolved |
| `P1` | Push succeeds but exposes personal identity, credentials, or legal risk |
| `P2` | Push succeeds but repo looks un-hardened to a prospective user/contributor |
| `P3` | Quality-of-life; fine for v0 but expected for mature public repo |

---

## P0 — Push blockers

### P0.1 — Large files in git history

GitHub rejects any blob ≥100 MB. Current history contains:

| Path in history | Size |
|-----------------|------|
| `google drive/models-20260417T194526Z-3-001.zip` | 159 MB |
| `google drive/models-20260417T194559Z-3-001.zip` | 159 MB |
| `google drive/FRACTAL AGI WEB OF LIFE - KNOWLEDGE PACK.zip` | 126 MB |
| `google drive/Unconfirmed 555890.crdownload` | 87 MB |
| `models/embeddings/all-MiniLM-L6-v2/model.safetensors` | 86 MB |
| `google drive/git-20260417T194735Z-3-001.zip` | 81 MB |

Removing them from the working tree (done — `git rm --cached`) does **not** rewrite history. Must purge via:

```bash
# Option A (recommended): git-filter-repo
brew install git-filter-repo
cd ~/DSH
git filter-repo --path 'google drive' --invert-paths --force
git filter-repo --path 'models/embeddings' --invert-paths --force

# Option B: orphan branch for clean single commit
git checkout --orphan clean-main
git add -A
git commit -m "feat: initial DSH public release"
git branch -D master
git branch -m master
```

### P0.2 — DOME-HUB private push also blocked

Same large files in history block the private DOME-HUB push too. Either:
- rewrite history (risks confusing collaborators)
- accept that private repo stays local-only until cleanup

**Decision needed:** rewrite both repos' history, or only DSH (public), and keep DOME-HUB local-only?

---

## P1 — Personal identity / credential exposure

### P1.1 — GitHub URL references still point to private DOME-HUB

| File | Line |
|------|------|
| `README.md` | 53, 217 |
| `MANUAL.md` | 13, 20, 365 |
| `INDEX.md` | 173 |
| `CLAUDE.md` | 5 |

**Fix:** replace with `garochee33/DSH` globally.

### P1.2 — Personal paths hardcoded in docs

| File | Line | Current | Target |
|------|------|---------|--------|
| `MANUAL.md` | 344 | `cd ~/DOME-HUB` | `cd ~/DSH` |
| `MANUAL.md` | 365 | `cd ~/DOME-HUB` | `cd ~/DSH` |
| `MANUAL.md` | 313 | `psql -U <username> -d postgres` | `psql -U "$USER" -d postgres` |
| `INDEX.md` | 166–173 | 7 rows with `~/DOME-HUB` | `$HOME/DSH/...` or `~/DSH/...` |

### P1.3 — Personal identity attribution in CLAUDE.md

`CLAUDE.md:199` — "DOME-HUB is the operator's sovereign node in the Trinity network."

`CLAUDE.md` is also `.gitignore`d already — but it's still in git history. If we purge, make sure the purge covers it everywhere.

### P1.4 — Scripts with hardcoded absolute paths

2 already fixed (`scripts/pre-spore-verify.py`, `scripts/dome-check.sh`). Still hardcoded:

| File | Notes |
|------|-------|
| `scripts/audit.sh` | line 48, 51 |
| `scripts/bootstrap.sh` | line 51 |
| `scripts/finish-security.sh` | 4 refs |
| `scripts/dome-pm.sh` | ~1 ref |
| `scripts/dome-sudo.sh` | ~1 ref |
| `scripts/optimize.sh` | 1 ref |
| `scripts/new-project.sh` | 2 refs |
| `scripts/zshrc-dome.sh` | 1 ref (`export DOME_ROOT=...`) |
| `scripts/akashic-start.sh` | 1 ref |
| `scripts/ingest.py` | hardcodes absolute home path |
| `akashic/record.py:13` | `DOME_ROOT = os.environ.get("DOME_ROOT", "~/DSH")` |
| `agents/example.py` | check for refs |

**Canonical fix pattern:**
- bash: `DOME_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"`
- python: `DOME_ROOT = pathlib.Path(__file__).resolve().parents[1]`

### P1.5 — `.env.example` documentation

`.env.example` includes real-seeming defaults (`${HOME}/DOME-HUB`) and env vars for Trinity endpoints. Add:

- A clear "DO NOT COMMIT secrets" banner at top
- Links to docs explaining each var
- Safe defaults that still work out-of-box without any keys

### P1.6 — Session log history with GPG key ID + member names

Earlier session logs (now untracked in DSH, but may still be in git history) referenced:
- GPG key ID (redacted)
- Member deposit references
- Trinity member identities

Purging history (P0.1) should remove these. Verify after purge via:
```bash
git log --all -p | grep -iE "personal-id-patterns" || echo "clean"
```

---

## P2 — Governance / repo hygiene

### P2.1 — Missing top-level governance files

None of these exist:
- `LICENSE` — which license? MIT? Apache-2.0? Custom Trinity?
- `SECURITY.md` — disclosure policy (e.g. `security@trinity-consortium.com`)
- `CONTRIBUTING.md` — how to propose changes
- `CODE_OF_CONDUCT.md` — standard Contributor Covenant or custom

### P2.2 — No CI workflow

`.github/workflows/` does not exist. Minimum for v0:
- `ci.yml` — runs `pnpm lint`, `pnpm typecheck`, `python -m pyflakes agents/ scripts/`, `pre-spore-verify.py`
- `secret-scan.yml` — gitleaks or trufflehog
- `deps-audit.yml` — `pnpm audit`, `pip-audit`

### P2.3 — Suspicious npm dep: `latest`

`package.json`:
```json
"dependencies": {
  "kiro-cli": "^0.0.1",
  "latest": "^0.2.0"
}
```

`latest` is a tiny (and unmaintained since 2019) package that prints "latest version" info. Typosquat-risk-adjacent — unlikely to be actually needed here. Remove unless there's a real caller.

Also: `kiro-cli@^0.0.1` is a 0.x package — unstable API; pin exact version.

### P2.4 — `CLAUDE.md` contradiction

`.gitignore` lists `CLAUDE.md` (line 19 — meant to be machine-local). But it was tracked in git and gets committed anyway because the ignore only stops *new* tracking, not existing.

**Fix:** after history purge, ensure `CLAUDE.md` is fully untracked. Provide `CLAUDE.md.template` in repo instead.

### P2.5 — Issue / PR templates

- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/feature_request.md`
- `.github/pull_request_template.md`

### P2.6 — Branch protection on `garochee33/DSH`

Enable in GitHub UI or `gh api`:
- Require PR review before merge to `master`/`main`
- Require status checks (CI jobs)
- Require signed commits (matches the GPG-signing protocol in PROTOCOLS.md)
- Restrict force-push

### P2.7 — Secret scanning + Dependabot

- Enable GitHub secret scanning (org/repo setting)
- Add `.github/dependabot.yml` for pip + npm

---

## P3 — Polish / expected for mature public repo

### P3.1 — Rename default branch

Current: `master`. Public convention: `main`. `gh repo create` defaulted to whatever the local used. Rename post-push via `gh api -X PATCH repos/garochee33/DSH -f default_branch=main` or leave as-is.

### P3.2 — README public-audience rewrite

Current README is great but written assuming reader = Trinity member. Public version should:
- Lead with DSH name + "Deep Space Habitat" acronym framing (already discussed)
- Clearly separate: "what DSH gives you locally" (scope A) vs "what the mesh upgrade gives you" (scope B via `spore.sh`)
- Remove any "Trinity Consortium — member only" lines unless they're explicit CTAs

### P3.3 — `docs/` structure

Currently DSH has no `docs/`. Consider seeding:
- `docs/ARCHITECTURE.md` — the two-phase architecture (DSH = local / `spore.sh` = mesh)
- `docs/SECURITY.md` — hardening checklist (this file's companion, for users)
- `docs/DEVELOPING.md` — how to build on top of DSH
- `docs/PROVIDERS.md` — MLX/Ollama/Anthropic/OpenAI tradeoffs

### P3.4 — Release workflow

- `CHANGELOG.md`
- semantic version tag (`v0.1.0`) on first public push
- GitHub release notes
- Homebrew formula (optional, enables `brew install dsh`)

### P3.5 — `spore.sh` public vs private

`spore.sh` embeds `__SPORE_TOKEN__` / `__USER_ID__` placeholders. Fine to keep in public — users run:
```bash
curl -fsSL https://trinity-consortium.com/api/compute/spore/download/<TOKEN> | bash
```
which fills in the placeholders server-side.

**But** — consider whether the public should see the engine implementation details in `spore.sh` (E8 lattice, bitboard, Mandelbulb internals) vs only the activation protocol. Current `spore.sh` leans toward the former. If Trinity wants IP stayed on the server, the public `spore.sh` should be a thin bootstrap that downloads the real logic after auth.

### P3.6 — Ollama bootstrap script

`README.md` says default model is `qwen3.5:9b` (per `.env.example`). No script to pull it. Add `scripts/ollama-init.sh` that detects RAM tier and pulls the best-fit model (llama3.1:8b for ≤16GB, qwen2.5-coder:14b for ≥18GB).

### P3.7 — Telemetry disclaimer

Public README should affirm "no telemetry. No analytics. No phone-home. No LLM call logging to Anthropic/OpenAI when running in `DOME_PROVIDER=local`." — since the name implies sovereignty.

---

## Action plan (in order)

1. **Purge history** (P0.1, P0.2) — `git filter-repo` on DSH; decide DOME-HUB separately
2. **Run `pnpm audit` + `pip-audit`** and fix findings
3. **Fix 11 hardcoded-path scripts** (P1.4) — follow canonical fix pattern
4. **Globalize GitHub URL references** (P1.1) — sed across docs
5. **Strip personal identity from docs** (P1.2, P1.3) — fresh voice, no personal names
6. **Add `LICENSE`, `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`** (P2.1)
7. **Add CI workflow** (P2.2)
8. **Remove `latest` npm dep** (P2.3)
9. **Add branch protection + secret scanning + dependabot** (P2.6, P2.7)
10. **Rebase public README for public audience** (P3.2)
11. **Squash-push clean history to `garochee33/DSH`**

Each step should be a separate commit/PR so hardening is auditable.

---

## Minimum viable first public push

If the goal is just "get *something* public pushed to `garochee33/DSH`" without full hardening:

1. Do **P0.1** only (purge large files from history)
2. Push whatever's left
3. Tag `v0.0.1-alpha` — labeled "not production-ready"
4. Track the remaining items in GitHub Issues

This gets a shell repo up in ~10 min without doing the full identity sweep.

Decision required: **full hardening first, or alpha push now + iterate?**
