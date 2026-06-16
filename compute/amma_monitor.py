"""
AMMA — Autonomous Meta-Morphic Architecture

Four sovereign capacities:
  1. Self-Heal  — frequency tune, golden needle, mitosis (reactive repair)
  2. Self-Learn — STDP coupling adaptation, pattern memory, reward signal
  3. Self-Grow  — topology expansion, synaptogenesis, pruning dead connections
  4. Self-Organize — emergent clustering, phase-locked assemblies, meridian routing

Thresholds (from AMMA Quad-Sensor doctrine):
  > 0.85  → HEALTHY (no action)
  0.60–0.85 → DRIFT (frequency tune)
  0.40–0.60 → ANOMALY (golden needle pulse)
  < 0.40  → CRITICAL (mitosis rejuvenation)
"""

import logging
from dataclasses import dataclass, field
from compute.sim_evolved import Lattice, get_neighbors_phase, DAMPING, PHI
from compute.solfeggio import diagnose_meridian, MERIDIAN_FREQUENCY_MAP, numerology_reduce
import numpy as np

_LOG = logging.getLogger(__name__)

THRESHOLD_HEALTHY = 0.85
THRESHOLD_DRIFT = 0.60
THRESHOLD_CRITICAL = 0.40
STAGNANT_THRESHOLD = 0.3

MERIDIAN_CODES = ["LU", "LI", "SP", "ST", "HT", "SI", "PC", "TE", "KI", "BL", "LR", "GB", "DU", "REN"]


@dataclass
class HealingEvent:
    tick: int
    coherence: float
    protocol: str  # frequency_tune | golden_needle | mitosis
    correction: float  # magnitude of applied correction


