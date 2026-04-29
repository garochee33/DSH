"""
DOME-HUB Working Memory — sliding window context with LLM auto-summarization
"""

from __future__ import annotations
from collections import deque
from typing import Callable


class WorkingMemory:
    def __init__(self, max_size: int = 20, llm_fn: Callable[[list[dict]], str] | None = None):
        """
        max_size: max messages before summarization
        llm_fn: callable(prompt) -> str for summarization; if None, oldest half is dropped
        """
        self.max_size = max_size
        self.llm_fn = llm_fn
        self._window: deque[dict] = deque()
        self._summary: str = ""

    def add(self, role: str, content: str):
        self._window.append({"role": role, "content": content})
        if len(self._window) >= self.max_size:
            self.summarize_if_full()

    def get(self) -> list[dict]:
        msgs = []
        if self._summary:
            msgs.append(
                {
                    "role": "system",
                    "content": f"[Prior context summary]\n{self._summary}",
                }
            )
        msgs.extend(self._window)
        return msgs

    def clear(self):
        self._window.clear()
        self._summary = ""

    def summarize_if_full(self):
        if len(self._window) < self.max_size:
            return
        half = self.max_size // 2
        to_summarize = [self._window.popleft() for _ in range(half)]
        if self.llm_fn:
            text = "\n".join(f"{m['role']}: {m['content']}" for m in to_summarize)
            prompt = f"Summarize this conversation concisely, preserving key facts:\n\n{text}"
            new_summary = self.llm_fn([{"role": "user", "content": prompt}])
            self._summary = (
                f"{self._summary}\n{new_summary}".strip()
                if self._summary
                else new_summary
            )
        # if no llm_fn, oldest messages are simply dropped (already popped)

    def __len__(self) -> int:
        return len(self._window)
