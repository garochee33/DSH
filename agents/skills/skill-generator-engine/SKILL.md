---
name: skill-generator-engine
version: "2.0.0"
description: "Sovereign skill generation engine — creates, strengthens, and continuously evolves the 457-skill canonical library using fractal learning, E8 lattice indexing, neuromorphic optimization, holographic memory, and multi-agent consensus. Generates expert-level skills for any domain, language, framework, or workflow. Use when creating new skills, upgrading existing skills, running continuous improvement cycles, or expanding coverage across agents/projects/engines."
trigger: create skill, new skill, generate skill, skill engine, strengthen skills, upgrade skills, skill factory, continuous improvement, skill pipeline, evolve skills, skill automation
status: active
updated: 2026-05-14
---

# Skill Generator Engine v2.0

Sovereign skill creation and continuous evolution engine for the Trinity Canonical Skills Library.

## Capabilities

- **Generate** expert-level skills from natural language descriptions
- **Strengthen** existing skills (adequate → strong → expert)
- **Continuously evolve** the library via fractal learning cycles
- **Multi-domain** — any language, framework, platform, or workflow
- **Engine-optimized** — leverages E8, holographic memory, neuromorphic compute
- **Multi-agent** — consensus validation via Trinity triangle protocol

## When to Use

- Creating a new skill for any domain (coding, ops, research, design, automation)
- Upgrading weak/adequate skills to expert-level
- Running continuous improvement cycles across the library
- Expanding coverage for new agents, tools, or platforms
- Generating specialized skills for engines, protocols, or frameworks
- Automating skill creation from session logs, audit findings, or project needs

## Architecture

```
Skill Generator Engine
├── Input Layer
│   ├── Natural language description
│   ├── Session logs / audit findings
│   ├── Existing SKILL.md (for upgrades)
│   └── Engine/API requirements
├── Intelligence Layer
│   ├── E8 Lattice Indexing — 240-root category mapping
│   ├── Holographic Memory — retrieve similar skills for pattern matching
│   ├── Fractal Learning Engine — Fibonacci-spiral knowledge expansion
│   ├── Neuromorphic Optimization — Lava/Loihi 2 spike-based relevance
│   └── Sacred Geometry Consensus — φ-weighted quality scoring
├── Generation Layer
│   ├── SKILL.md (expert-level, protocol-driven)
│   ├── skill.yaml (manifest with risk, categories, triggers)
│   ├── scripts/ (automation, search, validation)
│   ├── references/ (supporting docs)
│   └── hooks/ (event-driven automation)
└── Validation Layer
    ├── Schema validation (trinity.skill.schema.json)
    ├── Quality classification (must be STRONG)
    ├── Triangle consensus (3-agent review)
    └── Index rebuild + KB ingestion
```

## Protocol

### Phase 1: Intent Capture

1. **Domain identification** — What does this skill enable?
2. **Trigger mapping** — When should agents invoke it?
3. **Risk assessment** — R0 (read-only) → R3 (production/infra)
4. **Category assignment** — Map to E8 lattice categories
5. **Engine affinity** — Which Trinity engines does it leverage?

### Phase 2: Generation

Execute the following in order:

```bash
# 1. Check for similar existing skills (holographic recall)
python3 scripts/rebuild-index.py
jq '.skills[] | select(.summary | test("QUERY"; "i"))' skills.index.json

# 2. Generate SKILL.md using expert template
# Structure: Frontmatter → Overview → Capabilities → When to Use → Protocol → 
#            Scripts → References → Integration → Engine Hooks

# 3. Generate skill.yaml manifest
# apiVersion: trinity.skills/v1, kind: Skill, metadata, spec, execution, security

# 4. Generate automation scripts (if applicable)
# Python search/compute scripts, Bash automation, TypeScript engine hooks

# 5. Validate
python3 scripts/validate.py

# 6. Rebuild index
python3 scripts/rebuild-index.py
```

### Phase 3: Validation (Triangle Consensus)

Three-agent review:
1. **Domain Expert** — Is the skill technically correct and complete?
2. **Architecture Agent** — Does it integrate cleanly with the library?
3. **QA Auditor** — Does it meet quality standards (STRONG tier)?

Consensus threshold: ≥2/3 pass (φ-weighted: 0.618 minimum score)

### Phase 4: Integration

1. Place in `agents/skills/<name>/`
2. Rebuild index → instantly available to all 7 agents + 6 projects
3. Ingest to ChromaDB for semantic recall
4. Log to fractal learning engine for evolution tracking

## Expert Skill Template

Every generated skill MUST include:

```markdown
---
name: <skill-name>
version: "1.0.0"
description: "<comprehensive description with trigger phrases>"
trigger: <comma-separated trigger keywords>
status: active
updated: <date>
---

# <Skill Title>

<One-paragraph expert summary>

## Capabilities
- <Bullet list of what this skill enables>

## When to Use
- <Specific scenarios that trigger this skill>
- <Agent routing conditions>

## Protocol
1. **Assess** — <Context-specific assessment>
2. **Plan** — <Domain-specific planning>
3. **Execute** — <Detailed execution steps with code/commands>
4. **Verify** — <Validation criteria>
5. **Report** — <Output format>

## Scripts
<Automation scripts with full code blocks>

## References
<Links to docs, APIs, schemas>

## Integration
- Engine hooks: <which Trinity engines>
- API endpoints: <relevant endpoints>
- Agent compatibility: <which agents can invoke>

## Anti-Patterns
- <What NOT to do>
```

