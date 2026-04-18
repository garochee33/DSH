# kb/trinity-unified-ai — Trinity Seed Deposit Landing Zone

This directory is the authoritative landing zone for Trinity Consortium's
knowledge seed deposit into this sovereign DOME-HUB node.

## What this is

`trinity-unified-ai` is the KB API layer of the Mycelium Neural Mesh.
It runs locally at `http://127.0.0.1:3333` and exposes the full Trinity
knowledge base (10,907+ docs, E8 Merkle tree, pgvector embeddings) to
agents on this node.

## Connection

| Variable         | Value                        |
|------------------|------------------------------|
| `TRINITY_API_BASE` | `http://127.0.0.1:3333`    |
| `HUB_API_SECRET` | see `.env`                   |
| Auth header      | `x-hub-secret: <secret>`     |

## Key endpoints

```
GET  /health                          — liveness check
GET  /api/agents/list                 — registered agents
POST /api/knowledge/search            — semantic search (pgvector)
POST /api/ssii/ingest                 — ingest memory fragment
POST /api/mempalace/recall            — recall from MemPalace
GET  /api/mesh/peer/topology          — Mycelium mesh topology
```

## Agents that use this KB

- `kb_agent` — always local, data never leaves machine
- `analyst`  — local sovereignty
- `coder`    — IP stays on device

## Status

Once `trinity-unified-ai/spore.sh` has been run and the KB API is live,
this directory will be populated with synced context seeds from the mesh.

See: `~/.trinity-spore/` for mesh state after spore activation.
