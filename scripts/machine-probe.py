#!/usr/bin/env python3
"""
DOME-HUB machine-probe — sovereign self-introspection.

Probes hardware, OS, security posture, and runtime facts about THIS node
and emits a canonical JSON at `agents/core/.mesh/machine.json`.

Agents read this via `agents.core.machine.get_profile()`; they do not
shell out themselves — the profile is the ground truth.

Run manually:   python3 scripts/machine-probe.py
Or via pnpm:    pnpm probe  (if added to package.json)
"""
from __future__ import annotations

import json
import os
import pathlib
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

DOME_ROOT = pathlib.Path(
    os.environ.get("DOME_ROOT") or pathlib.Path(__file__).resolve().parents[1]
)
OUT = DOME_ROOT / "agents" / "core" / ".mesh" / "machine.json"


# ── helpers ──────────────────────────────────────────────────────────────
def _sh(cmd: list[str], timeout: int = 5) -> str:
    try:
        return subprocess.check_output(
            cmd, text=True, stderr=subprocess.DEVNULL, timeout=timeout
        ).strip()
    except Exception:
        return ""


def _sysctl(key: str) -> str:
    return _sh(["sysctl", "-n", key])


def _sysctl_int(key: str) -> int | None:
    v = _sysctl(key)
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _exists(path: str) -> bool:
    return pathlib.Path(path).exists()


def _has(cmd: str) -> bool:
    return shutil.which(cmd) is not None


# ── probes ───────────────────────────────────────────────────────────────
def probe_os() -> dict:
    return {
        "name": platform.system(),
        "release": platform.release(),
        "version": platform.mac_ver()[0] if platform.system() == "Darwin" else platform.version(),
        "kernel": platform.platform(),
        "arch": platform.machine(),
        "hostname": platform.node(),
    }


def _apple_chip_specs(brand: str) -> dict:
    """Known-good spec table for Apple Silicon (NPU TOPS, mem bandwidth).

    sysctl exposes chip brand but not NPU TOPS or memory bandwidth — we
    look those up from public Apple specs.
    """
    table = {
        "M1":        {"npu_tops": 11,   "mem_bandwidth_gbps": 68},
        "M1 Pro":    {"npu_tops": 11,   "mem_bandwidth_gbps": 200},
        "M1 Max":    {"npu_tops": 11,   "mem_bandwidth_gbps": 400},
        "M1 Ultra":  {"npu_tops": 22,   "mem_bandwidth_gbps": 800},
        "M2":        {"npu_tops": 15.8, "mem_bandwidth_gbps": 100},
        "M2 Pro":    {"npu_tops": 15.8, "mem_bandwidth_gbps": 200},
        "M2 Max":    {"npu_tops": 15.8, "mem_bandwidth_gbps": 400},
        "M2 Ultra":  {"npu_tops": 31.6, "mem_bandwidth_gbps": 800},
        "M3":        {"npu_tops": 18,   "mem_bandwidth_gbps": 100},
        "M3 Pro":    {"npu_tops": 18,   "mem_bandwidth_gbps": 150},
        "M3 Max":    {"npu_tops": 18,   "mem_bandwidth_gbps": 400},
        "M4":        {"npu_tops": 38,   "mem_bandwidth_gbps": 120},
        "M4 Pro":    {"npu_tops": 38,   "mem_bandwidth_gbps": 273},
        "M4 Max":    {"npu_tops": 38,   "mem_bandwidth_gbps": 546},
    }
    # Longest-prefix match (so "M4 Pro" wins over "M4" when brand = "Apple M4 Pro")
    for key in sorted(table.keys(), key=len, reverse=True):
        if key in brand:
            return {"chip_family": key, **table[key]}
    return {"chip_family": None, "npu_tops": None, "mem_bandwidth_gbps": None}


def probe_cpu() -> dict:
    brand = _sysctl("machdep.cpu.brand_string") or _sysctl("hw.model")
    total = _sysctl_int("hw.ncpu")
    perf = _sysctl_int("hw.perflevel0.logicalcpu")
    eff = _sysctl_int("hw.perflevel1.logicalcpu")

    cpu = {
        "brand": brand,
        "arch": platform.machine(),
        "cores_total": total,
        "cores_performance": perf,
        "cores_efficiency": eff,
        "frequency_hz_max": _sysctl_int("hw.cpufrequency_max"),
    }
    if brand and "Apple" in brand:
        cpu.update(_apple_chip_specs(brand))
    return cpu


def probe_gpu() -> dict:
    if platform.system() != "Darwin":
        return {"detected": False}
    raw = _sh(["system_profiler", "SPDisplaysDataType"], timeout=15)
    model = None
    cores = None
    m = re.search(r"Chipset Model:\s*(.+)", raw)
    if m:
        model = m.group(1).strip()
    m = re.search(r"Total Number of Cores:\s*(\d+)", raw)
    if m:
        cores = int(m.group(1))
    return {
        "detected": bool(model),
        "model": model,
        "cores": cores,
        "backend": "mps" if model else None,
    }


