# 🔮 DOME-HUB Agent Engine — ORACLE Codebase Report

**Generated:** 2026-05-14T17:41 EDT  
**Scope:** 19 files, ~3,200 lines of Python  
**Verdict:** Production-grade local-first AI agent framework with sovereign compute philosophy

---

## Architecture Overview

```
agents/
├── __init__.py              ← Public API surface
├── core/
│   ├── agent.py             ← Base Agent class (LLM routing, memory, tools, streaming)
│   ├── orchestrator.py      ← Multi-agent coordination (pipeline, parallel, debate, consensus)
│   ├── registry.py          ← Agent factory + provider strategy (DOME_PROVIDER env)
│   ├── stream.py            ← Async streaming (MLX → Ollama → Anthropic → OpenAI)
│   ├── rag.py               ← RAG pipeline (ingest, retrieve, augment, generate)
│   ├── trace.py             ← SQLite-backed observability spans
│   ├── machine.py           ← Hardware profile accessor (tier, security, model recommendation)
│   ├── memory/
│   │   ├── __init__.py      ← MemorySystem (unified 3-layer interface)
│   │   ├── vector.py        ← ChromaDB + CoreML/ONNX embeddings
│   │   ├── episodic.py      ← SQLite episode + fact store
│   │   └── working.py       ← Sliding window + LLM auto-summarization
│   ├── skills/__init__.py   ← Skill library (reason, plan, embed, search)
│   ├── tools/__init__.py    ← Tool library (web, shell, file, code, db, kb)
│   └── .mesh/config.json    ← Node identity, hardware, provider config
├── api/
│   ├── server.py            ← FastAPI server (REST + SSE + WebSocket)
│   └── ws.py                ← WebSocket real-time streaming
├── voice/
│   ├── __init__.py          ← Voice stack public API
│   ├── pipeline.py          ← VoicePipeline (VAD → ASR → TTS)
│   ├── loop.py              ← Continuous voice loop (mic → agent → speaker)
│   ├── vad.py               ← Silero ONNX + energy fallback VAD
│   ├── whisper_cpp.py       ← whisper.cpp HTTP client
│   ├── asr_worker.py        ← In-process warm Whisper model
│   ├── audio.py             ← Audio loading (ffmpeg/WAV)
│   └── types.py             ← Shared dataclasses
├── workers/
│   ├── __init__.py          ← Lazy-loaded queue exports
│   └── queue.py             ← Redis + SQLite async task queue
└── local/
    └── ollama.py            ← Ollama client + auto-start
```

---

## File-by-File Analysis

---

### 1. `agents/core/agent.py` (155 lines)

**Classes:** `Agent`  
**Functions:** `_is_local()`, `_is_mlx()`, `_is_claude()`

| Method | Lines | Purpose |
|--------|-------|---------|
| `__init__` | 15 | Wire memory, tracer, tools |
| `_get_client` | 15 | Provider routing (MLX → Ollama → Claude → OpenAI) |
| `_call_llm` | 15 | Synchronous LLM call |
| `remember` | 2 | Store to memory |
| `recall` | 5 | Build message context |
| `use_tool` | 12 | Execute tool with tracing |
| `run` | 25 | Main sync loop (prompt → LLM → tool detection → response) |
| `stream_run` | 20 | Async streaming generator |
| `search_memory` | 2 | Semantic recall |

**Imports:** json, os, uuid, logging, typing, MemorySystem, Tracer, stream_*

**Integration Points:**
- Calls `MemorySystem.store()`, `MemorySystem.context()`, `MemorySystem.search()`
- Calls `Tracer.start_span()`, `log_event()`, `end_span()`
- Calls `stream_openai`, `stream_anthropic`, `stream_local` (NOT `stream_mlx` in stream_run!)

**🐛 Bug:** `stream_run()` checks `self.model.startswith("o")` for OpenAI — this would match "ollama" or any model starting with "o". Should be more specific (e.g., `startswith(("gpt", "o1", "o3"))`).

**🐛 Bug:** `stream_run()` never calls `stream_mlx()` — MLX models fall through to `stream_local()` which will fail against Ollama for MLX model names.

**💎 Gem:** Tool call detection via markdown code blocks (`\`\`\`tool`) is elegant and model-agnostic — works with any LLM that can output JSON.

