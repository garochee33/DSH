---
status: active
updated: 2026-03-24
tags: []
related: []
---

# Unified AI System - Full Discovery Index
# Updated: Sat Mar 21 16:22:32 EDT 2026

## 📊 Statistics

| Component | Count | Location |
|-----------|-------|----------|
| **AI Files** |      320 | `ai-filesystem/` |
| **DB Tables** | 269 | `database/schema-full.ts` |
| **Agent Tools** | 21 | `ai-filesystem/agent-tools/` |
| **Engines** | 21 | `ai-filesystem/engines/` |
| **Swarm Modules** | 13 | `ai-filesystem/swarm/` |
| **API Providers** | 4 | `secrets/providers.json` |
| **Local Models** | 4 | Ollama |

## 🗂️ Directory Structure

```
~/.unified-ai/
├── AGENTS.md                          # Main documentation
├── STATUS.md                          # System status
├── FULL_DISCOVERY_INDEX.md            # This file
│
├── agents/
│   ├── amma/                         # A.M.M.A. self-healing
│   ├── sovereign/                    # Sovereign OS
│   ├── e8/                           # E8 Matrix
│   ├── monica/                       # Monica AI Router ⭐ NEW
│   └── agent-router/                 # Agent Router ⭐ NEW
│
├── ai-filesystem/                    # ⭐ NEW: 320 files
│   ├── MANIFEST.md
│   ├── agent-tools/                  # 21 tool files
│   ├── engines/                      # 21 engines
│   ├── swarm/                        # 13 modules
│   ├── bitboard/                     # E8 ecosystem
│   ├── core/                         # Core infrastructure
│   └── womb/                         # Womb-specific
│
├── database/                         # ⭐ NEW: 158 tables
│   ├── schema-full.ts
│   ├── TABLES_INDEX.txt
│   └── SCHEMA.md
│
├── agent-prompts/                    # ⭐ NEW
│   ├── codex_audit_prompt.md
│   ├── cursor_modernization_prompt.md
│   ├── reviewer_governance_prompt.md
│   ├── RUNBOOK.md
│   └── SYSTEM.md
│
├── knowledge-base/                   # ⭐ NEW
│   ├── INDEX.md
│   ├── PACKAGES.md
│   ├── PROJECTS.md
│   ├── SOURCES.md
│   └── WOMB.md
│
├── orchestration/
│   ├── agent-router.ts
│   ├── unified-cli.ts
│   ├── swarm/
│   │   └── config.toml
│   └── model-router.yaml
│
├── memory/
│   └── memory-manager.ts
│
├── skills/                           # 21 skills
│   ├── trinity-coding-standards/
│   ├── trinity-repo-navigator/
│   ├── verification-validation/
│   ├── end-to-end-wiring/
│   ├── v2/                          # 16 specialized
│   └── design-architect/
│
├── mcp/
│   └── unified-mcp.json
│
└── secrets/
    └── providers.json
```

## 🚀 Quick Access

### Monica AI
```bash
cat ~/.unified-ai/agents/monica/monica-brain.md
cat ~/.unified-ai/agents/monica/monica-system-boundary-spec.md
```

### Agent Router
```bash
cat ~/.unified-ai/agents/agent-router/route.ts
cat ~/.unified-ai/agents/agent-router/taxonomy.ts
```

### AI Filesystem
```bash
cat ~/.unified-ai/ai-filesystem/MANIFEST.md
ls ~/.unified-ai/ai-filesystem/agent-tools/
```

### Database Schema
```bash
cat ~/.unified-ai/database/SCHEMA.md
cat ~/.unified-ai/database/TABLES_INDEX.txt
```

### Agent Prompts
```bash
cat ~/.unified-ai/agent-prompts/SYSTEM.md
cat ~/.unified-ai/agent-prompts/RUNBOOK.md
```

### Knowledge Base
```bash
cat ~/.unified-ai/knowledge-base/INDEX.md
cat ~/.unified-ai/knowledge-base/PROJECTS.md
```

## 📈 Scale Comparison

| Metric | Original | Full Discovery | Growth |
|--------|----------|----------------|--------|
| AI Files | 117 |      320 | +203 |
| DB Tables | 85 | 269 | +184 |
| AI Systems | 3 | 6+ | +3 |
| Components | 20 skills | 21 skills + Monica + Router | + |

## 🔗 Integration Points

### Trinity Consortium
- Source: `~/projects/trinity-consortium/`
- AI: `server/ai/` (     320 files)
- DB: `shared/schema.ts` (269 tables)
- Router: `shared/agent-router/`
- Prompts: `.agent_prompts/`
- KB: `.agents/knowledge-base/`

### The Womb
- Source: `~/projects/the-womb/the-womb/`
- Monica: `apps/web/src/app/api/monica/`
- Brain: `packages/types/src/monica-brain.ts`

## ✅ Verification

Run to verify integration:
```bash
# Count integrated files
find ~/.unified-ai -type f | wc -l

# Check specific components
ls ~/.unified-ai/agents/monica/
ls ~/.unified-ai/agents/agent-router/
ls ~/.unified-ai/ai-filesystem/
ls ~/.unified-ai/database/
ls ~/.unified-ai/agent-prompts/
ls ~/.unified-ai/knowledge-base/
```
