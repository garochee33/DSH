# agents/core — Agent Framework Core

Base classes and subsystems for the DSH agent framework.

| File | Purpose |
|------|---------|
| `agent.py` | Base `Agent` class — provider routing, tool use, memory |
| `orchestrator.py` | Multi-agent orchestration |
| `registry.py` | Agent registry (16 agents: 6 core — researcher, coder, analyst, planner, kb_agent, local — plus 10 extended: security, devops, creative, mesh, akashic, healer, monitor, concierge, orchestrator, grok) |
| `rag.py` | RAG pipeline — chunk, embed, retrieve, augment, generate |
| `stream.py` | Streaming for OpenAI, Anthropic, Ollama, MLX |
| `trace.py` | Observability/tracing to SQLite |
| `trinity_client.py` | Trinity mesh client with local fallback |
| `machine.py` | Hardware introspection |
| `memory/` | 3-layer memory: vector (ChromaDB), episodic (SQLite), working (sliding window) |
| `skills/` | 10 core skills (reason, plan, extract, embed, search, etc.) |
| `tools/` | 11 tools (web_search, file_read, db_query, quantum_compute, etc.) |
