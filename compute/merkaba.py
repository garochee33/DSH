"""Merkaba Activation Sequence — dual-tetrahedra velocity matching at PHI."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

PHI = 1.6180339887
CONVERGENCE_THRESHOLD = 0.01
MAX_ITERATIONS = 50


@dataclass
class MerkabaState:
    spin_up: float
    spin_down: float
    ratio: float
    activated: bool


class MerkabaField:
    """Two counter-rotating tetrahedra converging to golden ratio spin."""

    def activate(self, lattice: np.ndarray) -> MerkabaState:
        phases = np.angle(lattice.astype(complex)) if not np.iscomplexobj(lattice) else np.angle(lattice)
        deriv = np.diff(phases.flatten())

        spin_up = float(np.mean(deriv[deriv > 0])) if np.any(deriv > 0) else 0.001
        spin_down = float(np.abs(np.mean(deriv[deriv < 0]))) if np.any(deriv < 0) else 0.001

        # Iteratively adjust toward PHI ratio
        for _ in range(MAX_ITERATIONS):
            ratio = spin_up / spin_down if spin_down != 0 else 0.0
            if abs(ratio - PHI) < CONVERGENCE_THRESHOLD:
                break
            # Nudge: scale up toward PHI * down
            spin_up = spin_up * 0.9 + (PHI * spin_down) * 0.1

        ratio = spin_up / spin_down if spin_down != 0 else 0.0
        return MerkabaState(
            spin_up=round(spin_up, 6),
            spin_down=round(spin_down, 6),
            ratio=round(ratio, 6),
            activated=abs(ratio - PHI) < CONVERGENCE_THRESHOLD,
        )
