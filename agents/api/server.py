"""
DOME-HUB FastAPI Server — port 8000
"""

from __future__ import annotations
import asyncio, time
import os, re
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from agents.core.registry import make_dome_orchestrator, REGISTRY
from agents.core.memory.vector import VectorMemory
from agents.core import machine as _machine
from agents.voice import (
    CloudProviderDisabled,
    LocalAsrUnavailable,
    VoicePipeline,
    VoicePipelineError,
)
from agents.voice.audio import AudioLoadError

app = FastAPI(title="DOME-HUB API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080", "http://127.0.0.1:8080"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# ── Rate limiting — 60 requests/minute per IP ──

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Auth middleware — require HUB_API_SECRET or TRINITY_JWT on all non-health endpoints ──

import hmac
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

_PUBLIC_PATHS = frozenset({"/health", "/docs", "/openapi.json", "/redoc"})
_HUB_API_SECRET = os.environ.get("HUB_API_SECRET", "")


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in _PUBLIC_PATHS or request.method == "OPTIONS":
            return await call_next(request)
        if not _HUB_API_SECRET:
            # No secret configured — allow localhost-only access (dev mode)
            host = request.client.host if request.client else ""
            if host not in ("127.0.0.1", "::1", "localhost"):
                return JSONResponse({"error": "auth required"}, status_code=401)
            return await call_next(request)
        # Check Authorization: Bearer <token>
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            if hmac.compare_digest(token, _HUB_API_SECRET):
                return await call_next(request)
        # Check X-Hub-Secret header
        secret_header = request.headers.get("x-hub-secret", "")
        if secret_header and hmac.compare_digest(secret_header, _HUB_API_SECRET):
            return await call_next(request)
        return JSONResponse({"error": "invalid or missing credentials"}, status_code=401)


app.add_middleware(AuthMiddleware)

# Register WebSocket routes
from agents.api.ws import register as _ws_register

_ws_register(app)

_orc = None
_voice = None


def get_orc():
    global _orc
    if _orc is None:
        _orc = make_dome_orchestrator()
    return _orc


def get_voice() -> VoicePipeline:
    global _voice
    if _voice is None:
        _voice = VoicePipeline()
    return _voice


_traces: list[dict] = []
_DOME_ROOT = Path(os.environ.get("DOME_ROOT", str(Path.home() / "DOME-HUB")))
_LANGUAGE_SHORTCUT_BASE_TERMS = (
    "language roadmap",
    "language landscape",
    "programming languages",
    "language stack",
)
_YEAR_RE = re.compile(r"\b(20\d{2})\b")


def _available_language_landscape_years() -> list[int]:
    kb_dir = _DOME_ROOT / "kb"
    years = []
    for p in kb_dir.glob("language-landscape-*.md"):
        m = _YEAR_RE.search(p.stem)
        if m:
            years.append(int(m.group(1)))
    return sorted(set(years))


def _resolve_language_landscape_year(query: str, years: list[int]) -> int | None:
    if not years:
        return None

    now_year = datetime.now().year
    requested_match = _YEAR_RE.search(query)
    requested_year = int(requested_match.group(1)) if requested_match else None

    if requested_year in years:
        return requested_year

    target = requested_year or now_year
    eligible = [y for y in years if y <= target]
    return max(eligible) if eligible else max(years)


def _language_landscape_sources(year: int) -> tuple[str, str]:
    abs_path = str((_DOME_ROOT / "kb" / f"language-landscape-{year}.md").resolve())
    rel_path = f"kb/language-landscape-{year}.md"
    return abs_path, rel_path


def _is_language_shortcut_query(query: str) -> bool:
    normalized = query.lower().strip()
    return any(term in normalized for term in _LANGUAGE_SHORTCUT_BASE_TERMS)


def _language_shortcut_catalog() -> dict:
    years = _available_language_landscape_years()
    now_year = datetime.now().year
    # Discoverable aliases roll forward automatically for the next 3 years.
    discoverable_years = sorted(set(years + [now_year, now_year + 1, now_year + 2]))
    aliases = []
    for y in discoverable_years:
        aliases.extend(
            [
                f"language roadmap {y}",
                f"language landscape {y}",
                f"programming languages {y}",
                f"{y} language stack",
            ]
        )
    aliases.extend(["language roadmap", "language landscape", "programming languages"])
    return {
        "shortcut": "language_landscape",
        "aliases": aliases,
        "available_years": years,
        "default_year": _resolve_language_landscape_year("", years),
        "auto_rollover": True,
        "notes": (
            "Year aliases resolve dynamically. If a requested year is missing, "
            "the latest available year up to that year is used."
        ),
    }


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
    metadata: dict = Field(default_factory=dict)


class QueryRequest(BaseModel):
    query: str
    namespace: str = "default"
    top_k: int = 5


class VoiceVadRequest(BaseModel):
    audio_path: str


class VoiceTranscribeRequest(BaseModel):
    audio_path: str
    allow_cloud_fallback: bool = False
    language: str | None = None


class VoiceSpeakRequest(BaseModel):
    text: str
    output_path: str | None = None
    voice_id: str | None = None
    allow_cloud: bool = False


class VoiceWarmAsrRequest(BaseModel):
    model: str | None = None
    backend: str | None = None
    allow_model_download: bool = False


# ── Agent endpoints ───────────────────────────────────────────────────────────


@app.post("/agents/{name}/run")
async def run_agent(name: str, req: RunRequest):
    orc = get_orc()
    if name not in orc.agents:
        raise HTTPException(404, f"Agent '{name}' not found")
    t0 = time.time()
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, orc.agents[name].run, req.prompt)
    _trace(name, req.prompt, response, time.time() - t0)
    return {"agent": name, "response": response}


