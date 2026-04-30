# agents/core — Agent Framework Core

Base classes and subsystems for the DSH agent framework.

| File | Purpose |
|------|---------|
| `agent.py` | Base `Agent` class — provider routing, tool use, memory |
| `orchestrator.py` | Multi-agent orchestration |
| `registry.py` | Agent registry (6 agents: researcher, coder, analyst, planner, kb_agent, local) |
| `rag.py` | RAG pipeline — chunk, embed, retrieve, augment, generate |
| `stream.py` | Streaming for OpenAI, Anthropic, Ollama, MLX |
| `trace.py` | Observability/tracing to SQLite |
| `trinity_client.py` | Trinity mesh client with local fallback |
| `machine.py` | Hardware introspection |
| `memory/` | 3-layer memory: vector (ChromaDB), episodic (SQLite), working (sliding window) |
| `skills/` | 10 core skills (reason, plan, extract, embed, search, etc.) |
| `tools/` | 10 tools (web_search, file_read, db_query, etc.) |
