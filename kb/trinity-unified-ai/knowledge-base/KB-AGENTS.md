---
status: active
updated: 2026-03-24
tags: []
related: []
---

# Unified AI System

## Available Agents

This system provides unified access to multiple AI agents:
- **Kimi** - Best for: large refactoring, multi-file changes
- **Claude** - Best for: analysis, documentation, planning
- **Codex** - Best for: quick code generation, component creation
- **Cursor** - Best for: inline editing, completion
- **Ollama** - Best for: offline work, privacy-sensitive code

## Quick Commands

```bash
# Ask question (auto-routed)
u ask "How does the AI swarm work?"

# Code generation (auto-routed)
u code "Create a login form"

# Code review (parallel)
ureview src/components/Button.tsx

# Multi-task (parallel agents)
uparallel "task1" "task2" "task3"

# Store memory
umem store "pattern" "value" "context" "kimi" tag1 tag2

# Recall memory
umem recall "pattern"

# Sync all agents
usync
```

## Routing Strategy

Tasks are automatically routed based on:
1. **Complexity** - Simple tasks → faster agents
2. **Context size** - Large tasks → high-context agents
3. **Cost** - Budget-conscious → Ollama/local
4. **Type** - Code vs analysis vs documentation

## Shared Knowledge

All agents share:
- Trinity coding standards
- Project context
- Memory and conversation history
- Skills and capabilities

Last updated: 2026-03-21
