"""Fractals skill — Mandelbrot, Julia, L-systems, attractors, IFS."""
from __future__ import annotations
import numpy as np

SKILL = "fractals"


def mandelbrot(width: int = 400, height: int = 300, max_iter: int = 100) -> np.ndarray:
    """Returns iteration count array for Mandelbrot set."""
    x = np.linspace(-2.5, 1.0, width)
    y = np.linspace(-1.25, 1.25, height)
    C = x[np.newaxis, :] + 1j * y[:, np.newaxis]
    Z = np.zeros_like(C)
    M = np.zeros(C.shape, dtype=int)
    for i in range(max_iter):
        mask = np.abs(Z) <= 2
        Z[mask] = Z[mask] ** 2 + C[mask]
        M[mask] += 1
    return M


def julia(c: complex = -0.7 + 0.27j, width: int = 400, height: int = 300,
          max_iter: int = 100) -> np.ndarray:
    x = np.linspace(-1.5, 1.5, width)
    y = np.linspace(-1.5, 1.5, height)
    Z = x[np.newaxis, :] + 1j * y[:, np.newaxis]
    M = np.zeros(Z.shape, dtype=int)
    for i in range(max_iter):
        mask = np.abs(Z) <= 2
        Z[mask] = Z[mask] ** 2 + c
        M[mask] += 1
    return M


def lsystem(axiom: str, rules: dict[str, str], depth: int) -> str:
    """Expand an L-system string to given depth."""
    s = axiom
    for _ in range(depth):
        s = "".join(rules.get(c, c) for c in s)
    return s


def lorenz(steps: int = 10000, dt: float = 0.01,
           sigma: float = 10, rho: float = 28, beta: float = 8/3) -> np.ndarray:
    """Lorenz attractor trajectory. Returns (steps, 3) array."""
    xyz = np.empty((steps, 3))
    xyz[0] = [0.1, 0.0, 0.0]
    for i in range(1, steps):
        x, y, z = xyz[i-1]
        xyz[i] = [
            x + dt * sigma * (y - x),
            y + dt * (x * (rho - z) - y),
            z + dt * (x * y - beta * z),
        ]
    return xyz


def fractal_dimension(points: np.ndarray, scales: int = 10) -> float:
    """Box-counting fractal dimension estimate."""
    mins, maxs = points.min(axis=0), points.max(axis=0)
    counts = []
    for k in range(1, scales + 1):
        eps = (maxs - mins).max() / (2 ** k)
        if eps == 0:
            break
        boxes = set(tuple(((p - mins) / eps).astype(int)) for p in points)
        counts.append((eps, len(boxes)))
    if len(counts) < 2:
        return 0.0
    eps_arr = np.log([c[0] for c in counts])
    cnt_arr = np.log([c[1] for c in counts])
    return float(-np.polyfit(eps_arr, cnt_arr, 1)[0])


def ifs(transforms: list[np.ndarray], n_points: int = 50000) -> np.ndarray:
    """Iterated Function System — random iteration algorithm."""
    import random
    p = np.array([0.0, 0.0])
    pts = np.empty((n_points, 2))
    for i in range(n_points):
        T = random.choice(transforms)
        p = T[:2, :2] @ p + T[:2, 2]
        pts[i] = p
    return pts


def verify() -> bool:
    M = mandelbrot(100, 80, 50)
    assert M.shape == (80, 100)
    s = lsystem("F", {"F": "F+F-F-F+F"}, 2)
    assert len(s) > 1
    traj = lorenz(100)
    assert traj.shape == (100, 3)
    return True
