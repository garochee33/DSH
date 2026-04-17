"""
DOME-HUB Observability / Tracing
Persists spans to SQLite at DOME-HUB/db/dome.db
"""

from __future__ import annotations
import sqlite3, time, uuid, json, functools
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).parents[2] / "db" / "dome.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS traces (
    trace_id    TEXT PRIMARY KEY,
    span_id     TEXT,
    name        TEXT,
    agent       TEXT,
    model       TEXT,
    prompt      TEXT,
    response    TEXT,
    tools_used  TEXT,
    latency_ms  REAL,
    token_count INTEGER,
    error       TEXT,
    events      TEXT,
    started_at  REAL,
    ended_at    REAL
)
"""


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.execute(_SCHEMA)
    c.commit()
    return c


class Span:
    def __init__(self, name: str):
        self.span_id = str(uuid.uuid4())
        self.trace_id = str(uuid.uuid4())
        self.name = name
        self.started_at = time.time()
        self.ended_at: float | None = None
        self.events: list[dict] = []
        self.data: dict[str, Any] = {}

    def to_row(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "name": self.name,
            "agent": self.data.get("agent"),
            "model": self.data.get("model"),
            "prompt": self.data.get("prompt"),
            "response": self.data.get("response"),
            "tools_used": json.dumps(self.data.get("tools_used", [])),
            "latency_ms": ((self.ended_at or time.time()) - self.started_at) * 1000,
            "token_count": self.data.get("token_count"),
            "error": self.data.get("error"),
            "events": json.dumps(self.events),
            "started_at": self.started_at,
            "ended_at": self.ended_at,
        }


class Tracer:
    def __init__(self):
        self._spans: dict[str, Span] = {}

    def start_span(self, name: str) -> str:
        span = Span(name)
        self._spans[span.span_id] = span
        return span.span_id

    def log_event(self, span_id: str, event: str, data: Any = None):
        span = self._spans.get(span_id)
        if span:
            span.events.append({"event": event, "data": data, "ts": time.time()})
            if isinstance(data, dict):
                span.data.update(data)

    def end_span(self, span_id: str):
        span = self._spans.pop(span_id, None)
        if not span:
            return
        span.ended_at = time.time()
        row = span.to_row()
        with _conn() as c:
            c.execute(
                """INSERT OR REPLACE INTO traces
                   (trace_id,span_id,name,agent,model,prompt,response,
                    tools_used,latency_ms,token_count,error,events,started_at,ended_at)
                   VALUES (:trace_id,:span_id,:name,:agent,:model,:prompt,:response,
                    :tools_used,:latency_ms,:token_count,:error,:events,:started_at,:ended_at)""",
                row,
            )
        return row["trace_id"]

    def get_trace(self, trace_id: str) -> dict | None:
        with _conn() as c:
            row = c.execute(
                "SELECT * FROM traces WHERE trace_id=?", (trace_id,)
            ).fetchone()
        if not row:
            return None
        cols = (
            [d[0] for d in c.description]
            if False
            else [
                "trace_id",
                "span_id",
                "name",
                "agent",
                "model",
                "prompt",
                "response",
                "tools_used",
                "latency_ms",
                "token_count",
                "error",
                "events",
                "started_at",
                "ended_at",
            ]
        )
        return dict(zip(cols, row))

    def list_traces(self, agent: str | None = None, limit: int = 50) -> list[dict]:
        cols = [
            "trace_id",
            "span_id",
            "name",
            "agent",
            "model",
            "prompt",
            "response",
            "tools_used",
            "latency_ms",
            "token_count",
            "error",
            "events",
            "started_at",
            "ended_at",
        ]
        with _conn() as c:
            if agent:
                rows = c.execute(
                    "SELECT * FROM traces WHERE agent=? ORDER BY started_at DESC LIMIT ?",
                    (agent, limit),
                ).fetchall()
            else:
                rows = c.execute(
                    "SELECT * FROM traces ORDER BY started_at DESC LIMIT ?", (limit,)
                ).fetchall()
        return [dict(zip(cols, r)) for r in rows]


_default_tracer = Tracer()


def trace(func=None, *, agent: str = "", model: str = ""):
    """Decorator: auto-traces any sync or async function."""

    def decorator(fn):
        @functools.wraps(fn)
        def sync_wrapper(*args, **kwargs):
            sid = _default_tracer.start_span(fn.__name__)
            _default_tracer.log_event(
                sid, "call", {"agent": agent, "model": model, "prompt": str(args)}
            )
            t0 = time.time()
            try:
                result = fn(*args, **kwargs)
                _default_tracer.log_event(
                    sid,
                    "result",
                    {"response": str(result), "latency_ms": (time.time() - t0) * 1000},
                )
                return result
            except Exception as e:
                _default_tracer.log_event(sid, "error", {"error": str(e)})
                raise
            finally:
                _default_tracer.end_span(sid)

        @functools.wraps(fn)
        async def async_wrapper(*args, **kwargs):
            sid = _default_tracer.start_span(fn.__name__)
            _default_tracer.log_event(
                sid, "call", {"agent": agent, "model": model, "prompt": str(args)}
            )
            t0 = time.time()
            try:
                result = await fn(*args, **kwargs)
                _default_tracer.log_event(
                    sid,
                    "result",
                    {"response": str(result), "latency_ms": (time.time() - t0) * 1000},
                )
                return result
            except Exception as e:
                _default_tracer.log_event(sid, "error", {"error": str(e)})
                raise
            finally:
                _default_tracer.end_span(sid)

        import asyncio

        return async_wrapper if asyncio.iscoroutinefunction(fn) else sync_wrapper

    return decorator(func) if func else decorator


def get_trace(trace_id: str) -> dict | None:
    return _default_tracer.get_trace(trace_id)


def list_traces(agent: str | None = None, limit: int = 50) -> list[dict]:
    return _default_tracer.list_traces(agent, limit)
