"""Tests for akashic record system."""
import os, pytest

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("DOME_ROOT", os.path.join(os.path.dirname(__file__), ".."))


def test_akashic_import():
    from akashic import write, query
    assert callable(write)
    assert callable(query)


def test_akashic_watcher_import():
    pytest.importorskip("watchdog")
    from akashic.watcher import WATCH_DIRS
    assert "kb" in WATCH_DIRS


def test_akashic_assembler_import():
    from akashic.assembler import assemble
    assert callable(assemble)
