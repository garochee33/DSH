"""ResourceMonitor — real-time CPU/RAM/MPS metrics for Apple M3 Pro."""
from __future__ import annotations

import asyncio
import time
from typing import AsyncGenerator

import psutil

try:
    import torch
    _TORCH = True
except ImportError:
    _TORCH = False

_TOTAL_RAM_GB: float = psutil.virtual_memory().total / (1024 ** 3)


class ResourceMonitor:
    """Polls CPU, RAM, and MPS availability."""

    def get_snapshot(self) -> dict:
        vm = psutil.virtual_memory()
        cpu_per_core = psutil.cpu_percent(percpu=True)
        snap: dict = {
            "ts": time.time(),
            "cpu_per_core": cpu_per_core,
            "cpu_avg": sum(cpu_per_core) / len(cpu_per_core),
            "ram_total_gb": _TOTAL_RAM_GB,
            "ram_used_gb": vm.used / (1024 ** 3),
            "ram_available_gb": vm.available / (1024 ** 3),
            "ram_pressure": vm.percent / 100.0,
            "mps_available": False,
            "mps_vram_used_gb": 0.0,
        }
        if _TORCH and torch.backends.mps.is_available():
            snap["mps_available"] = True
            try:
                snap["mps_vram_used_gb"] = torch.mps.current_allocated_memory() / (1024 ** 3)
            except Exception:
                pass
        return snap

    def is_under_pressure(self) -> bool:
        snap = self.get_snapshot()
        return snap["ram_pressure"] > 0.85 or snap["cpu_avg"] > 90.0

    async def watch(self, interval: float = 1.0) -> AsyncGenerator[dict, None]:
        while True:
            yield self.get_snapshot()
            await asyncio.sleep(interval)