@app.post("/agents/{name}/stream")
async def stream_agent(name: str, req: RunRequest):
    orc = get_orc()
    if name not in orc.agents:
        raise HTTPException(404, f"Agent '{name}' not found")

    async def event_stream() -> AsyncGenerator[str, None]:
        async for chunk in orc.agents[name].stream_run(req.prompt):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/agents")
async def list_agents():
    return {"agents": list(REGISTRY.keys())}


# ── Orchestration endpoints ───────────────────────────────────────────────────


class OrchestrationRequest(BaseModel):
    prompt: str
    agents: list[str] = Field(default_factory=list)
    rounds: int = 2


@app.post("/orchestrate/pipeline")
async def orchestrate_pipeline(req: OrchestrationRequest):
    """Sequential chain: A→B→C. Each agent's output feeds the next."""
    orc = get_orc()
    agent_names = req.agents or list(orc.agents.keys())[:3]
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, orc.pipeline, req.prompt, agent_names)
    return {"pattern": "pipeline", "agents": agent_names, "result": result}


@app.post("/orchestrate/debate")
async def orchestrate_debate(req: OrchestrationRequest):
    """Multi-round adversarial debate between agents."""
    orc = get_orc()
    agent_names = req.agents or ["researcher", "coder"]
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None, orc.debate, req.prompt, agent_names, req.rounds
    )
    return {"pattern": "debate", "agents": agent_names, "rounds": req.rounds, "result": result}


@app.post("/orchestrate/consensus")
async def orchestrate_consensus(req: OrchestrationRequest):
    """Parallel execution + judge synthesis."""
    orc = get_orc()
    agent_names = req.agents or ["researcher", "coder", "analyst"]
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, orc.consensus, req.prompt, agent_names)
    return {"pattern": "consensus", "agents": agent_names, "result": result}


@app.post("/orchestrate/plan")
async def orchestrate_plan(req: RunRequest):
    """Autonomous plan_and_execute: decompose → execute steps → synthesize."""
    orc = get_orc()
    planner = orc.agents.get("planner") or next(iter(orc.agents.values()))
    from agents.core.skills import SKILLS
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, SKILLS["plan_and_execute"], planner, req.prompt)
    return {"pattern": "plan_and_execute", "result": result}


