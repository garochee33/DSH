# agents/api — HTTP + WebSocket Server

FastAPI server exposing the agent framework over HTTP.

- `server.py` — REST API on port 8000 (`pnpm serve`)
- `ws.py` — WebSocket streaming endpoint

Endpoints: `/agents`, `/agents/{name}/run`, `/agents/{name}/stream`, `/rag/query`, `/health`, `/traces`, `/machine`
