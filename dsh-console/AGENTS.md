<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->
---

## Canonical Skill Library — single source of truth

Whichever agent you are (Kiro, Codex, Cursor, Kimi, OpenClaw, Claude Code, Trinity swarm, any LLM):

1. **`~/DOME-HUB/home/projects/trinity-consortium/skills/MASTER_INDEX.md`** — 67 unique skills aggregated across 11 tiers, 263 trigger keywords inverted-indexed.
2. **`~/DOME-HUB/home/projects/trinity-consortium/skills/SKILL_QUALITY_AUDIT.md`** — current quality tiers (9 A · 38 B · 0 C · 0 D · avg 72.6).
3. **Your tier's local `MASTER_INDEX.md`** — same content mirrored to `~/.codex/skills/`, `~/.cursor/skills/`, `~/.config/agents/skills/`, etc.

Load order: this AGENTS.md → MASTER_INDEX.md → specific SKILL.md → DOME-HUB CLAUDE.md (sovereign rules) → trinity-consortium CLAUDE.md (production rules).
