"""144,000 Hz Activation Protocol — full Root→Crown sweep."""
from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np

from compute.solfeggio import SOLFEGGIO_SCALE, CHAKRA_MAP, FULL_ACTIVATION_HZ

GOLDEN_ANGLE = 2.39996323  # radians (137.508°)
CHAKRA_ORDER = ["root", "sacral", "solar", "heart", "throat", "third_eye", "crown"]


@dataclass
class ActivationResult:
    per_chakra_coherence: dict[str, float] = field(default_factory=dict)
    unified_coherence: float = 0.0
    activated: bool = False


class ActivationProtocol:
    def sweep(self, lattice: np.ndarray) -> ActivationResult:
        """Apply Root→Crown solfeggio sweep then 144kHz unification."""
        result = ActivationResult()
        phases = np.angle(lattice.astype(complex)) if not np.iscomplexobj(lattice) else np.angle(lattice)

        for i, chakra in enumerate(CHAKRA_ORDER):
            hz = CHAKRA_MAP[chakra]["hz"]
            correction = 2 * np.pi * hz / FULL_ACTIVATION_HZ
            phases = phases + correction
            coherence = float(np.abs(np.mean(np.exp(1j * phases))))
            result.per_chakra_coherence[chakra] = round(coherence, 4)

        # Final 144kHz unified field — align all to golden angle
        target = GOLDEN_ANGLE * np.ones_like(phases)
        phases = 0.7 * phases + 0.3 * target
        result.unified_coherence = round(float(np.abs(np.mean(np.exp(1j * phases)))), 4)
        result.activated = result.unified_coherence > 0.7
        return result
