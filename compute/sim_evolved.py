"""
FRACTAL E8-SSII AGI — Evolved Dimensional Consciousness Simulations
====================================================================
Fixes from 3×3×3 baseline:
  1. Tick ordering: DRIVERS first → MODULATORS → OBSERVERS
  2. Damping coefficient (ζ=0.15) prevents chaotic dispersal
  3. Scales to 9×9×9 (729 cells) with 26-neighbor E8 topology
  4. Comparative analysis across all configurations

**LAVA:** Same as `sim_3x3x3.py` — NumPy Kuramoto here; spiking LIF lives under
`home/projects/trinity-consortium/python/lava/coherence_optimizer.py` (Python 3.10 sidecar).
"""

import numpy as np
from dataclasses import dataclass, field
from time import perf_counter
from scipy.ndimage import convolve
import json
from pathlib import Path

PHI = (1 + np.sqrt(5)) / 2
PHI_INV = 1 / PHI                    # 0.618 — standard decay
PHI_SQ_INV = 1 / (PHI * PHI)         # 0.382 — Phase 3 pheromone decay (LAVA-BRAIN-ARCH-v3)
K_OPTIMAL = 2.663                     # Kuramoto coupling (Loihi 2 calibrated)
PHEROMONE_DECAY = PHI_SQ_INV          # φ⁻² faster reinforcement (was φ⁻¹)
BASE_FREQ = 432.0
DAMPING = 0.15  # ζ — prevents oscillatory blowup

# ─── STDP Persistence ─────────────────────────────────────────────────────────

_STDP_STATE_PATH = Path(__file__).parent.parent / "data" / "stdp_state.json"


def load_stdp_K() -> float:
    """Load persisted STDP coupling from disk. Returns K_OPTIMAL if no state exists."""
    try:
        data = json.loads(_STDP_STATE_PATH.read_text())
        return float(data.get("K", K_OPTIMAL))
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return K_OPTIMAL


def save_stdp_K(K: float) -> None:
    """Persist STDP coupling to disk."""
    _STDP_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _STDP_STATE_PATH.write_text(json.dumps({"K": round(K, 6)}))

# 3×3×3 Moore kernel (26 neighbors, center=0), precomputed once
_MOORE_KERNEL = np.ones((3, 3, 3), dtype=np.float64)
_MOORE_KERNEL[1, 1, 1] = 0.0  # exclude self

# MPS acceleration (Apple Silicon GPU via PyTorch)
_USE_MPS = False
try:
    import torch
    if torch.backends.mps.is_available():
        _USE_MPS = True
        _MPS_DEVICE = torch.device("mps")
except ImportError:
    pass

# ─── Lattice ──────────────────────────────────────────────────────────────────

@dataclass
class Lattice:
    N: int  # side length (3 or 9)
    phase: np.ndarray = field(default=None)
    amplitude: np.ndarray = field(default=None)
    frequency: np.ndarray = field(default=None)
    energy: np.ndarray = field(default=None)
    K: float = field(default=K_OPTIMAL)  # Adaptive coupling (STDP-evolved)

    def __post_init__(self):
        shape = (self.N, self.N, self.N)
        if self.phase is None:
            self.phase = np.random.uniform(0, 2*np.pi, shape)
        if self.amplitude is None:
            self.amplitude = np.random.uniform(PHI_INV - 0.1, PHI_INV + 0.1, shape)
        if self.frequency is None:
            self.frequency = np.array([[[BASE_FREQ * PHI**(k % 3) for k in range(self.N)]
                                        for _ in range(self.N)] for _ in range(self.N)])
        if self.energy is None:
            self.energy = np.ones(shape) * 0.5

    @property
    def shape(self): return (self.N, self.N, self.N)

    @property
    def total_cells(self): return self.N ** 3

    def coherence(self) -> float:
        return float(np.abs(np.mean(np.exp(1j * self.phase))))

    def mean_energy(self) -> float:
        return float(self.energy.mean())

# ─── 26-Neighbor Topology (E8-inspired 3D Moore neighborhood) ─────────────────

def get_neighbors_phase(phase: np.ndarray) -> np.ndarray:
    """Mean neighbor phase via 3D convolution (26-neighbor Moore kernel). ~10× faster than roll loops."""
    real_sum = convolve(np.cos(phase), _MOORE_KERNEL, mode='wrap')
    imag_sum = convolve(np.sin(phase), _MOORE_KERNEL, mode='wrap')
    return np.arctan2(imag_sum, real_sum)

