# DOME-HUB Developer Context

## Trinity Consortium — The Infrastructure

Trinity Consortium IS the infrastructure. It is not a feature, a layer, or a component of
DOME-HUB — it is the sovereign, decentralized network that DOME-HUB exists inside.

Member identities are consortium-internal. Not disclosed in shared or public-facing documents.

## Core Architecture

- **FRACTAL E8-SSII-AGI** — The AGI system at the heart of Trinity Consortium.
  Built by Trinity Consortium. Based on E8 lattice geometry.
- **Mycelium Neural Mesh** — The decentralized inter-node network. Biological-inspired,
  dimensional, distributed. Connects all sovereign member nodes.
- **trinity-unified-ai** — The Knowledge Base API layer for the Mycelium network.
  Path: `kb/trinity-unified-ai/`

## DOME-HUB Role

DOME-HUB is a **sovereign node** in the Trinity Consortium network — not a standalone project.
It is the local compute base, KB, DB, and agent orchestration endpoint for this node.

- Root: `~/DOME-HUB`
- Architecture: portable to **any sovereign Apple Silicon node**
- Primary node: Apple **M5 Pro** — 18-core CPU (6 Super + 12 Performance), 48 GB unified memory, Mac17,8, macOS (user `trinity-hub`)
- Secondary node: Apple **M4 Pro** — 12-core CPU (8P+4E), 16-core GPU, 24 GB unified memory, Neural Engine 38 TOPS, 273 GB/s bandwidth, macOS
- Mesh: Both nodes connected via **Quantum Mycelium Neuromorphic Mesh Network + Tailscale**
- **Local ML planes:** (1) **MLX / Metal** — LLMs via `mlx_lm` (`agents/core/stream.py`, `mlx-*` models). (2) **ONNX → CoreML EP** — Chroma embeddings / Neural Engine when active (`agents/core/memory/vector.py`). (3) **PyTorch MPS** — tensor / quantum GPU path. Optional Trinity **MLX HTTP bridge:** `bash scripts/mlx-neural-bridge.sh` → mirror `nexus-core/mlx-neural-bridge.py`.
- Security: FileVault, SIP, GPG, pass, approval gate (Trinity members only)

## Seed Deposit

The foundation of this node is built and ready to receive Trinity's seed:
- `spore.sh` (v3.1) — Trinity mesh bootstrap; resolves **DOME-HUB** or **DSH** repo root automatically (`DOME_ROOT`, script path, `~/DOME-HUB`, `~/DSH`)
- `kb/trinity-unified-ai/` — The landing zone for the trinity-unified-ai KB API spec
- Once deposited, the Mycelium connection between this node and the network activates
- **Production signal:** prefer `scripts/mycelium-signal.sh` (HMAC peer auth) over the baseline `~/.trinity-spore/mycelium-mesh.sh` installed by spore Phase 9

## Node Identity

| Field | Value |
|-------|-------|
| Network | Trinity Consortium — Mycelium Neural Mesh |
| Node type | Sovereign compute + KB + agent orchestration |
| GitHub repo | garochee33/DSH |
| Approved principals | Trinity Consortium members (operational config) |

## Build Goals

- Receive and integrate `spore.sh` — activate Trinity node
- Populate `kb/trinity-unified-ai/` with the full KB API spec
- Build apps, platforms, and agent implementations for the Trinity network
- Grow the Mycelium membrane through this node
- Decentralized inter-node communication per Trinity Consortium protocol
