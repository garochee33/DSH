"""
Stigmergic Routing Skill — Physarum Flow + ACO Pheromone Optimization
=====================================================================
Bio-inspired routing for E8 lattice edge reinforcement:
  1. Physarum flow solver (adaptive transport network)
  2. ACO pheromone-based load balancing
  3. E8 edge reinforcement via preferential flow
"""

import numpy as np
from dataclasses import dataclass, field


@dataclass
class PhysarumNetwork:
    """Physarum-inspired adaptive transport network on a 3D lattice.

    Edges thicken with flow (positive feedback), atrophy without (negative feedback).
    Solves approximate Steiner tree for optimal mesh topology.
    """
    N: int
    conductance: np.ndarray = field(default=None)  # Edge weights (tube diameter)
    flow: np.ndarray = field(default=None)          # Current flow on each edge
    decay_rate: float = 0.05                        # Atrophy rate for unused edges
    growth_rate: float = 0.1                        # Reinforcement rate for used edges
    min_conductance: float = 0.01
    max_conductance: float = 5.0

    def __post_init__(self):
        # 6-connected edges for 3D lattice (3 directions × N³ nodes)
        n_edges = 3 * self.N ** 3
        if self.conductance is None:
            self.conductance = np.ones(n_edges) * 1.0
        if self.flow is None:
            self.flow = np.zeros(n_edges)

    def compute_flow(self, source: tuple, sink: tuple, pressure: float = 1.0) -> np.ndarray:
        """Compute flow through network given source/sink (simplified Kirchhoff)."""
        N = self.N
        n_nodes = N ** 3
        # Build Laplacian from conductances
        L = np.zeros((n_nodes, n_nodes))
        edge_idx = 0
        for i in range(N):
            for j in range(N):
                for k in range(N):
                    node = np.ravel_multi_index((i, j, k), (N, N, N))
                    for d, (di, dj, dk) in enumerate([(1,0,0),(0,1,0),(0,0,1)]):
                        ni, nj, nk = (i+di)%N, (j+dj)%N, (k+dk)%N
                        neighbor = np.ravel_multi_index((ni, nj, nk), (N, N, N))
                        c = self.conductance[edge_idx]
                        L[node, node] += c
                        L[neighbor, neighbor] += c
                        L[node, neighbor] -= c
                        L[neighbor, node] -= c
                        edge_idx += 1

        # Solve for pressure (ground sink node)
        src = np.ravel_multi_index(source, (N, N, N))
        snk = np.ravel_multi_index(sink, (N, N, N))
        rhs = np.zeros(n_nodes)
        rhs[src] = pressure
        rhs[snk] = -pressure

        # Regularize and solve
        L[snk, :] = 0
        L[snk, snk] = 1
        rhs[snk] = 0
        try:
            p = np.linalg.solve(L, rhs)
        except np.linalg.LinAlgError:
            p = np.zeros(n_nodes)

        # Compute edge flows from pressure differences
        edge_idx = 0
        for i in range(N):
            for j in range(N):
                for k in range(N):
                    node = np.ravel_multi_index((i, j, k), (N, N, N))
                    for d, (di, dj, dk) in enumerate([(1,0,0),(0,1,0),(0,0,1)]):
                        ni, nj, nk = (i+di)%N, (j+dj)%N, (k+dk)%N
                        neighbor = np.ravel_multi_index((ni, nj, nk), (N, N, N))
                        self.flow[edge_idx] = self.conductance[edge_idx] * abs(p[node] - p[neighbor])
                        edge_idx += 1

        return self.flow

    def adapt(self) -> None:
        """Physarum adaptation: reinforce high-flow edges, decay low-flow."""
        self.conductance += self.growth_rate * self.flow - self.decay_rate * self.conductance
        self.conductance = np.clip(self.conductance, self.min_conductance, self.max_conductance)

    @property
    def efficiency(self) -> float:
        """Network efficiency: ratio of active edges to total."""
        active = np.sum(self.conductance > 0.5)
        return float(active / len(self.conductance))


# ─── ACO Pheromone Routing ────────────────────────────────────────────────────

@dataclass
class PheromoneGrid:
    """Ant Colony Optimization pheromone grid for E8 lattice routing."""
    N: int
    pheromone: np.ndarray = field(default=None)
    evaporation: float = 0.1       # ρ: pheromone decay per tick
    deposit: float = 1.0           # Base deposit amount
    alpha: float = 1.0             # Pheromone weight in probability
    beta: float = 2.0              # Heuristic weight in probability

    def __post_init__(self):
        if self.pheromone is None:
            self.pheromone = np.ones((self.N, self.N, self.N)) * 0.5

    def select_next(self, current: tuple, destination: tuple) -> tuple:
        """Probabilistic next-hop selection based on pheromone + distance heuristic."""
        N = self.N
        i, j, k = current
        candidates = []
        probs = []

        for di, dj, dk in [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)]:
            ni, nj, nk = (i+di)%N, (j+dj)%N, (k+dk)%N
            tau = self.pheromone[ni, nj, nk] ** self.alpha
            # Heuristic: inverse distance to destination (Manhattan)
            dist = abs(ni - destination[0]) + abs(nj - destination[1]) + abs(nk - destination[2])
            eta = (1.0 / (dist + 1)) ** self.beta
            candidates.append((ni, nj, nk))
            probs.append(tau * eta)

        probs = np.array(probs)
        probs /= probs.sum() + 1e-10
        idx = np.random.choice(len(candidates), p=probs)
        return candidates[idx]

    def deposit_pheromone(self, path: list[tuple], quality: float = 1.0) -> None:
        """Deposit pheromone along a path proportional to quality."""
        amount = self.deposit * quality / (len(path) + 1)
        for (i, j, k) in path:
            self.pheromone[i, j, k] += amount

    def evaporate(self) -> None:
        """Global pheromone evaporation."""
        self.pheromone *= (1 - self.evaporation)
        self.pheromone = np.clip(self.pheromone, 0.01, 10.0)

    def route(self, source: tuple, destination: tuple, max_hops: int = 20) -> list[tuple]:
        """Route a message from source to destination using ACO."""
        path = [source]
        current = source
        for _ in range(max_hops):
            if current == destination:
                break
            current = self.select_next(current, destination)
            if current in path:  # Avoid loops
                break
            path.append(current)
        return path


# ─── E8 Edge Reinforcement ────────────────────────────────────────────────────

def e8_edge_reinforcement(lattice_coherence: np.ndarray, physarum: PhysarumNetwork) -> np.ndarray:
    """Reinforce E8 lattice edges based on coherence flow.

    High-coherence paths get thicker (more bandwidth).
    Low-coherence paths atrophy (resources redirected).
    """
    N = lattice_coherence.shape[0]
    # Use coherence gradient as flow source/sink
    max_pos = np.unravel_index(np.argmax(lattice_coherence), (N, N, N))
    min_pos = np.unravel_index(np.argmin(lattice_coherence), (N, N, N))

    # Compute flow from highest to lowest coherence
    physarum.compute_flow(max_pos, min_pos, pressure=float(np.max(lattice_coherence)))
    physarum.adapt()

    return physarum.conductance
