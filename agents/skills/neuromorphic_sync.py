"""
Neuromorphic Synchronization Skill — NeuroScale + STDP + Theta-Gamma
=====================================================================
Implements bio-inspired optimizations for the Kuramoto 3D lattice:
  1. NeuroScale local sync (no global barrier)
  2. STDP adaptive coupling (Hebbian weight evolution)
  3. Theta-gamma hierarchical monitoring (multi-timescale AMMA)

For full E8-240 spiking network + real k-NN + AMMA projection lens, use the canonical
`~/DOME-HUB/home/projects/trinity-consortium/scripts/e8_240_with_amma_lens.py`
(lava-snn-demo.py is legacy/superseded).
"""

import numpy as np
from dataclasses import dataclass, field

# ─── NeuroScale Local Sync ────────────────────────────────────────────────────

@dataclass
class NeuroScaleNode:
    """Local time management — node advances only when inputs are ready."""
    local_time: int = 0
    max_advance: int = 3  # T_adv: max ticks ahead of slowest neighbor

    def can_advance(self, neighbor_times: list[int]) -> bool:
        """Check if this node can advance its local clock."""
        if not neighbor_times:
            return True
        min_neighbor = min(neighbor_times)
        return (self.local_time - min_neighbor) < self.max_advance and \
               all(t >= self.local_time for t in neighbor_times)

    def advance(self) -> int:
        self.local_time += 1
        return self.local_time


def neuroscale_sync(phases: np.ndarray, coupling_fn, dt: float = 0.1) -> np.ndarray:
    """NeuroScale-inspired local sync: each node updates only when neighbors are ready.
    Eliminates global barrier — O(1) scaling for locally-connected networks."""
    N = phases.shape[0]
    nodes = [NeuroScaleNode() for _ in range(N ** 3)]
    new_phases = phases.copy()

    # Flatten for indexing
    flat = phases.flatten()
    updated = np.zeros(N ** 3, dtype=bool)

    # Each node checks local readiness (simulated single pass)
    for idx in range(N ** 3):
        i, j, k = np.unravel_index(idx, (N, N, N))
        # Get 6-connected neighbor times (simplified from 26 for efficiency)
        neighbors = []
        for di, dj, dk in [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)]:
            ni, nj, nk = (i+di) % N, (j+dj) % N, (k+dk) % N
            neighbors.append(nodes[np.ravel_multi_index((ni,nj,nk), (N,N,N))].local_time)

        if nodes[idx].can_advance(neighbors):
            # Apply coupling update
            neighbor_phases = []
            for di, dj, dk in [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)]:
                ni, nj, nk = (i+di) % N, (j+dj) % N, (k+dk) % N
                neighbor_phases.append(phases[ni, nj, nk])
            mean_neighbor = np.arctan2(
                np.mean(np.sin(neighbor_phases)),
                np.mean(np.cos(neighbor_phases))
            )
            new_phases[i, j, k] += dt * coupling_fn(mean_neighbor - phases[i, j, k])
            nodes[idx].advance()
            updated[idx] = True

    return new_phases % (2 * np.pi)


# ─── STDP Adaptive Coupling ──────────────────────────────────────────────────

@dataclass
class STDPState:
    """Spike-Timing-Dependent Plasticity state for adaptive coupling."""
    A_plus: float = 0.01       # LTP amplitude
    A_minus: float = 0.012     # LTD amplitude (slightly stronger → stability)
    tau_plus: float = 20.0     # LTP time constant (ms)
    tau_minus: float = 20.0    # LTD time constant (ms)
    w_min: float = 0.1         # Minimum coupling weight
    w_max: float = 5.0         # Maximum coupling weight


