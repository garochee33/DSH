"""
DOME-HUB Agent Registry — multi-provider, local-first, no single-vendor lock-in.

Provider strategy (controlled by DOME_PROVIDER env var):
  DOME_PROVIDER=local   → all agents use local Ollama models (air-gapped, sovereign)
  DOME_PROVIDER=claude  → all agents use Anthropic Claude (cloud, no OpenAI)
  DOME_PROVIDER=mixed   → per-agent optimal (default): local for KB/analysis,
                          Claude for research/planning that genuinely needs it

Set DOME_LOCAL_MODEL to override the default local model (default: llama3.1:8b).
The 'local' agent always uses Ollama regardless of DOME_PROVIDER.
"""

import os
from agents.core.agent import Agent
from agents.core.tools import ALL_TOOLS
from agents.core.orchestrator import Orchestrator

_PROVIDER = os.environ.get("DOME_PROVIDER", "mixed").lower()
_LOCAL = os.environ.get("DOME_LOCAL_MODEL", "llama3.1:8b")
_CLAUDE_STRONG = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-6")
_CLAUDE_FAST = "claude-sonnet-4-6"


def _model(local: str, cloud: str) -> str:
    """Pick local or cloud model based on DOME_PROVIDER."""
    if _PROVIDER == "local":
        return local
    if _PROVIDER == "claude":
        return cloud
    # mixed: use what was specified per-agent
    return local


def make_researcher() -> Agent:
    # Research needs web access anyway — cloud is acceptable here
    model = _CLAUDE_FAST if _PROVIDER != "local" else _LOCAL
    return Agent(
        name="researcher",
        model=model,
        system_prompt=(
            "You are a research agent inside DOME-HUB. Search the web, fetch pages, "
            "and synthesize accurate information. Prefer primary sources and cite them."
        ),
        tools=ALL_TOOLS,
        memory_namespace="researcher",
    )


def make_coder() -> Agent:
    # Code tasks run local by default — sensitive IP stays on device
    return Agent(
        name="coder",
        model=_model(_LOCAL, _CLAUDE_STRONG),
        system_prompt=(
            "You are an expert software engineer inside DOME-HUB. Write clean, efficient, "
            "secure code. Python 3.11, TypeScript strict, Go, Rust. MPS backend for PyTorch. "
            "Never suggest CUDA — this machine has Apple M3 Pro MPS only."
        ),
        tools=ALL_TOOLS,
        memory_namespace="coder",
    )


def make_analyst() -> Agent:
    # Analysis is local — data never leaves the machine
    return Agent(
        name="analyst",
        model=_model(_LOCAL, _CLAUDE_FAST),
        system_prompt=(
            "You are a data analyst inside DOME-HUB. Query SQLite (db/dome.db) and "
            "ChromaDB, analyze data, and produce clear, structured insights. "
            "All data is local and confidential."
        ),
        tools=ALL_TOOLS,
        memory_namespace="analyst",
    )


def make_planner() -> Agent:
    return Agent(
        name="planner",
        model=_model(_LOCAL, _CLAUDE_STRONG),
        system_prompt=(
            "You are a strategic planner inside DOME-HUB for Gadi Kedoshim / Trinity Consortium. "
            "Break down complex goals into clear, executable plans with explicit steps, "
            "owners, and success criteria."
        ),
        tools=ALL_TOOLS,
        memory_namespace="planner",
    )


def make_kb_agent() -> Agent:
    # KB is fully local — always use local model
    return Agent(
        name="kb_agent",
        model=_LOCAL,
        system_prompt=(
            "You are a knowledge base agent for DOME-HUB. Search, retrieve, and synthesize "
            "information from kb/ and the ChromaDB vector store (dome-kb). "
            "Return grounded answers with source references. No data leaves the machine."
        ),
        tools=ALL_TOOLS,
        memory_namespace="kb_agent",
    )


def make_local_agent(model: str | None = None) -> Agent:
    # Always local — air-gapped, no API calls
    return Agent(
        name="local",
        model=model or _LOCAL,
        system_prompt=(
            "You are a fully local AI assistant running on DOME-HUB via Ollama. "
            "No data leaves this machine. You are part of a sovereign, decentralized compute node."
        ),
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
