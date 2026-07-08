# Claude in DSH — Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                     DSH (local-first)                        │
│                                                                   │
│   ┌──────────────┐   ┌──────────────┐   ┌──────────────────────┐  │
│   │   agents/    │   │   kb/        │   │      db/             │  │
│   │  ├ claude/   │◄──┤  ├ claude/   │   │  ├ dome.db (SQLite)  │  │
│   │  ├ example.py│   │  ├ kiro-…    │   │  │   ├ sessions      │  │
│   │  └ …         │   │  └ trinity-… │   │  │   ├ stack         │  │
│   └──────┬───────┘   └──────┬───────┘   │  │   └ skills (new)  │  │
│          │                  │           │  └ chroma/            │  │
│          ▼                  ▼           └──────────┬────────────┘  │
│   ┌──────────────┐   ┌──────────────┐              │               │
│   │  compute/    │   │  scripts/    │              │               │
│   │  ├ claude-…  │   │  ├ bootstrap │              │               │
│   │  └ reqs.txt  │   │  └ new-proj  │              │               │
│   └──────┬───────┘   └──────────────┘              │               │
│          │                                          │               │
│          ▼                                          ▼               │
│   ┌────────────────────────────────────────────────────────────┐   │
│   │                    .venv (Python 3.14)                     │   │
│   │   anthropic · python-docx · python-pptx · openpyxl ·       │   │
│   │   reportlab · pypdf · pdfplumber · langchain · chromadb    │   │
│   └────────────────────────────────────────────────────────────┘   │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

## Runtime surfaces

1. **Cowork mode (desktop app)** — this session. Claude has tools + skills +
   access to the user's selected workspace folder.
2. **Claude Agent SDK** — programmatic. Used by `agents/claude/runner.py` to
   invoke Claude from inside a DSH pipeline.
3. **Claude Code (CLI)** — optional terminal surface for dev work.

## Data flow for a typical task

1. User prompt → Cowork UI → Claude.
2. Claude consults `kb/claude/` for skill/tool reference.
3. Claude picks a skill (e.g. `docx`) and reads `kb/claude/skills/docx/SKILL.md`.
4. Claude writes output file into `DSH/<subdir>/<file>`.
5. Claude records a row in `db/dome.db → sessions`.
6. Claude returns a `computer://` link to the user.

## Why we mirror skills locally

The live skill mount (`/sessions/<id>/mnt/.claude/skills/`) is session-scoped
and read-only. Copying the SKILL.md files into `kb/claude/skills/` gives us:

- Offline reference (git-tracked, searchable, reviewable).
- A seed for `skill-creator` to fork and customize internal DSH skills.
- A stable path agents can point at regardless of the session id.
