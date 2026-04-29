"""Tests for API server endpoints."""
import os, pytest

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("DOME_ROOT", os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from agents.api.server import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert "status" in r.json()


def test_list_agents():
    r = client.get("/agents")
    assert r.status_code == 200
    agents = r.json()["agents"]
    assert len(agents) == 6
    assert "researcher" in agents


def test_run_agent_not_found():
    r = client.post("/agents/nonexistent/run", json={"prompt": "test"})
    assert r.status_code == 404


def test_get_memory_not_found():
    r = client.get("/agents/nonexistent/memory")
    assert r.status_code == 404


def test_traces():
    r = client.get("/traces")
    assert r.status_code == 200
    assert "traces" in r.json()


def test_rag_query():
    r = client.post("/rag/query", json={"query": "test", "namespace": "test-ns"})
    assert r.status_code == 200
    assert "results" in r.json()
