# DSH Compute

Infrastructure and compute-environment definitions for everything running
inside DSH.


| File | Purpose |
|------|---------|
| `sim_3x3x3.py` | 3×3×3 lattice — 13 mechanics, Mandelbulb-style energy, unified coherence; NumPy Kuramoto with **K_OPTIMAL** (Loihi/LAVA calibration) |

Spiking **LAVA / Loihi2SimCfg** optimizer (separate Python **3.10** venv):  
See `kb/claude/skills/lava-neuro-sim/SKILL.md` and `docs/DSH-ARCHITECTURE.md` §3.

## QuantumDome

| Path | Purpose |
|------|---------|
| `quantum_dome/` | Resource monitor, scheduler, pool, `memory.py` (RAM/MPS pressure), profiler |

## Claude / bootstrap

| File | Purpose |
|------|---------|
| `claude-env.md` | Spec for the Claude (Anthropic) compute environment |
| `requirements.txt` | Pinned Python deps shared by the root `.venv` |
| `bootstrap-claude.sh` | Idempotent install + register script |

## Running

```bash
cd ~/DSH
bash compute/bootstrap-claude.sh
```

After bootstrap, Claude's entrypoint is `agents/claude/runner.py`.
