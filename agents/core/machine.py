"""
Machine profile accessor — DOME-HUB self-knowledge.

Agents and scripts read the canonical machine profile (probed once by
`scripts/machine-probe.py`) via this module. Do not re-probe in agent
code — the profile is the ground truth and is refreshed by setup/maintenance
flows, not per-call.

Typical usage:

    from agents.core.machine import get_profile, get_tier, recommend_local_model

    profile = get_profile()
    if profile["security"]["filevault"]:
        ...

    tier = get_tier()          # "sovereign", "guardian", ...
    model = recommend_local_model()  # "qwen2.5-coder:14b"
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
from typing import Any

DOME_ROOT = pathlib.Path(
    os.environ.get("DOME_ROOT") or pathlib.Path(__file__).resolve().parents[2]
)
PROFILE_PATH = DOME_ROOT / "agents" / "core" / ".mesh" / "machine.json"
PROBE_SCRIPT = DOME_ROOT / "scripts" / "machine-probe.py"


class ProfileMissingError(RuntimeError):
    """Raised when no machine profile has been generated yet."""


def _load() -> dict[str, Any]:
    if not PROFILE_PATH.exists():
        raise ProfileMissingError(
            f"No machine profile at {PROFILE_PATH}. "
            f"Run: python3 {PROBE_SCRIPT.relative_to(DOME_ROOT)}"
        )
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def get_profile(auto_probe: bool = False) -> dict[str, Any]:
    """Return the machine profile dict.

    If `auto_probe=True` and no profile exists, invoke the probe first.
    Default is False so callers see an explicit error if setup is incomplete.
    """
    try:
        return _load()
    except ProfileMissingError:
        if not auto_probe:
            raise
        subprocess.run(
            [sys.executable, str(PROBE_SCRIPT)],
            check=True,
        )
        return _load()


def get_tier() -> str:
    """Return the spore.sh-compatible hardware tier."""
    return get_profile().get("tier", "unknown")


def get_ram_gb() -> float | None:
    return get_profile()["memory"].get("total_gb")


def get_chip_family() -> str | None:
    return get_profile()["cpu"].get("chip_family")


def get_npu_tops() -> float | None:
    return get_profile()["cpu"].get("npu_tops")


def is_apple_silicon() -> bool:
    p = get_profile()
    return p["os"]["arch"] == "arm64" and p["os"]["name"] == "Darwin"


def recommend_local_model() -> str:
    """Pick a sensible default Ollama model for this node's tier."""
    tier = get_tier()
    return {
        "workstation": "qwen2.5-coder:32b",
        "heavy": "qwen2.5-coder:14b",
        "sovereign": "qwen2.5-coder:14b",
        "guardian": "llama3.1:8b",
        "scout": "llama3.1:8b",
        "seed": "phi3:mini",
    }.get(tier, "llama3.1:8b")


def security_posture() -> dict[str, bool]:
    """Compact security summary for agents that gate privileged actions."""
    s = get_profile().get("security", {})
    return {
        "filevault": bool(s.get("filevault")),
        "sip": bool(s.get("sip")),
        "gatekeeper": bool(s.get("gatekeeper")),
        "firewall": bool(s.get("firewall_enabled")),
        "dns_private": bool(s.get("dns_private")),
        "secrets_backend_present": bool(
            s.get("keychain_backend") or s.get("pass_initialized")
        ),
    }


def summary_one_liner() -> str:
    """Human-readable single line — useful for log headers / agent prompts."""
    p = get_profile()
    cpu = p["cpu"]
    mem = p["memory"]
    return (
        f"{cpu.get('brand', 'unknown')} · "
        f"{cpu.get('cores_total', '?')} cores "
        f"({cpu.get('cores_performance', '?')}P + {cpu.get('cores_efficiency', '?')}E) · "
        f"{mem.get('total_gb', '?')} GB RAM · "
        f"{cpu.get('npu_tops', '—')} TOPS NPU · "
        f"tier={p.get('tier', '?')}"
    )


__all__ = [
    "ProfileMissingError",
    "get_profile",
    "get_tier",
    "get_ram_gb",
    "get_chip_family",
    "get_npu_tops",
    "is_apple_silicon",
    "recommend_local_model",
    "security_posture",
    "summary_one_liner",
]
