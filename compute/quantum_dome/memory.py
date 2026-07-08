"""MemoryManager — RAM pressure monitoring and cache management."""
from __future__ import annotations

from contextlib import contextmanager

import psutil

try:
    import torch
    _TORCH = True
except ImportError:
    _TORCH = False


class MemoryManager:
    def monitor_pressure(self) -> float:
        return psutil.virtual_memory().percent / 100.0

    def get_available_gb(self) -> float:
        return psutil.virtual_memory().available / (1024 ** 3)

    def clear_torch_cache(self):
        if not _TORCH:
            return
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
        elif torch.cuda.is_available():
            torch.cuda.empty_cache()

    def auto_clear(self, threshold: float = 0.85):
        if self.monitor_pressure() > threshold:
            self.clear_torch_cache()

    def allocate_safe(self, size_gb: float) -> bool:
        return self.get_available_gb() > size_gb * 1.1  # 10% headroom

    @contextmanager
    def guard(self):
        try:
            yield
        finally:
            self.clear_torch_cache()
