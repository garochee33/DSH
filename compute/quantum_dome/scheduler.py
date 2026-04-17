"""WorkloadScheduler — routes tasks to MPS or CPU based on load."""
from __future__ import annotations

import heapq
import itertools
from typing import Callable

try:
    import torch
    _TORCH = True
except ImportError:
    _TORCH = False

from .core import ResourceMonitor

_PRIORITY = {"high": 0, "normal": 1, "low": 2}
# Tasks that benefit from GPU acceleration
_GPU_TASKS = {"inference", "embedding", "training"}
# Bytes per parameter (float32) — used for batch estimation
_BYTES_PER_PARAM = 4
# Unified memory fraction we're willing to use for a model
_MEM_FRACTION = 0.6


class WorkloadScheduler:
    def __init__(self, monitor: ResourceMonitor | None = None):
        self._monitor = monitor or ResourceMonitor()
        self._counter = itertools.count()
        # heap entries: (priority_int, seq, fn, args)
        self._queue: list = []

    # ------------------------------------------------------------------ routing
    def route(self, task_type: str) -> str:
        if task_type not in _GPU_TASKS:
            return "cpu"
        snap = self._monitor.get_snapshot()
        if snap["mps_available"] and not self._monitor.is_under_pressure():
            return "mps"
        return "cpu"

    def get_torch_device(self, task_type: str = "inference") -> "torch.device":
        if not _TORCH:
            raise RuntimeError("torch not installed")
        return torch.device(self.route(task_type))

    def auto_batch_size(self, model_param_count: int) -> int:
        snap = self._monitor.get_snapshot()
        available_bytes = snap["ram_available_gb"] * (1024 ** 3) * _MEM_FRACTION
        model_bytes = model_param_count * _BYTES_PER_PARAM
        if model_bytes <= 0:
            return 1
        batch = max(1, int(available_bytes / model_bytes))
        # Cap at 512 to stay sane
        return min(batch, 512)

    # ------------------------------------------------------------------ queue
    def enqueue(self, fn: Callable, *args, priority: str = "normal"):
        p = _PRIORITY.get(priority, 1)
        heapq.heappush(self._queue, (p, next(self._counter), fn, args))

    def dequeue(self):
        if self._queue:
            _, _, fn, args = heapq.heappop(self._queue)
            return fn, args
        return None, None
