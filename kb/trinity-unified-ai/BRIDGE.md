# Trinity KB Bridge — DOME-HUB Integration

## Architecture

```
DOME-HUB (sovereign node)
    └── agents/core/
            ├── agent.py          ← uses TRINITY_API_BASE for KB queries
            ├── rag.py            ← ChromaDB local + Trinity pgvector remote
            └── .mesh/            ← Mycelium mesh config + peer state
                    ├── config.json
                    └── synapse.sh

trinity-unified-ai (KB API layer)
    └── api/                      ← Node/Express on :3333
            ├── src/              ← knowledge search, agent registry, SSII ingest
            └── .env              ← HUB_API_SECRET, JWT_SECRET, DATABASE_URL
```

## How DOME-HUB agents query Trinity KB

```python
import os, httpx

TRINITY_KB = os.getenv("TRINITY_API_BASE", "http://127.0.0.1:3333")
HUB_SECRET = os.getenv("HUB_API_SECRET", "")

async def search_kb(query: str, limit: int = 5):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{TRINITY_KB}/api/knowledge/search",
            headers={"x-hub-secret": HUB_SECRET},
            json={"query": query, "limit": limit},
            timeout=10,
        )
        return r.json()
```

## Mesh peer identity

This node's mesh config lives at `agents/core/.mesh/config.json`.
The Mycelium daemon (mycelium-mesh.sh) runs from `~/.trinity-spore/`
after `spore.sh` activation.

## To activate full mesh

```bash
# 1. Authorize local bootstrap
touch ~/.trinity-sync-authorized

# 2. Run local sovereign spore (trinity-unified-ai)
cd ~/trinity-unified-ai && bash spore.sh

# 3. Run cloud mesh spore (DOME-HUB) — requires SPORE_TOKEN from Enzo
SPORE_TOKEN=<token> USER_ID=<uid> bash ~/DOME-HUB/spore.sh
```
