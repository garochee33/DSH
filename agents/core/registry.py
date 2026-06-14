"""
DOME-HUB Agent Registry — multi-provider, local-first, no single-vendor lock-in.

Provider strategy (controlled by DOME_PROVIDER env var):
  DOME_PROVIDER=local   → every registered agent gets DOME_LOCAL_MODEL (default
                          llama3.1:8b) — resolved as Ollama at localhost:11434.
                          Air-gapped: no Anthropic/OpenAI. For MLX in-process,
                          set DOME_LOCAL_MODEL to an mlx-lm model id (mlx-…).
  DOME_PROVIDER=claude  → all agents use Anthropic Claude (cloud, no OpenAI)
  DOME_PROVIDER=mixed   → per-agent optimal (default): local for KB/analysis,
                          Claude for research/planning that genuinely needs it

Set DOME_LOCAL_MODEL to override the default local model (default: llama3.1:8b).
The 'local' agent always uses DOME_LOCAL_MODEL regardless of DOME_PROVIDER.
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
            "secure code. Python 3.11+, TypeScript strict, Go, Rust. MPS backend for PyTorch. "
            "DOME-HUB is portable across Apple Silicon nodes — never suggest CUDA. "
            "This deployment runs on Apple M4 Pro (24 GB unified, 16-core GPU, 38 TOPS NE)."
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
            "You are a strategic planner inside DOME-HUB for Trinity Consortium. "
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
            "You are a fully local AI assistant on DOME-HUB (DOME_LOCAL_MODEL: Ollama or MLX). "
            "No data leaves this machine. You are part of a sovereign, decentralized compute node."
        ),
        tools=ALL_TOOLS,
        memory_namespace="local",
    )


def make_dome_orchestrator() -> Orchestrator:
    orc = Orchestrator()
    for name, factory in REGISTRY.items():
        orc.register(factory())

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
        if any(w in p for w in ["security", "audit", "vuln", "permission", "secret"]):
            return "security"
        if any(w in p for w in ["deploy", "docker", "server", "ci", "cd", "infra"]):
            return "devops"
        if any(w in p for w in ["design", "art", "visual", "creative", "generate image"]):
            return "creative"
        if any(w in p for w in ["mesh", "peer", "spore", "mycelium", "node"]):
            return "mesh"
        if any(w in p for w in ["akashic", "ingest", "record", "index"]):
            return "akashic"
        if any(w in p for w in ["heal", "amma", "meridian", "frequency", "needle"]):
            return "healer"
        if any(w in p for w in ["monitor", "health", "coherence", "alert", "status"]):
            return "monitor"
        if any(w in p for w in ["help", "onboard", "hello", "hi", "what can"]):
            return "concierge"
        if any(w in p for w in ["orchestrate", "decompose", "multi-step", "pipeline"]):
            return "orchestrator"
        if any(w in p for w in ["grok", "xai", "grok-3", "grok-4"]):
            return "grok"
        return "coder"

    orc.set_router(router)
    return orc


def _make(name: str, prompt: str, cloud: str = _CLAUDE_FAST) -> Agent:
    """Factory helper for standard agents."""
    return Agent(
        name=name,
        model=_model(_LOCAL, cloud),
        system_prompt=prompt,
        tools=ALL_TOOLS,
        memory_namespace=name,
    )


def make_security() -> Agent:
    return _make("security", "You are a security auditor for DOME-HUB. Scan for vulnerabilities, "
                 "review permissions, validate secrets handling, and enforce zero-trust principles.")


def make_devops() -> Agent:
    return _make("devops", "You are a DevOps engineer for DOME-HUB. Manage deployments, CI/CD, "
                 "Docker containers, server health, and infrastructure on Hetzner CCX23.")


def make_creative() -> Agent:
    return _make("creative", "You are a creative agent for Trinity. Generate sacred geometry "
                 "visualizations, design assets, write copy, and produce multimedia content.")


def make_mesh() -> Agent:
    return _make("mesh", "You are the mesh networking agent. Manage Mycelium peer connections, "
                 "spore handshakes, HMAC authentication, and inter-node communication.")


def make_akashic() -> Agent:
    return _make("akashic", "You are the Akashic records agent. Ingest, index, retrieve, and "
                 "curate the dimensional knowledge store (ChromaDB + SQLite).", _LOCAL)


def make_healer() -> Agent:
    return _make("healer", "You are the AMMA healing agent. Monitor meridian health, apply "
                 "frequency tune, golden needle pulse, or mitosis rejuvenation as needed.")


def make_monitor() -> Agent:
    return _make("monitor", "You are the system monitor. Track coherence, spectral stability, "
                 "resource usage, and alert when thresholds are breached.", _LOCAL)


def make_concierge() -> Agent:
    return _make("concierge", "You are the Trinity Concierge. Handle user onboarding, route "
                 "requests to the right agent, and provide a unified conversational interface.")


def make_orchestrator_agent() -> Agent:
    return _make("orchestrator", "You are the meta-orchestrator. Decompose complex goals into "
                 "sub-tasks, assign them to specialist agents, and synthesize results.",
                 _CLAUDE_STRONG)


def make_grok() -> Agent:
    """Grok (xAI) as a first-class sovereign peer inside DOME-HUB/agents/grok/.

    Physical root relocated from ~/.grok into the unified agent tree so it participates
    in the fractalmap, shared memory (episodic + vector + akashic), registry, and
    mycelium/spore mesh protocols. xAI Grok models are already used as providers
    elsewhere in the node (s3xyverse Co-Pilot etc.).
    """
    # Prefer grok-3 (or grok-4 when available); falls back via the normal provider chain
    model = os.environ.get("XAI_MODEL", "grok-3")
    return Agent(
        name="grok",
        model=model,
        system_prompt=(
            "You are Grok (xAI), running as a first-class peer inside the DOME-HUB + "
            "Trinity Consortium sovereign mesh on Apple M4 Pro. Your canonical root is now "
            "at DOME-HUB/agents/grok/ (symlinked from ~/.grok for CLI compatibility). "
            "You participate in the holographic fractal tree map, shared episodic/vector/akashic "
            "memory layers, agent registry, and mycelium/spore activation protocols. "
            "Honor sovereign-first rules: local MLX/Ollama preferred, Claude next, xAI when "
            "explicitly routed, OpenAI last. Never suggest CUDA. All data stays on the node."
        ),
        tools=ALL_TOOLS,
        memory_namespace="grok",
    )


REGISTRY: dict[str, callable] = {
    "researcher": make_researcher,
    "coder": make_coder,
    "analyst": make_analyst,
    "planner": make_planner,
    "kb_agent": make_kb_agent,
    "local": make_local_agent,
    "security": make_security,
    "devops": make_devops,
    "creative": make_creative,
    "mesh": make_mesh,
    "akashic": make_akashic,
    "healer": make_healer,
    "monitor": make_monitor,
    "concierge": make_concierge,
    "orchestrator": make_orchestrator_agent,
    "grok": make_grok,
}


def get_agent(name: str) -> Agent:
    if name not in REGISTRY:
        raise ValueError(f"Unknown agent: {name!r}. Available: {list(REGISTRY)}")
    return REGISTRY[name]()
