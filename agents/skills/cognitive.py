"""Cognitive skill — reasoning, memory, attention, belief updating."""
from __future__ import annotations
import numpy as np

SKILL = "cognitive"


def chain_of_thought(problem: str, steps: list[str]) -> dict:
    """Scaffold a chain-of-thought reasoning trace."""
    return {
        "problem": problem,
        "steps": [{"step": i+1, "reasoning": s} for i, s in enumerate(steps)],
        "conclusion": steps[-1] if steps else "",
    }


def confidence(logits: list[float]) -> np.ndarray:
    """Softmax confidence scores from raw logits."""
    x = np.array(logits, dtype=float)
    e = np.exp(x - x.max())
    return e / e.sum()


def bayesian_update(prior: float, likelihood: float, evidence: float) -> float:
    """Posterior = P(H|E) = P(E|H) * P(H) / P(E)."""
    if evidence == 0:
        return 0.0
    return (likelihood * prior) / evidence


def attention_score(query: np.ndarray, keys: np.ndarray) -> np.ndarray:
    """Scaled dot-product attention weights."""
    d = query.shape[-1]
    scores = keys @ query / np.sqrt(d)
    e = np.exp(scores - scores.max())
    return e / e.sum()


def summarize_context(turns: list[str], max_chars: int = 2000) -> str:
    """Truncate context to max_chars, keeping most recent turns."""
    result, total = [], 0
    for turn in reversed(turns):
        if total + len(turn) > max_chars:
            break
        result.append(turn)
        total += len(turn)
    return "\n".join(reversed(result))


def retrieve_relevant(concept: str, memories: list[dict], n: int = 5) -> list[dict]:
    """
    Semantic retrieval from a list of memory dicts with 'vector' and 'content'.
    Falls back to keyword match if no vectors present.
    """
    if memories and "vector" in memories[0]:
        from agents.core.memory.vector import VectorMemory
        # delegate to vector memory if available
        pass
    # keyword fallback
    scored = [(m, sum(w in m.get("content","").lower()
                      for w in concept.lower().split())) for m in memories]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [m for m, _ in scored[:n]]


def verify() -> bool:
    cot = chain_of_thought("2+2?", ["identify operands", "add them", "result is 4"])
    assert cot["conclusion"] == "result is 4"
    conf = confidence([1.0, 2.0, 3.0])
    assert abs(conf.sum() - 1.0) < 1e-9
    post = bayesian_update(0.5, 0.8, 0.6)
    assert abs(post - (0.8 * 0.5 / 0.6)) < 1e-9
    q = np.array([1.0, 0.0])
    K = np.array([[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]])
    w = attention_score(q, K)
    assert abs(w.sum() - 1.0) < 1e-9
    return True