@dataclass
class AMMAMonitor:
    """Attaches to a Lattice and applies self-healing, self-learning,
    self-growth, and self-organization when coherence shifts."""
    history: list[float] = field(default_factory=list)
    events: list[HealingEvent] = field(default_factory=list)
    interventions: int = 0
    stagnant_meridians: list[str] = field(default_factory=list)
    _learn_events: int = 0
    _grow_events: int = 0
    _organize_events: int = 0

    def check_and_heal(self, s: Lattice, tick: int, force: bool = False) -> Lattice:
        """Run after each simulation tick. Returns healed lattice.
        If force=True (topology preemptive), apply frequency_tune regardless of threshold."""
        coherence = s.coherence()
        self.history.append(coherence)

        if force:
            s = self._frequency_tune(s, coherence, tick)
            self.interventions += 1
            return s

        if coherence >= THRESHOLD_HEALTHY:
            return s

        if coherence >= THRESHOLD_DRIFT:
            s = self._frequency_tune(s, coherence, tick)
        elif coherence >= THRESHOLD_CRITICAL:
            s = self._golden_needle(s, coherence, tick)
        else:
            s = self._mitosis(s, coherence, tick)

        self.interventions += 1
        return s

    def _frequency_tune(self, s: Lattice, coherence: float, tick: int) -> Lattice:
        """Lightweight FFT offset correction for minor drift."""
        spectrum = np.fft.fftn(np.exp(1j * s.phase))
        dominant_freq = np.unravel_index(np.abs(spectrum).argmax(), spectrum.shape)
        # Apply corrective phase shift toward dominant mode
        correction_magnitude = (THRESHOLD_HEALTHY - coherence) * 0.1
        target_phase = np.angle(spectrum[dominant_freq])
        s.phase += correction_magnitude * np.sin(target_phase - s.phase) * (1 - DAMPING)
        s.phase %= (2 * np.pi)

        # Detect stagnant meridians and apply solfeggio healing
        slice_size = s.phase.shape[0] // 14
        if slice_size > 0:
            for idx, code in enumerate(MERIDIAN_CODES):
                start = idx * slice_size
                end = start + slice_size if idx < 13 else s.phase.shape[0]
                region = s.phase[start:end]
                if region.size == 0:
                    continue
                firing_rate = float(np.abs(np.mean(np.exp(1j * region))))
                if firing_rate < STAGNANT_THRESHOLD:
                    s = self._solfeggio_heal(s, code, firing_rate, tick)

        self.events.append(HealingEvent(tick, coherence, "frequency_tune", correction_magnitude))
        _LOG.info("AMMA frequency_tune @ tick=%d coherence=%.4f correction=%.4f",
                  tick, coherence, correction_magnitude)
        return s

    def _solfeggio_heal(self, s: Lattice, meridian_code: str, firing_rate: float, tick: int) -> Lattice:
        """Apply solfeggio frequency healing to a stagnant meridian region."""
        hz = diagnose_meridian(meridian_code, firing_rate)
        nr = numerology_reduce(int(hz))
        # Scale correction by numerology (3/6/9 are sacred multipliers)
        scale = nr / 9.0
        idx = MERIDIAN_CODES.index(meridian_code)
        slice_size = s.phase.shape[0] // 14
        start = idx * slice_size
        end = start + slice_size if idx < 13 else s.phase.shape[0]
        # Phase correction proportional to solfeggio numerology
        s.phase[start:end] += scale * np.sin(hz / 1000.0 - s.phase[start:end]) * 0.1
        s.phase %= (2 * np.pi)

        if meridian_code not in self.stagnant_meridians:
            self.stagnant_meridians.append(meridian_code)
        _LOG.info("AMMA solfeggio_heal @ tick=%d meridian=%s hz=%.1f numerology=%d firing=%.4f",
                  tick, meridian_code, hz, nr, firing_rate)
        return s

    def _golden_needle(self, s: Lattice, coherence: float, tick: int) -> Lattice:
        """Targeted φ-weighted correction at the weakest pressure point."""
        neighbor_phase = get_neighbors_phase(s.phase)
        deviation = np.abs(np.sin(s.phase - neighbor_phase))
        # Find the most deviant cell (pressure point)
        worst = np.unravel_index(deviation.argmax(), deviation.shape)
        # Apply golden ratio weighted correction
        correction_magnitude = (THRESHOLD_DRIFT - coherence) * PHI * 0.1
        s.phase[worst] = neighbor_phase[worst]  # snap to neighbors
        # Propagate healing outward (1-ring)
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                for dk in [-1, 0, 1]:
                    ni = (worst[0] + di) % s.N
                    nj = (worst[1] + dj) % s.N
                    nk = (worst[2] + dk) % s.N
                    s.phase[ni, nj, nk] += correction_magnitude * np.sin(
                        neighbor_phase[ni, nj, nk] - s.phase[ni, nj, nk]
                    )
        s.phase %= (2 * np.pi)

        self.events.append(HealingEvent(tick, coherence, "golden_needle", correction_magnitude))
        _LOG.info("AMMA golden_needle @ tick=%d coherence=%.4f target=%s",
                  tick, coherence, worst)
        return s

    def _mitosis(self, s: Lattice, coherence: float, tick: int) -> Lattice:
        """Emergency: reset the most degraded octant from healthy template."""
        # Identify the worst octant (1/8 of lattice)
        mid = s.N // 2 or 1
        octants = []
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    sl = (slice(i * mid, (i + 1) * mid),
                          slice(j * mid, (j + 1) * mid),
                          slice(k * mid, (k + 1) * mid))
                    region = s.phase[sl]
                    local_c = float(np.abs(np.mean(np.exp(1j * region)))) if region.size > 0 else 0.0
                    octants.append((local_c, sl))
        octants.sort(key=lambda x: x[0])
        worst_slice = octants[0][1]

        # Regenerate from global mean phase (healthy template)
        mean_phase = np.angle(np.mean(np.exp(1j * s.phase))) if s.phase.size > 0 else 0.0
        shape = s.phase[worst_slice].shape
        s.phase[worst_slice] = mean_phase + np.random.uniform(-0.1, 0.1, shape)
        s.phase %= (2 * np.pi)
        s.amplitude[worst_slice] = np.clip(s.amplitude[worst_slice] * PHI * 0.5, 0.01, 1.0)

        correction_magnitude = THRESHOLD_CRITICAL - coherence
        self.events.append(HealingEvent(tick, coherence, "mitosis", correction_magnitude))
        _LOG.warning("AMMA mitosis @ tick=%d coherence=%.4f — octant regenerated",
                     tick, coherence)
        return s

    # ─── SELF-LEARN: Hebbian pattern memory + reward-modulated coupling ────────

    def learn(self, s: Lattice, prev_phase: np.ndarray, reward: float = 0.0) -> Lattice:
        """STDP-driven self-learning: strengthen pathways that produce coherence gain.
        Optional reward signal biases learning toward goal states."""
        coherence_now = s.coherence()
        coherence_delta = coherence_now - (self.history[-1] if self.history else 0.0)

        # Hebbian: phase correlations that improved coherence get reinforced
        phase_diff = np.sin(s.phase - prev_phase)
        # Reward-modulated plasticity: external reward amplifies learning
        lr = 0.01 * (1.0 + reward) if coherence_delta > 0 else 0.005
        s.amplitude += lr * np.abs(phase_diff) * np.sign(coherence_delta)
        s.amplitude = np.clip(s.amplitude, 0.01, 2.0)

        # Memory trace: accumulate successful patterns
        if coherence_delta > 0.01:
            if not hasattr(self, '_learned_patterns'):
                self._learned_patterns = []
            self._learned_patterns.append(s.phase.copy())
            # Keep only top-K patterns (bounded memory)
            if len(self._learned_patterns) > 16:
                self._learned_patterns = self._learned_patterns[-16:]

        self._learn_events += 1
        return s

    # ─── SELF-GROW: topology expansion + synaptogenesis + pruning ─────────────

    def grow(self, s: Lattice) -> Lattice:
        """Adaptive topology: sprout new connections where coherence is strong,
        prune where coupling energy is wasted."""
        coherence = s.coherence()
        if coherence < THRESHOLD_DRIFT:
            return s  # don't grow during instability

        # Synaptogenesis: amplify high-coherence regions (they earned more weight)
        local_coh = np.abs(np.mean(np.exp(1j * s.phase), axis=(1, 2)))  # per-layer
        mean_coh = np.mean(local_coh) if local_coh.size > 0 else 0.0
        growth_mask = np.zeros_like(s.phase, dtype=bool)
        for i, c in enumerate(local_coh):
            if c > mean_coh:
                growth_mask[i] = True
        s.amplitude[growth_mask] *= 1.0 + 0.01 * PHI  # φ-scaled growth

        # Pruning: attenuate regions that never synchronize (energy waste)
        if len(self.history) >= 32:
            # Identify persistently weak nodes
            recent = np.array(self.history[-32:])
            if np.mean(recent) > THRESHOLD_HEALTHY:
                # Stable enough to prune: reduce amplitude of lowest-energy nodes
                energy = np.abs(np.exp(1j * s.phase))
                prune_mask = energy < np.percentile(energy, 5)
                s.amplitude[prune_mask] *= 0.95  # slow attrition, not instant death

        s.amplitude = np.clip(s.amplitude, 0.01, 2.0)
        self._grow_events += 1
        return s

    # ─── SELF-ORGANIZE: emergent clustering + phase-locked assemblies ─────────

    def organize(self, s: Lattice) -> Lattice:
        """Emergent structure formation: detect phase-locked clusters and
        reinforce boundaries between assemblies (differentiation)."""
        N = s.N
        # Detect clusters: connected components of similar phase
        flat = s.phase.flatten()
        # Pairwise phase similarity → cluster via k-means on unit circle
        z = np.exp(1j * flat)
        # Find dominant modes (top-3 phase attractors)
        spectrum = np.fft.fftn(np.exp(1j * s.phase))
        magnitudes = np.abs(spectrum)
        # Top-K modes define assembly centers
        k = min(3, max(1, N // 3))
        top_indices = np.argsort(magnitudes.flatten())[-k:]
        top_phases = np.angle(spectrum.flatten()[top_indices])

        # Assign each node to nearest assembly
        assignments = np.argmin(
            np.abs(np.subtract.outer(flat, top_phases)), axis=1
        ).reshape(s.phase.shape)

        # Reinforce within-assembly coupling, weaken between-assembly
        for cluster_id in range(k):
            mask = assignments == cluster_id
            if mask.sum() < 2:
                continue
            # Tighten internal coupling (mean-field pull toward cluster center)
            cluster_phases = s.phase[mask]
            cluster_mean = np.angle(np.mean(np.exp(1j * cluster_phases)))
            s.phase[mask] += 0.005 * np.sin(cluster_mean - s.phase[mask])

        s.phase %= (2 * np.pi)

        # Route meridians: assign clusters to meridian channels
        self._active_assemblies = k
        self._organize_events += 1
        return s

    # ─── QUANTUM LOOP: heal → learn → grow → organize → (repeat) ───────────

    def quantum_loop(self, s: Lattice, tick: int, prev_phase: np.ndarray = None,
                     reward: float = 0.0) -> Lattice:
        """The AMMA quantum loop — four capacities feeding back into each other.
        Each capacity's output becomes the next capacity's input.
        The loop is self-referential: organization creates conditions for healing,
        healing enables learning, learning drives growth, growth produces new
        structures to organize. ∞"""
        s = self.check_and_heal(s, tick)
        if prev_phase is not None:
            s = self.learn(s, prev_phase, reward)
        s = self.grow(s)
        s = self.organize(s)
        return s

    # Alias for backward compat
    full_cycle = quantum_loop

    @property
    def status(self) -> dict:
        last = self.history[-1] if self.history else 0.0
        if last >= THRESHOLD_HEALTHY:
            level = "HEALTHY"
        elif last >= THRESHOLD_DRIFT:
            level = "DRIFT"
        elif last >= THRESHOLD_CRITICAL:
            level = "ANOMALY"
        else:
            level = "CRITICAL"
        return {
            "coherence": last,
            "level": level,
            "interventions": self.interventions,
            "learn_events": self._learn_events,
            "grow_events": self._grow_events,
            "organize_events": self._organize_events,
            "active_assemblies": getattr(self, '_active_assemblies', 0),
            "learned_patterns": len(getattr(self, '_learned_patterns', [])),
            "last_event": self.events[-1].__dict__ if self.events else None,
        }
