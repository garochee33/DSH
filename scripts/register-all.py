#!/usr/bin/env python3
"""Register ALL agents, skills, and tools in dome.db — not just Claude."""
import os, sys, sqlite3
from pathlib import Path

DOME_ROOT = Path(os.environ.get("DOME_ROOT", Path.home() / "DSH"))
DB_PATH = DOME_ROOT / "db" / "dome.db"


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def upsert(conn, table, data, conflict_col="name"):
    cols = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    conflict = conflict_col if isinstance(conflict_col, str) else ", ".join(conflict_col)
    updates = ", ".join(f"{k}=excluded.{k}" for k in data if k not in (conflict_col if isinstance(conflict_col, str) else conflict_col))
    sql = f"INSERT INTO {table}({cols}) VALUES({placeholders}) ON CONFLICT({conflict}) DO UPDATE SET {updates}"
    conn.execute(sql, list(data.values()))


def register_agents(conn):
    agents = [
        {"name": "claude", "vendor": "anthropic", "version": "opus-4-6", "surface": "cli", "role": "sovereign-architect", "kb_path": "kb/claude", "entrypoint": "agents/claude/runner.py"},
        {"name": "kiro", "vendor": "aws", "version": "cli-1.0", "surface": "cli", "role": "ecosystem-manager", "kb_path": "kb/skills", "entrypoint": "agents/kiro/runner.py"},
        {"name": "codex", "vendor": "openai", "version": "latest", "surface": "cli", "role": "code-executor", "kb_path": "kb/skills", "entrypoint": "agents/Codex/"},
        {"name": "cursor", "vendor": "anysphere", "version": "agent-1.0", "surface": "ide", "role": "code-assistant", "kb_path": "kb/skills", "entrypoint": "agents/cursor/runner.py"},
        {"name": "kimi", "vendor": "moonshot", "version": "k2-0905", "surface": "api", "role": "reasoning", "kb_path": "kb/skills", "entrypoint": "agents/kimi/runner.py"},
        {"name": "local", "vendor": "ollama", "version": "ollama", "surface": "api", "role": "sovereign-inference", "kb_path": "kb/skills", "entrypoint": "agents/local/ollama.py"},
    ]
    for a in agents:
        a["updated_at"] = "2026-05-14T22:22:00"
        upsert(conn, "agents", a)
    print(f"  ✓ {len(agents)} agents registered")


def register_kb_skills(conn):
    skills = [
        {"name": "algorithms", "agent": "framework", "description": "Graph algorithms, optimization, crypto, pathfinding", "path": "kb/skills/algorithms/SKILL.md"},
        {"name": "cognitive", "agent": "framework", "description": "CoT, ToT, memory models, meta-cognition, Bayesian", "path": "kb/skills/cognitive/SKILL.md"},
        {"name": "compute", "agent": "framework", "description": "HPC, JIT, quantum circuits, MPS, GPU tensor", "path": "kb/skills/compute/SKILL.md"},
        {"name": "fractals", "agent": "framework", "description": "Mandelbrot, Julia, L-systems, IFS, attractors", "path": "kb/skills/fractals/SKILL.md"},
        {"name": "frequency", "agent": "framework", "description": "FFT, wavelets, solfeggio, brainwave bands, cymatics", "path": "kb/skills/frequency/SKILL.md"},
        {"name": "math", "agent": "framework", "description": "Symbolic math, linear algebra, tensors, number theory", "path": "kb/skills/math/SKILL.md"},
        {"name": "skill-creator", "agent": "framework", "description": "Meta-skill for generating new skills", "path": "kb/skills/skill-creator/SKILL.md"},
        {"name": "greenergyfl-finance", "agent": "framework", "description": "GreenEnergyFL financial tracking", "path": "kb/skills/greenergyfl-finance/SKILL.md"},
        {"name": "visual-storytelling", "agent": "framework", "description": "Visual storytelling architecture", "path": "kb/skills/visual-storytelling.md"},
        {"name": "cto-build-framework-validator", "agent": "kiro", "description": "CTO governance validation", "path": "agents/skills/cto-build-framework-validator/SKILL.md"},
        {"name": "ui-ux-pro-max", "agent": "kiro", "description": "AI-powered design intelligence", "path": "home/.kiro/skills/ui-ux-pro-max/SKILL.md"},
        {"name": "visual-storytelling-architect", "agent": "kiro", "description": "Narrative-arc design for scroll-driven platforms", "path": "home/.kiro/skills/visual-storytelling-architect/SKILL.md"},
        {"name": "lava-neuro-sim", "agent": "claude", "description": "LAVA neuromorphic simulation on Loihi 2", "path": "kb/claude/skills/lava-neuro-sim/SKILL.md"},
    ]
    for s in skills:
        s["updated_at"] = "2026-05-14T22:22:00"
        upsert(conn, "skills", s, conflict_col=["agent", "name"])
    print(f"  ✓ {len(skills)} skills registered")


def register_framework_tools(conn):
    tools = [
        {"name": "web_search", "agent": "framework", "category": "web", "description": "Search the web via DuckDuckGo"},
        {"name": "web_fetch", "agent": "framework", "category": "web", "description": "Fetch and extract content from URL"},
        {"name": "shell_run", "agent": "framework", "category": "core", "description": "Execute shell command"},
        {"name": "file_read", "agent": "framework", "category": "core", "description": "Read file contents"},
        {"name": "file_write", "agent": "framework", "category": "core", "description": "Write content to file"},
        {"name": "file_list", "agent": "framework", "category": "core", "description": "List directory contents"},
        {"name": "code_run", "agent": "framework", "category": "core", "description": "Execute Python code"},
        {"name": "db_query", "agent": "framework", "category": "data", "description": "Query SQLite database"},
        {"name": "db_write", "agent": "framework", "category": "data", "description": "Write to SQLite database"},
        {"name": "kb_search", "agent": "framework", "category": "data", "description": "Search knowledge base (ChromaDB)"},
    ]
    for t in tools:
        t["updated_at"] = "2026-05-14T22:22:00"
        upsert(conn, "tools", t, conflict_col=["agent", "name"])
    print(f"  ✓ {len(tools)} framework tools registered")


def main():
    print(f"Registering all agents/skills/tools in {DB_PATH}")
    conn = get_db()
    try:
        register_agents(conn)
        register_kb_skills(conn)
        register_framework_tools(conn)
        conn.commit()
        print("\n✅ All registrations complete.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
