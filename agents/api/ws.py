"""
DSH WebSocket — real-time agent streaming with PQC auth
"""

from __future__ import annotations
import asyncio, json, hashlib, hmac, os
import logging

from fastapi import WebSocket, WebSocketDisconnect, Query

from agents.core.registry import make_dome_orchestrator

_orc = None
_LOG = logging.getLogger(__name__)
_WS_SECRET = os.environ.get("DOME_WS_SECRET", os.environ.get("HUB_API_SECRET", ""))


def _verify_token(token: str) -> bool:
    """Verify WS auth token: HMAC-SHA3-256(secret, 'dome-ws-auth'). Quantum-resistant."""
    if not _WS_SECRET:
        return True  # No secret configured = local-only mode (sovereign)
    expected = hmac.HMAC(_WS_SECRET.encode(), b"dome-ws-auth", hashlib.sha3_256).hexdigest()
    return hmac.compare_digest(token, expected)


def get_orc():
    global _orc
    if _orc is None:
        _orc = make_dome_orchestrator()
    return _orc


async def ws_agent(websocket: WebSocket, agent_name: str, token: str = Query(default="")):
    """Mount at /ws/{agent_name}?token=<hmac>"""
    # Auth gate
    if not _verify_token(token):
        await websocket.close(code=4001, reason="Unauthorized")
        _LOG.warning("WS auth rejected for agent=%s", agent_name)
        return

    orc = get_orc()
    if agent_name not in orc.agents:
        await websocket.accept()
        await websocket.send_text(
            json.dumps({"type": "error", "content": f"Agent '{agent_name}' not found"})
        )
        await websocket.close()
        return

    await websocket.accept()
    _LOG.info("WS connected: agent=%s", agent_name)
    try:
        while True:
            prompt = await websocket.receive_text()
            try:
                loop = asyncio.get_running_loop()
                response: str = await loop.run_in_executor(
                    None, orc.agents[agent_name].run, prompt
                )
                for word in response.split(" "):
                    await websocket.send_text(
                        json.dumps({"type": "token", "content": word + " "})
                    )
                    await asyncio.sleep(0)
                await websocket.send_text(json.dumps({"type": "done", "content": ""}))
            except Exception as e:
                await websocket.send_text(
                    json.dumps({"type": "error", "content": str(e)})
                )
    except WebSocketDisconnect:
        _LOG.debug("WS disconnected: agent=%s", agent_name)


# ── Mount helper ─────────────────────────────────────────────────────────────


def register(app):
    """Register WebSocket route on an existing FastAPI app."""
    from fastapi import WebSocket as WS, Query as Q

    @app.websocket("/ws/{agent_name}")
    async def _ws(websocket: WS, agent_name: str, token: str = Q(default="")):
        await ws_agent(websocket, agent_name, token)
