# Grok Skills — Local + Trinity Mesh Mirrors

This directory (and the one that will be populated at `agents/grok/skills/`) contains skills in Grok's native `SKILL.md` + `scripts/` format.

The physical skills live alongside the rest of the Grok root at `DOME-HUB/agents/grok/skills/`.

## Current Grok-Native Skills (after root move)

- `best-of-n/`
- `check/`
- `create-skill/`
- `docx/`, `pptx/`, `xlsx/`
- `help/`
- `implement/`, `review/`, `design/`, `pr-babysit/` (from bundled)

See the full list under the moved `~/.grok/skills/` (now `agents/grok/skills/`) and `agents/grok/bundled/skills/`.

## Trinity Sovereign Skills (mirrored / loadable)

High-signal capabilities from the DOME-HUB / trinity-unified-ai mesh are exposed here for Grok consumption:

- `neuromorphic_sync` — STDP + theta-gamma + NeuroScale (from `agents/skills/neuromorphic_sync.py`)
- `frequency` — Fourier, Solfeggio, brainwave, Schumann (from `agents/skills/frequency.py`)
- `sacred_geometry` — E8, Merkaba, Flower of Life, golden ratio primitives
- `pqc_mesh_auth` — Post-quantum crypto for agent mesh
- `stigmergic_routing` — Physarum + ACO style agent coordination
- `fractals` — Mandelbrot, IFS, L-systems (also `agents/skills/fractals.py`)
- `super_compute_brain_diagnostics` — Living probes + report generator for the full Super Compute Brain layer (meninges, E8, Mandelbulb, LAVA, God Mode, AMMA). Use canonical `home/projects/trinity-consortium/scripts/e8_240_with_amma_lens.py` (real E8 k-NN + AMMA lens) for E8-240 neuromorphic runs. Legacy `lava-snn-demo.py` superseded. Canonical in `trinity-unified-ai/skills-library/skills/super-compute-brain-diagnostics/`. Local bridge at `agents/skills/super_compute_brain_diagnostics.py`.
- `cognitive`, `compute`, `skill-creator`, etc.

## Bridging Strategy

1. Canonical source for Trinity skills lives in:
   - `DOME-HUB/agents/skills/<name>.py` + `SKILL.md`
   - `DOME-HUB/kb/skills/`
   - `trinity-unified-ai/skills-library/`

2. Codex-style mirror (see `scripts/sync-dome-skills.py`) can be extended to also emit `SKILL.md` packages into `agents/grok/skills/<name>/` so the Grok CLI can discover them with zero friction.

3. For now, Grok skills reference the central paths in their frontmatter or documentation.

## Adding a New Skill

- For Grok-only: drop `SKILL.md` + scripts/ under `agents/grok/skills/<name>/`
- For mesh-wide: add to `agents/skills/` + `kb/skills/` then run the sync bridge (future `sync-grok-skills.py`)

All skills under this tree are automatically included in the fractalmap (`L1/agents.md`) and the sovereign archive.

---

**Mesh status**: Grok is now a full peer. Its skills participate in the same registry and fractal tree as Claude, Kiro, Codex, and the Trinity runners.