"""
DOME-HUB FastAPI Server — port 8000
"""

from __future__ import annotations
import asyncio, time
from typing import AsyncGenerator

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agents.core.registry import make_dome_orchestrator, REGISTRY
from agents.core.memory.vector import VectorMemory

app = FastAPI(title="DOME-HUB API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080", "http://127.0.0.1:8080"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Register WebSocket routes
from agents.api.ws import register as _ws_register

_ws_register(app)

_orc = None


def get_orc():
    global _orc
    if _orc is None:
        _orc = make_dome_orchestrator()
    return _orc


_traces: list[dict] = []


def _trace(agent: str, prompt: str, response: str, elapsed: float):
    _traces.append(
        {
            "agent": agent,
            "prompt": prompt[:200],
            "response": response[:200],
            "elapsed": elapsed,
            "ts": time.time(),
        }
    )
    if len(_traces) > 200:
        _traces.pop(0)


# ── Models ────────────────────────────────────────────────────────────────────


class RunRequest(BaseModel):
    prompt: str


class IngestRequest(BaseModel):
    text: str
    namespace: str = "default"
    metadata: dict = {}


class QueryRequest(BaseModel):
    query: str
    namespace: str = "default"
    top_k: int = 5


# ── Agent endpoints ───────────────────────────────────────────────────────────


@app.post("/agents/{name}/run")
async def run_agent(name: str, req: RunRequest):
    orc = get_orc()
    if name not in orc.agents:
        raise HTTPException(404, f"Agent '{name}' not found")
    t0 = time.time()
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, orc.agents[name].run, req.prompt)
    _trace(name, req.prompt, response, time.time() - t0)
    return {"agent": name, "response": response}


@app.post("/agents/{name}/stream")
async def stream_agent(name: str, req: RunRequest):
    orc = get_orc()
    if name not in orc.agents:
        raise HTTPException(404, f"Agent '{name}' not found")

    async def event_stream() -> AsyncGenerator[str, None]:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, orc.agents[name].run, req.prompt)
        # Emit token by token (word-level simulation; real streaming requires LLM stream support)
        for word in response.split(" "):
            yield f"data: {word} \n\n"
            await asyncio.sleep(0)
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/agents")
async def list_agents():
    return {"agents": list(REGISTRY.keys())}


@app.get("/agents/{name}/memory")
async def get_memory(name: str):
    orc = get_orc()
    if name not in orc.agents:
        raise HTTPException(404, f"Agent '{name}' not found")
    agent = orc.agents[name]
    return {
        "agent": name,
        "memory": [{"role": m.role, "content": m.content} for m in agent.memory],
    }


@app.delete("/agents/{name}/memory")
async def clear_memory(name: str):
    orc = get_orc()
    if name not in orc.agents:
        raise HTTPException(404, f"Agent '{name}' not found")
    orc.agents[name].clear_memory()
    return {"agent": name, "status": "cleared"}


# ── RAG endpoints ─────────────────────────────────────────────────────────────


@app.post("/rag/ingest")
async def rag_ingest(req: IngestRequest):
    vm = VectorMemory(req.namespace)
    mid = vm.store(req.text, req.metadata)
    return {"id": mid, "namespace": req.namespace}


@app.post("/rag/query")
async def rag_query(req: QueryRequest):
    vm = VectorMemory(req.namespace)
    results = vm.search(req.query, top_k=req.top_k)
    return {"results": results}


# ── Traces ────────────────────────────────────────────────────────────────────


@app.get("/traces")
async def list_traces(limit: int = 50):
    return {"traces": _traces[-limit:]}


# ── Health ────────────────────────────────────────────────────────────────────


async def _check(name: str, url: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            r = await client.get(url)
            return {"name": name, "status": "ok", "code": r.status_code}
    except Exception as e:
        return {"name": name, "status": "error", "error": str(e)}


@app.get("/health")
async def health():
    checks = await asyncio.gather(
        _check("postgres", "http://localhost:5432"),  # will fail gracefully
        _check("redis", "http://localhost:6379"),
        _check("chroma", "http://localhost:8001/api/v1/heartbeat"),
        _check("ollama", "http://localhost:11434/api/tags"),
    )
    # postgres/redis aren't HTTP — mark them via socket check instead
    import socket

    def tcp_ok(host: str, port: int) -> bool:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            return False

    stack = {
        "postgres": "ok" if tcp_ok("localhost", 5432) else "unavailable",
        "redis": "ok" if tcp_ok("localhost", 6379) else "unavailable",
        "chroma": next(
            (c["status"] for c in checks if c["name"] == "chroma"), "unknown"
        ),
        "ollama": next(
            (c["status"] for c in checks if c["name"] == "ollama"), "unknown"
        ),
    }
    return {"status": "ok", "stack": stack}


# ── Entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("agents.api.server:app", host="0.0.0.0", port=8000, reload=True)
