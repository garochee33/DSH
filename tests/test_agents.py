"""Tests for agent framework: imports, registry, tools, skills."""
import os, pytest

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("DOME_ROOT", os.path.join(os.path.dirname(__file__), ".."))


def test_agent_import():
    from agents import Agent, REGISTRY, ALL_TOOLS, SKILLS
    assert Agent is not None


def test_registry_has_6_agents():
    from agents.core.registry import REGISTRY
    assert len(REGISTRY) == 6
    assert set(REGISTRY.keys()) == {"researcher", "coder", "analyst", "planner", "kb_agent", "local"}


def test_all_tools_has_10():
    from agents.core.tools import ALL_TOOLS
    assert len(ALL_TOOLS) == 10


def test_skills_has_10():
    from agents.core.skills import SKILLS
    skill_names = {"reason", "reflect", "plan", "plan_and_execute", "summarize",
                   "extract", "embed", "similarity", "search_memory", "search_code"}
    assert skill_names.issubset(set(SKILLS.keys()))


def test_extended_skills_load():
    from agents.skills import SKILLS as skill_list
    assert "math" in skill_list
    assert "sacred_geometry" in skill_list
    assert len(skill_list) == 7


def test_agent_creation():
    from agents.core.registry import REGISTRY
    for name, factory in REGISTRY.items():
        agent = factory()
        assert agent.name == name
        assert hasattr(agent, "run")
        assert hasattr(agent, "mem")


def test_make_dome_orchestrator():
    from agents.core.registry import make_dome_orchestrator
    orc = make_dome_orchestrator()
    assert len(orc.agents) == 6
