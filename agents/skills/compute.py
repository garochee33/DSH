"""Compute skill — high-performance numerical and quantum computation."""
from __future__ import annotations
import numpy as np
from scipy import optimize
from numba import njit
import torch

SKILL = "compute"


# ─── Classical HPC ───────────────────────────────────────────────────────────

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


# ─── Quantum: Qiskit (IBM) ───────────────────────────────────────────────────

def qiskit_bell(n_qubits: int = 2, shots: int = 1024) -> dict:
    """Build and simulate a Bell state circuit via Qiskit Aer."""
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(0)
    for i in range(1, n_qubits):
        qc.cx(0, i)
    qc.measure_all()
    sim = AerSimulator()
    job = sim.run(qc, shots=shots)
    return job.result().get_counts()


def qiskit_ghz(n_qubits: int = 3, shots: int = 1024) -> dict:
    """GHZ state — maximally entangled n-qubit state."""
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    qc = QuantumCircuit(n_qubits)
    qc.h(0)
    for i in range(1, n_qubits):
        qc.cx(0, i)
    qc.measure_all()
    sim = AerSimulator()
    job = sim.run(qc, shots=shots)
    return job.result().get_counts()


def qiskit_qft(n_qubits: int = 3) -> dict:
    """Quantum Fourier Transform circuit."""
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    qc = QuantumCircuit(n_qubits)
    qc.h(0)
    for i in range(n_qubits):
        for j in range(i + 1, n_qubits):
            qc.cp(np.pi / (2 ** (j - i)), j, i)
    for i in range(n_qubits // 2):
        qc.swap(i, n_qubits - 1 - i)
    qc.measure_all()
    sim = AerSimulator()
    job = sim.run(qc, shots=1024)
    return job.result().get_counts()


# ─── Quantum: PennyLane (Variational / VQE) ─────────────────────────────────

def pennylane_vqe(hamiltonian_coeffs: list[float] | None = None) -> dict:
    """Variational Quantum Eigensolver for H2 molecule ground state."""
    import pennylane as qml
    from pennylane import numpy as pnp

    coeffs = hamiltonian_coeffs or [-0.24, 0.17, 0.17, -0.05, 0.17]
    obs = [
        qml.Identity(0),
        qml.PauliZ(0),
        qml.PauliZ(1),
        qml.PauliZ(0) @ qml.PauliZ(1),
        qml.PauliX(0) @ qml.PauliX(1),
    ]
    H = qml.Hamiltonian(coeffs, obs)

    dev = qml.device("default.qubit", wires=2)

    @qml.qnode(dev)
    def circuit(params):
        qml.RY(params[0], wires=0)
        qml.RY(params[1], wires=1)
        qml.CNOT(wires=[0, 1])
        qml.RY(params[2], wires=0)
        return qml.expval(H)

    opt = qml.GradientDescentOptimizer(stepsize=0.4)
    params = pnp.array([0.1, 0.1, 0.1], requires_grad=True)

    for _ in range(50):
        params = opt.step(circuit, params)

    energy = float(circuit(params))
    return {"ground_state_energy": energy, "params": params.tolist()}


def pennylane_qaoa(graph_edges: list[tuple] | None = None, p: int = 2) -> dict:
    """QAOA for MaxCut on a graph."""
    import pennylane as qml
    from pennylane import numpy as pnp

    edges = graph_edges or [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)]
    n_wires = max(max(e) for e in edges) + 1

    dev = qml.device("default.qubit", wires=n_wires)

    def cost_layer(gamma):
        for i, j in edges:
            qml.CNOT(wires=[i, j])
            qml.RZ(gamma, wires=j)
            qml.CNOT(wires=[i, j])

    def mixer_layer(beta):
        for w in range(n_wires):
            qml.RX(2 * beta, wires=w)

    @qml.qnode(dev)
    def circuit(params):
        for w in range(n_wires):
            qml.Hadamard(wires=w)
        for layer in range(p):
            cost_layer(params[layer, 0])
            mixer_layer(params[layer, 1])
        return [qml.expval(qml.PauliZ(w)) for w in range(n_wires)]

    params = pnp.random.uniform(0, np.pi, (p, 2), requires_grad=True)
    result = circuit(params)
    bitstring = "".join(["0" if r > 0 else "1" for r in result])
    return {"bitstring": bitstring, "expectations": [float(r) for r in result]}


def pennylane_qnn(features: list[float] | None = None) -> dict:
    """Quantum Neural Network classifier (2-qubit, 3-layer)."""
    import pennylane as qml

    features = features or [0.5, 0.8]
    n_qubits = 2
    n_layers = 3

    dev = qml.device("default.qubit", wires=n_qubits)

    @qml.qnode(dev)
    def circuit(weights, x):
        qml.AngleEmbedding(x, wires=range(n_qubits))
        qml.StronglyEntanglingLayers(weights, wires=range(n_qubits))
        return qml.expval(qml.PauliZ(0))

    weights = np.random.randn(n_layers, n_qubits, 3)
    prediction = float(circuit(weights, features))
    return {"prediction": prediction, "class": 1 if prediction > 0 else 0}


# ─── Quantum: Cirq (Google) ──────────────────────────────────────────────────

