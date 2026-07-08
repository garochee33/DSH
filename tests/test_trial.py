"""Tests for DSH trial period tracker."""
import os
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Redirect trial tracker to a temp DB."""
    db_path = tmp_path / "db" / "dome.db"
    db_path.parent.mkdir(parents=True)
    monkeypatch.setattr("agents.core.trial.DB_PATH", db_path)
    # Reset singleton
    import agents.core.trial as t
    t._tracker = None
    yield db_path


def test_trial_creates_table(temp_db):
    from agents.core.trial import get_tracker
    tracker = get_tracker()
    conn = sqlite3.connect(temp_db)
    row = conn.execute("SELECT install_date, trial_days, hub_holding_verified FROM trial_state WHERE id=1").fetchone()
    assert row is not None
    assert row[1] == 90
    assert row[2] == 0


def test_trial_status_fresh_install(temp_db):
    from agents.core.trial import get_tracker
    status = get_tracker().status()
    assert status.days_remaining == 90
    assert status.is_expired is False
    assert status.is_degraded is False
    assert status.hub_holding_verified is False


def test_trial_status_expired(temp_db):
    from agents.core.trial import get_tracker
    # First call creates the table + row
    get_tracker()
    # Backdate install to 91 days ago
    from datetime import datetime, timezone, timedelta
    old_date = (datetime.now(timezone.utc) - timedelta(days=91)).isoformat()
    conn = sqlite3.connect(temp_db)
    conn.execute("UPDATE trial_state SET install_date=? WHERE id=1", (old_date,))
    conn.commit()

    import agents.core.trial as t
    t._tracker = None  # reset singleton
    status = get_tracker().status()
    assert status.days_remaining == 0
    assert status.is_expired is True
    assert status.is_degraded is True


def test_trial_not_degraded_if_hub_verified(temp_db):
    from agents.core.trial import get_tracker
    get_tracker()  # ensure table exists
    from datetime import datetime, timezone, timedelta
    old_date = (datetime.now(timezone.utc) - timedelta(days=91)).isoformat()
    conn = sqlite3.connect(temp_db)
    conn.execute("UPDATE trial_state SET install_date=?, hub_holding_verified=1 WHERE id=1", (old_date,))
    conn.commit()

    import agents.core.trial as t
    t._tracker = None
    status = get_tracker().status()
    assert status.is_expired is True
    assert status.is_degraded is False
    assert status.hub_holding_verified is True
