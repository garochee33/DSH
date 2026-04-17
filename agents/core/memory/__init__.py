"""
DOME-HUB Memory System — unified interface over vector, episodic, and working memory
"""
from __future__ import annotations
from .vector import VectorMemory
from .episodic import EpisodicMemory
from .working import WorkingMemory

__all__ = ["VectorMemory", "EpisodicMemory", "WorkingMemory", "MemorySystem"]


class MemorySystem:
    """Wires all three memory layers into a single interface."""

    def __init__(
        self,
        agent: str,
        session: str,
        namespace: str | None = None,
        working_size: int = 20,
        llm_fn=None,
    ):
        self.agent = agent
        self.session = session
        self.vector = VectorMemory(namespace=namespace or agent)
        self.episodic = EpisodicMemory()
        self.working = WorkingMemory(max_size=working_size, llm_fn=llm_fn)

    def store(self, role: str, content: str, metadata: dict | None = None) -> dict:
        """Store a message across all three layers. Returns IDs."""
        meta = {**(metadata or {}), "agent": self.agent, "session": self.session, "role": role}
        vid = self.vector.store(content, meta)
        eid = self.episodic.log(self.agent, self.session, role, content)
        self.working.add(role, content)
        return {"vector_id": vid, "episode_id": eid}

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Semantic search over vector memory filtered to this agent."""
        return self.vector.search(query, top_k=top_k, where={"agent": self.agent})

    def context(self) -> list[dict]:
        """Current working memory window (with summary prefix if present)."""
        return self.working.get()

    def facts(self) -> dict[str, str]:
        return self.episodic.recall_facts(self.agent)

    def store_fact(self, key: str, value: str):
        return self.episodic.store_fact(self.agent, key, value)

    def get_fact(self, key: str) -> str | None:
        return self.episodic.get_fact(self.agent, key)