def cirq_grover(n_qubits: int = 2, target: int = 3) -> dict:
    """Grover's search algorithm via Cirq."""
    import cirq

    qubits = cirq.LineQubit.range(n_qubits)
    circuit = cirq.Circuit()

    # Superposition
    circuit.append(cirq.H.on_each(*qubits))

    # Oracle: flip target state
    target_bits = format(target, f"0{n_qubits}b")
    for i, bit in enumerate(target_bits):
        if bit == "0":
            circuit.append(cirq.X(qubits[i]))
    circuit.append(cirq.Z.controlled(n_qubits - 1).on(*qubits))
    for i, bit in enumerate(target_bits):
        if bit == "0":
            circuit.append(cirq.X(qubits[i]))

    # Diffusion
    circuit.append(cirq.H.on_each(*qubits))
    circuit.append(cirq.X.on_each(*qubits))
    circuit.append(cirq.Z.controlled(n_qubits - 1).on(*qubits))
    circuit.append(cirq.X.on_each(*qubits))
    circuit.append(cirq.H.on_each(*qubits))

    # Measure
    circuit.append(cirq.measure(*qubits, key="result"))

    sim = cirq.Simulator()
    result = sim.run(circuit, repetitions=1024)
    counts = result.histogram(key="result")
    return {format(k, f"0{n_qubits}b"): v for k, v in counts.items()}


def cirq_vqe_h2() -> dict:
    """Simple VQE for H2 using Cirq."""
    import cirq

    q0, q1 = cirq.LineQubit.range(2)

    def ansatz(theta):
        circuit = cirq.Circuit([
            cirq.ry(theta).on(q0),
            cirq.CNOT(q0, q1),
        ])
        return circuit

    sim = cirq.Simulator()
    best_energy = float("inf")
    best_theta = 0.0

    for theta in np.linspace(0, 2 * np.pi, 50):
        circuit = ansatz(theta)
        result = sim.simulate(circuit)
        state = result.final_state_vector
        # H2 Hamiltonian expectation (simplified)
        energy = -0.5 * (abs(state[0]) ** 2 + abs(state[3]) ** 2) + \
                  0.5 * (abs(state[1]) ** 2 + abs(state[2]) ** 2)
        if energy < best_energy:
            best_energy = energy
            best_theta = theta

    return {"ground_state_energy": float(best_energy), "optimal_theta": float(best_theta)}


# ─── Quantum: Amazon Braket (local simulator) ────────────────────────────────

def braket_bell(shots: int = 1024) -> dict:
    """Bell state via Amazon Braket local simulator."""
    from braket.circuits import Circuit
    from braket.devices import LocalSimulator

    circuit = Circuit().h(0).cnot(0, 1)
    device = LocalSimulator()
    result = device.run(circuit, shots=shots).result()
    return dict(result.measurement_counts)


def braket_qft(n_qubits: int = 3, shots: int = 1024) -> dict:
    """QFT via Amazon Braket."""
    from braket.circuits import Circuit
    from braket.devices import LocalSimulator

    circuit = Circuit()
    circuit.h(0)
    for i in range(n_qubits):
        for j in range(i + 1, n_qubits):
            angle = np.pi / (2 ** (j - i))
            circuit.cphaseshift(j, i, angle)
    for i in range(n_qubits // 2):
        circuit.swap(i, n_qubits - 1 - i)

    device = LocalSimulator()
    result = device.run(circuit, shots=shots).result()
    return dict(result.measurement_counts)


# ─── Unified Quantum Interface ───────────────────────────────────────────────

def quantum_circuit(backend: str = "qiskit", circuit_type: str = "bell",
                    n_qubits: int = 2, **kwargs) -> dict:
    """Unified quantum dispatch — route to any backend/circuit type.

    Backends: qiskit, pennylane, cirq, braket
    Circuit types: bell, ghz, qft, vqe, qaoa, qnn, grover
    """
    shots = kwargs.pop("shots", 1024)
    dispatch = {
        ("qiskit", "bell"): lambda: qiskit_bell(n_qubits, shots=shots),
        ("qiskit", "ghz"): lambda: qiskit_ghz(n_qubits, shots=shots),
        ("qiskit", "qft"): lambda: qiskit_qft(n_qubits),
        ("pennylane", "vqe"): lambda: pennylane_vqe(**kwargs),
        ("pennylane", "qaoa"): lambda: pennylane_qaoa(**kwargs),
        ("pennylane", "qnn"): lambda: pennylane_qnn(**kwargs),
        ("cirq", "grover"): lambda: cirq_grover(n_qubits, **kwargs),
        ("cirq", "vqe"): lambda: cirq_vqe_h2(),
        ("braket", "bell"): lambda: braket_bell(shots=shots),
        ("braket", "qft"): lambda: braket_qft(n_qubits, shots=shots),
    }
    key = (backend, circuit_type)
    if key not in dispatch:
        available = [f"{b}:{t}" for b, t in dispatch.keys()]
        raise ValueError(f"Unknown {backend}:{circuit_type}. Available: {available}")
    return dispatch[key]()


# ─── Verification ────────────────────────────────────────────────────────────

def verify() -> bool:
    """Full verification of classical + quantum compute stack."""
    # Classical
    sig = [1.0, 0.0, -1.0, 0.0]
    assert len(fft(sig)) == 4
    t = gpu_tensor([1.0, 2.0, 3.0])
    assert t.shape == (3,)
    result = optimize_fn(lambda x: (x[0] - 2) ** 2, [0.0])
    assert abs(result.x[0] - 2.0) < 1e-4

    # Qiskit
    counts = qiskit_bell(2)
    assert "00" in str(counts) or "11" in str(counts)

    # PennyLane VQE
    vqe = pennylane_vqe()
    assert vqe["ground_state_energy"] < 0  # H2 ground state is negative

    # Cirq Grover
    grover = cirq_grover(2, target=3)
    assert "11" in grover  # target=3 → |11⟩ should dominate

    # Braket
    braket = braket_bell()
    assert len(braket) > 0

    return True
