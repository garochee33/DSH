# agents/claude

Local entrypoint for Anthropic's Claude inside DOME-HUB.

## Files

| File | Purpose |
|------|---------|
| `agent.yaml` | Agent manifest (name, model, skills, kb path) |
| `runner.py` | CLI entrypoint — `python runner.py --prompt "..."` |
| `__init__.py` | Package marker |

## Usage

```bash
# From DOME-HUB root
source .venv/bin/activate
python agents/claude/runner.py --prompt "Summarize kb/claude/architecture.md"
```

Add `--model claude-opus-4-6` / `claude-sonnet-4-6` / `claude-haiku-4-5-20251001`
to pick a model. Defaults to whatever `ANTHROPIC_MODEL` is set to, or
`claude-opus-4-6`.

## Where the skills come from

Two layers:

1. **Built-in skills** (docx/pdf/pptx/xlsx/…) — referenced by path to
   `kb/claude/skills/<name>/SKILL.md`. Claude reads them at the top of a run.
2. **Custom DOME-HUB skills** — drop a new `<name>/SKILL.md` into
   `kb/claude/skills/` and re-run `scripts/register-claude.py`.

## Related

- Knowledge base: `kb/claude/`
- Compute env: `compute/claude-env.md`
- Registry: `db/dome.db` → `agents`, `skills`, `tools` tables
