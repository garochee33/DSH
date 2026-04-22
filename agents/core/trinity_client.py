"""
Trinity Client — open-core Phase 2 accessor.

Three-layer architecture this client lives inside:
  - DSH (public, open-source)                  ← this repo
  - trinity-unified-ai (public platform,       ← this client talks to it
    paid API, own sovereign UI)                  at TRINITY_API_BASE
  - trinity-consortium (private command        ← not exposed to this client
    center, not customer-facing)                 or its users

DSH Phase 1 is fully operational on its own (local-first sovereignty).
Phase 2 activates when Trinity-issued credentials are present in the
environment — at which point trinity-unified-ai's KB API, Trinity engines,
and persistent Fractal Memory become available via authenticated HTTP.

Credentials are issued by Kommunity DAO membership at https://kommunity.life.

Provider modes (DOME_PROVIDER env var):
    "local"   → never attempt Trinity; use local ChromaDB + local agents only
    "trinity" → require Trinity credentials; raise if missing or degraded
    "mixed"   → prefer Trinity when credentials present; fall back to local
                when Trinity is unreachable or returns 402/403 (default)

Credentials (read from .env or process env):
    TRINITY_API_BASE    — default "http://127.0.0.1:3333"
    HUB_API_SECRET      — service-to-service header auth
    TRINITY_JWT         — member JWT (tier + quota claims)
    SPORE_TOKEN         — mesh peer activation (used by spore.sh, not by this client)

Philosophy: users are never silently gated. Every upgrade prompt is visible
and points to https://kommunity.life (Request Access).

Typical usage:

    from agents.core.trinity_client import TrinityClient

    client = TrinityClient()
    if client.is_premium():
        results = client.kb_search("E8 lattice nearest root")
    else:
        results = LocalVectorMemory("dome-kb").search("E8 lattice nearest root")

    # Or use the convenience wrapper which handles the fallback:
    results = client.search_with_fallback("E8 lattice nearest root")
"""
from __future__ import annotations

import json
import os
import pathlib
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DOME_ROOT = pathlib.Path(
    os.environ.get("DOME_ROOT") or pathlib.Path(__file__).resolve().parents[2]
)

UPGRADE_URL = "https://kommunity.life"
UPGRADE_MSG = (
    "Phase 2 access required. Request Access at "
    + UPGRADE_URL
    + " — Kommunity membership issues the SPORE_TOKEN + JWT that unlock "
    + "the trinity-unified-ai API."
)


class TrinityPhase2Required(RuntimeError):
    """Raised in 'trinity' mode when Trinity credentials are missing or the
    service rejects authentication. Never raised in 'local' or 'mixed'
    mode — those degrade gracefully."""


class TrinityQuotaExhausted(RuntimeError):
    """Raised when the authenticated tier has consumed its quota for this
    period. Carries the upgrade URL so UIs can surface it inline."""


@dataclass
class TrinityStatus:
    """Observable state — cheap to inspect; used by dashboards and CLI tools
    to show whether Phase 2 is active and what tier is authorized."""

    provider: str           # "local" | "trinity" | "mixed"
    mode: str               # "local" (offline) | "premium" (Phase 2 live)
    api_base: str
    has_hub_secret: bool
    has_jwt: bool
    reachable: bool | None  # None = not probed yet
    last_error: str | None = None


def _load_env_file(path: pathlib.Path) -> None:
    """Minimal .env loader (no python-dotenv dependency for Phase 1)."""
    if not path.is_file():
        return
    try:
        for raw in path.read_text(encoding="utf-8").splitlines():
            s = raw.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, _, v = s.partition("=")
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            # Respect values already set in the process env — do not override.
            os.environ.setdefault(k, v)
    except Exception:
        # .env loading must never crash — it is a convenience only.
        return


