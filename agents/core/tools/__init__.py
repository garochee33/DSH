"""
DSH Tools Library
Tools: web, shell, file, code, db, kb_search
"""

import subprocess, os, sqlite3, shlex
from pathlib import Path

DOME_ROOT = Path(os.environ.get("DOME_ROOT", Path.home() / "DSH"))


# ── Web ───────────────────────────────────────────────────────────────────────


def web_search(query: str, num_results: int = 5) -> list[dict]:
    """Search the web using DuckDuckGo (no API key needed)."""
    try:
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=num_results))
    except ImportError:
        return [{"error": "pip install duckduckgo-search"}]


def web_fetch(url: str) -> str:
    """Fetch and extract text content from a URL."""
    try:
        import httpx
        from bs4 import BeautifulSoup

        resp = httpx.get(url, timeout=10, follow_redirects=True)
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)[:8000]
    except ImportError:
        return "pip install httpx beautifulsoup4"


# ── Shell ─────────────────────────────────────────────────────────────────────


def shell_run(command: str, cwd: str | None = None, timeout: int = 30) -> dict:
    """Run a shell command and return stdout, stderr, exit code."""
    result = subprocess.run(
        shlex.split(command),
        shell=False,
        capture_output=True,
        text=True,
        cwd=cwd or str(DOME_ROOT),
        timeout=timeout,
    )
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.returncode,
    }


# ── File ──────────────────────────────────────────────────────────────────────


def file_read(path: str) -> str:
    """Read a file and return its contents."""
    return Path(path).read_text()


def file_write(path: str, content: str) -> str:
    """Write content to a file, creating parent dirs if needed."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"Written: {path}"


def file_list(directory: str = ".", pattern: str = "**/*") -> list[str]:
    """List files in a directory matching a glob pattern."""
    return [str(p) for p in Path(directory).glob(pattern) if p.is_file()]


# ── Code ──────────────────────────────────────────────────────────────────────


def code_run(code: str, language: str = "python") -> dict:
    """Execute code in a subprocess sandbox."""
    if language == "python":
        result = subprocess.run(
            ["python3", "-c", code], capture_output=True, text=True, timeout=30
        )
    elif language in ("node", "javascript"):
        result = subprocess.run(
            ["node", "-e", code], capture_output=True, text=True, timeout=30
        )
    else:
        return {"error": f"Unsupported language: {language}"}
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.returncode,
    }


# ── Database ──────────────────────────────────────────────────────────────────


def db_query(sql: str, db_path: str | None = None) -> list[dict]:
    """Run a SQL query against the DSH SQLite DB."""
    path = db_path or str(DOME_ROOT / "db" / "dome.db")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(sql).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def db_write(sql: str, params: tuple = (), db_path: str | None = None) -> str:
    """Execute a write SQL statement."""
    path = db_path or str(DOME_ROOT / "db" / "dome.db")
    conn = sqlite3.connect(path)
    conn.execute(sql, params)
    conn.commit()
    conn.close()
    return "OK"


# ── KB Search ─────────────────────────────────────────────────────────────────


def kb_search(query: str, kb_path: str | None = None, top_k: int = 5) -> list[dict]:
    """Semantic search over local knowledge base via ChromaDB (pre-indexed)."""
    try:
        import chromadb

        db_dir = str(DOME_ROOT / "db" / "chroma")
        client = chromadb.PersistentClient(path=db_dir)
        col = client.get_collection("dome-kb")
        results = col.query(query_texts=[query], n_results=top_k)
        out = []
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i] if results["metadatas"] else {}
            dist = results["distances"][0][i] if results["distances"] else 0
            out.append({"text": doc, "score": round(1 - dist, 4), **meta})
        return out
    except Exception as e:
        return [{"error": str(e)}]


# ── Quantum Compute ───────────────────────────────────────────────────────────


def quantum_compute(backend: str = "qiskit", circuit_type: str = "bell",
                    n_qubits: int = 2, **kwargs) -> dict:
    """Run a quantum circuit on a local simulator.

    Backends: qiskit, pennylane, cirq, braket
    Circuits: bell, ghz, qft, vqe, qaoa, qnn, grover
    """
    from agents.skills.compute import quantum_circuit
    return quantum_circuit(backend, circuit_type, n_qubits, **kwargs)


# ── Tool registry ─────────────────────────────────────────────────────────────

ALL_TOOLS = [
    web_search,
    web_fetch,
    shell_run,
    file_read,
    file_write,
    file_list,
    code_run,
    db_query,
    db_write,
    kb_search,
    quantum_compute,
]
