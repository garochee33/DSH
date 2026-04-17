"""DOME-HUB API package — FastAPI server and WebSocket endpoints."""

from agents.api.server import app
from agents.api.ws import register, ws_agent

__all__ = ["app", "register", "ws_agent"]
