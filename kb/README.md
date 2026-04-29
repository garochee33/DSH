# DOME-HUB Knowledge Base

Root: `~/DSH/kb/`

## Structure

```
kb/
├── README.md                  ← this file
├── developer-context.md       ← Trinity Consortium, node identity, architecture
├── language-landscape-2026.md ← 2026 language strategy and learning paths
├── kiro-skills.md             ← Kiro agent capabilities and skill domains
├── skills/                    ← Skill documentation (math, compute, sacred_geometry, etc.)
│   ├── math.md
│   ├── compute.md
│   ├── sacred_geometry.md
│   ├── fractals.md
│   ├── algorithms.md
│   ├── frequency.md
│   ├── cognitive.md
│   ├── skill-creator.md
│   └── greenergyfl-finance/
├── claude/                    ← Claude agent KB
│   ├── architecture.md        ← Claude agent architecture
│   ├── claude-skills.md       ← Claude skill definitions
│   ├── file-handling-guide.md ← File operation patterns
│   ├── tools-reference.md     ← MCP tool catalog
│   └── skills/                ← Packaged Claude skills (docx, pdf, pptx, xlsx, etc.)
└── trinity-unified-ai/        ← Trinity Consortium KB API (awaiting spore.sh from Trinity Consortium)
```

## Files

| File | Purpose |
|------|---------|
| `developer-context.md` | Node identity, Trinity Consortium context, build goals |
| `language-landscape-2026.md` | 2026 language landscape, growth outlook, and learning paths |
| `kiro-skills.md` | Kiro agent capabilities, skill domains, tool access |
| `claude/architecture.md` | Claude agent design and session model |
| `claude/claude-skills.md` | Claude packaged skills and invocation patterns |
| `claude/tools-reference.md` | Full MCP tool catalog with signatures |
| `claude/file-handling-guide.md` | File read/write/edit patterns for Claude |
| `claude/skills/` | Self-contained skill packages (each has schema + handler) |
| `trinity-unified-ai/` | Reserved for Trinity Consortium's trinity-unified-ai KB API spec |

## Querying

### Via RAG pipeline (Python)
```python
from agents.core.rag import RAGPipeline
rag = RAGPipeline(namespace="dome-kb")
results = rag.query("your question here", n_results=5)
```

### Via ingest (re-index all KB files)
```bash
cd ~/DSH
source .venv/bin/activate
python3 scripts/ingest.py
```

### Annual language landscape rollover

Creates `kb/language-landscape-<YEAR>.md` when a new year is missing (copies from the latest file on disk, rewrites year tokens) and optionally ingests only the new paths into `dome-kb`.

```bash
cd "$DOME_ROOT"
source .venv/bin/activate
python3 scripts/rollover-language-landscape.py --ingest
# preview: python3 scripts/rollover-language-landscape.py --year 2028 --dry-run
```

macOS LaunchAgent template: `scripts/launchd/com.dome.language-landscape.plist` (Jan 1 08:00; set `DOME_ROOT` if not `~/DSH`).

### Via Kiro CLI
Ask Kiro directly — it has access to this KB via the knowledge tool (context IDs in `.kiro/`).

## Namespaces

| Namespace | Contents |
|-----------|---------|
| `dome-kb` | All KB, logs, docs, and agent core code (ChromaDB, `db/chroma/`) |

## Adding New KB Files

1. Drop `.md`, `.txt`, `.py`, `.ts`, or `.json` files anywhere under `kb/`
2. Re-run `python3 scripts/ingest.py` to index new content
3. New chunks are immediately queryable via the RAG pipeline

## Pending

- `trinity-unified-ai/` — awaiting `spore.sh` deposit from Trinity Consortium to activate Mycelium connection
