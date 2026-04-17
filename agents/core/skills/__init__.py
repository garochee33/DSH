"""
DOME-HUB Skills Library
Skills: reasoning, planning, summarize, embed, search
"""
from __future__ import annotations
from typing import Any


# ── Reasoning ─────────────────────────────────────────────────────────────────

def reason(agent, question: str, context: str = "") -> str:
    """Chain-of-thought reasoning on a question."""
    prompt = f"""Think step by step.
{f'Context: {context}' if context else ''}
Question: {question}
Reasoning:"""
    return agent.run(prompt)


def reflect(agent, response: str) -> str:
    """Self-critique and improve a previous response."""
    return agent.run(
        f"Review this response critically and improve it:\n\n{response}\n\nImproved version:"
    )


# ── Planning ──────────────────────────────────────────────────────────────────

def plan(agent, goal: str) -> list[str]:
    """Break a goal into ordered steps."""
    response = agent.run(
        f"Break this goal into clear, ordered steps. Return as a numbered list.\nGoal: {goal}"
    )
    lines = [l.strip() for l in response.split("\n") if l.strip()]
    return [l for l in lines if l[0].isdigit()]


def plan_and_execute(agent, goal: str) -> list[dict]:
    """Plan a goal then execute each step."""
    steps = plan(agent, goal)
    results = []
    for step in steps:
        result = agent.run(f"Execute this step: {step}")
        results.append({"step": step, "result": result})
    return results


# ── Summarize ─────────────────────────────────────────────────────────────────

def summarize(agent, text: str, style: str = "concise") -> str:
    """Summarize text. Styles: concise, bullet, detailed."""
    styles = {
        "concise": "Summarize in 2-3 sentences.",
        "bullet": "Summarize as bullet points.",
        "detailed": "Write a detailed summary preserving key information.",
    }
    return agent.run(f"{styles.get(style, styles['concise'])}\n\nText:\n{text}")


def extract(agent, text: str, what: str) -> Any:
    """Extract specific information from text."""
    return agent.run(f"Extract {what} from the following text. Return only the extracted data.\n\n{text}")


# ── Embed ─────────────────────────────────────────────────────────────────────

def embed(texts: list[str], model: str = "all-MiniLM-L6-v2"):
    """Generate embeddings for a list of texts."""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(model).encode(texts)


def similarity(text_a: str, text_b: str) -> float:
    """Compute cosine similarity between two texts."""
    import numpy as np
    embs = embed([text_a, text_b])
    return float(np.dot(embs[0], embs[1]) / (np.linalg.norm(embs[0]) * np.linalg.norm(embs[1])))


# ── Search ────────────────────────────────────────────────────────────────────

def search_memory(agent, query: str, top_k: int = 5) -> list[dict]:
    """Semantic search over agent's memory."""
    import numpy as np
    if not agent.memory:
        return []
    texts = [m.content for m in agent.memory]
    embs = embed(texts + [query])
    doc_embs, query_emb = embs[:-1], embs[-1]
    scores = np.dot(doc_embs, query_emb)
    top_idx = scores.argsort()[-top_k:][::-1]
    return [{"score": float(scores[i]), "message": agent.memory[i]} for i in top_idx]


def search_code(query: str, root: str, extensions: list[str] | None = None) -> list[dict]:
    """Search codebase for relevant files using embeddings."""
    from pathlib import Path
    import numpy as np
    exts = extensions or [".py", ".ts", ".js", ".go", ".rs"]
    files = [f for f in Path(root).rglob("*") if f.suffix in exts and ".venv" not in str(f)]
    if not files:
        return []
    contents = [f.read_text(errors="ignore")[:1000] for f in files]
    embs = embed(contents + [query])
    doc_embs, query_emb = embs[:-1], embs[-1]
    scores = np.dot(doc_embs, query_emb)
    top_idx = scores.argsort()[-5:][::-1]
    return [{"score": float(scores[i]), "file": str(files[i])} for i in top_idx]


# ── Skill registry ────────────────────────────────────────────────────────────

SKILLS = {
    "reason": reason,
    "reflect": reflect,
    "plan": plan,
    "plan_and_execute": plan_and_execute,
    "summarize": summarize,
    "extract": extract,
    "embed": embed,
    "similarity": similarity,
    "search_memory": search_memory,
    "search_code": search_code,
}