def stdp_update(coupling: np.ndarray, phases: np.ndarray, prev_phases: np.ndarray,
                state: STDPState = None) -> np.ndarray:
    """STDP-inspired adaptive coupling: strengthen connections that lead to sync.

    Phase advance = "spike timing". If node j's phase leads and node i follows
    (converges), strengthen K_ij. If coupling doesn't help, weaken.
    """
    if state is None:
        state = STDPState()

    N = coupling.shape[0]
    # Phase velocity as proxy for "spike timing"
    velocity = phases.flatten() - prev_phases.flatten()
    velocity = np.arctan2(np.sin(velocity), np.cos(velocity))  # wrap to [-π, π]

    new_coupling = coupling.copy()
    flat_phase = phases.flatten()

    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            # Δt proxy: phase difference change
            dt_proxy = velocity[j] - velocity[i]
            if dt_proxy > 0:
                # j leads, i follows → potentiate (LTP)
                dw = state.A_plus * np.exp(-abs(dt_proxy) / state.tau_plus)
            else:
                # i leads, j doesn't follow → depress (LTD)
                dw = -state.A_minus * np.exp(-abs(dt_proxy) / state.tau_minus)
            new_coupling[i, j] = np.clip(
                coupling[i, j] + dw, state.w_min, state.w_max
            )

    return new_coupling


def stdp_lattice_update(phases: np.ndarray, prev_phases: np.ndarray,
                        K: float, state: STDPState = None) -> float:
    """Simplified STDP for scalar coupling K: adjust global K based on convergence rate."""
    if state is None:
        state = STDPState()

    coherence_now = float(np.abs(np.mean(np.exp(1j * phases))))
    coherence_prev = float(np.abs(np.mean(np.exp(1j * prev_phases))))
    delta_coherence = coherence_now - coherence_prev

    if delta_coherence > 0:
        # Converging → potentiate (increase K slightly)
        K_new = K + state.A_plus * delta_coherence
    else:
        # Diverging → depress (decrease K slightly)
        K_new = K - state.A_minus * abs(delta_coherence)

    return float(np.clip(K_new, state.w_min, state.w_max))


# ─── Theta-Gamma Hierarchical Monitoring ─────────────────────────────────────

@dataclass
class ThetaGammaMonitor:
    """Multi-timescale AMMA monitoring inspired by neural oscillation coupling.

    Fast (gamma): local meridian phase-locking check every tick
    Slow (theta): global health sweep every theta_period ticks
    Cross-coupling: gamma amplitude modulated by theta phase
    """
    theta_period: int = 8       # Global sweep every N ticks (≈ 8Hz theta)
    gamma_per_theta: int = 7    # Local checks per global sweep (7±2 items)
    theta_tick: int = 0
    gamma_tick: int = 0
    theta_history: list = field(default_factory=list)
    gamma_history: list = field(default_factory=list)

    def tick(self, lattice_phases: np.ndarray) -> dict:
        """Run one monitoring tick. Returns health report."""
        self.gamma_tick += 1
        N = lattice_phases.shape[0]

        # Gamma: fast local coherence check
        local_coherences = []
        for i in range(N):
            for j in range(N):
                for k in range(N):
                    # 6-neighbor local coherence
                    neighbors = []
                    for di, dj, dk in [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)]:
                        ni, nj, nk = (i+di)%N, (j+dj)%N, (k+dk)%N
                        neighbors.append(lattice_phases[ni, nj, nk])
                    local_c = abs(np.mean(np.exp(1j * np.array(neighbors))))
                    local_coherences.append(local_c)

        gamma_coherence = float(np.mean(local_coherences))
        self.gamma_history.append(gamma_coherence)

        report = {
            "gamma_coherence": gamma_coherence,
            "gamma_min": float(np.min(local_coherences)),
            "gamma_tick": self.gamma_tick,
        }

        # Theta: slow global sweep
        if self.gamma_tick % self.theta_period == 0:
            self.theta_tick += 1
            global_coherence = float(np.abs(np.mean(np.exp(1j * lattice_phases))))
            self.theta_history.append(global_coherence)

            # Cross-frequency coupling: modulation index
            if len(self.gamma_history) >= self.theta_period:
                recent_gamma = np.array(self.gamma_history[-self.theta_period:])
                mi = float(np.std(recent_gamma) / (np.mean(recent_gamma) + 1e-10))
            else:
                mi = 0.0

            report.update({
                "theta_coherence": global_coherence,
                "theta_tick": self.theta_tick,
                "modulation_index": mi,
                "healthy": global_coherence > 0.85,
            })

        return report
