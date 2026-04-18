# engines/

All AI engine source code for the Trinity ecosystem.
**Updated:** 2026-04-07
**Engine directories:** 32 | **Standalone files:** INDEX.md, local-embeddings.ts, machine-profile.json

## IMPORTANT — Duplication Policy
Files that appear in multiple subfolders are NOT safe to delete without line-by-line diff.
Sources diverged across projects. Always archive before removing anything.

---

## Subfolders (32 directories)

| Folder | Files | Source | Notes |
|--------|-------|--------|-------|
| ai-filesystem/ | 457 | the-womb packages | Womb-enhanced version with bitboard/E8 extensions. Has MORE code than v3 equivalents. |
| agent-router/ | 9 | consortium server/ai/external/ | Unified agent router — classify, score, delegate, normalize. GEMS harvest 2026-03-24. |
| auth/ | 14 | trinity-consortium server/auth/ | Authentication middleware and JWT handling. |
| bitboard/ | 51 | trinity-consortium server/ai/bitboard/ | E8 lattice, hyper kernel, RL, search. |
| compute/ | 5 | trinity-consortium server/compute/ | PBFT consensus + distributed compute. |
| consensus/ | 3 | trinity-consortium server/ai/consensus/ | PBFT, Gossip, CRDT consensus engines. |
| continuous-improvement/ | 6 | trinity-consortium server/ai/continuous-improvement/ | Self-improvement pipeline. |
| core/ | 58 | trinity-consortium server/core/ | Core errors, governance, and utilities. |
| crew/ | 26 | trinity-consortium server/ai/crew/ | Crew/agent execution layer. |
| domains/ | 101 | trinity-consortium | Route handlers (Express). Not pure engines — kept here as canonical server-side domain logic. |
| fractal/ | 9 | trinity-consortium server/fractal/ | E8 lattice fractal engine. |
| holographic/ | 8 | trinity-consortium server/ai/ | Holographic state management engines. |
| integrations/ | 40 | trinity-consortium server/integrations/ | External service integrations (Google, Stripe, Discord, etc). |
| memory/ | 10 | trinity-consortium server/ai/ | Conversation + CRDT memory. |
| middleware/ | 26 | trinity-consortium server/middleware/ | Express middleware. |
| nexus-core/ | 5 | trinity-consortium | Nexus core module. |
| observability/ | 3 | trinity-consortium server/ai/ | Metrics + observability. |
| ref/ | 328 | trinity-unified-ai | REF summary engine (auto-generated). |
| sacred-geometry/ | 58 | trinity-consortium server/ai/engines/ | Sacred geometry + fractal engines. No overlap with ai-filesystem/. |
| scripts/ | 3 | trinity-unified-ai | Engine utility scripts. |
| server-utils/ | 10 | trinity-consortium server/utils/ | Shared server utilities. |
| shaders/ | 3 | the-womb ecosystem-visualizer/ | dimensional-portal.ts, mycelium-flow.ts GLSL shaders. GEMS harvest 2026-03-24. |
| stigmergic/ | 156 | trinity-consortium | Stigmergic routing and pheromone-based coordination. |
| swarm/ | 33 | trinity-consortium server/ai/swarm/ | Swarm orchestration. May overlap with ai-filesystem/swarm/ — NOT verified yet. |
| swarm-extended/ | 5 | ~/ai/ (desktop) | Adaptive throttle, cost planner, guardrails. |
| tests/ | 4 | trinity-consortium | Engine test files. |
| trinity-agent-system/ | 9 | the-womb upgrade-visualizer/ | E8 bitboard, sacred-geometry, realm-asset-schema, chamber-catalog. GEMS harvest 2026-03-24. |
| trinity-clone/ | 140 | trinity-consortium | Trinity clone module. |
| types/ | 5 | trinity-consortium shared/ | Shared TypeScript types. |
| unified-router/ | 11 | trinity-consortium server/ai/ | Model routing + unified AI router. |
| utils/ | 10 | trinity-consortium server/utils/ | Shared utilities. |
| womb-ai-core/ | 28 | the-womb packages/ai-core/ | Womb AI core package (cost governor, bitboard, fractal). |

---

## Known Overlap (NOT yet diffed — do not delete)
- `ai-filesystem/swarm/` vs `swarm/` — different versions, ai-filesystem has bitboard integration
- `ai-filesystem/` vs `projects/trinity-consortium-v3/server/ai/` — ai-filesystem is womb-enhanced
- `womb-ai-core/` vs `ai-filesystem/` cost files — may overlap, needs diff

## Cleanup TODO (future)
1. Diff `ai-filesystem/swarm/` vs `swarm/` line by line
2. Diff `womb-ai-core/` cost files vs `ai-filesystem/` cost files
3. Archive confirmed identical files to `knowledge-base/archive/engine-duplicates/`
4. Never delete — only archive pending human review
