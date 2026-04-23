# DOME-HUB Compute

Infrastructure and compute-environment definitions for everything running
inside DOME-HUB.

## Files

| File | Purpose |
|------|---------|
| `claude-env.md` | Spec for the Claude (Anthropic) compute environment |
| `requirements.txt` | Pinned Python deps shared by the root `.venv` |
| `bootstrap-claude.sh` | Idempotent install + register script |

## Running

```bash
cd ~/DOME-HUB
bash compute/bootstrap-claude.sh
```

After bootstrap, Claude's entrypoint is `agents/claude/runner.py`.