def probe_memory() -> dict:
    total_bytes = _sysctl_int("hw.memsize")
    pagesize = _sysctl_int("hw.pagesize") or 16384
    vm = _sh(["vm_stat"])
    free_pages = 0
    m = re.search(r"Pages free:\s+(\d+)", vm)
    if m:
        free_pages = int(m.group(1))
    return {
        "total_bytes": total_bytes,
        "total_gb": round(total_bytes / (1024**3), 2) if total_bytes else None,
        "free_bytes_estimate": free_pages * pagesize if free_pages else None,
        "unified": platform.machine() == "arm64",
    }


def probe_storage() -> dict:
    usage = shutil.disk_usage("/")
    filevault = "On" in _sh(["fdesetup", "status"])
    return {
        "root_total_bytes": usage.total,
        "root_free_bytes": usage.free,
        "root_used_bytes": usage.used,
        "filevault": filevault,
    }


def probe_security() -> dict:
    fv = "On" in _sh(["fdesetup", "status"])
    sip = "enabled" in _sh(["csrutil", "status"])
    gatekeeper = "enabled" in _sh(["spctl", "--status"])

    fw_state = _sh(["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"])
    firewall_on = bool(re.search(r"enabled|blocking", fw_state, re.I))

    stealth = _sh(["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getstealthmode"])
    stealth_on = "on" in stealth.lower()

    # GPG / pass
    has_gpg = bool(_sh(["/opt/homebrew/bin/gpg", "--list-secret-keys"]))
    pass_init = (pathlib.Path.home() / ".password-store").is_dir()

    # Keychain (sovereign default per DOME-HUB baseline)
    keychain_ok = subprocess.call(
        ["security", "find-generic-password", "-s", "dome/HUB_API_SECRET"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ) == 0

    # Git signing (global)
    signing = _sh(["git", "config", "--global", "commit.gpgsign"]) == "true"

    # DNS through dnscrypt-proxy
    dns = _sh(["scutil", "--dns"])
    dns_private = "127.0.0.1" in dns.splitlines()[0] if dns else False

    return {
        "filevault": fv,
        "sip": sip,
        "gatekeeper": gatekeeper,
        "firewall_enabled": firewall_on,
        "firewall_stealth": stealth_on,
        "gpg_key_present": has_gpg,
        "pass_initialized": pass_init,
        "keychain_backend": keychain_ok,
        "git_commit_signing": signing,
        "dns_private": dns_private,
    }


def probe_runtime() -> dict:
    pythons = {}
    for v in ("3.10", "3.11", "3.12", "3.13", "3.14"):
        path = shutil.which(f"python{v}") or shutil.which(f"python3.{v.split('.')[1]}")
        if path:
            pythons[v] = path

    return {
        "python_current": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "python_executable": sys.executable,
        "pythons_available": pythons,
        "node_version": _sh(["node", "--version"]),
        "pnpm_version": _sh(["pnpm", "--version"]),
        "brew": _has("brew"),
        "go_version": _sh(["go", "version"]),
        "rust_version": _sh(["rustc", "--version"]),
        "ollama_running": _has("ollama") and "running" in _sh(["brew", "services", "list"]).lower(),
        "docker": _has("docker"),
    }


def classify_tier(ram_gb: float | None, has_gpu: bool) -> str:
    """Tier thresholds aligned with scripts/ollama-init.sh."""
    if ram_gb is None:
        return "unknown"
    if ram_gb >= 64:
        return "workstation"
    if ram_gb >= 32:
        return "heavy"
    if ram_gb >= 18:
        return "sovereign"
    if ram_gb >= 12:
        return "guardian"
    if ram_gb >= 8:
        return "scout"
    return "seed"


def main() -> int:
    cpu = probe_cpu()
    gpu = probe_gpu()
    mem = probe_memory()
    os_ = probe_os()
    storage = probe_storage()
    security = probe_security()
    runtime = probe_runtime()

    tier = classify_tier(mem.get("total_gb"), gpu.get("detected", False))

    profile = {
        "probed_at": datetime.now(timezone.utc).isoformat(),
        "probe_version": "1.0.0",
        "dome_root": str(DOME_ROOT),
        "tier": tier,
        "os": os_,
        "cpu": cpu,
        "gpu": gpu,
        "memory": mem,
        "storage": storage,
        "security": security,
        "runtime": runtime,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(profile, indent=2), encoding="utf-8")

    print(f"✓ Machine profile written: {OUT.relative_to(DOME_ROOT)}")
    print(f"  chip:    {cpu.get('brand', 'unknown')}  ({cpu.get('chip_family') or '—'})")
    print(f"  cores:   {cpu.get('cores_total')} "
          f"({cpu.get('cores_performance') or '?'}P + {cpu.get('cores_efficiency') or '?'}E)")
    print(f"  gpu:     {gpu.get('model', '—')}  ({gpu.get('cores', '?')}-core)")
    print(f"  npu:     {cpu.get('npu_tops', '—')} TOPS")
    print(f"  ram:     {mem.get('total_gb', '?')} GB  (bandwidth: {cpu.get('mem_bandwidth_gbps', '?')} GB/s)")
    print(f"  tier:    {tier}")
    print(f"  secure:  FV={security['filevault']} SIP={security['sip']} "
          f"FW={security['firewall_enabled']} DNS={security['dns_private']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