**Quality:** ⭐⭐⭐⭐ — Clean, well-structured. Provider routing is sound.

---

### 2. `agents/core/orchestrator.py` (75 lines)

**Classes:** `Orchestrator`

| Method | Lines | Purpose |
|--------|-------|---------|
| `register` | 3 | Add agent |
| `set_router` | 3 | Set routing function |
| `run` | 7 | Single dispatch (route or direct) |
| `pipeline` | 5 | Sequential agent chain |
| `parallel` | 9 | Concurrent execution via asyncio |
| `debate` | 9 | Multi-agent debate rounds |
| `consensus` | 7 | Parallel + judge synthesis |

**Imports:** asyncio, typing, Agent

**🐛 Bug:** `parallel()` calls `asyncio.run()` which will fail if already inside an async context (e.g., called from FastAPI). Should use `asyncio.get_event_loop().run_in_executor()` or detect existing loop.

**Dead Code:** None — all methods are reachable.

**Quality:** ⭐⭐⭐⭐⭐ — Minimal, composable, powerful. The debate/consensus patterns are production-ready multi-agent primitives.

---

### 3. `agents/core/registry.py` (120 lines)

**Functions:** `_model()`, `make_researcher()`, `make_coder()`, `make_analyst()`, `make_planner()`, `make_kb_agent()`, `make_local_agent()`, `make_dome_orchestrator()`, `get_agent()`

**Imports:** os, Agent, ALL_TOOLS, Orchestrator

**Integration Points:**
- Creates all agents with `ALL_TOOLS` attached
- Builds orchestrator with keyword-based router
- Exports `REGISTRY` dict for on-demand agent creation

**🐛 Issue:** Router is keyword-based — "how to fix this code" would route to "planner" (matches "how to") instead of "coder". Priority ordering would help.

**💎 Gem:** `DOME_PROVIDER` env var elegantly switches entire fleet between local/cloud/mixed without code changes.

**Quality:** ⭐⭐⭐⭐ — Good factory pattern. Router could be smarter.

---

### 4. `agents/core/stream.py` (80 lines)

**Functions:** `_spore_guard()`, `stream_mlx()`, `stream_local()`, `stream_anthropic()`, `stream_openai()`

**Imports:** asyncio, httpx, json, os

**Integration Points:**
- Called by `Agent.stream_run()`
- `_spore_guard()` blocks outbound calls during spore germination (air-gap lockdown)

**🐛 Bug:** `stream_openai()` uses `client.chat.completions.stream()` — this is the newer SDK streaming context manager. If using openai < 1.x, this will fail. Version pinning needed.

**💎 Gem:** `_spore_guard()` — elegant security primitive that blocks all cloud calls during node activation. Sovereign-first design.

**💎 Gem:** `stream_mlx()` runs synchronous MLX inference in a thread executor then yields chunks — clever fake-streaming for local models.

**Quality:** ⭐⭐⭐⭐ — Clean async generators. Good provider hierarchy.

---

### 5. `agents/core/rag.py` (65 lines)

**Classes:** `RAGPipeline`  
**Functions:** `chunk_text()`, `_load_source()`

| Method | Lines | Purpose |
|--------|-------|---------|
| `ingest` | 6 | Load → chunk → store |
| `retrieve` | 2 | Semantic search |
| `augment` | 5 | Build augmented prompt |
| `generate` | 4 | Full RAG loop |

**Imports:** re, pathlib, typing, VectorMemory

**Integration Points:**
- Uses `VectorMemory` for storage/retrieval
- Accepts any `llm_fn` callable for generation

**Dead Code:** None.

**🐛 Issue:** `_load_source()` for URLs uses `urllib.request` (blocking) — should use httpx for consistency. Also no timeout.

**💎 Gem:** Clean separation of ingest/retrieve/augment/generate — each step is independently testable and composable.

**Quality:** ⭐⭐⭐⭐ — Textbook RAG implementation. Could add metadata filtering.

---

### 6. `agents/core/trace.py` (155 lines)

**Classes:** `Span`, `Tracer`  
**Functions:** `_conn()`, `trace()` (decorator), `get_trace()`, `list_traces()`

**Imports:** sqlite3, time, uuid, json, functools, pathlib