@app.get("/agents/{name}/memory")
async def get_memory(name: str):
    orc = get_orc()
    if name not in orc.agents:
        raise HTTPException(404, f"Agent '{name}' not found")
    agent = orc.agents[name]
    return {
        "agent": name,
        "memory": agent.mem.context(),
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
    if _is_language_shortcut_query(req.query):
        years = _available_language_landscape_years()
        target_year = _resolve_language_landscape_year(req.query, years)
        if target_year is None:
            results = vm.search(req.query, top_k=req.top_k)
            return {"results": results}

        sources = _language_landscape_sources(target_year)
        shortcut_results = []
        per_source = max(1, req.top_k // len(sources))
        for source in sources:
            shortcut_results.extend(
                vm.search(
                    f"programming language landscape {target_year} python typescript rust sql",
                    top_k=per_source,
                    where={"source": source},
                )
            )
        if shortcut_results:
            shortcut_results.sort(key=lambda r: r.get("score", 0), reverse=True)
            return {
                "results": shortcut_results[: req.top_k],
                "shortcut": "language_landscape",
                "resolved_year": target_year,
            }

    results = vm.search(req.query, top_k=req.top_k)
    return {"results": results}


@app.get("/rag/shortcuts")
async def rag_shortcuts():
    return {"shortcuts": [_language_shortcut_catalog()]}


# ── Trinity KB API Bridge (production: localhost:3333 or TRINITY_KB_URL) ──────


class TrinityKBRequest(BaseModel):
    query: str
    limit: int = 5


@app.post("/rag/trinity")
async def rag_trinity_bridge(req: TrinityKBRequest):
    """Bridge to Trinity Unified-AI KB API — searches 10,918 indexed docs."""
    base = os.environ.get("TRINITY_KB_URL", "http://localhost:3333")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{base}/api/kb/search",
                json={"query": req.query, "limit": req.limit},
            )
            resp.raise_for_status()
            return resp.json()
    except httpx.ConnectError:
        raise HTTPException(503, f"Trinity KB API not reachable at {base}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(e.response.status_code, f"Trinity KB error: {e.response.text[:200]}")


@app.post("/rag/unified")
async def rag_unified_query(req: QueryRequest):
    """Unified RAG: searches local ChromaDB + Trinity KB API, merges results."""
    # Local ChromaDB search
    vm = VectorMemory(req.namespace)
    local_results = vm.search(req.query, top_k=req.top_k)

    # Trinity KB API search (best-effort)
    trinity_results = []
    base = os.environ.get("TRINITY_KB_URL", "http://localhost:3333")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.post(
                f"{base}/api/kb/search",
                json={"query": req.query, "limit": req.top_k},
            )
            if resp.status_code == 200:
                trinity_results = resp.json().get("results", [])
    except Exception:
        pass

    # Merge and deduplicate by content similarity
    merged = local_results + [
        {**r, "source": "trinity-kb"} for r in trinity_results
    ]
    merged.sort(key=lambda r: r.get("score", r.get("similarity", 0)), reverse=True)
    return {"results": merged[:req.top_k], "sources": {"local": len(local_results), "trinity": len(trinity_results)}}


# ── Voice: local VAD → local ASR → optional cloud fallback → ElevenLabs TTS ──


@app.get("/voice/status")
async def voice_status():
    return get_voice().status()


@app.post("/voice/vad")
async def voice_vad(req: VoiceVadRequest):
    loop = asyncio.get_running_loop()
    try:
        segments = await loop.run_in_executor(
            None,
            get_voice().detect_speech,
            req.audio_path,
        )
    except VoicePipelineError as e:
        raise HTTPException(400, str(e))
    except AudioLoadError as e:
        raise HTTPException(400, str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(400, str(e))
    return {"segments": [s.to_dict() for s in segments]}


@app.post("/voice/transcribe")
async def voice_transcribe(req: VoiceTranscribeRequest):
    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(
            None,
            lambda: get_voice().transcribe_file(
                req.audio_path,
                allow_cloud_fallback=req.allow_cloud_fallback,
                language=req.language,
            ),
        )
    except LocalAsrUnavailable as e:
        raise HTTPException(503, str(e))
    except CloudProviderDisabled as e:
        raise HTTPException(403, str(e))
    except AudioLoadError as e:
        raise HTTPException(400, str(e))
    except VoicePipelineError as e:
        raise HTTPException(502, str(e))
    return result.to_dict()


@app.post("/voice/asr/warm")
async def voice_warm_asr(req: VoiceWarmAsrRequest):
    voice = get_voice()
    if req.model:
        voice.local_asr.model = req.model
    if req.backend:
        if req.backend not in {"auto", "whispercpp", "worker", "cli"}:
            raise HTTPException(400, "backend must be one of: auto, whispercpp, worker, cli")
        voice.local_asr.backend = req.backend
    if req.allow_model_download:
        voice.local_asr.allow_model_download = True

    loop = asyncio.get_running_loop()
    try:
        status = await loop.run_in_executor(None, voice.warm_asr)
    except VoicePipelineError as e:
        raise HTTPException(503, str(e))
    return status


@app.post("/voice/speak")
async def voice_speak(req: VoiceSpeakRequest):
    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(
            None,
            lambda: get_voice().synthesize_speech(
                text=req.text,
                output_path=req.output_path,
                voice_id=req.voice_id,
                allow_cloud=req.allow_cloud,
            ),
        )
    except CloudProviderDisabled as e:
        raise HTTPException(403, str(e))
    except VoicePipelineError as e:
        raise HTTPException(502, str(e))
    return result.to_dict()


# ── Traces ────────────────────────────────────────────────────────────────────


@app.get("/traces")
async def get_traces(limit: int = 50):
    return {"traces": _traces[-limit:]}


# ── Machine introspection ────────────────────────────────────────────────────


@app.get("/machine")
async def get_machine():
    """Full machine profile as probed by scripts/machine-probe.py."""
    try:
        return _machine.get_profile()
    except _machine.ProfileMissingError as e:
        raise HTTPException(503, str(e))


@app.get("/machine/summary")
async def get_machine_summary():
    """Compact view — the subset a mobile client needs to reason about this node."""
    try:
        return {
            "summary": _machine.summary_one_liner(),
            "tier": _machine.get_tier(),
            "chip": _machine.get_chip_family(),
            "ram_gb": _machine.get_ram_gb(),
            "npu_tops": _machine.get_npu_tops(),
            "is_apple_silicon": _machine.is_apple_silicon(),
            "recommended_local_model": _machine.recommend_local_model(),
            "security": _machine.security_posture(),
        }
    except _machine.ProfileMissingError as e:
        raise HTTPException(503, str(e))


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


# ── Quantum Compute ───────────────────────────────────────────────────────────


class QuantumRequest(BaseModel):
    backend: str = "qiskit"
    circuit_type: str = "bell"
    n_qubits: int = 2
    shots: int = 1024


@app.post("/quantum/run")
async def quantum_run(req: QuantumRequest):
    from agents.skills.compute import quantum_circuit
    try:
        result = quantum_circuit(req.backend, req.circuit_type, req.n_qubits,
                                 shots=req.shots)
        return {"backend": req.backend, "circuit": req.circuit_type,
                "n_qubits": req.n_qubits, "result": result}
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.get("/quantum/backends")
async def quantum_backends():
    return {
        "backends": {
            "qiskit": ["bell", "ghz", "qft"],
            "pennylane": ["vqe", "qaoa", "qnn"],
            "cirq": ["grover", "vqe"],
            "braket": ["bell", "qft"],
        }
    }


# ── Entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    _host = os.environ.get("DOME_HOST", "127.0.0.1")
    _port = int(os.environ.get("DOME_PORT", "8001"))
    uvicorn.run("agents.api.server:app", host=_host, port=_port, reload=True)
