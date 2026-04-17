"""
DOME-HUB Task Queue — Redis-backed with SQLite persistence
"""
from __future__ import annotations
import asyncio, json, sqlite3, time, uuid
from pathlib import Path
from typing import Optional

import httpx
import redis.asyncio as aioredis

from agents.core.registry import make_dome_orchestrator

DB_PATH = Path.home() / "DOME-HUB" / "db" / "tasks.db"
REDIS_URL = "redis://localhost:6379"
QUEUE_KEY = "dome:queue"
QUEUE_HIGH = "dome:queue:high"

_orc = None
def get_orc():
    global _orc
    if _orc is None:
        _orc = make_dome_orchestrator()
    return _orc


# ── SQLite persistence ────────────────────────────────────────────────────────

def _db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            agent TEXT NOT NULL,
            prompt TEXT NOT NULL,
            priority INTEGER DEFAULT 0,
            callback_url TEXT,
            status TEXT DEFAULT 'pending',
            result TEXT,
            error TEXT,
            created_at REAL,
            updated_at REAL
        )
    """)
    conn.commit()
    return conn


def _upsert(task_id: str, **fields):
    fields["updated_at"] = time.time()
    cols = ", ".join(f"{k} = ?" for k in fields)
    conn = _db()
    conn.execute(f"UPDATE tasks SET {cols} WHERE id = ?", (*fields.values(), task_id))
    conn.commit()
    conn.close()


def _insert_task(task_id: str, agent: str, prompt: str, priority: int, callback_url: Optional[str]):
    conn = _db()
    conn.execute(
        "INSERT INTO tasks (id, agent, prompt, priority, callback_url, status, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?)",
        (task_id, agent, prompt, priority, callback_url, "pending", time.time(), time.time()),
    )
    conn.commit()
    conn.close()


def _get_task(task_id: str) -> Optional[dict]:
    conn = _db()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    if not row:
        return None
    cols = ["id", "agent", "prompt", "priority", "callback_url", "status", "result", "error", "created_at", "updated_at"]
    return dict(zip(cols, row))


# ── TaskQueue ─────────────────────────────────────────────────────────────────

class TaskQueue:
    def __init__(self, redis_url: str = REDIS_URL):
        self.redis_url = redis_url
        self._redis: Optional[aioredis.Redis] = None

    async def _r(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = await aioredis.from_url(self.redis_url, decode_responses=True)
        return self._redis

    async def enqueue(
        self,
        agent: str,
        prompt: str,
        priority: int = 0,
        callback_url: Optional[str] = None,
    ) -> str:
        task_id = str(uuid.uuid4())
        payload = json.dumps({"id": task_id, "agent": agent, "prompt": prompt, "callback_url": callback_url})
        _insert_task(task_id, agent, prompt, priority, callback_url)
        r = await self._r()
        queue = QUEUE_HIGH if priority > 0 else QUEUE_KEY
        await r.rpush(queue, payload)
        return task_id

    async def get_status(self, task_id: str) -> Optional[dict]:
        task = _get_task(task_id)
        if not task:
            return None
        return {"status": task["status"], "result": task["result"], "error": task["error"]}

    async def worker(self):
        """Process tasks from queue (high-priority first)."""
        r = await self._r()
        orc = get_orc()
        while True:
            # BLPOP blocks until a task is available; check high-priority first
            item = await r.blpop([QUEUE_HIGH, QUEUE_KEY], timeout=5)
            if item is None:
                continue
            _, raw = item
            try:
                task = json.loads(raw)
                task_id = task["id"]
                _upsert(task_id, status="running")
                result = await asyncio.get_event_loop().run_in_executor(
                    None, orc.agents.get(task["agent"], next(iter(orc.agents.values()))).run, task["prompt"]
                )
                _upsert(task_id, status="done", result=result)
                if task.get("callback_url"):
                    await _fire_callback(task["callback_url"], task_id, result, None)
            except Exception as e:
                _upsert(task_id, status="failed", error=str(e))
                if task.get("callback_url"):
                    await _fire_callback(task["callback_url"], task_id, None, str(e))


async def _fire_callback(url: str, task_id: str, result: Optional[str], error: Optional[str]):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(url, json={"task_id": task_id, "result": result, "error": error})
    except Exception:
        pass


async def start_workers(n: int = 2, redis_url: str = REDIS_URL):
    """Start N concurrent worker coroutines."""
    q = TaskQueue(redis_url)
    await asyncio.gather(*[q.worker() for _ in range(n)])


if __name__ == "__main__":
    asyncio.run(start_workers(2))
