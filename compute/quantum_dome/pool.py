"""ComputePool — thread + process pools for CPU-bound and async work."""
from __future__ import annotations

import asyncio
import os
from concurrent.futures import Future, ProcessPoolExecutor, ThreadPoolExecutor
from typing import Any, Callable, Iterable

_CPU_COUNT = os.cpu_count() or 12


class ComputePool:
    def __init__(self):
        self._threads = ThreadPoolExecutor(max_workers=_CPU_COUNT)
        self._procs: ProcessPoolExecutor | None = None  # lazy — avoids fork issues at import

    def _proc_pool(self) -> ProcessPoolExecutor:
        if self._procs is None:
            self._procs = ProcessPoolExecutor(max_workers=max(1, _CPU_COUNT // 2))
        return self._procs

    def submit(self, fn: Callable, *args, priority: str = "normal") -> Future:
        """Submit to thread pool (priority is advisory — logged but not enforced here)."""
        return self._threads.submit(fn, *args)

    def submit_cpu(self, fn: Callable, *args) -> Future:
        """Submit CPU-bound work to process pool."""
        return self._proc_pool().submit(fn, *args)

    async def submit_async(self, fn: Callable, *args) -> Any:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._threads, fn, *args)

    def map(self, fn: Callable, items: Iterable, workers: int | None = None) -> list:
        pool = ThreadPoolExecutor(max_workers=workers or _CPU_COUNT)
        try:
            return list(pool.map(fn, items))
        finally:
            pool.shutdown(wait=True)

    def shutdown(self):
        self._threads.shutdown(wait=True)
        if self._procs:
            self._procs.shutdown(wait=True)
