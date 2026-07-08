"""
DSH capability skills — core skill modules.
"""
from agents.skills.math import SKILL as MATH_SKILL
from agents.skills.compute import SKILL as COMPUTE_SKILL
from agents.skills.algorithms import SKILL as ALGORITHMS_SKILL
from agents.skills.cognitive import SKILL as COGNITIVE_SKILL

SKILLS = {
    "math": MATH_SKILL,
    "compute": COMPUTE_SKILL,
    "algorithms": ALGORITHMS_SKILL,
    "cognitive": COGNITIVE_SKILL,
}

__all__ = ["SKILLS"]
