"""
DOME-HUB Agent Registry
Pre-built agents ready to use
"""
from agents.core.agent import Agent
from agents.core.tools import ALL_TOOLS
from agents.core.orchestrator import Orchestrator


# ── Pre-built agents ──────────────────────────────────────────────────────────

def make_researcher() -> Agent:
    return Agent(
        name="researcher",
        model="gpt-4o",
        system_prompt="You are a research agent. Search the web, fetch pages, and synthesize accurate information.",
        tools=ALL_TOOLS,
    )

def make_coder() -> Agent:
    return Agent(
        name="coder",
        model="gpt-4o",
        system_prompt="You are an expert software engineer. Write clean, efficient code. Use tools to read/write files and run code.",
        tools=ALL_TOOLS,
    )

def make_analyst() -> Agent:
    return Agent(
        name="analyst",
        model="gpt-4o",
        system_prompt="You are a data analyst. Query databases, analyze data, and produce clear insights.",
        tools=ALL_TOOLS,
    )

def make_planner() -> Agent:
    return Agent(
        name="planner",
        model="gpt-4o",
        system_prompt="You are a strategic planner. Break down complex goals into clear, executable plans.",
        tools=ALL_TOOLS,
    )

def make_kb_agent() -> Agent:
    return Agent(
        name="kb_agent",
        model="gpt-4o",
        system_prompt="You are a knowledge base agent. Search, retrieve, and synthesize information from the DOME-HUB knowledge base.",
        tools=ALL_TOOLS,
    )

def make_local_agent(model: str = "llama3") -> Agent:
    """Agent running on local Ollama model (no API key needed)."""
    return Agent(
        name="local",
        model=model,
        system_prompt="You are a helpful local AI assistant running on DOME-HUB.",
        tools=ALL_TOOLS,
    )


# ── Default orchestrator ──────────────────────────────────────────────────────

def make_dome_orchestrator() -> Orchestrator:
    orc = Orchestrator()
    orc.register(make_researcher())
    orc.register(make_coder())
    orc.register(make_analyst())
    orc.register(make_planner())
    orc.register(make_kb_agent())

    # Auto-router: pick agent based on keywords
    def router(prompt: str, agents: list[str]) -> str:
        p = prompt.lower()
        if any(w in p for w in ["search", "find", "research", "web", "news"]): return "researcher"
        if any(w in p for w in ["code", "write", "build", "debug", "fix", "script"]): return "coder"
        if any(w in p for w in ["data", "query", "sql", "analyze", "stats"]): return "analyst"
        if any(w in p for w in ["plan", "goal", "strategy", "steps", "how to"]): return "planner"
        if any(w in p for w in ["kb", "knowledge", "remember", "recall", "context"]): return "kb_agent"
        return "coder"  # default

    orc.set_router(router)
    return orc


# ── Quick access ──────────────────────────────────────────────────────────────

REGISTRY = {
    "researcher": make_researcher,
    "coder": make_coder,
    "analyst": make_analyst,
    "planner": make_planner,
    "kb_agent": make_kb_agent,
    "local": make_local_agent,
}

def get_agent(name: str) -> Agent:
    if name not in REGISTRY:
        raise ValueError(f"Unknown agent: {name}. Available: {list(REGISTRY.keys())}")
    return REGISTRY[name]()
