"""
DOME-HUB Episodic Memory — SQLite-backed episode and fact storage
"""
from __future__ import annotations
import sqlite3, time, uuid
from pathlib import Path

DB_PATH = Path.home() / "DOME-HUB" / "db" / "episodic.db"


class EpisodicMemory:
    def __init__(self, db_path: Path = DB_PATH):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS episodes (
                id TEXT PRIMARY KEY,
                agent TEXT NOT NULL,
                session TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                ts REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS facts (
                id TEXT PRIMARY KEY,
                agent TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                ts REAL NOT NULL,
                UNIQUE(agent, key)
            );
            CREATE INDEX IF NOT EXISTS idx_ep_session ON episodes(agent, session);
            CREATE INDEX IF NOT EXISTS idx_facts_agent ON facts(agent, key);
        """)
        self.conn.commit()

    def log(self, agent: str, session: str, role: str, content: str) -> str:
        eid = str(uuid.uuid4())
        self.conn.execute(
            "INSERT INTO episodes VALUES (?,?,?,?,?,?)",
            (eid, agent, session, role, content, time.time())
        )
        self.conn.commit()
        return eid

    def recall_session(self, agent: str, session: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM episodes WHERE agent=? AND session=? ORDER BY ts",
            (agent, session)
        ).fetchall()
        return [dict(r) for r in rows]

    def recall_facts(self, agent: str) -> dict[str, str]:
        rows = self.conn.execute(
            "SELECT key, value FROM facts WHERE agent=?", (agent,)
        ).fetchall()
        return {r["key"]: r["value"] for r in rows}

    def store_fact(self, agent: str, key: str, value: str) -> str:
        fid = str(uuid.uuid4())
        self.conn.execute(
            "INSERT INTO facts VALUES (?,?,?,?,?) ON CONFLICT(agent,key) DO UPDATE SET value=excluded.value, ts=excluded.ts",
            (fid, agent, key, value, time.time())
        )
        self.conn.commit()
        return fid

    def get_fact(self, agent: str, key: str) -> str | None:
        row = self.conn.execute(
            "SELECT value FROM facts WHERE agent=? AND key=?", (agent, key)
        ).fetchone()
        return row["value"] if row else None

    def close(self):
        self.conn.close()
