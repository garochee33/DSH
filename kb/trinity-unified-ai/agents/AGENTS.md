# Global AGENTS.md - Trinity Development Environment

This file provides context for AI assistants working across all Trinity projects.

## Active Projects

| Project | Path | Type | Priority |
|---------|------|------|----------|
| the-womb | `/Users/enzogaroche/projects/the-womb/the-womb` | Full-stack AI platform | HIGH |
| trinity-consortium | `/Users/enzogaroche/trinity-consortium` | Next.js web app | MEDIUM |
| trinity-dev-console | `/Users/enzogaroche/projects/trinity-dev-console` | Dev tools | MEDIUM |

## Quick Navigation

### For AI/Agent Development
→ Use `trinity-repo-navigator` skill for complete codebase map
→ Use `trinity-coding-standards` skill for patterns and conventions

### For Testing & Validation
→ Use `verification-validation` skill for V&V workflows
→ Run: `~/.config/agents/skills/verification-validation/scripts/full-validation.sh`

### For Service Integration
→ Use `end-to-end-wiring` skill for connectivity patterns
→ Run: `~/.config/agents/skills/end-to-end-wiring/scripts/connectivity-check.sh`

## Common Commands

```bash
# Validation
vv-full          # Full validation suite
vv-static        # Static checks only
vv-connectivity  # Service connectivity check

# Development
cd-womb          # cd to the-womb project
cd-consortium    # cd to trinity-consortium
cd-console       # cd to trinity-dev-console
```

## Quality Gates (Must Pass)
1. ✅ Static analysis (lint + typecheck)
2. ✅ Unit tests passing
3. ✅ Integration tests (for API changes)
4. ✅ E2E validation (before deploy)

## Key Principles
- **Strict TypeScript**: No `any`, explicit return types
- **Cost Tracking**: All AI calls must track execution and cost
- **Tier-Based Access**: Respect member/admin tier system
- **Energy Conservation**: Swarm operations must conserve energy
- **Security**: No secrets in code, validate all inputs
- **LOCAL LLM FIRST**: Always try Ollama local models before cloud API (zero cost, sovereign, private)

## Local LLM First — Dispatch Policy

**RULE: All agents must attempt local model dispatch before cloud API calls.**

| Agent Type | Local Model | Cloud Fallback |
|------------|-------------|----------------|
| Builder / Deployer / Emissary | `qwen2.5-coder:14b` | `claude-sonnet-4-6` |
| Debugger / Reviewer / Auditor | `deepseek-r1:14b` | `claude-sonnet-4-6` |
| Analyst / Researcher / Oracle | `qwen3.5:9b` | `gemini-2.5-pro` |
| Documenter / Scribe / Curator | `qwen3.5:7b` | `claude-haiku-4-5` |
| Architect / God / Security | (cloud-only — high-stakes) | `claude-opus-4-6` |

Escalate to cloud when: local output quality < threshold, context window overflow, multi-tool coordination, or user requests explicit cloud model.

## Orchestration Modes (activated by autoboot Phase 7B)

Five modes run in sequence to wire the full Trinity agent ecosystem:

1. **LOCAL_SOVEREIGN** — bind local LLM routing (Ollama + NVIDIA RTX detection)
2. **FULL_MERKABA** — activate all 10 MERKABA protocols via KB API
3. **SACRED_RESONANCE** — wire harmony meridians M1–M12 + φ-weighted Fourier FFT
4. **WOMB_MYCELIUM** — activate mycelium membrane: pheromone grid + Merkle snapshot
5. **FRACTAL_BATTLE** — Kuramoto sync + adversarial chaos injection

All modes are passed to `POST /api/system/activate/full-alchemist` for final GOD MODE (score 100/100).

## Memory & Context
- Skills are loaded from `~/.config/agents/skills/`
- Use MCP memory for cross-session persistence
- Document key decisions in project AGENTS.md files
- Per-agent files: `agents/per-agent/*.md` — each agent's model, tools, skills, invocation rules
- Orchestration runbook: `agents/prompts/RUNBOOK.md`
