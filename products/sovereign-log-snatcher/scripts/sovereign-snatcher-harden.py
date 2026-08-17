#!/usr/bin/env python3
"""Harden gate for Sovereign Log Snatcher. Uses SKY_HUB_ROOT. Does not invent entity execution."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("SKY_HUB_ROOT") or Path(__file__).resolve().parents[1]).resolve()
SOVEREIGN = Path(os.environ.get("SOVEREIGN_ROOT") or ROOT.parent).resolve()
PY = ROOT / ".venv" / "bin" / "python"
if not PY.is_file():
    PY = Path(sys.executable)
SNATCHER = ROOT / "scripts" / "sovereign-snatcher.py"
LABEL = "com.skyhub.sovereign-snatcher"
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
        "schema": "sky.sovereign.snatcher-harden/v1",
        "product": "Sovereign Log Snatcher",
        "at": datetime.now(timezone.utc).isoformat(),
        "sky_hub_root": str(ROOT),
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

    test_code, test_out = sh(
        [str(PY), "-m", "pytest", str(ROOT / "tests" / "test_sovereign_snatcher.py"), "-q"],
        timeout=90,
    )
    report["unit_tests"] = {"rc": test_code, "ok": test_code == 0, "tail": test_out[-800:]}

    amma: dict = {"attempted": False}
    abba: dict = {"attempted": False}
    try:
        sys.path.insert(0, str(ROOT))
        sys.path.insert(0, str(ROOT / "scripts"))
        from compute.harness.admission import EntityClient  # noqa: E402

        amma["attempted"] = True
        try:
            obs = EntityClient("amma").call({"method": "observe"})
            amma["observe_ok"] = bool(obs.get("ok", True))
            amma["workload_executed"] = bool(obs.get("workload_executed", False))
        except Exception as ex:
            amma["observe_ok"] = False
            amma["observe_error"] = f"{type(ex).__name__}: {ex}"
        abba["attempted"] = True
        try:
            st = EntityClient("abba").call({"method": "status"})
            abba["status_ok"] = bool(st.get("ok", True))
            abba["workload_execution_enabled"] = st.get("workload_execution_enabled")
            abba["workload_executed"] = st.get("workload_executed")
        except Exception as ex:
            abba["status_ok"] = False
            abba["status_error"] = f"{type(ex).__name__}: {ex}"
    except Exception as ex:
        amma["import_error"] = f"{type(ex).__name__}: {ex}"
    report["amma"] = amma
    report["abba"] = abba

    report["harden_ok"] = bool(
        report["self_check"].get("ok")
        and report["launchd"].get("print_ok")
        and report["launchd"].get("interval_900")
        and report["launchd"].get("plist_exists")
        and report["custody"].get("ok")
        and report["unit_tests"].get("ok")
    )
    outp = ROOT / "evidence" / "runs" / f"SOVEREIGN-LOG-SNATCHER-HARDEN-{stamp}.json"
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
                "unit_tests": report["unit_tests"].get("ok"),
                "amma_observe": amma.get("observe_ok"),
                "abba_status": abba.get("status_ok"),
            },
            indent=2,
            default=str,
        )
    )
    return 0 if report["harden_ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