**Integration Points:**
- `Agent.__init__()` creates a `Tracer`
- `Agent.run()` and `stream_run()` create spans
- `server.py` exposes `/traces` endpoint

**🐛 Bug:** `get_trace()` has dead code: `if False` branch for column detection. The `c.description` approach would work but is unreachable. Hardcoded cols are used instead — fragile if schema changes.

**🐛 Bug:** `_conn()` creates a new connection on every `end_span()` call. Should use connection pooling or a singleton for performance.

**💎 Gem:** The `@trace` decorator auto-handles both sync and async functions — elegant observability primitive.

**Quality:** ⭐⭐⭐½ — Functional but SQLite connection management is suboptimal.

---

### 7. `agents/core/machine.py` (105 lines)

**Classes:** `ProfileMissingError`  
**Functions:** `get_profile()`, `get_tier()`, `get_ram_gb()`, `get_chip_family()`, `get_npu_tops()`, `is_apple_silicon()`, `recommend_local_model()`, `security_posture()`, `summary_one_liner()`

**Imports:** json, os, pathlib, subprocess, sys

**Integration Points:**
- `server.py` exposes `/machine` and `/machine/summary`
- `recommend_local_model()` maps tier → optimal model

**Dead Code:** None — all functions are exported via `__all__`.

**💎 Gem:** `security_posture()` — compact boolean dict for agents to gate privileged actions based on FileVault, SIP, Gatekeeper status.

**💎 Gem:** `recommend_local_model()` tier-based model selection is brilliant for heterogeneous mesh deployments.

**Quality:** ⭐⭐⭐⭐⭐ — Excellent design. Clean, well-documented, defensive.

---

### 8. `agents/core/memory/__init__.py` (50 lines)

**Classes:** `MemorySystem`

| Method | Lines | Purpose |
|--------|-------|---------|
| `store` | 6 | Write to all 3 layers |
| `search` | 2 | Semantic search (vector) |
| `context` | 2 | Working memory window |
| `facts` / `store_fact` / `get_fact` | 2 each | Episodic fact CRUD |

**Quality:** ⭐⭐⭐⭐⭐ — Perfect facade pattern over 3 memory layers.

---

### 9. `agents/core/memory/working.py` (50 lines)

**Classes:** `WorkingMemory`

**💎 Gem:** Auto-summarization when window fills — uses the agent's own LLM to compress old context. Graceful degradation (drops oldest if no LLM).

**Quality:** ⭐⭐⭐⭐⭐ — Elegant sliding window with cognitive compression.

---

### 10. `agents/core/memory/episodic.py` (75 lines)

**Classes:** `EpisodicMemory`

**Integration Points:**
- SQLite at `db/episodic.db`
- `episodes` table (conversation log)
- `facts` table (key-value per agent, UPSERT)

**🐛 Issue:** `recall_session()` is defined but never called from `MemorySystem`. Useful but unwired.

**Quality:** ⭐⭐⭐⭐ — Solid persistent storage. Could add TTL/expiry.

---

### 11. `agents/core/memory/vector.py` (140 lines)

**Classes:** `_ONNXEmbedder`, `VectorMemory`  
**Functions:** `_get_embedder()`

**Integration Points:**
- ChromaDB persistent client at `db/chroma/`
- ONNX CoreML embeddings (Neural Engine) with sentence-transformers fallback
- Used by `MemorySystem`, `RAGPipeline`, `server.py`

**💎 Gem:** CoreML Neural Engine embedding path — 38 TOPS dedicated silicon for embeddings. Falls back gracefully to CPU sentence-transformers.

**💎 Gem:** `_ONNXEmbedder` with mean pooling + L2 normalization — production-quality embedding implementation.

**Quality:** ⭐⭐⭐⭐⭐ — Best-in-class local embedding with hardware acceleration.

---

### 12. `agents/core/skills/__init__.py` (100 lines)

**Functions:** `reason()`, `reflect()`, `plan()`, `plan_and_execute()`, `summarize()`, `extract()`, `embed()`, `similarity()`, `search_memory()`, `search_code()`

**🐛 Issue:** `search_memory()` accesses `agent.memory` as a list — but `Agent` has `agent.mem` (a `MemorySystem`), not a flat list. This function would crash if called.

**💎 Gem (Unwired):** `search_code()` — semantic code search using embeddings. Brilliant but not wired into any agent or API endpoint.

