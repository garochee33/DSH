"""
DOME-HUB Agent Registry
All agents default to Claude (Anthropic) — sovereign, local-first.
Override per-agent with ANTHROPIC_MODEL env var or explicit model= arg.
"""

import os
from agents.core.agent import Agent
from agents.core.tools import ALL_TOOLS
from agents.core.orchestrator import Orchestrator

# Default model follows env var; fall back to Opus for max capability
_DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-6")
# Fast/cheap model for lighter tasks
_FAST_MODEL = "claude-sonnet-4-6"


def make_researcher() -> Agent:
    return Agent(
        name="researcher",
        model=_DEFAULT_MODEL,
        system_prompt="You are a research agent inside DOME-HUB. Search the web, fetch pages, and synthesize accurate information. Prefer primary sources and cite them.",
        tools=ALL_TOOLS,
        memory_namespace="researcher",
    )


def make_coder() -> Agent:
    return Agent(
        name="coder",
        model=_DEFAULT_MODEL,
        system_prompt="You are an expert software engineer inside DOME-HUB. Write clean, efficient, secure code. Use tools to read/write files and run code. Follow DOME-HUB conventions: Python 3.11, TypeScript strict, Go, Rust. Use MPS backend for PyTorch.",
        tools=ALL_TOOLS,
        memory_namespace="coder",
    )


def make_analyst() -> Agent:
    return Agent(
        name="analyst",
        model=_DEFAULT_MODEL,
        system_prompt="You are a data analyst inside DOME-HUB. Query SQLite (db/dome.db) and ChromaDB, analyze data, and produce clear, structured insights.",
        tools=ALL_TOOLS,
        memory_namespace="analyst",
    )


def make_planner() -> Agent:
    return Agent(
        name="planner",
        model=_DEFAULT_MODEL,
        system_prompt="You are a strategic planner inside DOME-HUB. Break down complex goals into clear, executable plans with explicit steps, owners, and success criteria.",
        tools=ALL_TOOLS,
        memory_namespace="planner",
    )


def make_kb_agent() -> Agent:
    return Agent(
        name="kb_agent",
        model=_FAST_MODEL,
        system_prompt="You are a knowledge base agent for DOME-HUB. Search, retrieve, and synthesize information from kb/ and the ChromaDB vector store (dome-kb, 1815 chunks). Return grounded answers with source references.",
        tools=ALL_TOOLS,
        memory_namespace="kb_agent",
    )


def make_local_agent(model: str = "llama3") -> Agent:
    return Agent(
        name="local",
        model=model,
        system_prompt="You are a helpful local AI assistant running on DOME-HUB via Ollama. No data leaves the machine.",
        tools=ALL_TOOLS,
        memory_namespace="local",
    )


def make_dome_orchestrator() -> Orchestrator:
    orc = Orchestrator()
    for factory in (
        make_researcher,
        make_coder,
        make_analyst,
        make_planner,
        make_kb_agent,
    ):
        orc.register(factory())
    orc.register(make_local_agent())

    def router(prompt: str, agents: list[str]) -> str:
        p = prompt.lower()
        if any(w in p for w in ["search", "find", "research", "web", "news"]):
            return "researcher"
        if any(w in p for w in ["code", "write", "build", "debug", "fix", "script"]):
            return "coder"
        if any(w in p for w in ["data", "query", "sql", "analyze", "stats"]):
            return "analyst"
        if any(w in p for w in ["plan", "goal", "strategy", "steps", "how to"]):
            return "planner"
        if any(w in p for w in ["kb", "knowledge", "remember", "recall", "context"]):
            return "kb_agent"
        return "coder"

    orc.set_router(router)
    return orc


REGISTRY: dict[str, callable] = {
    "researcher": make_researcher,
    "coder": make_coder,
    "analyst": make_analyst,
    "planner": make_planner,
    "kb_agent": make_kb_agent,
    "local": make_local_agent,
}


def get_agent(name: str) -> Agent:
    if name not in REGISTRY:
        raise ValueError(f"Unknown agent: {name!r}. Available: {list(REGISTRY)}")
    return REGISTRY[name]()
