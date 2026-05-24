# Cursor Agent

Real cursor-agent runner inside DOME-HUB. Shells out to the local `cursor-agent` CLI.

## Verified state (2026-04-26)

- Binary: `~/.local/bin/cursor-agent` (version `2026.02.27-e7d2ef6`)
- Auth: macOS Keychain — `cursor-access-token` + `cursor-refresh-token` (auto-discovered)
- Optional override: `CURSOR_API_KEY` env

## Usage

```bash
# Full mode (write + shell tools)
python agents/cursor/runner.py --prompt "Add a typecheck script to package.json"

# Plan mode (read-only)
python agents/cursor/runner.py --prompt "Plan the refactor of server/ai/orchestration-engine.ts" --mode plan

# Ask mode (Q&A only)
python agents/cursor/runner.py --prompt "Explain how amma-self-heal.ts works" --mode ask

# Working directory override
python agents/cursor/runner.py --prompt "..." --workdir ~/projects/trinity-consortium
```

## Output formats

| Format | Use case |
|---|---|
| `json` (default) | Programmatic — extracts assistant text |
| `text` | Human-readable raw output |
| `stream-json` | Stream of partial JSON deltas (advanced) |

## Modes

| Mode | Tool access |
|---|---|
| `full` (default) | Read + write + shell |
| `plan` | Read-only; produces a plan, no edits |
| `ask` | Q&A only |

## Programmatic use

```python
from pathlib import Path

from agents.cursor import CursorRunner, run

# One-shot
text = run("Explain the AMMA Sacred Geometry Classifier")

# Reusable
runner = CursorRunner(mode="plan", workdir=str(Path.home() / "projects" / "trinity-consortium"))
plan_text = runner.run("Refactor amma-self-heal.ts for tier separation")
```

## Constraints

- Never bypass git hooks (cursor-agent honors repo hooks)
- Never commit secrets (auth lives in Keychain only)
- Refuses: malware, WMD, CSAM (per agent.yaml)
