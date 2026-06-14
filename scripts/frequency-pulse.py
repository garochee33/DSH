"""
Mycelium Frequency Pulse — E8 node harmonic signature for mesh synchronization.

Called by mycelium-signal.sh before each mesh heartbeat. Runs the full Kuramoto
simulation with AMMA healing + MPS acceleration to convergence, then emits the
node's resonance state (phase, dominant frequency, coherence) so peer nodes can
phase-lock via Kuramoto coupling before distributed computation begins.

Output: JSON to stdout (consumed by bash caller)
"""

import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from agents.skills.frequency import schumann_resonances, fft_spectrum, synthesize
from compute.sim_evolved import run_sim, ALL_ORDERED, Lattice, K_OPTIMAL, PHI, BASE_FREQ, _USE_MPS

_MESH_CONFIG = os.path.join(os.path.dirname(__file__), "..", "agents", "core", ".mesh", "config.json")


def load_e8_config() -> dict:
    try:
        with open(_MESH_CONFIG) as f:
            cfg = json.load(f)
        return cfg.get("e8", {})
    except Exception:
        return {"rootIndex": 33, "activeRoots": 240, "tier": "sovereign"}


def compute_pulse() -> dict:
    """Run full simulation to convergence, then emit harmonic pulse."""
    e8 = load_e8_config()
    e8_root = e8.get("rootIndex", 33)
    active_roots = e8.get("activeRoots", 240)
    tier = e8.get("tier", "sovereign")

    # Run full Kuramoto sim with AMMA healing to convergence (64 ticks is enough)
    result = run_sim(
        label=f"pulse-e8r{e8_root}",
        N=3,
        pipeline=ALL_ORDERED,
        ticks=64,
        seed=e8_root,
        amma=True,
    )

    # Node's resonance frequency: BASE_FREQ * PHI^(root mod 7)
    schumann = schumann_resonances()
    node_freq = BASE_FREQ * (PHI ** (e8_root % 7))
    harmonic_index = e8_root % len(schumann)
    earth_coupling = schumann[harmonic_index]

    # Generate spectral signature from converged state
    probe = synthesize(
        frequencies=[node_freq, earth_coupling, node_freq * PHI],
        amplitudes=[result.final_coherence, 0.618, 0.382],
        duration=0.01,
        sr=44100,
    )
    spectrum = fft_spectrum(probe, 44100)
    peak_idx = int(np.argmax(spectrum["magnitudes"]))
    peak_freq = float(spectrum["frequencies"][peak_idx])
    peak_mag = float(20 * np.log10(spectrum["magnitudes"][peak_idx] + 1e-10))

    # Phase from converged lattice (reconstruct final state)
    np.random.seed(e8_root)
    lattice = Lattice(N=3)
    for _ in range(64):
        for _, fn in ALL_ORDERED:
            lattice = fn(lattice)
    phase = float(np.angle(np.mean(np.exp(1j * lattice.phase))))

    return {
        "e8Root": e8_root,
        "activeRoots": active_roots,
        "tier": tier,
        "nodeFreqHz": round(node_freq, 4),
        "earthCouplingHz": earth_coupling,
        "harmonicRatio": round(node_freq / earth_coupling, 6),
        "phase": round(phase, 6),
        "coherence": round(result.final_coherence, 6),
        "peakCoherence": round(result.peak_coherence, 6),
        "convergenceTick": result.convergence_tick,
        "kCoupling": K_OPTIMAL,
        "spectralPeakHz": round(peak_freq, 2),
        "spectralEnergyDb": round(peak_mag, 2),
        "mpsAccelerated": _USE_MPS,
        "ammaActive": True,
        "phi": PHI,
        "baseFreq": BASE_FREQ,
        "elapsedMs": round(result.elapsed_ms, 1),
    }


if __name__ == "__main__":
    pulse = compute_pulse()

    # Sign the pulse with ML-DSA-87 (post-quantum signature). The signing backend
    # (liboqs / `oqs`) is optional at install time. Mesh transport requires a signed
    # pulse, so the default behaviour is fail-closed: if the backend is missing we
    # refuse to emit a silently-unsigned pulse. Set DOME_ALLOW_UNSIGNED_PULSE=1 to
    # emit an explicitly-flagged unsigned pulse for local development only.
    try:
        # liboqs-python prints a banner to stdout on import; redirect it to stderr so
        # the pulse stdout stays pure JSON for the bash caller (mycelium-signal.sh).
        import contextlib
        with contextlib.redirect_stdout(sys.stderr):
            from compute.crypto.pqc import ensure_node_keys, sign_json, sha3
            signing_kp, kem_kp = ensure_node_keys()
        pulse["pqcSignature"] = sign_json(pulse, signing_kp.secret_key)
        pulse["pqcPubKeyHash"] = sha3(signing_kp.public_key)[:32]  # first 32 chars
        pulse["kemPubKeyHash"] = sha3(kem_kp.public_key)[:32]
        pulse["pqcSigned"] = True
    except ModuleNotFoundError as exc:
        if os.environ.get("DOME_ALLOW_UNSIGNED_PULSE") != "1":
            sys.stderr.write(
                f"frequency-pulse: PQC signing backend unavailable ({exc.name}); refusing to "
                "emit an unsigned mesh pulse. Install liboqs/oqs, or set "
                "DOME_ALLOW_UNSIGNED_PULSE=1 for local development only.\n"
            )
            sys.exit(2)
        pulse["pqcSigned"] = False
        pulse["pqcSignature"] = None

    print(json.dumps(pulse))
