# Claude Compute Environment

Specification for the local Python environment that Claude (via the
Claude Agent SDK) runs in when invoked from inside DSH.

---

## Runtime

- **Python:** 3.11.9 (pinned by `DSH/.python-version`)
- **Venv:** `DSH/.venv` (root) — shared with the rest of DSH
- **Node:** 20 (pinned by `.nvmrc`, needed for the `pptxgenjs` slide path)
- **OS:** macOS (Apple **M5 Pro**, MPS-capable; DSH is portable across Apple Silicon) · Linux sandbox for Bash tool

## Install

```bash
cd ~/DSH
source .venv/bin/activate
pip install -r compute/requirements.txt

# Optional: Node toolchain for pptxgenjs-based presentation path
nvm use
pnpm install
```

A one-shot bootstrap is provided:

```bash
bash compute/bootstrap-claude.sh
```

## Environment variables

Copy `.env.example` → `.env` at the repo root (never commit `.env`).

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` | Required. Use `pass dome/anthropic-key` (GPG-encrypted) and export at shell time. |
| `ANTHROPIC_MODEL`   | Default: `claude-opus-4-6`. Override per-run. |
| `CLAUDE_AGENT_WORKDIR` | Absolute path Claude treats as its workspace. Default: `DSH/`. |
| `CLAUDE_AGENT_SKILL_DIR` | Path to mirror skill bundles. Default: `DSH/kb/claude/skills`. |

## Compute profile

| Resource | Value |
|----------|-------|
| CPU      | 18-core M5 Pro (6S + 12P, ARM64) |
| GPU      | 18-core (Apple MPS) |
| Neural Engine | 40+ TOPS |
| RAM      | 48 GB unified memory |
| Disk     | FileVault-encrypted |

For PyTorch workloads use the MPS backend (see `MANUAL.md § 5`).

## Smoke test

After install, run:

```bash
python agents/claude/runner.py --prompt "Say hello and list your top 3 skills."
```

Expected: a 3-5 sentence response and a zero exit code.
