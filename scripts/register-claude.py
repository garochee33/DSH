#!/usr/bin/env python3
"""Register Claude, its skills, and its tools in db/dome.db.

Idempotent — uses UPSERT semantics keyed on (category, name).
Creates additional tables (`skills`, `tools`, `agents`) if they don't exist.
Writes a session row documenting the registration run.
"""

from __future__ import annotations

import datetime as dt
import pathlib
import sqlite3
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
DB = REPO / "db" / "dome.db"


CLAUDE_AGENT = {
    "name": "claude",
    "vendor": "Anthropic",
    "version": "opus-4-6",
    "surface": "cowork-desktop + agent-sdk + claude-code",
    "role": "document-gen / orchestration / browser-automation",
    "kb_path": "kb/claude/",
    "entrypoint": "agents/claude/runner.py",
}

SKILLS = [
    # (name, description_short)
    ("docx", "Word document creation, editing, TOC, tracked changes, forms"),
    ("pdf", "PDF extract, merge, split, forms, OCR, watermark"),
    ("pptx", "Slide deck creation and editing"),
    ("xlsx", "Spreadsheet creation, formulas, charts, analysis"),
    ("schedule", "Scheduled / recurring background tasks"),
    ("setup-cowork", "Guided Cowork onboarding (plugin/skill/connector)"),
    ("skill-creator", "Author, evaluate, and optimize skills"),
    ("consolidate-memory", "Periodic memory hygiene / dedupe / prune"),
    # DSH sovereign-node skills (Phase 1 foundation)
    ("dsh-setup", "Install DSH on a fresh Mac — one guided flow"),
    ("machine-probe", "Node self-introspection — chip, tier, security, model recommendations"),
    ("sovereign-lockdown", "Full sovereign lockdown — daemons, DNS, firewall, pf anchor"),
    ("trinity-activate", "Phase 2 — join Trinity mesh via spore.sh"),
    ("lava-neuro-sim", "Run a Lava SNN on Loihi 2 simulation backend"),
    ("dsh-ingest", "Rebuild dome.db + ChromaDB + verify all skills load"),
    ("sovereign-audit", "Produce consolidated hardening report with remediation"),
]

TOOLS = [
    # (name, category, description)
    ("Bash", "core", "Sandboxed Ubuntu shell"),
    ("Read", "core", "Read a file (docs, images, PDFs, notebooks)"),
    ("Write", "core", "Create / overwrite a file"),
    ("Edit", "core", "Exact-string replacement in a file"),
    ("Glob", "core", "Filename pattern search"),
    ("Grep", "core", "Ripgrep content search"),
    ("Agent", "core", "Spawn subagents (general / explore / plan / …)"),
    ("Skill", "core", "Invoke a loaded skill"),
    ("ToolSearch", "core", "Fetch schema for a deferred tool"),
    ("AskUserQuestion", "interaction", "Structured multiple-choice prompts"),
    ("TaskCreate", "tasks", "Add a task to the session task list"),
    ("TaskList", "tasks", "List current tasks"),
    ("TaskUpdate", "tasks", "Update task status"),
    ("TaskGet", "tasks", "Fetch a task by id"),
    ("TaskStop", "tasks", "Stop a running task"),
    ("WebSearch", "web", "Compliance-filtered web search"),
    ("WebFetch", "web", "Compliance-filtered URL fetch"),
    ("Monitor", "tasks", "Stream output from a long-running bg job"),
    ("PushNotification", "interaction", "Send a notification to user"),
    ("NotebookEdit", "editor", "Edit Jupyter notebook cells"),
    ("mcp__Claude_in_Chrome__*", "browser", "Chrome browser automation suite"),
    ("mcp__scheduled-tasks__*", "automation", "Scheduled task manager"),
    ("mcp__mcp-registry__*", "discovery", "MCP connector discovery"),
    ("mcp__plugins__*", "discovery", "Plugin discovery"),
    ("mcp__cowork__*", "interaction", "Cowork UI (present files / request dir)"),
    ("mcp__session_info__*", "introspection", "Session history / transcript"),
]


def now() -> str:
    return dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"