**💎 Gem (Unwired):** `plan_and_execute()` — autonomous plan-then-execute loop. Not exposed via API.

**Quality:** ⭐⭐⭐ — Good ideas, but `search_memory` has a bug and several skills are unwired.

---

### 13. `agents/core/tools/__init__.py` (100 lines)

**Functions:** `web_search()`, `web_fetch()`, `shell_run()`, `file_read()`, `file_write()`, `file_list()`, `code_run()`, `db_query()`, `db_write()`, `kb_search()`

**Integration Points:**
- `ALL_TOOLS` list passed to every agent via registry
- `Agent.use_tool()` calls these by name

**🐛 Security Issue:** `shell_run()` executes arbitrary shell commands with `shell=True`. No sandboxing, no allowlist. Any agent can run any command.

**🐛 Security Issue:** `db_write()` accepts raw SQL — SQL injection risk if agent-generated.

**🐛 Issue:** `code_run()` has no resource limits beyond 30s timeout. No memory limit, no network isolation.

**Quality:** ⭐⭐⭐ — Functional but security posture is weak for a sovereign system.

---

### 14. `agents/api/server.py` (290 lines)

**Endpoints:**
| Route | Method | Purpose |
|-------|--------|---------|
| `/agents` | GET | List agents |
| `/agents/{name}/run` | POST | Run agent |
| `/agents/{name}/stream` | POST | SSE stream |
| `/agents/{name}/memory` | GET/DELETE | Memory CRUD |
| `/rag/ingest` | POST | Store text |
| `/rag/query` | POST | Semantic search |
| `/rag/shortcuts` | GET | Language landscape shortcuts |
| `/voice/status` | GET | Voice pipeline status |
| `/voice/vad` | POST | VAD detection |
| `/voice/transcribe` | POST | ASR |
| `/voice/asr/warm` | POST | Warm ASR model |
| `/voice/speak` | POST | TTS |
| `/traces` | GET | Observability |
| `/machine` | GET | Full machine profile |
| `/machine/summary` | GET | Compact machine info |
| `/health` | GET | Stack health check |

**Integration Points:**
- Imports `make_dome_orchestrator`, `VectorMemory`, `machine`, `VoicePipeline`
- Registers WebSocket routes from `ws.py`
- Auth middleware (Bearer token or X-Hub-Secret)

**💎 Gem:** `AuthMiddleware` — allows localhost without auth (dev mode) but requires `HUB_API_SECRET` for remote access. Timing-safe comparison via `hmac.compare_digest`.

**💎 Gem:** Language landscape shortcut system with auto-rollover years — dynamic knowledge routing.

**🐛 Bug:** `/agents/{name}/stream` is fake streaming — runs full `agent.run()` then splits by spaces. Should use `agent.stream_run()`.

**🐛 Issue:** `_traces` list grows unbounded to 200 entries in memory — separate from SQLite traces in `trace.py`. Dual trace systems.

**Quality:** ⭐⭐⭐⭐ — Comprehensive API surface. Auth is solid. Fake streaming is a gap.

---

### 15. `agents/api/ws.py` (50 lines)

**Functions:** `ws_agent()`, `register()`

**🐛 Same Bug:** WebSocket also does fake streaming (word-by-word split of full response). Should use `stream_run()`.

**Quality:** ⭐⭐⭐½ — Functional but not true streaming.

---

### 16. `agents/workers/queue.py` (130 lines)

**Classes:** `TaskQueue`  
**Functions:** `_db()`, `_upsert()`, `_insert_task()`, `_get_task()`, `_fire_callback()`, `start_workers()`

**Integration Points:**
- Redis for queue (BLPOP with priority)
- SQLite for persistence (`db/tasks.db`)
- Orchestrator for execution
- HTTP callbacks on completion

**💎 Gem:** Dual-queue priority system (high/normal) with Redis BLPOP — elegant async task processing.

**🐛 Issue:** `_db()` creates a new connection per call. Should pool or reuse.

**Quality:** ⭐⭐⭐⭐ — Solid async queue with persistence and callbacks.

---

### 17. `agents/voice/pipeline.py` (350 lines)