class TrinityClient:
    """Phase 2 HTTP accessor. All methods are sync (urllib) to keep the
    public DSH client free of third-party deps."""

    def __init__(self, load_env: bool = True) -> None:
        if load_env:
            _load_env_file(DOME_ROOT / ".env")

        self.api_base: str = os.environ.get("TRINITY_API_BASE", "http://127.0.0.1:3333").rstrip("/")
        self.hub_secret: str | None = os.environ.get("HUB_API_SECRET") or None
        self.jwt: str | None = os.environ.get("TRINITY_JWT") or None
        self.provider: str = os.environ.get("DOME_PROVIDER", "mixed").lower()
        if self.provider not in ("local", "trinity", "mixed"):
            self.provider = "mixed"

    # ── mode predicates ────────────────────────────────────────────────

    def has_credentials(self) -> bool:
        return bool(self.hub_secret or self.jwt)

    def is_premium(self) -> bool:
        """True when this client should prefer Trinity over local.

        local   → always False (never try Trinity)
        trinity → always True (fail fast if no creds)
        mixed   → True if any credential present
        """
        if self.provider == "local":
            return False
        if self.provider == "trinity":
            return True
        return self.has_credentials()  # mixed

    def status(self, probe: bool = False) -> TrinityStatus:
        """Return a TrinityStatus snapshot. `probe=True` performs a /health
        request; omit for zero-network inspection."""
        reachable: bool | None = None
        last_error: str | None = None
        mode = "premium" if self.is_premium() else "local"
        if probe and self.provider != "local":
            try:
                _ = self._get("/health", timeout=3)
                reachable = True
            except Exception as e:  # noqa: BLE001
                reachable = False
                last_error = str(e)
        return TrinityStatus(
            provider=self.provider,
            mode=mode,
            api_base=self.api_base,
            has_hub_secret=bool(self.hub_secret),
            has_jwt=bool(self.jwt),
            reachable=reachable,
            last_error=last_error,
        )

    # ── HTTP helpers ───────────────────────────────────────────────────

    def _headers(self) -> dict[str, str]:
        h: dict[str, str] = {"Accept": "application/json"}
        if self.jwt:
            h["Authorization"] = f"Bearer {self.jwt}"
        if self.hub_secret:
            h["x-hub-secret"] = self.hub_secret
        return h

    def _get(self, path: str, params: dict[str, Any] | None = None, timeout: int = 10) -> Any:
        url = f"{self.api_base}{path}"
        if params:
            url += "?" + urlencode(params)
        req = Request(url, headers=self._headers(), method="GET")
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _post(self, path: str, body: dict[str, Any], timeout: int = 30) -> Any:
        url = f"{self.api_base}{path}"
        data = json.dumps(body).encode("utf-8")
        headers = self._headers()
        headers["Content-Type"] = "application/json"
        req = Request(url, data=data, headers=headers, method="POST")
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    # ── public API surface ─────────────────────────────────────────────

    def health(self) -> dict[str, Any]:
        """Unauthenticated liveness probe. Returns server self-report."""
        return self._get("/health", timeout=5)

    def kb_search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Semantic search against the Trinity KB. Phase 2 only."""
        self._require_phase2("kb_search")
        try:
            resp = self._get("/api/search", params={"q": query, "limit": limit})
        except HTTPError as e:
            self._translate_http_error(e)
            raise
        return list(resp.get("results", []))

    def engine_call(self, engine: str, body: dict[str, Any]) -> Any:
        """Invoke a Trinity engine by name. Phase 2 only."""
        self._require_phase2(f"engine_call({engine})")
        try:
            return self._post(f"/api/engine/execute/{engine}", body)
        except HTTPError as e:
            self._translate_http_error(e)
            raise

    def e8_nearest_root(self, vector: list[float], limit: int = 5) -> dict[str, Any]:
        """E8 lattice nearest-root lookup. Phase 2 only."""
        self._require_phase2("e8_nearest_root")
        try:
            return self._post(
                "/api/e8-compute/nearest-root",
                {"vector": list(vector), "limit": limit},
            )
        except HTTPError as e:
            self._translate_http_error(e)
            raise

    def agent_execute(self, agent_name: str, instruction: str, context: dict[str, Any] | None = None) -> Any:
        """Execute a Trinity sovereign agent. Phase 2 only."""
        self._require_phase2(f"agent_execute({agent_name})")
        body: dict[str, Any] = {"agentName": agent_name, "instruction": instruction}
        if context is not None:
            body["context"] = context
        try:
            return self._post("/api/agent/execute", body)
        except HTTPError as e:
            self._translate_http_error(e)
            raise

    # ── fallback wrappers for caller convenience ─────────────────────

    def search_with_fallback(self, query: str, limit: int = 5) -> dict[str, Any]:
        """Search Trinity KB if premium; otherwise return local ChromaDB
        results. Always returns a dict with 'source' ∈ {'trinity', 'local'}
        so callers can surface which path was used."""
        if self.is_premium():
            try:
                results = self.kb_search(query, limit=limit)
                return {"source": "trinity", "results": results}
            except TrinityPhase2Required:
                if self.provider == "trinity":
                    raise
                # mixed → fall through to local
            except (HTTPError, URLError):
                if self.provider == "trinity":
                    raise
                # mixed → fall through to local
        return {"source": "local", "results": self._local_kb_search(query, limit=limit), "upgrade": UPGRADE_URL}

    # ── private helpers ────────────────────────────────────────────────

    def _require_phase2(self, feature: str) -> None:
        if self.provider == "local":
            raise TrinityPhase2Required(
                f"{feature} requires Phase 2 (Trinity credentials). "
                f"Provider is 'local'. {UPGRADE_MSG}"
            )
        if self.provider == "trinity" and not self.has_credentials():
            raise TrinityPhase2Required(
                f"{feature} requires Phase 2 credentials. "
                f"Set TRINITY_JWT or HUB_API_SECRET in $DOME_ROOT/.env. {UPGRADE_MSG}"
            )
        if self.provider == "mixed" and not self.has_credentials():
            raise TrinityPhase2Required(
                f"{feature} requires Phase 2 credentials. {UPGRADE_MSG}"
            )

    def _translate_http_error(self, e: HTTPError) -> None:
        if e.code == 401:
            raise TrinityPhase2Required(
                f"Trinity rejected the provided credentials (401). "
                f"Refresh your JWT at {UPGRADE_URL} or check HUB_API_SECRET."
            ) from None
        if e.code == 402:
            raise TrinityQuotaExhausted(
                f"Quota exhausted on current tier (402). Upgrade at {UPGRADE_URL}."
            ) from None
        if e.code == 403:
            raise TrinityPhase2Required(
                f"Current tier does not include this route (403). Upgrade at {UPGRADE_URL}."
            ) from None
        # Other HTTPErrors propagate as-is.

    def _local_kb_search(self, query: str, limit: int) -> list[dict[str, Any]]:
        """Fall back to the local ChromaDB `dome-kb` namespace.

        Kept inline to avoid importing chromadb when not needed.
        """
        try:
            from agents.core.memory.vector import VectorMemory  # type: ignore
        except Exception:
            return [{"error": "local KB unavailable", "upgrade": UPGRADE_URL}]
        try:
            vm = VectorMemory("dome-kb")
            if hasattr(vm, "query"):
                return vm.query(query, n_results=limit)  # type: ignore[no-any-return]
            if hasattr(vm, "search"):
                return vm.search(query, top_k=limit)  # type: ignore[no-any-return]
        except Exception as e:  # noqa: BLE001
            return [{"error": f"local KB query failed: {e}", "upgrade": UPGRADE_URL}]
        return []


# ── module-level convenience ──────────────────────────────────────────


_default: TrinityClient | None = None


def default_client() -> TrinityClient:
    """Return a process-wide default client. Lazy-initialized."""
    global _default
    if _default is None:
        _default = TrinityClient()
    return _default


__all__ = [
    "TrinityClient",
    "TrinityStatus",
    "TrinityPhase2Required",
    "TrinityQuotaExhausted",
    "UPGRADE_URL",
    "UPGRADE_MSG",
    "default_client",
]