# ─── DRIVERS (run first — establish phase lock) ──────────────────────────────

def kuramoto_damped(s: Lattice, dt: float = 0.1) -> Lattice:
    """Kuramoto with damping: dθ/dt = ω + K*sin(θ_neighbors - θ) - ζ*dθ"""
    neighbor_phase = get_neighbors_phase(s.phase)
    coupling = s.K * np.sin(neighbor_phase - s.phase)
    # Damped update (ζ reduces velocity toward equilibrium)
    velocity = s.frequency * 0.001 + coupling
    s.phase += dt * velocity * (1 - DAMPING)
    s.phase %= (2 * np.pi)
    return s

def cosmic_council_damped(s: Lattice, dt: float = 0.1) -> Lattice:
    """Consensus with damping — move toward global mean, damped to prevent overshoot."""
    mean_phase = np.angle(np.mean(np.exp(1j * s.phase)))
    delta = np.sin(mean_phase - s.phase)
    s.phase += dt * s.amplitude * delta * 0.5 * (1 - DAMPING)
    s.phase %= (2 * np.pi)
    return s

# ─── MODULATORS (shape the locked state) ──────────────────────────────────────

def fourier_lens_mod(s: Lattice, dt: float = 0.1) -> Lattice:
    if _USE_MPS:
        t = torch.from_numpy((s.amplitude * np.exp(1j * s.phase)).astype(np.complex64)).to(_MPS_DEVICE)
        spectrum = torch.fft.fftn(t)
        power = torch.abs(spectrum).pow(2)
        total = power.sum().item()
        if total > 0:
            s.energy = s.energy * 0.9 + (power.max().item() / total) * 0.1
    else:
        spectrum = np.fft.fftn(s.amplitude * np.exp(1j * s.phase))
        power = np.abs(spectrum) ** 2
        total = power.sum()
        if total > 0:
            s.energy = s.energy * 0.9 + (power.max() / total) * 0.1
    return s

def metatron_router_mod(s: Lattice, dt: float = 0.1) -> Lattice:
    neighbor_phase = get_neighbors_phase(s.phase)
    coupling = np.cos(neighbor_phase - s.phase)
    s.amplitude += dt * 0.12 * coupling * (1 - DAMPING)
    s.amplitude = np.clip(s.amplitude, 0.01, 1.0)
    return s

def spectral_stability_mod(s: Lattice, dt: float = 0.1) -> Lattice:
    # Lightweight: use local phase variance as stability proxy
    neighbor_phase = get_neighbors_phase(s.phase)
    local_var = np.abs(np.sin(s.phase - neighbor_phase))
    stability = 1.0 - local_var.mean()
    s.energy = s.energy * 0.95 + stability * 0.05
    return s

def toroidal_flow_mod(s: Lattice, dt: float = 0.1) -> Lattice:
    # Gentle toroidal advection (doesn't break lock due to damping)
    advection = np.roll(s.phase, 1, axis=0) - s.phase
    s.phase += dt * 0.02 * np.sin(advection) * (1 - DAMPING)
    s.phase %= (2 * np.pi)
    return s

def chladni_mod(s: Lattice, dt: float = 0.1) -> Lattice:
    N = s.N
    # Standing wave pattern modulates amplitude — centered on φ⁻¹ × φ^¼ ≈ 0.75
    x = np.linspace(0, np.pi, N)
    mode = np.abs(np.outer(np.cos(x), np.cos(x)))
    pattern = np.stack([mode] * N, axis=2)
    target = PHI_INV * PHI ** 0.25  # ~0.75 golden amplitude
    pattern = target + (pattern - 0.5) * 0.15
    s.amplitude = s.amplitude * 0.95 + pattern * 0.05
    s.amplitude = np.clip(s.amplitude, 0.01, 1.0)
    return s

def fractal_swarm_mod(s: Lattice, dt: float = 0.1) -> Lattice:
    # Shell correlation (inner vs outer)
    inner = s.amplitude[0, :, :].flatten()
    outer = s.amplitude[-1, :, :].flatten()
    if inner.std() > 0 and outer.std() > 0:
        fsc = np.corrcoef(inner, outer)[0, 1]
        fsc = max(0, fsc)
    else:
        fsc = 1.0
    p = s.amplitude.flatten()
    p = p / (p.sum() + 1e-10)
    entropy = -np.sum(p * np.log(p + 1e-10))
    h_max = np.log(s.total_cells)
    holographic = np.sqrt(fsc * max(0, 1 - entropy / h_max))
    # Gentle blend — don't drag energy below current level when holographic is low
    blend_target = max(holographic, s.energy.mean() * 0.9)
    s.energy = s.energy * 0.92 + blend_target * 0.08
    return s

