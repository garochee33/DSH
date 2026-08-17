#!/usr/bin/env python3
"""Local self-check for Sovereign Log Snatcher. No remote calls."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("SNATCHER_ROOT") or Path(__file__).resolve().parents[1]).resolve()
home_sovereign = Path.home() / "sovereign"
default_sovereign = home_sovereign if home_sovereign.is_dir() else Path.home() / ".sovereign"
SOVEREIGN = Path(os.environ.get("SOVEREIGN_ROOT") or default_sovereign).resolve()
PY = Path(sys.executable)
SNATCHER = ROOT / "scripts" / "sovereign-snatcher.py"
LABEL = "com.sovereign.log-snatcher"
PLIST = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"
CUSTODY = SOVEREIGN / "runtime" / "sovereign-snatcher"


def sh(cmd: list[str] | str, timeout: float = 60) -> tuple[int, str]:
    try:
        r = subprocess.run(
            cmd,
            shell=isinstance(cmd, str),
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(ROOT),
        )
        return r.returncode, ((r.stdout or "") + (r.stderr or ""))[-4000:]
    except Exception as ex:
        return 2, f"{type(ex).__name__}: {ex}"


def _json_out(code: int, out: str) -> dict:
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return {"ok": False, "raw": out[-500:], "rc": code}


def main() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report: dict = {
        "schema": "sovereign.snatcher-harden/v1",
        "product": "Sovereign Log Snatcher",
        "at": datetime.now(timezone.utc).isoformat(),
        "snatcher_root": str(ROOT),
        "sovereign_root": str(SOVEREIGN),
    }

    sc_code, sc_out = sh([str(PY), str(SNATCHER), "--self-check"], timeout=30)
    report["self_check"] = _json_out(sc_code, sc_out)
    report["self_check_rc"] = sc_code

    uid = os.getuid()
    lc_code, lc_out = sh(f"launchctl print gui/{uid}/{LABEL}")
    pgrep_code, pgrep_out = sh("pgrep -lf sovereign-snatcher.py")
    launchd_alive = lc_code == 0 and (
        "state = running" in lc_out
        or "state = xpcproxy" in lc_out
        or pgrep_code == 0
    )
    interval_900 = "SOVEREIGN_SNATCHER_INTERVAL => 900" in lc_out or (
        PLIST.is_file() and "900" in PLIST.read_text() and "SOVEREIGN_SNATCHER_INTERVAL" in PLIST.read_text()
    )
    report["launchd"] = {
        "print_ok": launchd_alive,
        "interval_900": interval_900,
        "pgrep": pgrep_out.strip()[:200],
        "plist_exists": PLIST.is_file(),
    }

    custody_ok = CUSTODY.is_dir() and os.access(CUSTODY, os.W_OK)
    mode = oct(CUSTODY.stat().st_mode & 0o777) if CUSTODY.is_dir() else None
    report["custody"] = {"path": str(CUSTODY), "ok": custody_ok, "mode": mode}

    report["harden_ok"] = bool(
        report["self_check"].get("ok")
        and report["launchd"].get("print_ok")
        and report["launchd"].get("interval_900")
        and report["launchd"].get("plist_exists")
        and report["custody"].get("ok")
    )
    outp = ROOT / "receipts" / f"SOVEREIGN-LOG-SNATCHER-HARDEN-{stamp}.json"
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(report, indent=2, default=str))
    print(
        json.dumps(
            {
                "wrote": str(outp),
                "harden_ok": report["harden_ok"],
                "self_check": report["self_check"].get("ok"),
                "launchd_running": report["launchd"].get("print_ok"),
                "interval_900": report["launchd"].get("interval_900"),
            },
            indent=2,
            default=str,
        )
    )
    return 0 if report["harden_ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
