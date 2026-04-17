"""
Pre-spore capability skills — loaded and verified before spore.sh activation.
"""
from agents.skills.math import SKILL as MATH_SKILL
from agents.skills.compute import SKILL as COMPUTE_SKILL
from agents.skills.sacred_geometry import SKILL as SACRED_GEOMETRY_SKILL
from agents.skills.fractals import SKILL as FRACTALS_SKILL
from agents.skills.algorithms import SKILL as ALGORITHMS_SKILL
from agents.skills.frequency import SKILL as FREQUENCY_SKILL
from agents.skills.cognitive import SKILL as COGNITIVE_SKILL

SKILLS = [
    MATH_SKILL,
    COMPUTE_SKILL,
    SACRED_GEOMETRY_SKILL,
    FRACTALS_SKILL,
    ALGORITHMS_SKILL,
    FREQUENCY_SKILL,
    COGNITIVE_SKILL,
]

__all__ = ["SKILLS"]
