# Claude File Handling Guide

Concise rules for how Claude creates, reads, and delivers files inside DOME-HUB.

---

## Paths

| Path | Role |
|------|------|
| `/sessions/<id>/` | Claude's scratch space. Not visible to the user. |
| `/sessions/<id>/mnt/DOME-HUB/` | The user's workspace folder. Persistent on the host. Final deliverables go here. |
| `/sessions/<id>/mnt/uploads/` | Files the user uploaded to the chat. |
| `/sessions/<id>/mnt/.claude/skills/` | Built-in SKILL.md files (read-only mount). |

Never reveal internal `/sessions/...` paths in user-facing messages —
refer to them as "my working folder" or "the folder you selected".

---

## Create vs. edit

- **Create new files:** use the `Write` tool. Must be a fresh path.
- **Modify existing files:** always `Read` first, then use `Edit` (exact-string replace).
- Re-writing an existing file with `Write` requires a `Read` first.

## Trigger matrix

| Request contains | File type | Notes |
|------------------|-----------|-------|
| "write a document/report/post" | `.md` or `.docx` | Use `docx` skill for polished output. |
| "make a presentation/deck" | `.pptx` | Always load the `pptx` skill first. |
| "create a spreadsheet/budget" | `.xlsx` | Always load the `xlsx` skill first. |
| "fill/extract from PDF" | `.pdf` | Always load the `pdf` skill first. |
| "create a component/script" | language-specific | `.py`, `.jsx`, `.ts`, etc. |

## Output strategy by length

- **< 100 lines** → write directly to `DOME-HUB/` in one call.
- **> 100 lines** → create an empty file in `DOME-HUB/`, then fill it with iterative `Edit`s.

## Sharing files with the user

Use the `computer://` URL scheme and short, verb-first link text:

```
[View your report](computer:///sessions/<id>/mnt/DOME-HUB/report.docx)
```

- One link per deliverable.
- No lengthy post-amble explaining the file — the user can open it themselves.
- Do not link folders; link individual files.

## Uploaded files

| Extension | Already in context? | Action |
|-----------|--------------------|--------|
| `.md`, `.txt`, `.html`, `.csv` | Yes (as text) | Use the text directly. |
| `.png`, `.pdf` | Yes (as image) | Vision-read directly. |
| everything else | No | Use `Read` from `/mnt/uploads/`. |

## Package installation in the sandbox

- `npm install -g <pkg>` — persistent across shell calls.
- `pip install <pkg> --break-system-packages` — required flag on the sandbox image.
- For complex Python projects, create a venv.

## Artifacts (inline rendering)

Special file types render inline in Cowork:

- `.md`, `.html`, `.jsx`, `.mermaid`, `.svg`, `.pdf`

For React artifacts:

- Single file, default export, no required props.
- Tailwind core utilities only (no custom classes).
- No `localStorage` / `sessionStorage`.
- Allowed libraries: lucide-react, recharts, mathjs, lodash, d3, plotly, three@r128,
  papaparse, sheetjs, shadcn/ui, chart.js, tone, mammoth, tensorflow.