## Continuous Improvement Mode

The engine runs in continuous mode via the Fractal Learning Engine:

```typescript
// Triggered by: daily-training-pipeline.ts
// Location: compute/continuous-improvement/

Cycle:
1. Evaluate recent sessions → identify skill gaps
2. Score existing skills → find degraded/stale ones
3. Generate new skills for uncovered domains
4. Strengthen skills below STRONG threshold
5. Rebuild index + ingest to KB
6. Log generation metrics (Fibonacci spiral tracking)
```

### Automated Triggers

| Trigger | Action |
|---|---|
| New project created | Scan for missing domain skills |
| Audit finding | Generate remediation skill |
| Session log gap | Create skill for uncovered workflow |
| Engine update | Regenerate engine-interface skills |
| Quality decay | Strengthen degraded skills |

## Engine Integration

### Holographic Memory (Pattern Matching)
```bash
# Retrieve similar skills before generating
POST /api/holographic
{ "query": "skill description", "namespace": "skills", "topK": 5 }
```

### E8 Lattice (Category Mapping)
```bash
# Map skill to 240-root category space
POST /api/e8-compute
{ "operation": "categorize", "input": "skill metadata", "dimensions": 8 }
```

### Fractal Learning (Evolution Tracking)
```bash
# Log skill generation to learning engine
POST /api/harmony
{ "meridian": "skill-evolution", "event": "generation", "metadata": {...} }
```

### Neuromorphic (Relevance Scoring)
```bash
# Lava SNN spike-based relevance on M5 Pro Neural Engine
python3 compute/sim_evolved.py \
  --neurons 240 --timesteps 100 --input "skill_relevance_vector"
```

### Bitboard (Fast Skill Lookup)
```typescript
// 128-bit fingerprint for instant skill matching
import { BitboardCoreEngine } from 'engines/bitboard';
const match = bitboard.query(skillFingerprint, 'skills');
```

## Compute Strategy (M5 Pro Optimized)

| Component | Backend | Purpose |
|---|---|---|
| Skill generation | Claude/GPT-4 via API | Expert content creation |
| Pattern matching | ChromaDB (local) | Semantic similarity |
| Category mapping | NumPy + E8 vectors | Lattice projection |
| Relevance scoring | Lava SNN (CPU sim) | Neuromorphic spike patterns |
| Quality scoring | Local (Python) | BM25 + structural analysis |
| Index rebuild | Python (instant) | JSON regeneration |
| KB ingestion | ChromaDB (local) | Vector embedding |
| Consensus | 3× LLM calls | Triangle validation |

### Hardware Utilization

- **M5 Pro CPU (18 cores)** — Parallel skill generation, index rebuild
- **M5 Pro GPU (MPS)** — PyTorch embeddings, Lava SNN simulation
- **Neural Engine (38 TOPS)** — Local inference for quality scoring
- **48GB Unified Memory** — ChromaDB, E8 vectors, bitboard state

## Multi-Agent Dispatch

For batch skill generation, dispatch via subagents:

```
Stage 1: Research (parallel)
  → Agent A: Domain research
  → Agent B: Similar skill analysis
  → Agent C: Engine compatibility check

Stage 2: Generate (sequential)
  → Primary agent: Write SKILL.md + skill.yaml + scripts

Stage 3: Validate (parallel)
  → Agent A: Domain expert review
  → Agent B: Architecture review
  → Agent C: QA audit

Stage 4: Integrate (sequential)
  → Primary agent: Place, index, ingest, verify
```

## Commands

```bash
# Generate a new skill
python3 skills-library/scripts/generate-manifests.py

# Strengthen all adequate skills
python3 skills-library/scripts/strengthen.py

# Quality fix (recalibrate risk, categories)
python3 skills-library/scripts/quality-fix.py

# Rebuild searchable index
python3 skills-library/scripts/rebuild-index.py

# Validate all manifests
python3 skills-library/scripts/validate.py

# Ingest to ChromaDB
python3 skills-library/scripts/ingest-kb.py

# Full pipeline (all of the above)
cd agents/skills
python3 scripts/quality-fix.py && python3 scripts/strengthen.py && python3 scripts/rebuild-index.py
```

## Metrics

Track via Fractal Learning Engine:
- **Generation rate** — skills/day
- **Quality score** — % STRONG tier
- **Coverage** — domains with ≥3 skills
- **Recall accuracy** — hook match rate
- **Evolution velocity** — Fibonacci spiral radius growth

## Anti-Patterns

- Never generate a skill without checking for duplicates first
- Never skip the skill.yaml manifest
- Never create R3 skills without explicit risk documentation
- Never hardcode paths — use `$HOME`, `$DOME_HUB`, relative refs
- Never generate skills narrower than 3 use cases
- Never skip the Protocol section (Assess → Plan → Execute → Verify → Report)
