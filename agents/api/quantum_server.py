"""DOME-HUB Quantum API — minimal production server (port 8001)

Self-contained: no dependency on agents/__init__.py or numba/torch.
"""
import hmac, json, logging, os, time
from collections import deque
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("dome-hub-quantum")

app = FastAPI(title="DOME-HUB Quantum API")

# ── Metrics store (last 100 requests) ────────────────────────────────────────
_metrics = deque(maxlen=100)
_start_time = time.time()
_SECRET = os.environ.get("HUB_API_SECRET", "")


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path in ("/health", "/docs", "/openapi.json"):
        return await call_next(request)
    if not _SECRET:
        return await call_next(request)
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer ") and hmac.compare_digest(auth[7:], _SECRET):
        return await call_next(request)
    return JSONResponse({"error": "auth required"}, status_code=401)


class QuantumRequest(BaseModel):
    backend: str = "qiskit"
    circuit_type: str = "bell"
    n_qubits: int = 2
    shots: int = 1024


@app.get("/health")
async def health():
    return {"status": "ok", "service": "dome-hub-quantum", "uptime": time.time() - _start_time, "requests_total": len(_metrics)}

@app.get("/metrics")
async def metrics():
    if not _metrics:
        return {"total": 0, "avg_latency_ms": 0, "p95_latency_ms": 0, "errors": 0}
    latencies = [m["latency_ms"] for m in _metrics if m.get("ok")]
    errors = sum(1 for m in _metrics if not m.get("ok"))
    latencies.sort()
    p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0
    return {
        "total": len(_metrics),
        "avg_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else 0,
        "p95_latency_ms": round(p95, 2),
        "max_latency_ms": round(max(latencies), 2) if latencies else 0,
        "errors": errors,
        "uptime_s": round(time.time() - _start_time, 1),
    }


# ── Quantum backends (lazy imports) ──────────────────────────────────────────

def _qiskit_bell(n_qubits=2, shots=1024):
    from qiskit import QuantumCircuit
    from qiskit.primitives import StatevectorSampler
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(0)
    for i in range(1, n_qubits):
        qc.cx(0, i)
    qc.measure_all()
    sampler = StatevectorSampler()
    result = sampler.run([qc], shots=shots).result()
    counts = result[0].data.meas.get_counts()
    return {"counts": counts, "backend": "qiskit", "circuit": "bell", "n_qubits": n_qubits}


def _qiskit_ghz(n_qubits=3, shots=1024):
    from qiskit import QuantumCircuit
    from qiskit.primitives import StatevectorSampler
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(0)
    for i in range(1, n_qubits):
        qc.cx(0, i)
    qc.measure_all()
    sampler = StatevectorSampler()
    result = sampler.run([qc], shots=shots).result()
    counts = result[0].data.meas.get_counts()
    return {"counts": counts, "backend": "qiskit", "circuit": "ghz", "n_qubits": n_qubits}


def _qiskit_qft(n_qubits=3):
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import QFT
    from qiskit.quantum_info import Statevector
    qc = QuantumCircuit(n_qubits)
    qc.compose(QFT(n_qubits), inplace=True)
    sv = Statevector.from_instruction(qc)
    return {"statevector_norm": float(sv.data.conj() @ sv.data).real, "backend": "qiskit", "circuit": "qft", "n_qubits": n_qubits}


def _pennylane_vqe(**kwargs):
    import pennylane as qml
    from pennylane import numpy as pnp
    symbols = ["H", "H"]
    coords = pnp.array([0.0, 0.0, -0.6614, 0.0, 0.0, 0.6614])
    H, qubits = qml.qchem.molecular_hamiltonian(symbols, coords)
    dev = qml.device("default.qubit", wires=qubits)
    @qml.qnode(dev)
    def circuit(params):
        qml.BasisState(pnp.array([1, 1, 0, 0]), wires=range(qubits))
        qml.DoubleExcitation(params[0], wires=[0, 1, 2, 3])
        return qml.expval(H)
    opt = qml.GradientDescentOptimizer(stepsize=0.4)
    params = pnp.array([0.0])
    for _ in range(20):
        params = opt.step(circuit, params)
    energy = float(circuit(params))
    return {"ground_state_energy": energy, "backend": "pennylane", "circuit": "vqe"}


def _pennylane_qaoa(**kwargs):
    import pennylane as qml
    from pennylane import numpy as pnp
    n = kwargs.get("n_nodes", 4)
    edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
    cost_h = qml.Hamiltonian(
        [0.5] * len(edges),
        [qml.PauliZ(e[0]) @ qml.PauliZ(e[1]) for e in edges],
    )
    mixer_h = qml.Hamiltonian([1.0] * n, [qml.PauliX(i) for i in range(n)])
    dev = qml.device("default.qubit", wires=n)
    p = 2
    @qml.qnode(dev)
    def qaoa_circuit(gammas, betas):
        for i in range(n):
            qml.Hadamard(wires=i)
        for layer in range(p):
            qml.ApproxTimeEvolution(cost_h, gammas[layer], 1)
            qml.ApproxTimeEvolution(mixer_h, betas[layer], 1)
        return qml.expval(cost_h)
    opt = qml.GradientDescentOptimizer(stepsize=0.1)
    gammas = pnp.array([0.5, 0.5])
    betas = pnp.array([0.5, 0.5])
    for _ in range(10):
        gammas, betas = opt.step(qaoa_circuit, gammas, betas)
    cost = float(qaoa_circuit(gammas, betas))
    return {"cost": cost, "backend": "pennylane", "circuit": "qaoa", "layers": p}