def ensure_schema(cur: sqlite3.Cursor) -> None:
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            title TEXT,
            content TEXT,
            tags TEXT,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS stack (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            name TEXT,
            version TEXT,
            status TEXT,
            updated_at TEXT,
            UNIQUE(category, name)
        );
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            vendor TEXT,
            version TEXT,
            surface TEXT,
            role TEXT,
            kb_path TEXT,
            entrypoint TEXT,
            updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent TEXT,
            name TEXT,
            description TEXT,
            path TEXT,
            updated_at TEXT,
            UNIQUE(agent, name)
        );
        CREATE TABLE IF NOT EXISTS tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent TEXT,
            name TEXT,
            category TEXT,
            description TEXT,
            updated_at TEXT,
            UNIQUE(agent, name)
        );
        """
    )


def upsert_stack(cur, category, name, version, status):
    # stack table is pre-existing without a unique constraint, so we emulate UPSERT manually.
    existing = cur.execute(
        "SELECT id FROM stack WHERE category=? AND name=?", (category, name)
    ).fetchone()
    if existing:
        cur.execute(
            "UPDATE stack SET version=?, status=?, updated_at=? WHERE id=?",
            (version, status, now(), existing[0]),
        )
    else:
        cur.execute(
            "INSERT INTO stack(category,name,version,status,updated_at) VALUES(?,?,?,?,?)",
            (category, name, version, status, now()),
        )


def main() -> int:
    if not DB.parent.exists():
        DB.parent.mkdir(parents=True)
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        ensure_schema(cur)

        # agents table
        cur.execute(
            """INSERT INTO agents(name,vendor,version,surface,role,kb_path,entrypoint,updated_at)
                 VALUES(:name,:vendor,:version,:surface,:role,:kb_path,:entrypoint,:ts)
               ON CONFLICT(name) DO UPDATE SET
                 vendor=excluded.vendor,
                 version=excluded.version,
                 surface=excluded.surface,
                 role=excluded.role,
                 kb_path=excluded.kb_path,
                 entrypoint=excluded.entrypoint,
                 updated_at=excluded.updated_at""",
            {**CLAUDE_AGENT, "ts": now()},
        )
        upsert_stack(cur, "agent", CLAUDE_AGENT["name"], CLAUDE_AGENT["version"], "installed")

        # skills
        for name, desc in SKILLS:
            path = f"kb/claude/skills/{name}"
            cur.execute(
                """INSERT INTO skills(agent,name,description,path,updated_at)
                     VALUES(?,?,?,?,?)
                   ON CONFLICT(agent,name) DO UPDATE SET
                     description=excluded.description,
                     path=excluded.path,
                     updated_at=excluded.updated_at""",
                ("claude", name, desc, path, now()),
            )
            upsert_stack(cur, "skill", f"claude.{name}", "1.0", "available")

        # tools
        for name, category, desc in TOOLS:
            cur.execute(
                """INSERT INTO tools(agent,name,category,description,updated_at)
                     VALUES(?,?,?,?,?)
                   ON CONFLICT(agent,name) DO UPDATE SET
                     category=excluded.category,
                     description=excluded.description,
                     updated_at=excluded.updated_at""",
                ("claude", name, category, desc, now()),
            )
            upsert_stack(cur, "tool", f"claude.{name}", "1.0", "available")

        # session row
        today = dt.date.today().isoformat()
        cur.execute(
            """INSERT INTO sessions(date,title,content,tags,created_at)
                 VALUES(?,?,?,?,?)""",
            (
                today,
                "Claude environment registered",
                "Registered Claude agent, 8 skills, and tool catalog via scripts/register-claude.py",
                "claude,setup,compute,kb",
                now(),
            ),
        )

        con.commit()

        # summary
        print("== stack (claude-related) ==")
        for row in cur.execute(
            "SELECT category,name,version,status FROM stack "
            "WHERE name='claude' OR name LIKE 'claude.%' ORDER BY category,name"
        ):
            print(" ", *row)
        print(f"\nSkills: {cur.execute('SELECT COUNT(*) FROM skills').fetchone()[0]}")
        print(f"Tools : {cur.execute('SELECT COUNT(*) FROM tools').fetchone()[0]}")
        print(f"Agents: {cur.execute('SELECT COUNT(*) FROM agents').fetchone()[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