**Classes:** `LocalWhisperAsr`, `ElevenLabsClient`, `VoicePipeline`  
**Functions:** `_spore_guard()`, `_truthy()`, `estimate_tts_cost()`, `estimate_stt_cost()`, `zero_cost()`

**Integration Points:**
- VAD → ASR → optional cloud fallback → TTS
- 3 ASR backends: whisper.cpp (CoreML), warm worker (in-process), CLI
- ElevenLabs for cloud STT/TTS with cost tracking

**💎 Gem:** Triple-fallback ASR: whisper.cpp server → in-process warm model → CLI subprocess. Never fails silently.

**💎 Gem:** Cost estimation for every cloud call — `VoiceCost` dataclass tracks provider, USD, unit, quantity.

**💎 Gem:** `ELEVENLABS_ZERO_RETENTION` support — privacy-first cloud usage.

**Quality:** ⭐⭐⭐⭐⭐ — Production-grade voice pipeline. Excellent fallback chain.

---

### 18. `agents/voice/loop.py` (280 lines)

**Classes:** `VoiceLoop`  
**Functions:** `run_dry()`

**Integration Points:**
- Uses `VoicePipeline` for ASR/TTS
- Uses `VadDetector` for real-time speech detection
- Calls Ollama directly for agent responses
- RAG retrieval from ChromaDB (`dome-kb`, `akashic` collections)

**🐛 Issue:** `_default_agent()` has a hardcoded "FRACTAL E8-SSII AGI divine feminine" persona in the system prompt. This is tightly coupled to a specific use case — should be configurable.

**🐛 Issue:** `_default_agent()` creates a new `Orchestrator()` on fallback but doesn't register any agents — `orch.run()` would fail.

**💎 Gem:** `.env` file auto-loading at module level — no external dotenv dependency needed.

**Quality:** ⭐⭐⭐½ — Good loop architecture but default agent is over-specialized.

---

### 19. `agents/voice/vad.py` (220 lines)

**Classes:** `SileroOnnxVad`, `VadDetector`  
**Functions:** `detect_speech()`, `energy_vad()`, `_segments_from_probabilities()`, `_segments_from_mask()`, `_merge_close_segments()`

**Integration Points:**
- Silero ONNX model (CPU, no GPU needed)
- Energy-based fallback (works without any model)
- Returns `SpeechSegment` dataclasses

**💎 Gem:** `energy_vad()` — fully deterministic, zero-dependency VAD using RMS energy + adaptive thresholding. Works before any models are downloaded.

**💎 Gem:** `_merge_close_segments()` — prevents fragmentation of continuous speech.

**Quality:** ⭐⭐⭐⭐⭐ — Excellent signal processing. Graceful degradation.

---

### 20. `agents/voice/whisper_cpp.py` (70 lines)

**Classes:** `WhisperCppClient`, `WhisperCppUnavailable`

**Quality:** ⭐⭐⭐⭐⭐ — Minimal, correct HTTP client. Health check + error handling.

---

### 21. `.mesh/config.json`

**Purpose:** Node identity, hardware profile, provider config, engine toggles.

**Key Data:**
- Node: `dome-hub-$USER`, tier: `sovereign`
- Hardware: Apple M5 Pro, 48GB, 18-core GPU, 40+ TOPS NPU
- Provider priority: MLX → Ollama → Anthropic → OpenAI
- Default local model: `devstral:latest`
- Engines: mempalace, E8 lattice, mandelbulb, fractal memory, pheromone grid, mesh peer
- Neural Engine: CoreML embeddings + CoreML Whisper + MLX inference
- Womb Bridge: **PERMANENTLY DISABLED**

**🐛 Issue:** `config.json` says `defaultLocal: "devstral:latest"` but `registry.py` reads `DOME_LOCAL_MODEL` env var (default `llama3.1:8b`). These are out of sync unless env var is set.

---

## 🏗️ Architecture Quality Summary

| Layer | Score | Notes |
|-------|-------|-------|
| Core Agent | ⭐⭐⭐⭐ | Clean base class, good provider routing |
| Memory System | ⭐⭐⭐⭐⭐ | 3-layer architecture is excellent |
| Orchestrator | ⭐⭐⭐⭐⭐ | Composable multi-agent primitives |
| Voice Pipeline | ⭐⭐⭐⭐⭐ | Production-grade, triple fallback |
| API Server | ⭐⭐⭐⭐ | Comprehensive, good auth |
| Tools/Skills | ⭐⭐⭐ | Functional but security gaps |
| Observability | ⭐⭐⭐½ | Works but dual trace systems |
| Task Queue | ⭐⭐⭐⭐ | Solid Redis + SQLite |