def _pennylane_qnn(**kwargs):
    import pennylane as qml
    from pennylane import numpy as pnp
    n_wires = 4
    dev = qml.device("default.qubit", wires=n_wires)
    @qml.qnode(dev)
    def qnn(inputs, weights):
        qml.AngleEmbedding(inputs, wires=range(n_wires))
        qml.StronglyEntanglingLayers(weights, wires=range(n_wires))
        return [qml.expval(qml.PauliZ(i)) for i in range(n_wires)]
    weights = pnp.random.uniform(0, 2 * pnp.pi, (3, n_wires, 3))
    inputs = pnp.array([0.1, 0.2, 0.3, 0.4])
    out = qnn(inputs, weights)
    return {"output": [float(o) for o in out], "backend": "pennylane", "circuit": "qnn"}


def _cirq_grover(n_qubits=2, **kwargs):
    import cirq
    target = kwargs.get("target", 3)
    qubits = cirq.LineQubit.range(n_qubits)
    circuit = cirq.Circuit()
    circuit.append(cirq.H.on_each(*qubits))
    # Oracle
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
    circuit.append(cirq.measure(*qubits, key="result"))
    sim = cirq.Simulator()
    result = sim.run(circuit, repetitions=1024)
    counts = result.histogram(key="result")
    return {format(k, f"0{n_qubits}b"): v for k, v in counts.items()}


def _cirq_vqe():
    import cirq, numpy as np
    q0, q1 = cirq.LineQubit.range(2)
    def ansatz(theta):
        c = cirq.Circuit([cirq.ry(theta)(q0), cirq.CNOT(q0, q1)])
        return c
    def energy(theta):
        c = ansatz(theta)
        sim = cirq.Simulator()
        result = sim.simulate(c)
        sv = result.final_state_vector
        H = np.array([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]], dtype=complex)
        return float(np.real(sv.conj() @ H @ sv))
    best_theta, best_e = 0, 999
    for theta in np.linspace(0, 2 * np.pi, 50):
        e = energy(theta)
        if e < best_e:
            best_e, best_theta = e, theta
    return {"ground_energy": best_e, "optimal_theta": best_theta, "backend": "cirq", "circuit": "vqe"}


def _braket_bell(shots=1024):
    try:
        from braket.circuits import Circuit
        from braket.devices import LocalSimulator
        circuit = Circuit().h(0).cnot(0, 1)
        device = LocalSimulator()
        result = device.run(circuit, shots=shots).result()
        return dict(result.measurement_counts)
    except ImportError:
        from qiskit import QuantumCircuit
        from qiskit.primitives import StatevectorSampler
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()
        sampler = StatevectorSampler()
        result = sampler.run([qc], shots=shots).result()
        return result[0].data.meas.get_counts()


def _braket_qft(n_qubits=3, shots=1024):
    return _qiskit_qft(n_qubits)


_DISPATCH = {
    ("qiskit", "bell"): _qiskit_bell,
    ("qiskit", "ghz"): _qiskit_ghz,
    ("qiskit", "qft"): _qiskit_qft,
    ("pennylane", "vqe"): _pennylane_vqe,
    ("pennylane", "qaoa"): _pennylane_qaoa,
    ("pennylane", "qnn"): _pennylane_qnn,
    ("cirq", "grover"): _cirq_grover,
    ("cirq", "vqe"): _cirq_vqe,
    ("braket", "bell"): _braket_bell,
    ("braket", "qft"): _braket_qft,
}


@app.post("/quantum/run")
async def quantum_run(req: QuantumRequest):
    key = (req.backend, req.circuit_type)
    if key not in _DISPATCH:
        available = [f"{b}:{t}" for b, t in _DISPATCH.keys()]
        _metrics.append({"ok": False, "error": "unknown_circuit", "ts": time.time()})
        return JSONResponse({"error": f"Unknown {req.backend}:{req.circuit_type}", "available": available}, status_code=400)
    t0 = time.time()
    try:
        result = _DISPATCH[key](n_qubits=req.n_qubits, shots=req.shots) if req.backend != "pennylane" else _DISPATCH[key]()
        latency_ms = (time.time() - t0) * 1000
        _metrics.append({"ok": True, "backend": req.backend, "circuit": req.circuit_type, "latency_ms": latency_ms, "ts": time.time()})
        logger.info(f"quantum_run {req.backend}:{req.circuit_type} n={req.n_qubits} → {latency_ms:.1f}ms")
        if latency_ms > 5000:
            logger.warning(f"SLOW quantum_run {req.backend}:{req.circuit_type} took {latency_ms:.0f}ms")
        return {"ok": True, "result": result, "latency_ms": round(latency_ms, 2)}
    except Exception as e:
        latency_ms = (time.time() - t0) * 1000
        _metrics.append({"ok": False, "backend": req.backend, "circuit": req.circuit_type, "latency_ms": latency_ms, "error": str(e), "ts": time.time()})
        logger.error(f"quantum_run FAILED {req.backend}:{req.circuit_type}: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/quantum/backends")
async def quantum_backends():
    return {
        "backends": ["qiskit", "pennylane", "cirq", "braket"],
        "circuits": ["bell", "ghz", "qft", "vqe", "qaoa", "qnn", "grover"],
    }