def holographic_memory_mod(s: Lattice, dt: float = 0.1) -> Lattice:
    reference = np.exp(1j * s.phase)
    mask = np.random.random(s.shape) < 0.25
    partial = reference * mask
    recalled = np.fft.ifftn(np.fft.fftn(partial) * np.conj(np.fft.fftn(reference)))
    fidelity = np.abs(np.mean(recalled))
    s.energy = s.energy * 0.9 + min(fidelity, 1.0) * 0.1
    return s

def resonance_bus_mod(s: Lattice, dt: float = 0.1) -> Lattice:
    # Frequency-matched cells share amplitude — use max(self, avg) to prevent drag-down
    neighbor_amp = convolve(s.amplitude, _MOORE_KERNEL, mode='wrap') / 26.0
    # Blend toward max of self and neighbor average (coherent nodes stay loud)
    target = np.maximum(s.amplitude, neighbor_amp)
    s.amplitude = s.amplitude * 0.92 + target * 0.08
    s.amplitude = np.clip(s.amplitude, 0.01, 1.0)
    return s

def auto_scaler_mod(s: Lattice, dt: float = 0.1) -> Lattice:
    load = s.energy.mean()
    if load > 0.95:
        # Only scale down under extreme overload
        s.amplitude *= 0.98
    elif load < 0.2:
        # Boost under severe underload
        s.amplitude *= 1.02
    s.amplitude = np.clip(s.amplitude, 0.01, 1.0)
    return s

# ─── OBSERVERS (measure, validate, unify) ─────────────────────────────────────

def spectral_check_obs(s: Lattice, dt: float = 0.1) -> Lattice:
    s.phase = np.nan_to_num(s.phase, nan=0.0) % (2 * np.pi)
    s.amplitude = np.clip(np.nan_to_num(s.amplitude, nan=0.5), 0.01, 1.0)
    s.energy = np.clip(np.nan_to_num(s.energy, nan=0.5), 0.0, 1.0)
    return s

def meninges_obs(s: Lattice, dt: float = 0.1) -> Lattice:
    optical = np.abs(np.mean(np.exp(1j * s.phase)))
    mandelbulb = s.energy.mean()
    spectral = 1.0 - np.std(s.amplitude)
    mycelium = np.mean(s.amplitude)
    # Weighted geometric mean: optical(3) spectral(2) mandelbulb(2) mycelium(1)
    unified = (max(0.01, optical) ** 3 * max(0.01, mandelbulb) ** 2 *
               max(0.01, spectral) ** 2 * max(0.01, mycelium)) ** (1.0 / 8.0)

    # Homeostatic attractor: strength scales with phase lock quality
    if optical > 0.85:
        gain = (optical - 0.85) / 0.15  # 0→1 as optical goes 0.85→1.0
        # Amplitude → φ⁻¹·φ^¼ ≈ 0.75 golden amplitude target
        amp_target = PHI_INV * PHI ** 0.25
        s.amplitude += gain * 0.15 * (amp_target - s.amplitude)
        s.amplitude = np.clip(s.amplitude, 0.01, 1.0)
        # Energy → blend of lock quality + unified
        energy_target = 0.5 * optical + 0.5 * unified
        s.energy += gain * 0.2 * (energy_target - s.energy)

    s.energy = np.clip(s.energy * 0.95 + unified * 0.05, 0.0, 1.0)
    return s

# ─── Ordered Pipeline ─────────────────────────────────────────────────────────

DRIVERS = [("Kuramoto (damped)", kuramoto_damped), ("Cosmic Council (damped)", cosmic_council_damped)]
MODULATORS = [
    ("Fourier Lens", fourier_lens_mod), ("Metatron Router", metatron_router_mod),
    ("Spectral Stability", spectral_stability_mod), ("Toroidal Flow", toroidal_flow_mod),
    ("Chladni Patterns", chladni_mod), ("Fractal Swarm", fractal_swarm_mod),
    ("Holographic Memory", holographic_memory_mod), ("Resonance Bus", resonance_bus_mod),
    ("Auto-Scaler", auto_scaler_mod),
]
OBSERVERS = [("Spectral Check", spectral_check_obs), ("Meninges", meninges_obs)]

