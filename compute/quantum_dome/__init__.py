"""QuantumDome — hardware-aware compute scheduler for Apple M3 Pro."""
from __future__ import annotations

from typing import Any, Callable

from .core import ResourceMonitor
from .memory import MemoryManager
from .pool import ComputePool
from .profiler import ComputeProfiler
from .scheduler import WorkloadScheduler


class QuantumDome:
    def __init__(self):
        self.monitor = ResourceMonitor()
        self.scheduler = WorkloadScheduler(self.monitor)
        self.pool = ComputePool()
        self.memory = MemoryManager()
        self.profiler = ComputeProfiler()

    # ---------------------------------------------------------------- properties
    @property
    def device(self) -> str:
        return self.scheduler.route("inference")

    @property
    def available_ram(self) -> float:
        return self.memory.get_available_gb()

    @property
    def cpu_usage(self) -> float:
        return self.monitor.get_snapshot()["cpu_avg"]

    @property
    def is_healthy(self) -> bool:
        return not self.monitor.is_under_pressure()

    # ---------------------------------------------------------------- run
    def run(
        self,
        fn: Callable,
        *args,
        task_type: str = "inference",
        priority: str = "normal",
    ) -> Any:
        self.memory.auto_clear()
        device = self.scheduler.route(task_type)
        with self.profiler.profile(getattr(fn, "__name__", str(fn)), device=device):
            future = self.pool.submit(fn, *args, priority=priority)
            return future.result()

    async def run_async(
        self,
        fn: Callable,
        *args,
        task_type: str = "inference",
    ) -> Any:
        self.memory.auto_clear()
        device = self.scheduler.route(task_type)
        with self.profiler.profile(getattr(fn, "__name__", str(fn)), device=device):
            return await self.pool.submit_async(fn, *args)

    # ---------------------------------------------------------------- status / optimize
    def status(self) -> dict:
        snap = self.monitor.get_snapshot()
        snap["device"] = self.device
        snap["available_ram_gb"] = self.available_ram
        snap["is_healthy"] = self.is_healthy
        snap["profile_count"] = len(self.profiler.get_report())
        return snap

    def optimize(self):
        self.memory.clear_torch_cache()
        # Recreate pools to release any stale threads
        self.pool.shutdown()
        self.pool = ComputePool()


__all__ = ["QuantumDome"]
