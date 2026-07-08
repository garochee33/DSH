"""ComputeProfiler — timing, RAM delta, and SQLite trace storage."""
from __future__ import annotations

import functools
import sqlite3
import time
from contextlib import contextmanager
from typing import Any

import psutil


class ComputeProfiler:
    def __init__(self):
        self._records: list[dict] = []

    @contextmanager
    def profile(self, name: str, device: str = "cpu"):
        vm_before = psutil.virtual_memory().used
        t0 = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - t0
            ram_delta = (psutil.virtual_memory().used - vm_before) / (1024 ** 3)
            self._records.append({
                "name": name,
                "device": device,
                "elapsed_s": round(elapsed, 6),
                "ram_delta_gb": round(ram_delta, 6),
                "ts": time.time(),
            })

    def get_report(self) -> list[dict]:
        return list(self._records)

    def save_to_db(self, db_path: str):
        con = sqlite3.connect(db_path)
        con.execute(
            "CREATE TABLE IF NOT EXISTS traces "
            "(name TEXT, device TEXT, elapsed_s REAL, ram_delta_gb REAL, ts REAL)"
        )
        con.executemany(
            "INSERT INTO traces VALUES (:name,:device,:elapsed_s,:ram_delta_gb,:ts)",
            self._records,
        )
        con.commit()
        con.close()

    def trace(self, fn=None, *, device: str = "cpu"):
        """Decorator: @profiler.trace or @profiler.trace(device='mps')."""
        if fn is None:
            return lambda f: self.trace(f, device=device)

        @functools.wraps(fn)
        def wrapper(*args, **kwargs) -> Any:
            with self.profile(fn.__qualname__, device=device):
                return fn(*args, **kwargs)

        return wrapper
