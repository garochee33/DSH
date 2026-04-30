# tests — Test Suite

34 pytest tests across 6 modules. Run: `pnpm test`

| Module | Tests | Coverage |
|--------|-------|----------|
| `test_agents.py` | 7 | Registry, tools, skills, creation, orchestrator |
| `test_memory.py` | 6 | WorkingMemory, EpisodicMemory, MemorySystem |
| `test_api.py` | 6 | Health, agents, 404s, traces, RAG |
| `test_trinity.py` | 3 | Client init, fallback, env wiring |
| `test_core.py` | 9 | Tracer, stream, RAG, quantum, skill verify |
| `test_akashic.py` | 3 | Imports, watcher, assembler |
