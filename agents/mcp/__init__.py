"""Trinity MCP servers — sovereign tool surfaces over stdio.

This package hosts MCP (Model Context Protocol) servers that expose
DSH internals to Claude Code and other MCP-aware hosts.

Servers
-------
- ``vault-server.py`` — Obsidian second-brain vault: search, read, write,
  list, and registry-sync.

All servers are stdio-only (no network listener), enforce path containment
under their configured root, and use Trinity vocabulary (Mycelium Signal,
pheromone, MERKABA, member/admin).
"""

__all__: list[str] = []
