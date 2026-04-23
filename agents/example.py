"""
DOME-HUB Agent Stack — Usage Examples
"""

import os, sys

sys.path.insert(0, os.environ.get("DOME_ROOT", os.path.expanduser("~/DOME-HUB")))

from agents import get_agent, make_dome_orchestrator, SKILLS

# ── Single agent ──────────────────────────────────────────────────────────────

# Coder agent
coder = get_agent("coder")
print(coder.run("Write a Python function to chunk text into overlapping windows"))

# ── Skills ────────────────────────────────────────────────────────────────────

planner = get_agent("planner")
steps = SKILLS["plan"](planner, "Build a REST API for the DOME-HUB knowledge base")
for step in steps:
    print(step)

# ── Orchestrator (auto-routes to best agent) ──────────────────────────────────

orc = make_dome_orchestrator()
print(orc.run("Search for the latest news on mycelium neural networks"))  # → researcher
print(orc.run("Write a FastAPI endpoint for kb search"))  # → coder
print(orc.run("Plan the trinity-unified-ai KB API architecture"))  # → planner

# ── Pipeline (chain agents) ───────────────────────────────────────────────────

result = orc.pipeline(
    "Build a sovereign AI knowledge base",
    ["planner", "coder"],  # planner makes steps, coder implements
)
print(result)

# ── Parallel + consensus ──────────────────────────────────────────────────────

answer = orc.consensus(
    "What is the best architecture for a decentralized neural network?",
    ["researcher", "analyst", "planner"],
    judge="planner",
)
print(answer)
