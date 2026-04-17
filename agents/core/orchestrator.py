"""
DOME-HUB Agent Orchestrator
Coordinates multiple agents: routing, pipelines, parallel execution
"""

from __future__ import annotations
import asyncio
from typing import Callable
from agents.core.agent import Agent


class Orchestrator:
    def __init__(self):
        self.agents: dict[str, Agent] = {}
        self.router: Callable | None = None

    def register(self, agent: Agent):
        self.agents[agent.name] = agent
        return self

    def set_router(self, fn: Callable):
        """Set a function that picks which agent handles a prompt."""
        self.router = fn
        return self

    # ── Single dispatch ───────────────────────────────────────────────────────

    def run(self, prompt: str, agent_name: str | None = None) -> str:
        """Run prompt through a specific agent or auto-route."""
        if agent_name:
            return self.agents[agent_name].run(prompt)
        if self.router:
            name = self.router(prompt, list(self.agents.keys()))
            return self.agents[name].run(prompt)
        # Default: first agent
        return next(iter(self.agents.values())).run(prompt)

    # ── Pipeline ──────────────────────────────────────────────────────────────

    def pipeline(self, prompt: str, agent_names: list[str]) -> str:
        """Pass output of each agent as input to the next."""
        result = prompt
        for name in agent_names:
            result = self.agents[name].run(result)
        return result

    # ── Parallel ──────────────────────────────────────────────────────────────

    def parallel(self, prompt: str, agent_names: list[str]) -> dict[str, str]:
        """Run same prompt through multiple agents simultaneously."""

        async def _run_all():
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(None, self.agents[n].run, prompt)
                for n in agent_names
            ]
            results = await asyncio.gather(*tasks)
            return dict(zip(agent_names, results))

        return asyncio.run(_run_all())

    # ── Debate ────────────────────────────────────────────────────────────────

    def debate(self, topic: str, agent_names: list[str], rounds: int = 2) -> list[dict]:
        """Agents debate a topic for N rounds."""
        history = []
        context = f"Topic: {topic}"
        for _ in range(rounds):
            for name in agent_names:
                response = self.agents[name].run(f"{context}\n\nYour response:")
                history.append({"agent": name, "response": response})
                context += f"\n\n{name}: {response}"
        return history

    # ── Consensus ─────────────────────────────────────────────────────────────

    def consensus(
        self, prompt: str, agent_names: list[str], judge: str | None = None
    ) -> str:
        """Get responses from multiple agents, synthesize with a judge agent."""
        responses = self.parallel(prompt, agent_names)
        summary = "\n\n".join([f"{k}: {v}" for k, v in responses.items()])
        judge_agent = self.agents.get(judge) or next(iter(self.agents.values()))
        return judge_agent.run(
            f"Synthesize these responses into one best answer:\n\n{summary}"
        )

    def __repr__(self):
        return f"Orchestrator(agents={list(self.agents.keys())})"
