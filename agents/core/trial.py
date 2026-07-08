"""
DSH Trial Period Tracker
Tracks 90-day trial in SQLite. After expiry without HUB holding → read-only degradation.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DB_PATH = Path(__file__).parents[2] / "db" / "dome.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS trial_state (
    id                    INTEGER PRIMARY KEY CHECK (id = 1),
    install_date          TEXT NOT NULL,
    trial_days            INTEGER NOT NULL DEFAULT 90,
    hub_holding_verified  INTEGER NOT NULL DEFAULT 0,
    license_validated_at  TEXT
)
"""


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.execute(_SCHEMA)
    c.commit()
    return c


def _ensure_row(c: sqlite3.Connection) -> None:
    row = c.execute("SELECT 1 FROM trial_state WHERE id=1").fetchone()
    if not row:
        c.execute(
            "INSERT INTO trial_state (id, install_date, trial_days, hub_holding_verified) VALUES (1, ?, 90, 0)",
            (datetime.now(timezone.utc).isoformat(),),
        )
        c.commit()


@dataclass
class TrialStatus:
    days_remaining: int
    is_expired: bool
    is_degraded: bool
    install_date: str
    hub_holding_verified: bool


class TrialTracker:
    def __init__(self) -> None:
        self._conn = _conn()
        _ensure_row(self._conn)

    def status(self) -> TrialStatus:
        row = self._conn.execute(
            "SELECT install_date, trial_days, hub_holding_verified FROM trial_state WHERE id=1"
        ).fetchone()
        install_date, trial_days, hub_verified = row
        elapsed = (datetime.now(timezone.utc) - datetime.fromisoformat(install_date)).days
        remaining = max(0, trial_days - elapsed)
        expired = remaining == 0
        degraded = expired and not hub_verified
        return TrialStatus(
            days_remaining=remaining,
            is_expired=expired,
            is_degraded=degraded,
            install_date=install_date,
            hub_holding_verified=bool(hub_verified),
        )

    def validate_with_trinity(self, api_base: str, jwt: str, hub_secret: str) -> dict:
        """POST /api/v1/license/validate on Trinity API.
        On success with sufficient HUB holding, updates hub_holding_verified=True."""
        url = f"{api_base.rstrip('/')}/api/v1/license/validate"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jwt}",
            "x-hub-secret": hub_secret,
        }
        req = Request(url, data=b"{}", headers=headers, method="POST")
        try:
            with urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except (HTTPError, URLError):
            raise

        if data.get("hub_holding_sufficient") or data.get("valid"):
            now = datetime.now(timezone.utc).isoformat()
            self._conn.execute(
                "UPDATE trial_state SET hub_holding_verified=1, license_validated_at=? WHERE id=1",
                (now,),
            )
            self._conn.commit()
        return data


# Module-level singleton — auto-initializes table on first import
_tracker: TrialTracker | None = None


def get_tracker() -> TrialTracker:
    global _tracker
    if _tracker is None:
        _tracker = TrialTracker()
    return _tracker