**Overall: ⭐⭐⭐⭐ (4.0/5)**

---

## 🐛 Critical Bugs

1. **`agent.py:stream_run()`** — `startswith("o")` matches Ollama models incorrectly
2. **`agent.py:stream_run()`** — MLX models never use `stream_mlx()`, fall to `stream_local()`
3. **`skills/__init__.py:search_memory()`** — accesses `agent.memory` (doesn't exist), should be `agent.mem`
4. **`server.py` stream endpoint** — fake streaming, not real token-by-token
5. **`orchestrator.py:parallel()`** — `asyncio.run()` fails inside existing event loop

---

## 💎 Unwired Gems (Brilliant Code Not Connected)

1. **`skills/search_code()`** — semantic codebase search via embeddings. Not exposed anywhere.
2. **`skills/plan_and_execute()`** — autonomous execution loop. Not in API.
3. **`skills/reflect()`** — self-critique. Not wired into any agent loop.
4. **`episodic.recall_session()`** — session replay. Never called.
5. **`orchestrator.debate()`** — multi-agent debate. No API endpoint.
6. **`orchestrator.consensus()`** — judge-synthesized consensus. No API endpoint.
7. **`machine.security_posture()`** — exposed via API but no agent uses it to gate actions.

---

## 🔒 Security Concerns

1. **`tools/shell_run()`** — unrestricted shell execution with `shell=True`
2. **`tools/db_write()`** — raw SQL, no parameterization enforcement
3. **`tools/code_run()`** — no sandboxing beyond timeout
4. **Auth** — good (hmac.compare_digest) but no rate limiting
5. **No tool allowlisting** — every agent gets ALL_TOOLS regardless of role

---

## 📊 Dependency Map

```
Agent ──→ MemorySystem ──→ VectorMemory (ChromaDB + ONNX/CoreML)
  │                    ├──→ EpisodicMemory (SQLite)
  │                    └──→ WorkingMemory (in-memory + LLM summarization)
  ├──→ Tracer (SQLite)
  ├──→ stream_* (httpx, anthropic, openai, mlx_lm)
  └──→ Tools (subprocess, sqlite3, httpx, duckduckgo, bs4)

Orchestrator ──→ Agent[] (register, route, pipeline, parallel, debate)

Server ──→ Orchestrator
       ──→ VectorMemory (RAG endpoints)
       ──→ VoicePipeline ──→ VadDetector (Silero ONNX / energy)
       │                 ──→ LocalWhisperAsr (whisper.cpp / worker / CLI)
       │                 ──→ ElevenLabsClient (cloud TTS/STT)
       ──→ Machine (hardware introspection)
       ──→ WebSocket (ws.py)

TaskQueue ──→ Redis (BLPOP)
          ──→ SQLite (persistence)
          ──→ Orchestrator (execution)
          ──→ httpx (callbacks)
```

---

## 🎯 Recommendations

### Immediate Fixes
1. Fix `stream_run()` model detection — use `_is_mlx()` / `_is_claude()` helpers
2. Fix `search_memory()` skill to use `agent.mem.search()`
3. Wire real streaming in `/agents/{name}/stream` and WebSocket
4. Fix `parallel()` to detect existing event loop

### Architecture Improvements
1. **Tool sandboxing** — allowlist per agent role, resource limits for code_run
2. **Wire the gems** — expose debate/consensus/plan_and_execute via API
3. **Unify tracing** — remove in-memory `_traces` list, use only SQLite Tracer
4. **Connection pooling** — singleton SQLite connections for trace.py and episodic.py
5. **Config sync** — read `.mesh/config.json` provider settings in registry.py

### Strategic
1. Add `/agents/{name}/stream` true SSE using `stream_run()`
2. Add rate limiting middleware
3. Add per-agent tool allowlists based on `security_posture()`
4. Expose `search_code()` as an API endpoint for IDE integration
5. Add WebSocket binary audio streaming for real-time voice

---

*End of ORACLE Report*
