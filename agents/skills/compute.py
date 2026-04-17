"""Compute skill — high-performance numerical and quantum computation."""
from __future__ import annotations
import numpy as np
from scipy import optimize
from numba import njit
import torch

SKILL = "compute"


def jit_compute(fn, *args):
    """JIT-compile a function with numba and run it."""
    return njit(fn)(*args)


def fft(signal: list[float]) -> np.ndarray:
    return np.fft.fft(np.array(signal))


def optimize_fn(fn, x0: list[float]) -> optimize.OptimizeResult:
    return optimize.minimize(fn, x0, method="L-BFGS-B")


def gpu_tensor(data) -> torch.Tensor:
    """Move tensor to MPS (Apple GPU) if available, else CPU."""
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    return torch.tensor(data, dtype=torch.float32).to(device)


def quantum_circuit(n_qubits: int = 2) -> dict:
    """Build and simulate a basic Bell state circuit via Qiskit."""
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    sim = AerSimulator()
    job = sim.run(qc, shots=1024)
    return job.result().get_counts()


def verify() -> bool:
    sig = [1.0, 0.0, -1.0, 0.0]
    assert len(fft(sig)) == 4
    t = gpu_tensor([1.0, 2.0, 3.0])
    assert t.shape == (3,)
    result = optimize_fn(lambda x: (x[0] - 2) ** 2, [0.0])
    assert abs(result.x[0] - 2.0) < 1e-4
    return True
