"""DSH Workers package — Redis-backed async task queue."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agents.workers.queue import TaskQueue, start_workers

__all__ = ["TaskQueue", "start_workers"]


def __getattr__(name: str) -> Any:
    """Lazily expose queue symbols without pre-importing queue at package import time."""
    if name in __all__:
        from agents.workers.queue import TaskQueue, start_workers

        exports = {"TaskQueue": TaskQueue, "start_workers": start_workers}
        return exports[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
