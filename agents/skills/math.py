"""Math skill — symbolic and numerical mathematics."""
from __future__ import annotations
import numpy as np
import sympy as sp
from mpmath import mp, mpf, nstr

SKILL = "math"


def symbolic(expr: str) -> sp.Expr:
    """Parse and simplify a symbolic expression."""
    return sp.simplify(sp.sympify(expr))


def differentiate(expr: str, var: str = "x") -> sp.Expr:
    x = sp.Symbol(var)
    return sp.diff(sp.sympify(expr), x)


def integrate(expr: str, var: str = "x") -> sp.Expr:
    x = sp.Symbol(var)
    return sp.integrate(sp.sympify(expr), x)


def solve(expr: str, var: str = "x") -> list:
    x = sp.Symbol(var)
    return sp.solve(sp.sympify(expr), x)


def eigenvalues(matrix: list[list[float]]) -> np.ndarray:
    return np.linalg.eigvals(np.array(matrix, dtype=float))


def precision_compute(expr: str, dps: int = 50) -> str:
    """Evaluate expression to arbitrary precision."""
    mp.dps = dps
    return nstr(mp.mpf(sp.N(sp.sympify(expr), dps)), dps)


def verify() -> bool:
    x = sp.Symbol("x")
    # check symbolic equality via expand
    assert sp.expand(symbolic("x**2 + 2*x + 1") - (x + 1) ** 2) == 0
    assert differentiate("x**3", "x") == 3 * x ** 2
    assert abs(float(sp.N(sp.sympify(precision_compute("pi", 10)))) - 3.14159) < 0.001
    return True
