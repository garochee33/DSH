"""Tests for memory system: working, episodic, vector, MemorySystem."""
import os, pytest

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("DOME_ROOT", os.path.join(os.path.dirname(__file__), ".."))


class TestWorkingMemory:
    def test_add_and_get(self):
        from agents.core.memory.working import WorkingMemory
        wm = WorkingMemory(max_size=10)
        wm.add("user", "hello")
        wm.add("assistant", "hi")
        ctx = wm.get()
        assert len(ctx) == 2
        assert ctx[0]["role"] == "user"
        assert ctx[1]["content"] == "hi"

    def test_clear(self):
        from agents.core.memory.working import WorkingMemory
        wm = WorkingMemory()
        wm.add("user", "test")
        wm.clear()
        assert len(wm) == 0
        assert wm.get() == []

    def test_summarize_drops_oldest_without_llm(self):
        from agents.core.memory.working import WorkingMemory
        wm = WorkingMemory(max_size=4)
        for i in range(4):
            wm.add("user", f"msg-{i}")
        # After hitting max_size, oldest half should be dropped
        assert len(wm) == 2

    def test_summary_prefix_with_llm(self):
        from agents.core.memory.working import WorkingMemory
        wm = WorkingMemory(max_size=4, llm_fn=lambda msgs: "summary-text")
        for i in range(4):
            wm.add("user", f"msg-{i}")
        ctx = wm.get()
        assert ctx[0]["role"] == "system"
        assert "summary-text" in ctx[0]["content"]


class TestEpisodicMemory:
    def test_log_and_recall(self, tmp_path):
        os.environ["DOME_ROOT"] = str(tmp_path)
        # Re-import to pick up new DOME_ROOT
        import importlib
        import agents.core.memory.episodic as ep
        importlib.reload(ep)
        mem = ep.EpisodicMemory(db_path=tmp_path / "db" / "test_episodic.db")
        eid = mem.log("test-agent", "sess-1", "user", "hello world")
        assert len(eid) == 36  # UUID
        history = mem.recall_session("test-agent", "sess-1")
        assert len(history) == 1
        assert history[0]["content"] == "hello world"
        mem.close()

    def test_facts(self, tmp_path):
        import importlib
        import agents.core.memory.episodic as ep
        importlib.reload(ep)
        db_path = tmp_path / "db" / "test_facts.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        mem = ep.EpisodicMemory(db_path=db_path)
        mem.store_fact("agent-a", "color", "blue")
        assert mem.get_fact("agent-a", "color") == "blue"
        facts = mem.recall_facts("agent-a")
        assert facts["color"] == "blue"
        mem.close()


class TestMemorySystem:
    def test_store_and_context(self, tmp_path):
        os.environ["DOME_ROOT"] = str(tmp_path)
        from agents.core.memory import MemorySystem
        ms = MemorySystem(agent="test", session="s1", namespace="test-ns")
        ids = ms.store("user", "hello memory")
        assert "vector_id" in ids
        assert "episode_id" in ids
        ctx = ms.context()
        assert len(ctx) == 1
        assert ctx[0]["content"] == "hello memory"
