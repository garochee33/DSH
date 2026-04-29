# Skill: Sacred Geometry

Domain: `trinity` | Depth: `axiom`

## Capabilities
- E8 lattice construction and root system computation
- Platonic solids: vertices, edges, faces, dual forms
- Phi (golden ratio) based constructions
- Flower of Life, Metatron's Cube, Vesica Piscis geometry
- Toroidal field geometry
- Merkaba (star tetrahedron) coordinates
- Sacred ratio relationships: phi, pi, sqrt(2), sqrt(3), sqrt(5)

## Mathematical Foundation
- E8 root system: 240 roots in 8-dimensional space
- Golden ratio: φ = (1 + √5) / 2 ≈ 1.6180339887...
- Platonic solids are the only convex regular polyhedra (5 total)
- Torus: parametric surface fundamental to field geometry

## Libraries
| Library | Purpose |
|---------|---------|
| numpy   | Coordinate computation |
| sympy   | Exact symbolic ratios |
| matplotlib | Visualization |

## Module
`agents/skills/sacred_geometry.py`

## Key Functions
- `e8_roots()` — all 240 E8 root vectors
- `platonic(name)` — vertices/faces for tetrahedron, cube, octahedron, icosahedron
- `golden_ratio()` — exact symbolic phi
- `flower_of_life(rings)` — circle centers for n rings
- `merkaba()` — star tetrahedron vertex coordinates
- `torus(R, r, n)` — toroidal surface mesh
