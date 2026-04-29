"""Tests for tracer, stream, RAG, and orchestrator modules."""
import os, pytest

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("DOME_ROOT", os.path.join(os.path.dirname(__file__), ".."))


class TestTracer:
    def test_start_and_end_span(self):
        from agents.core.trace import Tracer
        t = Tracer()
        sid = t.start_span("test-span")
        assert sid is not None
        t.end_span(sid)

    def test_list_traces(self):
        from agents.core.trace import Tracer
        t = Tracer()
        sid = t.start_span("trace-test")
        t.end_span(sid)
        traces = t.list_traces(limit=10)
        assert len(traces) >= 1


class TestRAG:
    def test_rag_import(self):
        from agents.core.rag import RAGPipeline
        assert RAGPipeline is not None


class TestStream:
    def test_stream_functions_exist(self):
        from agents.core.stream import stream_openai, stream_anthropic, stream_local, stream_mlx
        assert callable(stream_openai)
        assert callable(stream_anthropic)
        assert callable(stream_local)
        assert callable(stream_mlx)


class TestOrchestrator:
    def test_orchestrator_import(self):
        from agents.core.orchestrator import Orchestrator
        assert Orchestrator is not None


class TestOllamaClient:
    def test_client_import(self):
        from agents.local.ollama import OllamaClient, make_local_agent
        assert OllamaClient is not None
        assert callable(make_local_agent)


class TestQuantumDome:
    def test_quantum_imports(self):
        from compute.quantum_dome import QuantumDome, WorkloadScheduler, ComputePool
        assert QuantumDome is not None


class TestSkillVerify:
    def test_all_skills_have_verify(self):
        from agents.skills import math, compute, sacred_geometry, fractals, algorithms, frequency, cognitive
        for mod in [math, compute, sacred_geometry, fractals, algorithms, frequency, cognitive]:
            assert hasattr(mod, "SKILL"), f"{mod.__name__} missing SKILL"
            assert hasattr(mod, "verify"), f"{mod.__name__} missing verify()"
            assert mod.verify() is True, f"{mod.__name__}.verify() failed"
