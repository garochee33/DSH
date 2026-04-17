# DOME-HUB Agent Architecture

Sovereign, local-first multi-agent system. All agents default to local Ollama inference; cloud providers are opt-in.

## Directory Structure

```
agents/
├── __init__.py          # Top-level exports: Agent, Orchestrator, SKILLS, REGISTRY, …
├── example.py           # Usage examples
│
├── core/                # Agent engine
│   ├── agent.py         # Agent base class — LLM routing, memory, tools, tracing
│   ├── orchestrator.py  # Multi-agent coordination: route, pipeline, parallel, debate, consensus
│   ├── registry.py      # Named agent factories + DOME orchestrator builder
│   ├── stream.py        # Async streaming: MLX, Ollama, Anthropic, OpenAI
│   ├── rag.py           # RAG pipeline: ingest → chunk → embed → retrieve → generate
│   ├── trace.py         # SQLite-backed observability (spans, events, latency)
│   ├── memory/
│   │   ├── __init__.py  # MemorySystem — unified interface over all three layers
│   │   ├── vector.py    # VectorMemory — ChromaDB semantic search
│   │   ├── episodic.py  # EpisodicMemory — SQLite episode + fact store
│   │   └── working.py   # WorkingMemory — sliding window with LLM summarization
│   ├── skills/
│   │   └── __init__.py  # SKILLS dict: reason, reflect, plan, summarize, embed, search
│   └── tools/
│       └── __init__.py  # ALL_TOOLS list: web, shell, file, code, db, kb_search
│
├── api/
│   ├── server.py        # FastAPI server (port 8000) — REST + SSE endpoints
│   └── ws.py            # WebSocket endpoint /ws/{agent_name}
│
├── workers/
│   └── queue.py         # Redis task queue + SQLite persistence + async workers
│
├── local/
│   └── ollama.py        # OllamaClient — local LLM inference via Ollama HTTP API
│
└── claude/
    ├── runner.py        # CLI runner for Claude agent (uses ANTHROPIC_API_KEY)
    └── agent.yaml       # Claude agent manifest
```

## Provider Routing

Controlled by the `DOME_PROVIDER` environment variable:

| `DOME_PROVIDER` | Behaviour |
|---|---|
| `local` (default) | All agents use Ollama — fully air-gapped |
| `claude` | All agents use Anthropic Claude |
| `mixed` | Per-agent optimal: local for KB/analysis, Claude for research/planning |

Override the local model: `DOME_LOCAL_MODEL=llama3.1:8b` (default).

## Agents

| Name | Default Model | Role |
|---|---|---|
| `researcher` | claude-sonnet / llama3 | Web search, synthesis, citations |
| `coder` | llama3 / claude-opus | Code generation, debugging, review |
| `analyst` | llama3 | Data analysis, SQL, ChromaDB queries |
| `planner` | llama3 / claude-opus | Goal decomposition, strategy |
| `kb_agent` | llama3 (always local) | Knowledge base retrieval, grounded answers |
| `local` | llama3 (always local) | General-purpose, fully air-gapped |

## Memory System

Each agent has a `MemorySystem` wiring three layers:

- **VectorMemory** — ChromaDB, persistent semantic search across sessions
- **EpisodicMemory** — SQLite, per-session message log + named facts
- **WorkingMemory** — in-process sliding window (default 20 msgs) with LLM auto-summarization

## API Endpoints

Start the server: `uvicorn agents.api.server:app --port 8000`

| Method | Path | Description |
|---|---|---|
| `POST` | `/agents/{name}/run` | Run a prompt, return full response |
| `POST` | `/agents/{name}/stream` | Run a prompt, stream SSE tokens |
| `GET` | `/agents` | List registered agents |
| `GET` | `/agents/{name}/memory` | Get agent's working memory |
| `DELETE` | `/agents/{name}/memory` | Clear agent's working memory |
| `POST` | `/rag/ingest` | Ingest text into a vector namespace |
| `POST` | `/rag/query` | Semantic search over a namespace |
| `GET` | `/traces` | Recent execution traces |
| `GET` | `/health` | Stack health (Postgres, Redis, Chroma, Ollama) |
| `WS` | `/ws/{agent_name}` | Real-time streaming over WebSocket |

## Task Queue

Redis-backed async queue with SQLite persistence and HTTP callbacks.

```python
from agents.workers.queue import TaskQueue, start_workers

q = TaskQueue()
task_id = await q.enqueue("coder", "Write a merge sort", priority=1)
status = await q.get_status(task_id)

# Start workers (run as a separate process)
await start_workers(n=2)
```

## Quick Start

```python
from agents import get_agent, make_dome_orchestrator, SKILLS

# Single agent
coder = get_agent("coder")
print(coder.run("Write a binary search in Python"))

# Auto-routed orchestrator
orc = make_dome_orchestrator()
print(orc.run("Search for recent papers on RAG"))   # → researcher
print(orc.run("Debug this Python traceback: ..."))  # → coder

# Skills
planner = get_agent("planner")
steps = SKILLS["plan"](planner, "Build a sovereign AI knowledge base")

# RAG
from agents import RAGPipeline
rag = RAGPipeline(namespace="docs", llm_fn=coder._call_llm)
rag.ingest("kb/developer-context.md")
print(rag.generate("What is DOME-HUB?"))
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DOME_PROVIDER` | `mixed` | Provider strategy: `local`, `claude`, `mixed` |
| `DOME_LOCAL_MODEL` | `llama3.1:8b` | Default Ollama model |
| `ANTHROPIC_MODEL` | `claude-opus-4-6` | Default Claude model |
| `DOME_ROOT` | `~/DOME-HUB` | Root directory for DBs and models |
| `ANTHROPIC_API_KEY` | — | Required for Claude agents |
| `OPENAI_API_KEY` | — | Required for GPT agents (avoid for sensitive work) |
