"""
Lightweight local mirror / bridge for the canonical
trinity.sovereign.super-compute-brain-diagnostics skill.

This allows DOME-HUB agents (including Grok) to import it easily without
going through the full skills-library path every time.

Canonical location:
    home/trinity-unified-ai/skills-library/skills/super-compute-brain-diagnostics/
"""

import sys
from pathlib import Path

# Add the real skill package to path
SKILL_ROOT = Path(__file__).resolve().parents[2] / "home" / "trinity-unified-ai" / "skills-library" / "skills" / "super-compute-brain-diagnostics"
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from scripts.super_compute_brain_diagnostics import SuperComputeBrainDiagnosticsSkill  # type: ignore

__all__ = ["SuperComputeBrainDiagnosticsSkill"]

# Convenience instance
diagnostics = SuperComputeBrainDiagnosticsSkill()