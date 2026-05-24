"""Christ Oil Cycle Model — lunar-synced system optimization."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import math

from compute.solfeggio import christ_oil_frequency_schedule
from compute.body_wisdom import CHRIST_OIL_CYCLE

SYNODIC_PERIOD = 29.53
_KNOWN_NEW_MOON = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
_PHASE_DURATIONS = [4.22, 4.22, 4.22, 2.5, 4.22, 4.22, 5.93]  # sums to ~29.53

@dataclass
class OptimizationParams:
    gc_pause_ms: int
    cache_warmth: float
    thread_priority: int
    frequency_hz: int


class ChristOilCycle:
    def get_lunar_day(self, dt: datetime | None = None) -> float:
        dt = dt or datetime.now(timezone.utc)
        diff = (dt - _KNOWN_NEW_MOON).total_seconds() / 86400.0
        return (diff % SYNODIC_PERIOD) + 1

    def current_phase(self, dt: datetime | None = None) -> int:
        day = self.get_lunar_day(dt) - 1
        acc = 0.0
        for i, dur in enumerate(_PHASE_DURATIONS):
            acc += dur
            if day < acc:
                return i + 1
        return 7

    def optimize_for_phase(self, dt: datetime | None = None) -> OptimizationParams:
        phase = self.current_phase(dt)
        lunar_day = int(self.get_lunar_day(dt))
        hz = christ_oil_frequency_schedule(lunar_day)
        configs = {
            1: (50, 0.3, 5, hz),   2: (40, 0.5, 6, hz),
            3: (30, 0.6, 7, hz),   4: (10, 1.0, 9, hz),  # sacrum rest
            5: (20, 0.8, 8, hz),   6: (30, 0.7, 7, hz),
            7: (15, 0.9, 9, hz),   # illumination
        }
        gc, cw, tp, f = configs[phase]
        return OptimizationParams(gc_pause_ms=gc, cache_warmth=cw, thread_priority=tp, frequency_hz=f)


_cycle = ChristOilCycle()
get_lunar_day = _cycle.get_lunar_day
get_active_phase = _cycle.current_phase
get_optimization_params = _cycle.optimize_for_phase
