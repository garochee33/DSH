# DOME-HUB Knowledge Base

Root: `~/DOME-HUB/kb/`
Last updated: 2026-05-23

## Canonical indexes

| Index | Path |
|-------|------|
| Skill registry + **master index map** | `kb/skills/INDEX.md` |
| DOME-HUB root | `../INDEX.md` |
| Master architecture | `../docs/DOME-HUB-ARCHITECTURE.md` |
| KB overview | `kb/README.md` (this file) |
| TU-AI | `trinity-unified-ai/docs/INDEX.md`, `trinity-unified-ai/engines/INDEX.md`, `trinity-unified-ai/knowledge-base/INDEX.md` |
| **Public export (DSH)** | `../docs/PUBLIC_PROD_HARDENING.md` — P0–P3 gap list; DOME-HUB vs DSH reconciliation |
| Fractalmap | `../skills/fractalmap/SKILL.md` |
| Agent runbooks | `../AGENTS.md`, `../MANUAL.md`, `../CLAUDE.md` |
| Core protocols | `../PROTOCOLS.md` — cross-check checklist; neuromorphic + visual-storytelling policy |
| Sovereign Gate Doctrine | `../docs/SOVEREIGN_GATE_DOCTRINE.md` — mandatory pre-push/deploy gate + full audit |

## Structure

```
kb/
├── README.md                  ← this file
├── developer-context.md       ← Trinity Consortium, node identity, architecture
├── language-landscape-2026.md ← 2026 language strategy and learning paths
├── kiro-skills.md             ← Kiro agent capabilities (19 skill domains)
├── skills/                    ← Skill knowledge modules
│   ├── INDEX.md               ← Skill registry (canonical source)
│   ├── algorithms.md          ← Algorithm design and analysis
│   ├── cognitive.md           ← Cognitive architecture patterns
│   ├── compute.md             ← Compute orchestration, QuantumDome
│   ├── fractals.md            ← Fractal geometry, Mandelbulb, E8 lattice
│   ├── frequency.md           ← Frequency analysis, signal processing, cymatics
│   ├── math.md                ← Mathematical foundations
│   ├── sacred_geometry.md     ← Sacred geometry engines, Metatron, toroidal
│   ├── skill-creator.md       ← Meta-skill for creating new skills
│   ├── visual-storytelling.md ← Visual-storytelling skill chain
│   └── greenergyfl-finance/   ← GreenEnergyFL finance skill
├── claude/                    ← Claude agent KB
│   ├── architecture.md        ← Claude agent architecture
│   ├── claude-skills.md       ← Claude skill definitions
│   ├── file-handling-guide.md ← File operation patterns
│   ├── tools-reference.md     ← MCP tool catalog
│   └── skills/                ← Packaged Claude skills (docx, pdf, pptx, xlsx, etc.)
└── trinity-unified-ai/        ← Trinity Consortium KB API (10,918 docs, 32 engines)
    ├── README.md              ← KB API overview
    ├── BRIDGE.md              ← DOME-HUB ↔ Trinity bridge spec
    ├── architecture/          ← System architecture docs
    ├── engines/               ← 1,075 TypeScript engine files
    ├── knowledge-base/        ← Harmonic registry, God Mode, discovery index
    ├── agents/                ← 36-agent registry + global context
    └── docs/                  ← 34 commands, 3 launchd services
```

## LAVA/Loihi 2 — Neuromorphic Computing

Neuromorphic compute context is discoverable via:
- `kb/skills/INDEX.md` § LAVA/Loihi 2
- `kb/kiro-skills.md` § 12 (LAVA/Loihi 2)
- `docs/DOME-HUB-ARCHITECTURE.md` §3 (includes **Trinity mirror** table)
- `home/projects/trinity-consortium/python/lava/coherence_optimizer.py` (spiking SNN, `Loihi2SimCfg`)
- `logs/session-2026-05-09-mandelbulb-optical-meninges-loihi.md`
- `compute/sim_3x3x3.py`, `compute/sim_evolved.py` (NumPy Kuramoto + Mandelbulb coherence; **K_OPTIMAL** from Loihi line)

## Simulation Files

| File | Purpose |
|------|---------|
| `compute/sim_3x3x3.py` | 3×3×3 lattice sim — 13 consciousness mechanics |
| `compute/sim_evolved.py` | Evolved sim — damped, ordered, 9×9×9 scaling |
| `compute/quantum_dome/` | QuantumDome framework (scheduler, pool, memory, profiler) |

## Files

| File | Purpose |
|------|---------|
| `developer-context.md` | Node identity, Trinity Consortium context, build goals |
| `language-landscape-2026.md` | 2026 language landscape, growth outlook, and learning paths |
| `kiro-skills.md` | Kiro agent capabilities (19 domains), tool access |
| `skills/INDEX.md` | Canonical skill registry, LAVA/sim pointers, **canonical index map** (all repo indexes) |
| `claude/architecture.md` | Claude agent design and session model |
| `claude/claude-skills.md` | Claude packaged skills and invocation patterns |
| `claude/tools-reference.md` | Full MCP tool catalog with signatures |
| `claude/file-handling-guide.md` | File read/write/edit patterns for Claude |
| `claude/skills/` | Self-contained skill packages (each has schema + handler) |
| `trinity-unified-ai/` | Trinity KB API slice: `docs/INDEX.md`, `engines/INDEX.md`, `knowledge-base/INDEX.md` (full DB: 10,918+ docs) |

## Querying

### Via RAG pipeline (Python)
```python
from agents.core.rag import RAGPipeline
rag = RAGPipeline(namespace="dome-kb")
results = rag.query("your question here", n_results=5)
```

### Via ingest (re-index all KB files)
```bash
cd ~/DOME-HUB
source .venv/bin/activate
python3 scripts/ingest.py
```

### Via Kiro CLI
Ask Kiro directly — it has access to this KB via the knowledge tool.

## Namespaces

| Namespace | Vectors | Contents |
|-----------|---------|----------|
| `dome-kb` | 10,670 | All KB, logs, docs, and agent core code |
| `akashic` | 53 | Episodic memory, session facts |

## Adding New KB Files

1. Drop `.md`, `.txt`, `.py`, `.ts`, or `.json` files anywhere under `kb/`
2. Re-run `python3 scripts/ingest.py` to index new content
3. New chunks are immediately queryable via the RAG pipeline

## Cross-Check Protocol

After adding new KB content, verify:
1. `kb/skills/INDEX.md` lists the new skill
2. `kiro-skills.md` references the capability
3. `INDEX.md` (root) has the file path
4. Run `pnpm ingest` to re-index ChromaDB
