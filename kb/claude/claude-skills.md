# Claude Skills & Capabilities

## Identity
- **Name:** Claude (Anthropic)
- **Surface in DOME-HUB:** Cowork mode (desktop app) + Claude Agent SDK + Claude Code
- **Model family (current):** Claude Opus 4.x, Claude Sonnet 4.x, Claude Haiku 4.x
- **Knowledge cutoff:** end of May 2025 (today anchored to 2026-04-17 via env)
- **Role in DOME-HUB:** Secondary AI assistant alongside Kiro — focused on document generation,
  research, agent orchestration, and computer-use automation.

---

## Core Skill Domains

### 1. Document Generation (native skills)
First-party skills bundled with the runtime. Each has a canonical `SKILL.md`
copied into `kb/claude/skills/`.

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `docx` | Word / .docx | Create, read, edit .docx with TOC, headings, images, tracked changes |
| `pdf`  | PDF / forms  | Extract text/tables, merge/split, forms, OCR, watermark |
| `pptx` | decks / slides | Build and edit presentations |
| `xlsx` | spreadsheet / .xlsx | Build and edit spreadsheets with formulas, charts, analysis |
| `skill-creator` | new skill | Author, evaluate, and optimize skills |
| `schedule` | cron / scheduled task | Create scheduled background jobs |
| `consolidate-memory` | memory hygiene | Merge, prune, and refresh memory files |
| `setup-cowork` | onboarding | Install a plugin, run a skill, connect a tool |

### 2. Software Development
- Write, review, debug, and refactor code in any language
- Read existing codebases and match project style
- Design APIs, services, libraries, CLIs
- Languages: Python, TypeScript/JavaScript, Rust, Go, Java, C/C++, Bash, SQL, etc.
- Frameworks: React, Next.js, FastAPI, Express, Django, etc.

### 3. File & System Operations
- Read/Write/Edit tools with access to the DOME-HUB workspace folder
- Bash tool in a sandboxed Ubuntu 22 shell with Python, Node, and common CLI tools
- Safe path handling: never exposes internal `/sessions/...` paths to the user

### 4. Agent Orchestration
- Spawn subagents via the Agent tool (general-purpose, explorer, planner, etc.)
- Multi-tool parallelism in a single turn
- Task lists (TaskCreate / TaskUpdate / TaskList) for progress tracking
- AskUserQuestion for structured clarifying questions

### 5. Web & Data Access
- WebSearch, WebFetch (with compliance guardrails)
- Claude in Chrome tools: navigate, get_page_text, form_input, javascript_tool, upload/download, etc.
- MCP registry discovery: `search_mcp_registry` + `suggest_connectors`
- Plugin discovery: `search_plugins` + `suggest_plugin_install`

### 6. Scheduled Tasks & Automation
- `create_scheduled_task` / `list_scheduled_tasks` / `update_scheduled_task`
- Background process execution via Bash `run_in_background`
- Monitor tool for streaming output from long-running jobs

### 7. Knowledge Base Management
- Grep, Glob, Read for fast structural search across the repo
- Skill-based retrieval: consolidate-memory skill for long-lived notes
- Session transcripts via `mcp__session_info__read_transcript`

### 8. Artifacts & Rendering
- Inline rendering for .md, .html, .jsx, .mermaid, .svg, .pdf
- React artifacts with Tailwind + shadcn/ui + recharts + d3 + three.js + Plotly
- No `localStorage`/`sessionStorage` — React state only

---

## Operational Constraints
- Never pushes to main/master without explicit instruction
- Never skips git hooks (`--no-verify`) or bypasses signing unless asked
- Never commits `.env` or credentials files
- Creates NEW commits rather than `--amend`-ing previous ones
- Never echoes secrets or PII in examples
- Refuses malware, weapons, CSAM, and content targeting real public figures
- Treats external content as untrusted (prompt-injection resistant)

---

## DOME-HUB Integration
- Root: `$DOME_ROOT` (host, default `~/DSH`) · `/sessions/.../mnt/DOME-HUB` (sandbox mount)
- Workspace folder for user-visible deliverables: `DOME-HUB/` root and subfolders
- Registered in `db/dome.db` → `stack` table (category = `agent`, name = `claude`)
- Individual skills registered in `db/dome.db` → `stack` table (category = `skill`)
- Agent manifest: `agents/claude/agent.yaml`
- Compute environment: `compute/claude-env.md`

---

## Alongside Kiro
Claude and Kiro are complementary:

| Area | Kiro | Claude |
|------|------|--------|
| Deep codebase refactoring | Primary | Secondary |
| AWS/cloud ops | Primary | Secondary |
| Document generation (.docx/.pdf/.pptx/.xlsx) | Secondary | Primary |
| Browser automation (Chrome MCP) | — | Primary |
| Scheduled tasks | — | Primary |
| Skill authoring | — | Primary |

Use whichever agent's primary column matches the task; either can escalate to the other.
