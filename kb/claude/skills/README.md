# Claude Skills — Local Mirror

Offline mirror of the skills Claude has access to in this DOME-HUB environment.
Copied from the session mount at `/sessions/<id>/mnt/.claude/skills/` so the repo
can reference them without an active session.

Each subfolder is a complete skill bundle:

| Folder | SKILL.md purpose |
|--------|------------------|
| `docx/` | Word document creation, editing, tracked changes, forms |
| `pdf/`  | PDF extract, merge, split, forms, OCR, watermark |
| `pptx/` | Slide deck creation and editing |
| `xlsx/` | Spreadsheet creation, formulas, charts, analysis |
| `skill-creator/` | Author, evaluate, and optimize skills (includes agents, eval viewer) |
| `schedule/` | Create scheduled / recurring tasks |
| `setup-cowork/` | Guided onboarding — install plugin, try a skill, connect tools |
| `consolidate-memory/` | Periodic memory hygiene pass |

## Structure inside a skill

```
<skill>/
├── SKILL.md          # frontmatter + instructions (always present)
├── LICENSE.txt       # Anthropic proprietary license
├── scripts/          # helper Python scripts (where applicable)
└── references/       # extra documentation (skill-creator only)
```

## How Claude uses these

1. A user request triggers a skill match against the `description` in each SKILL.md.
2. Claude invokes the skill (via the `Skill` tool or reads the SKILL.md directly).
3. Skill scripts are executed from the live session mount, not this mirror — this
   folder is a **reference / audit copy**, not an execution path.

## Updating

Re-run `scripts/sync-claude-skills.sh` (see below) to refresh from the live mount.

```bash
bash scripts/sync-claude-skills.sh
```
