"""Sacred Geometry skill — E8, Platonic solids, phi, toroidal fields."""
from __future__ import annotations
import numpy as np
import sympy as sp

SKILL = "sacred_geometry"

PHI = (1 + np.sqrt(5)) / 2  # golden ratio
PHI_EXACT = (1 + sp.sqrt(5)) / 2  # symbolic


def golden_ratio(symbolic: bool = False):
    return PHI_EXACT if symbolic else PHI


def e8_roots() -> np.ndarray:
    """
    Generate all 240 root vectors of the E8 root system.
    Two sets:
      1. All permutations of (±1, ±1, 0, 0, 0, 0, 0, 0) — 112 roots
      2. All (±½, ±½, ±½, ±½, ±½, ±½, ±½, ±½) with even number of minus signs — 128 roots
    """
    roots = []
    # Set 1: ±1 in two positions
    from itertools import combinations, product
    for i, j in combinations(range(8), 2):
        for si, sj in product([-1, 1], repeat=2):
            v = np.zeros(8)
            v[i], v[j] = si, sj
            roots.append(v)
    # Set 2: all ±½ with even number of minus signs
    for signs in product([-1, 1], repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(np.array(signs) * 0.5)
    return np.array(roots)  # shape (240, 8)


def platonic(name: str) -> dict:
    """Return vertices and faces for a Platonic solid."""
    name = name.lower()
    if name == "tetrahedron":
        v = np.array([[1,1,1],[1,-1,-1],[-1,1,-1],[-1,-1,1]], dtype=float)
        f = [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]
    elif name == "cube":
        v = np.array([[s0,s1,s2] for s0 in [-1,1] for s1 in [-1,1] for s2 in [-1,1]], dtype=float)
        f = [[0,1,3,2],[4,5,7,6],[0,1,5,4],[2,3,7,6],[0,2,6,4],[1,3,7,5]]
    elif name == "octahedron":
        v = np.array([[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]], dtype=float)
        f = [[0,2,4],[0,2,5],[0,3,4],[0,3,5],[1,2,4],[1,2,5],[1,3,4],[1,3,5]]
    elif name == "icosahedron":
        t = PHI
        v = np.array([[0,1,t],[0,-1,t],[0,1,-t],[0,-1,-t],
                       [1,t,0],[-1,t,0],[1,-t,0],[-1,-t,0],
                       [t,0,1],[t,0,-1],[-t,0,1],[-t,0,-1]], dtype=float)
        v /= np.linalg.norm(v[0])
        f = []  # faces omitted for brevity — vertices are the key output
    else:
        raise ValueError(f"Unknown solid: {name}")
    return {"vertices": v, "faces": f}


def flower_of_life(rings: int = 2) -> np.ndarray:
    """Circle centers for the Flower of Life pattern."""
    centers = [(0.0, 0.0)]
    r = 1.0
    for ring in range(1, rings + 1):
        for k in range(6 * ring):
            angle = np.pi / 3 * (k / ring)
            x = ring * r * np.cos(angle)
            y = ring * r * np.sin(angle)
            centers.append((x, y))
    return np.array(centers)


def merkaba() -> np.ndarray:
    """Star tetrahedron (Merkaba) — two interlocked tetrahedra."""
    up   = np.array([[ 1, 1, 1],[ 1,-1,-1],[-1, 1,-1],[-1,-1, 1]], dtype=float)
    down = -up
    return np.vstack([up, down])


def torus(R: float = 2.0, r: float = 1.0, n: int = 64) -> np.ndarray:
    """Toroidal surface mesh. Returns (n, n, 3) array."""
    u = np.linspace(0, 2 * np.pi, n)
    v = np.linspace(0, 2 * np.pi, n)
    U, V = np.meshgrid(u, v)
    X = (R + r * np.cos(V)) * np.cos(U)
    Y = (R + r * np.cos(V)) * np.sin(U)
    Z = r * np.sin(V)
    return np.stack([X, Y, Z], axis=-1)


def verify() -> bool:
    roots = e8_roots()
    assert roots.shape == (240, 8), f"E8 root count wrong: {roots.shape}"
    assert abs(golden_ratio() - 1.6180339887) < 1e-9
    cube = platonic("cube")
    assert len(cube["vertices"]) == 8
    t = torus()
    assert t.shape == (64, 64, 3)
    return True
