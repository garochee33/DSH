#!/usr/bin/env python3
"""
Pre-Spore Verification — confirm all skills loaded and operational.
Must pass 100% before spore.sh is executed.

Run: python3 scripts/pre-spore-verify.py
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

SKILLS = [
    ("math",            "agents.skills.math"),
    ("compute",         "agents.skills.compute"),
    ("sacred_geometry", "agents.skills.sacred_geometry"),
    ("fractals",        "agents.skills.fractals"),
    ("algorithms",      "agents.skills.algorithms"),
    ("frequency",       "agents.skills.frequency"),
    ("cognitive",       "agents.skills.cognitive"),
]

DEPS = ["numpy", "scipy", "sympy", "numba", "torch", "qiskit",
        "pennylane", "cirq", "matplotlib", "networkx", "mpmath", "pandas"]

passed, failed = [], []


def check(label: str, fn):
    try:
        fn()
        print(f"  ✦ {label}")
        passed.append(label)
    except Exception as e:
        print(f"  ✗ {label}: {e}")
        failed.append(label)


print("\n═══════════════════════════════════════")
print("  PRE-SPORE VERIFICATION — DOME-HUB")
print("═══════════════════════════════════════\n")

print("[ Dependencies ]")
for dep in DEPS:
    check(dep, lambda d=dep: __import__(d))

print("\n[ Skill Modules ]")
for name, module_path in SKILLS:
    def _load(mp=module_path):
        import importlib
        mod = importlib.import_module(mp)
        assert hasattr(mod, "SKILL"), "missing SKILL constant"
        assert hasattr(mod, "verify"), "missing verify()"
    check(f"import:{name}", _load)

print("\n[ Skill Verification ]")
for name, module_path in SKILLS:
    def _verify(mp=module_path):
        import importlib
        mod = importlib.import_module(mp)
        assert mod.verify() is True
    check(f"verify:{name}", _verify)

print("\n[ Akashic Field ]")
def _akashic():
    from akashic.record import write, query
    eid = write("pre-spore verification passed", domain="meta", depth="event", node="system")
    assert len(eid) == 36  # uuid4
check("akashic:write+query", _akashic)

print("\n═══════════════════════════════════════")
total = len(passed) + len(failed)
print(f"  {len(passed)}/{total} checks passed")
if failed:
    print(f"\n  FAILED:")
    for f in failed:
        print(f"    ✗ {f}")
    print("\n  ⚠  NOT READY FOR SPORE — fix failures above")
    sys.exit(1)
else:
    print("\n  ✅ ALL SYSTEMS GO — READY FOR SPORE.SH")
print("═══════════════════════════════════════\n")