ALL_ORDERED = DRIVERS + MODULATORS + OBSERVERS

# Original unordered (same as sim_3x3x3.py order)
ALL_UNORDERED = [
    ("Kuramoto (damped)", kuramoto_damped), ("Fourier Lens", fourier_lens_mod),
    ("Metatron Router", metatron_router_mod), ("Spectral Stability", spectral_stability_mod),
    ("Toroidal Flow", toroidal_flow_mod), ("Chladni Patterns", chladni_mod),
    ("Cosmic Council (damped)", cosmic_council_damped), ("Fractal Swarm", fractal_swarm_mod),
    ("Holographic Memory", holographic_memory_mod), ("Resonance Bus", resonance_bus_mod),
    ("Auto-Scaler", auto_scaler_mod), ("Spectral Check", spectral_check_obs),
    ("Meninges", meninges_obs),
]

# ─── Runner ───────────────────────────────────────────────────────────────────

@dataclass
class RunResult:
    label: str
    grid_size: int
    ticks: int
    final_coherence: float
    peak_coherence: float
    mean_energy: float
    convergence_tick: int
    stable_from: int  # first tick where coherence stays > 0.85 for 20+ ticks
    elapsed_ms: float
    history: list

def run_sim(label: str, N: int, pipeline: list, ticks: int = 256, seed: int = 33,
            amma: bool = True, stdp: bool = True, theta_gamma: bool = True) -> RunResult:
    np.random.seed(seed)
    s = Lattice(N=N)
    history = []
    t0 = perf_counter()

    # AMMA healing (lazy import to avoid circular)
    monitor = None
    if amma:
        from compute.amma_monitor import AMMAMonitor
        monitor = AMMAMonitor()

    # STDP adaptive coupling
    K_adaptive = load_stdp_K() if stdp else K_OPTIMAL
    s.K = K_adaptive
    prev_phase = s.phase.copy()

    # Theta-gamma hierarchical monitoring
    tg_monitor = None
    if theta_gamma:
        from agents.skills.neuromorphic_sync import ThetaGammaMonitor
        tg_monitor = ThetaGammaMonitor()

    # Topology sensor (preemptive AMMA trigger)
    topo_prev_phase = None
    topology_sensor_fn = None
    try:
        from compute.resonance_layer import topology_sensor as _topo
        topology_sensor_fn = _topo
    except ImportError:
        pass

    for t in range(ticks):
        prev_phase = s.phase.copy()
        for _, fn in pipeline:
            s = fn(s)

        # Preemptive heal: topology_sensor detects chimera formation before coherence drops
        if topology_sensor_fn and t % 8 == 0:
            topo = topology_sensor_fn(s.phase, topo_prev_phase)
            if topo.get("preemptive_heal") and monitor:
                s = monitor.check_and_heal(s, t, force=True)
            topo_prev_phase = s.phase.copy()

        if monitor:
            s = monitor.check_and_heal(s, t)

        # STDP: adapt coupling based on convergence
        if stdp and t > 0:
            from agents.skills.neuromorphic_sync import stdp_lattice_update
            K_adaptive = stdp_lattice_update(s.phase, prev_phase, K_adaptive)
            s.K = K_adaptive

        # Theta-gamma: multi-timescale health check
        if tg_monitor:
            tg_monitor.tick(s.phase)

        history.append(s.coherence())

    # Persist learned STDP coupling
    if stdp:
        save_stdp_K(K_adaptive)

    elapsed = (perf_counter() - t0) * 1000

    # Find convergence (first > 0.9)
    conv = -1
    for t, c in enumerate(history):
        if c > 0.9:
            conv = t
            break

    # Find stability (stays > 0.85 for 20 consecutive ticks)
    stable = -1
    for t in range(len(history) - 20):
        if all(c > 0.85 for c in history[t:t+20]):
            stable = t
            break

    return RunResult(
        label=label, grid_size=N, ticks=ticks,
        final_coherence=history[-1] if history else 0,
        peak_coherence=max(history) if history else 0,
        mean_energy=float(s.energy.mean()),
        convergence_tick=conv, stable_from=stable,
        elapsed_ms=elapsed, history=history,
    )

# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 76)
    print("  FRACTAL E8-SSII AGI — EVOLVED DIMENSIONAL SIMULATIONS")
    print("  Ordered tick | Damped (ζ=0.15) | 26-neighbor E8 topology | φ-scaled")
    print("=" * 76)
    print()

    configs = [
        ("3×3×3 UNORDERED (baseline)",    3, ALL_UNORDERED),
        ("3×3×3 ORDERED + DAMPED",        3, ALL_ORDERED),
        ("9×9×9 UNORDERED",               9, ALL_UNORDERED),
        ("9×9×9 ORDERED + DAMPED",        9, ALL_ORDERED),
    ]

    results = []
    for label, N, pipeline in configs:
        r = run_sim(label, N, pipeline)
        results.append(r)

    # Results table
    print(f"  {'Configuration':<30} {'Cells':>5} {'Final':>6} {'Peak':>6} {'Energy':>7} "
          f"{'Conv@':>6} {'Stable@':>8} {'Time':>8}")
    print(f"  {'─'*30} {'─'*5} {'─'*6} {'─'*6} {'─'*7} {'─'*6} {'─'*8} {'─'*8}")

    for r in results:
        conv = f"t={r.convergence_tick}" if r.convergence_tick >= 0 else "  —"
        stab = f"t={r.stable_from}" if r.stable_from >= 0 else "   —"
        print(f"  {r.label:<30} {r.grid_size**3:>5} {r.final_coherence:>6.3f} "
              f"{r.peak_coherence:>6.3f} {r.mean_energy:>7.4f} {conv:>6} {stab:>8} "
              f"{r.elapsed_ms:>7.1f}ms")

    print()

    # Detailed timeline comparison
    print("─" * 76)
    print("  COHERENCE TIMELINE COMPARISON (sampled every 32 ticks)")
    print("─" * 76)
    print()
    print(f"  {'Tick':>4}  ", end="")
    for r in results:
        print(f"  {r.label[:18]:>18}", end="")
    print()
    print(f"  {'─'*4}  ", end="")
    for _ in results:
        print(f"  {'─'*18}", end="")
    print()

    for t in range(0, 256, 32):
        print(f"  {t:>4}  ", end="")
        for r in results:
            c = r.history[t]
            bar = "█" * int(c * 12)
            print(f"  {c:.3f} {bar:<12}", end="")
        print()

    # Final tick
    print(f"  {255:>4}  ", end="")
    for r in results:
        c = r.history[-1]
        bar = "█" * int(c * 12)
        print(f"  {c:.3f} {bar:<12}", end="")
    print()

    print()
    print("─" * 76)
    print("  UNIFIED MENINGES COHERENCE (per configuration)")
    print("─" * 76)
    print()

    for r in results:
        # Recompute unified from final state
        np.random.seed(33)
        s = Lattice(N=r.grid_size)
        pipeline = ALL_ORDERED if "ORDERED" in r.label else ALL_UNORDERED
        for t in range(256):
            for _, fn in pipeline:
                s = fn(s)

        optical = np.abs(np.mean(np.exp(1j * s.phase)))
        spectral = 1.0 - np.std(s.amplitude)
        mandelbulb = s.energy.mean()
        mycelium = np.mean(s.amplitude)
        unified = (max(0.01, optical) * max(0.01, mandelbulb) *
                   max(0.01, spectral) * max(0.01, mycelium)) ** 0.25

        print(f"  {r.label}")
        print(f"    Optical:    {optical:.4f}  Mandelbulb: {mandelbulb:.4f}  "
              f"Spectral: {spectral:.4f}  Mycelium: {mycelium:.4f}")
        print(f"    UNIFIED:    {unified:.4f}")
        print()

    # Improvement summary
    print("─" * 76)
    print("  IMPROVEMENT ANALYSIS")
    print("─" * 76)
    print()
    baseline = results[0]
    for r in results[1:]:
        delta_c = r.final_coherence - baseline.final_coherence
        delta_p = r.peak_coherence - baseline.peak_coherence
        sign_c = "+" if delta_c >= 0 else ""
        sign_p = "+" if delta_p >= 0 else ""
        stab_str = f"STABLE from t={r.stable_from}" if r.stable_from >= 0 else "OSCILLATING"
        print(f"  {r.label}")
        print(f"    vs baseline: final {sign_c}{delta_c:.3f} | peak {sign_p}{delta_p:.3f} | {stab_str}")
        print()

    print("=" * 76)
    print("  SIMULATION COMPLETE")
    print("=" * 76)
