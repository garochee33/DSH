# Repo Flow: Private DOME-HUB -> Public DSH

## Canonical Roles

- `DOME-HUB` (`~/DOME-HUB`) is the private canonical repo.
- `DSH` (`~/DSH`) is the public sanitized distribution.
- Direction of truth is one-way by default: `DOME-HUB -> DSH`.

## Export Pipeline

Run from `~/DOME-HUB`.

```bash
# 1) Safety gate only (current repo)
pnpm public:check

# 2) Build export set + safety check + diff preview (no writes)
pnpm public:export:dry

# 3) Apply overlay sync into DSH (no deletions)
pnpm public:export

# 4) Optional strict mirror (deletes files in DSH not in export set)
pnpm public:export:prune
```

## Policy Files

- Allowlist: `config/public-export.allowlist`
- Denylist: `config/public-export.denylist`

Rules:
- Add any newly open-source-safe path to allowlist.
- Add private, machine-local, or sensitive paths to denylist.
- If a file appears in both, denylist wins.
- `README.md`, `MANUAL.md`, and `.gitignore` are denylisted to preserve DSH public-facing identity and contributor hygiene policy.

## Safety Gate Coverage

`public-safety-check.sh` blocks export when it detects:

- forbidden secret-like files (`.env`, key/cert files, etc.)
- high-confidence credential signatures
- direct long-form API key assignments
- absolute local path leaks for current machine home path

Optional stricter path enforcement:

```bash
bash scripts/public-safety-check.sh --source . --strict-paths
```

## Recommended Release Routine

1. Work in `DOME-HUB` as private canonical.
2. Run `pnpm check` and `pnpm public:check`.
3. Run `pnpm public:export:dry` and inspect diff.
4. Run `pnpm public:export`.
5. Review and commit inside `~/DSH`.
