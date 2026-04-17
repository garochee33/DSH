"""
DOME-HUB WebSocket — real-time agent streaming
"""
from __future__ import annotations
import asyncio, json

from fastapi import WebSocket, WebSocketDisconnect
from agents.core.registry import make_dome_orchestrator

_orc = None
def get_orc():
    global _orc
    if _orc is None:
        _orc = make_dome_orchestrator()
    return _orc


async def ws_agent(websocket: WebSocket, agent_name: str):
    """Mount at /ws/{agent_name}"""
    orc = get_orc()
    if agent_name not in orc.agents:
        await websocket.accept()
        await websocket.send_text(json.dumps({"type": "error", "content": f"Agent '{agent_name}' not found"}))
        await websocket.close()
        return

    await websocket.accept()
    try:
        while True:
            prompt = await websocket.receive_text()
            try:
                loop = asyncio.get_event_loop()
                response: str = await loop.run_in_executor(None, orc.agents[agent_name].run, prompt)
                # Stream word by word
                for word in response.split(" "):
                    await websocket.send_text(json.dumps({"type": "token", "content": word + " "}))
                    await asyncio.sleep(0)
                await websocket.send_text(json.dumps({"type": "done", "content": ""}))
            except Exception as e:
                await websocket.send_text(json.dumps({"type": "error", "content": str(e)}))
    except WebSocketDisconnect:
        pass


# ── Mount helper (call from server.py or standalone app) ─────────────────────

def register(app):
    """Register WebSocket route on an existing FastAPI app."""
    from fastapi import WebSocket as WS
    @app.websocket("/ws/{agent_name}")
    async def _ws(websocket: WS, agent_name: str):
        await ws_agent(websocket, agent_name)
