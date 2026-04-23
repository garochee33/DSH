# Claude Compute Environment

Specification for the local Python environment that Claude (via the
Claude Agent SDK) runs in when invoked from inside DOME-HUB.

---

## Runtime

- **Python:** 3.11.9 (pinned by `DOME-HUB/.python-version`)
- **Venv:** `DOME-HUB/.venv` (root) — shared with the rest of DOME-HUB
- **Node:** 20 (pinned by `.nvmrc`, needed for the `pptxgenjs` slide path)
- **OS:** macOS 26.3 (Apple M3 Pro, MPS-capable) · Linux sandbox for Bash tool

## Install

```bash
cd ~/DOME-HUB
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
| `CLAUDE_AGENT_WORKDIR` | Absolute path Claude treats as its workspace. Default: `DOME-HUB/`. |
| `CLAUDE_AGENT_SKILL_DIR` | Path to mirror skill bundles. Default: `DOME-HUB/kb/claude/skills`. |

## Compute profile

| Resource | Value |
|----------|-------|
| CPU      | 12-core M4 Pro (8P + 4E, ARM64) |
| GPU      | 16-core (Apple MPS) |
| Neural Engine | 38 TOPS |
| RAM      | 24 GB unified memory |
| Disk     | FileVault-encrypted |

For PyTorch workloads use the MPS backend (see `MANUAL.md § 5`).

## Smoke test

After install, run:

```bash
python agents/claude/runner.py --prompt "Say hello and list your top 3 skills."
```

Expected: a 3-5 sentence response and a zero exit code.
