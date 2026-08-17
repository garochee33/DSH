#!/usr/bin/env python3
"""Sovereign Log Snatcher — gather vendor logs into local runtime custody.

This process has no network client. Custody stays under $SOVEREIGN_ROOT/runtime/.
Move = empty vendor telemetry residue. Copy = snapshot live logs in place.
Does not prove OS-level zero egress.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import shutil
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

PRODUCT = "Sovereign Log Snatcher"
TELEMETRY_NAMES = {
    "telemetry.log",
    "cursor-sentry-events.log",
    "extHostTelemetry.log",
    "workerExtHostTelemetry.log",
}
SKIP_DIR_NAMES = {
    "Cache",
    "CachedData",
    "CachedExtensionVSIXs",
    "Code Cache",
    "GPUCache",
    "Service Worker",
    "node_modules",
    ".git",
    "Partitions",
    "IndexedDB",
    "blob_storage",
}
DENY_NAMES = {"auth.json", "cookies", "id_ed25519"}
DENY_SUFFIXES = {".pem", ".key"}
SECRET_RE = re.compile(r"(?i)(\bbearer\s+[a-z0-9._\-]{8,}|sk-[a-z0-9]{20,}|xox[baprs]-[a-z0-9-]+)")
SECRET_SCAN_MAX = 64 * 1024
PROCESS_MONITOR_AGE_S = 120
MAX_COPY_BYTES = 2 * 1024 * 1024 * 1024
DEFAULT_MIN_FREE_BYTES = 2 * 1024 * 1024 * 1024
PRODUCT_INTERVAL_FLOOR = 900
BANNED_NET_ROOTS = {"socket", "urllib", "requests", "http"}


def _env_path(name: str, default: Path) -> Path:
    raw = os.environ.get(name)
    return Path(raw).expanduser().resolve() if raw else default.resolve()


def module_has_no_network_client(path: Path | None = None) -> bool:
    src = (path or Path(__file__)).read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in BANNED_NET_ROOTS:
                    return False
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in BANNED_NET_ROOTS:
                return False
    return True


class Snatcher:
    def __init__(
        self,
        *,
        home: Path | None = None,
        sovereign: Path | None = None,
        sky: Path | None = None,
        policy_path: Path | None = None,
    ) -> None:
        script_sky = Path(__file__).resolve().parents[1]
        self.sky = sky or _env_path("SKY_HUB_ROOT", script_sky)
        self.sovereign = sovereign or _env_path("SOVEREIGN_ROOT", self.sky.parent)
        self.home = (home or Path.home()).expanduser().resolve()
        if policy_path is not None:
            self.policy_path = policy_path
        else:
            candidates = [
                self.sky / "db" / "sovereign-snatcher-policy.json",
                self.sky / "config" / "sovereign-snatcher-policy.json",
            ]
            self.policy_path = next((p for p in candidates if p.is_file()), candidates[0])
        self.policy = self._load_policy()
        self.interval_s = self._int(
            os.environ.get("SOVEREIGN_SNATCHER_INTERVAL")
            or os.environ.get("CURSOR_LOG_CUSTODIAN_INTERVAL")
            or self.policy.get("interval_s"),
            900,
        )
        self.retention_days = self._int(
            os.environ.get("SOVEREIGN_SNATCHER_RETENTION_DAYS")
            or os.environ.get("CURSOR_LOG_CUSTODIAN_RETENTION_DAYS")
            or self.policy.get("retention_days"),
            30,
        )
        self.min_free_bytes = self._int(self.policy.get("min_free_bytes"), DEFAULT_MIN_FREE_BYTES)
        custody_rel = self.policy.get("custody_rel") or "runtime/sovereign-snatcher"
        custody = Path(custody_rel)
        self.custody = custody.resolve() if custody.is_absolute() else (self.sovereign / custody).resolve()
        runtime = (self.sovereign / "runtime").resolve()
        if not str(self.custody).startswith(str(runtime)):
            raise RuntimeError(f"custody path escapes sovereign runtime: {self.custody}")
        operator_rel = self.policy.get("operator_rel") or "Sovereign Snatcher"
        self.operator = self.sovereign / operator_rel
        self.state_path = self.custody / "state.json"
        self.receipts_dir = self.custody / "receipts"
        self.app_support = self.home / "Library" / "Application Support"
        self.library_logs = self.home / "Library" / "Logs"
        self.launchd_label = str(self.policy.get("launchd_label") or "com.skyhub.sovereign-snatcher")

    @staticmethod
    def _int(value: object, default: int) -> int:
        try:
            return int(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return default

    def _load_policy(self) -> dict:
        try:
            if self.policy_path.is_file():
                return json.loads(self.policy_path.read_text())
        except (OSError, json.JSONDecodeError):
            pass
        return {}

    def source_enabled(self, name: str) -> bool:
        src = (self.policy.get("sources") or {}).get(name)
        if not isinstance(src, dict):
            return True
        return bool(src.get("enabled", True))

    def _free_bytes(self) -> int:
        target = self.custody if self.custody.exists() else self.custody.parent
        return int(shutil.disk_usage(target).free)

    def disk_budget_ok(self) -> bool:
        if self.min_free_bytes <= 0:
            return True
        try:
            return self._free_bytes() >= self.min_free_bytes
        except OSError:
            return False

    def ensure_tree(self) -> None:
        for p in (self.custody, self.state_path.parent, self.receipts_dir):
            p.mkdir(parents=True, exist_ok=True)
            try:
                os.chmod(p, 0o700)
            except OSError:
                pass
        self._ensure_operator_folder()

    def _ensure_operator_folder(self) -> None:
        self.operator.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(self.operator, 0o700)
        except OSError:
            pass
        links = {
            "custody": self.custody,
            "policy.json": self.policy_path if self.policy_path.is_file() else None,
            "scripts/sovereign-snatcher.py": Path(__file__).resolve(),
            "state.json": self.state_path,
        }
        (self.operator / "scripts").mkdir(parents=True, exist_ok=True)
        for name, target in links.items():
            if target is None:
                continue
            if name != "state.json" and not target.exists():
                continue
            dest = self.operator / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                if dest.is_symlink() or dest.exists():
                    if dest.is_symlink() and dest.resolve() == target.resolve():
                        continue
                    if dest.is_symlink() or dest.is_file():
                        dest.unlink()
                dest.symlink_to(target)
            except OSError:
                pass

    def day_bucket(self, source: str) -> Path:
        day = datetime.now(timezone.utc).strftime("%Y%m%d")
        d = self.custody / source / day
        d.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(d, 0o700)
            os.chmod(d.parent, 0o700)
        except OSError:
            pass
        return d

    @staticmethod
    def _rel_safe(path: Path, root: Path) -> str:
        try:
            return str(path.relative_to(root))
        except ValueError:
            return path.name

    @staticmethod
    def _fingerprint(path: Path) -> str | None:
        try:
            st = path.stat()
        except OSError:
            return None
        return f"{st.st_size}:{int(st.st_mtime)}"

    def _chmod_file(self, path: Path) -> None:
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass

    def _within_custody(self, dest: Path) -> bool:
        try:
            return str(dest.resolve()).startswith(str(self.custody.resolve()))
        except OSError:
            return False

    def _prepare_dest(self, dest: Path) -> Path:
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(dest.parent, 0o700)
        except OSError:
            pass
        return dest

    def _is_telemetry_name(self, name: str) -> bool:
        lower = name.lower()
        return name in TELEMETRY_NAMES or "telemetry" in lower or "sentry" in lower

    def _denied_name(self, path: Path) -> bool:
        name = path.name.lower()
        if name in DENY_NAMES:
            return True
        if path.suffix.lower() in DENY_SUFFIXES:
            return True
        return False

    def _secret_shaped(self, path: Path) -> bool:
        try:
            st = path.stat()
            if st.st_size == 0 or st.st_size > SECRET_SCAN_MAX:
                return False
            suffix = path.suffix.lower()
            if suffix not in {"", ".log", ".txt", ".json", ".jsonl"}:
                return False
            data = path.read_bytes()[:SECRET_SCAN_MAX]
            if b"\0" in data:
                return False
            return bool(SECRET_RE.search(data.decode("utf-8", errors="ignore")))
        except OSError:
            return False

    def _deny_result(self, src: Path, action: str) -> dict:
        return {"ok": False, "reason": "denied_name", "src": str(src), "action": action}

    def move_file(self, src: Path, dest_root: Path, rel_root: Path | None, root_label: str) -> dict:
        if not src.is_file():
            return {"ok": False, "reason": "not_file", "src": str(src), "action": "move"}
        if self._denied_name(src):
            return self._deny_result(src, "move")
        if rel_root is not None and (rel_root in src.parents or src.parent == rel_root):
            rel = self._rel_safe(src, rel_root)
            dest = dest_root / rel
        else:
            dest = dest_root / root_label / src.name
        dest = self._prepare_dest(dest)
        digest = self._fingerprint(src)
        if dest.exists() and digest and digest == self._fingerprint(dest):
            try:
                src.unlink()
                return {
                    "ok": True,
                    "src": str(src),
                    "dest": str(dest),
                    "bytes": 0,
                    "action": "move",
                    "dedup_deleted_vendor": True,
                }
            except OSError as e:
                return {"ok": False, "reason": f"dedup_unlink: {e}", "src": str(src), "action": "move"}
        if dest.exists():
            stamp = datetime.now(timezone.utc).strftime("%H%M%S")
            dest = dest.with_name(dest.name + f".{stamp}")
        try:
            shutil.move(str(src), str(dest))
            self._chmod_file(dest)
            if not self._within_custody(dest):
                dest.unlink(missing_ok=True)
                return {"ok": False, "reason": "dest_escaped_custody", "src": str(src), "action": "move"}
            return {
                "ok": True,
                "src": str(src),
                "dest": str(dest),
                "bytes": dest.stat().st_size,
                "action": "move",
            }
        except OSError as e:
            return {"ok": False, "reason": f"{type(e).__name__}: {e}", "src": str(src), "action": "move"}

    def copy_file(self, src: Path, dest_root: Path, rel_root: Path | None, root_label: str) -> dict:
        if src.is_symlink() and not src.exists():
            return {"ok": False, "reason": "broken_symlink", "src": str(src), "action": "copy"}
        if not src.is_file():
            return {"ok": False, "reason": "not_file", "src": str(src), "action": "copy"}
        if self._denied_name(src):
            return self._deny_result(src, "copy")
        try:
            size = src.stat().st_size
        except OSError as e:
            return {"ok": False, "reason": f"stat: {e}", "src": str(src), "action": "copy"}
        if size > MAX_COPY_BYTES:
            return {"ok": False, "reason": "too_large", "src": str(src), "action": "copy"}
        if self._secret_shaped(src):
            return {
                "ok": False,
                "reason": "skipped_secret_shape",
                "src": str(src),
                "action": "copy",
            }
        if rel_root is not None and (rel_root in src.parents or src.parent == rel_root):
            rel = self._rel_safe(src, rel_root)
            dest = dest_root / rel
        else:
            dest = dest_root / root_label / src.name
        dest = self._prepare_dest(dest)
        fp = self._fingerprint(src)
        if dest.exists() and fp and fp == self._fingerprint(dest):
            return {
                "ok": True,
                "src": str(src),
                "dest": str(dest),
                "bytes": 0,
                "action": "copy",
                "unchanged": True,
            }
        tmp = dest.with_name(dest.name + ".snatch-tmp")
        try:
            shutil.copy2(src, tmp)
            tmp.replace(dest)
            self._chmod_file(dest)
            if not self._within_custody(dest):
                dest.unlink(missing_ok=True)
                return {"ok": False, "reason": "dest_escaped_custody", "src": str(src), "action": "copy"}
            return {
                "ok": True,
                "src": str(src),
                "dest": str(dest),
                "bytes": dest.stat().st_size,
                "action": "copy",
            }
        except OSError as e:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass
            return {"ok": False, "reason": f"{type(e).__name__}: {e}", "src": str(src), "action": "copy"}

    def copy_sqlite(self, src: Path, dest_root: Path, root_label: str) -> dict:
        if not src.is_file():
            return {"ok": False, "reason": "not_file", "src": str(src), "action": "sqlite-backup"}
        if self._denied_name(src):
            return self._deny_result(src, "sqlite-backup")
        dest = self._prepare_dest(dest_root / root_label / src.name)
        meta = dest.with_name(dest.name + ".src-meta")
        fp = self._fingerprint(src)
        if meta.is_file() and dest.is_file():
            try:
                if meta.read_text().strip() == fp:
                    return {
                        "ok": True,
                        "src": str(src),
                        "dest": str(dest),
                        "bytes": 0,
                        "action": "sqlite-backup",
                        "unchanged": True,
                    }
            except OSError:
                pass
        tmp = dest.with_name(dest.name + ".snatch-tmp")
        try:
            tmp.unlink(missing_ok=True)
            src_conn = sqlite3.connect(f"file:{src}?mode=ro", uri=True)
            try:
                dst_conn = sqlite3.connect(str(tmp))
                try:
                    src_conn.backup(dst_conn)
                finally:
                    dst_conn.close()
            finally:
                src_conn.close()
            tmp.replace(dest)
            self._chmod_file(dest)
            meta.write_text(fp or "")
            self._chmod_file(meta)
            if not self._within_custody(dest):
                dest.unlink(missing_ok=True)
                meta.unlink(missing_ok=True)
                return {"ok": False, "reason": "dest_escaped_custody", "src": str(src), "action": "sqlite-backup"}
            return {
                "ok": True,
                "src": str(src),
                "dest": str(dest),
                "bytes": dest.stat().st_size,
                "action": "sqlite-backup",
            }
        except (OSError, sqlite3.Error) as e:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass
            return {
                "ok": False,
                "reason": f"{type(e).__name__}: {e}",
                "src": str(src),
                "action": "sqlite-backup",
            }

    def _walk_files(self, root: Path) -> list[Path]:
        out: list[Path] = []
        if not root.is_dir():
            return out
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
            for name in filenames:
                p = Path(dirpath) / name
                if p.is_symlink():
                    continue
                if p.is_file():
                    out.append(p)
        return out

    def _collect_electron(
        self,
        *,
        app: Path,
        dest_root: Path,
        copy_all_logs: bool,
        move_telemetry: bool,
        move_sentry_crashpad: bool,
        process_monitor: bool,
    ) -> list[dict]:
        results: list[dict] = []
        logs = app / "logs"
        if logs.is_dir():
            for p in self._walk_files(logs):
                if move_telemetry and self._is_telemetry_name(p.name):
                    results.append(self.move_file(p, dest_root, app, "logs"))
                elif copy_all_logs:
                    results.append(self.copy_file(p, dest_root, app, "logs"))
        if move_sentry_crashpad:
            sentry = app / "sentry"
            if sentry.is_dir():
                for p in self._walk_files(sentry):
                    results.append(self.move_file(p, dest_root, app, "sentry"))
            crashpad = app / "Crashpad"
            for sub in ("completed", "pending", "new", "attached"):
                d = crashpad / sub
                if not d.is_dir():
                    continue
                for p in self._walk_files(d):
                    results.append(self.move_file(p, dest_root, app, f"crashpad/{sub}"))
        if process_monitor:
            pm = app / "process-monitor"
            if pm.is_dir():
                for p in pm.iterdir():
                    if not p.is_file():
                        continue
                    if p.suffix not in {".log", ".json", ".txt", ""}:
                        continue
                    try:
                        age = time.time() - p.stat().st_mtime
                    except OSError:
                        continue
                    if age >= PROCESS_MONITOR_AGE_S:
                        results.append(self.move_file(p, dest_root, app, "process-monitor"))
        return results

    def collect_cursor(self) -> list[dict]:
        if not self.source_enabled("cursor"):
            return []
        dest = self.day_bucket("cursor")
        app = self.app_support / "Cursor"
        results = self._collect_electron(
            app=app,
            dest_root=dest,
            copy_all_logs=True,
            move_telemetry=True,
            move_sentry_crashpad=True,
            process_monitor=True,
        )
        audit = self.home / "Desktop" / "cursor-audit"
        if audit.is_dir():
            for name in ("captures.jsonl", "captures.old.jsonl", "ALERTS.log"):
                p = audit / name
                if p.is_file():
                    results.append(self.move_file(p, dest, None, "cursor-audit"))
        return results

    def collect_antigravity(self) -> list[dict]:
        if not self.source_enabled("antigravity"):
            return []
        dest = self.day_bucket("antigravity")
        app = self.app_support / "Antigravity"
        results = self._collect_electron(
            app=app,
            dest_root=dest,
            copy_all_logs=True,
            move_telemetry=True,
            move_sentry_crashpad=True,
            process_monitor=False,
        )
        lib = self.library_logs / "Antigravity"
        if lib.is_dir():
            for p in lib.iterdir():
                if p.is_file() and not p.is_symlink():
                    results.append(self.copy_file(p, dest, lib, "library-logs"))
        return results

    def collect_kiro(self) -> list[dict]:
        if not self.source_enabled("kiro"):
            return []
        dest = self.day_bucket("kiro")
        app = self.app_support / "Kiro"
        results = self._collect_electron(
            app=app,
            dest_root=dest,
            copy_all_logs=True,
            move_telemetry=False,
            move_sentry_crashpad=False,
            process_monitor=False,
        )
        gs = app / "User" / "globalStorage"
        if gs.is_dir():
            for p in gs.rglob("telemetryCache"):
                if p.is_file():
                    results.append(self.copy_file(p, dest, app, "telemetryCache"))
        return results

    def collect_codex(self) -> list[dict]:
        if not self.source_enabled("codex"):
            return []
        dest = self.day_bucket("codex")
        root = self.home / ".codex"
        results: list[dict] = []
        db = root / "logs_2.sqlite"
        if db.is_file():
            results.append(self.copy_sqlite(db, dest, "sqlite"))
        log_dir = root / "log"
        for p in self._walk_files(log_dir):
            results.append(self.copy_file(p, dest, root, "log"))
        return results

    def collect_claude(self) -> list[dict]:
        if not self.source_enabled("claude"):
            return []
        dest = self.day_bucket("claude")
        root = self.home / ".claude"
        results: list[dict] = []
        debug = root / "debug"
        for p in self._walk_files(debug):
            results.append(self.copy_file(p, dest, root, "debug"))
        daemon = root / "daemon.log"
        if daemon.is_file():
            results.append(self.copy_file(daemon, dest, root, "daemon"))
        return results

    def collect_ollama(self) -> list[dict]:
        if not self.source_enabled("ollama"):
            return []
        dest = self.day_bucket("ollama")
        results: list[dict] = []
        for p in (
            Path("/opt/homebrew/var/log/ollama.log"),
            Path("/usr/local/var/log/ollama.log"),
        ):
            if p.is_file():
                results.append(self.copy_file(p, dest, p.parent, "brew"))
        return results

    def prune_custody(self) -> int:
        if self.retention_days <= 0 or not self.custody.is_dir():
            return 0
        cutoff = datetime.now(timezone.utc).date() - timedelta(days=self.retention_days)
        removed = 0
        for source_dir in self.custody.iterdir():
            if not source_dir.is_dir() or source_dir.name.startswith("."):
                continue
            if source_dir.name in {"receipts"}:
                continue
            for child in source_dir.iterdir():
                if not child.is_dir():
                    continue
                try:
                    day = datetime.strptime(child.name, "%Y%m%d").date()
                except ValueError:
                    continue
                if day < cutoff:
                    shutil.rmtree(child, ignore_errors=True)
                    removed += 1
        return removed

    def write_state(self, payload: dict) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(payload, indent=2, default=str))
        self._chmod_file(self.state_path)
        self._ensure_operator_folder()

    def write_receipt(self, payload: dict) -> Path:
        self.receipts_dir.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(self.receipts_dir, 0o700)
        except OSError:
            pass
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        compact = {k: payload[k] for k in payload if k not in {"ok_sample", "skip_sample"}}
        path = self.receipts_dir / f"{stamp}.json"
        path.write_text(json.dumps(compact, indent=2, default=str))
        self._chmod_file(path)
        return path

    def status(self) -> dict:
        last: dict = {}
        if self.state_path.is_file():
            try:
                last = json.loads(self.state_path.read_text())
            except (OSError, json.JSONDecodeError):
                last = {}
        at = last.get("at")
        next_at = None
        if at:
            try:
                parsed = datetime.fromisoformat(str(at))
                next_at = (parsed + timedelta(seconds=self.interval_s)).isoformat()
            except ValueError:
                next_at = None
        return {
            "schema": "sky.sovereign.snatcher-status/v1",
            "product": PRODUCT,
            "custody": str(self.custody),
            "operator": str(self.operator),
            "interval_s": self.interval_s,
            "retention_days": self.retention_days,
            "last_tick": at,
            "next_tick_est": next_at,
            "per_source": last.get("per_source"),
            "bytes": last.get("bytes"),
            "moved": last.get("moved"),
            "copied": last.get("copied"),
            "skipped": last.get("skipped"),
            "process_has_no_network_client": module_has_no_network_client(),
        }

    def self_check(self) -> dict:
        self.ensure_tree()
        runtime = (self.sovereign / "runtime").resolve()
        no_net = module_has_no_network_client()
        checks = {
            "policy_present": self.policy_path.is_file(),
            "custody_under_runtime": str(self.custody).startswith(str(runtime)),
            "custody_writable": os.access(self.custody, os.W_OK),
            "operator_dir": self.operator.is_dir(),
            "state_dir_ok": self.state_path.parent.is_dir(),
            "interval_s": self.interval_s,
            "interval_meets_product_floor": self.interval_s >= PRODUCT_INTERVAL_FLOOR,
            "retention_days": self.retention_days,
            "launchd_label": self.launchd_label,
            "process_has_no_network_client": no_net,
            "disk_budget_ok": self.disk_budget_ok(),
            "min_free_bytes": self.min_free_bytes,
            "sources": {
                "cursor": (self.app_support / "Cursor").is_dir(),
                "antigravity": (self.app_support / "Antigravity").is_dir(),
                "kiro": (self.app_support / "Kiro").is_dir(),
                "codex": (self.home / ".codex").is_dir(),
                "claude": (self.home / ".claude").is_dir(),
                "ollama": Path("/opt/homebrew/var/log/ollama.log").is_file()
                or Path("/usr/local/var/log/ollama.log").is_file(),
            },
            "sources_enabled": {
                name: self.source_enabled(name)
                for name in ("cursor", "antigravity", "kiro", "codex", "claude", "ollama")
            },
            "symlink_cursor_home": (self.home / ".cursor").is_symlink(),
        }
        checks["ok"] = all(
            [
                checks["custody_under_runtime"],
                checks["custody_writable"],
                checks["state_dir_ok"],
                checks["interval_meets_product_floor"],
                checks["retention_days"] >= 1,
                bool(checks["launchd_label"]),
                checks["process_has_no_network_client"],
            ]
        )
        checks["policy_schema"] = self.policy.get("schema")
        checks["product"] = PRODUCT
        return checks

    def _empty_per_source(self) -> dict:
        return {
            name: {"ok": 0, "unchanged": 0, "skipped": 0, "bytes": 0, "disabled": not self.source_enabled(name)}
            for name in ("cursor", "antigravity", "kiro", "codex", "claude", "ollama")
        }

    def tick(self) -> dict:
        self.ensure_tree()
        if not self.disk_budget_ok():
            report = {
                "schema": "sky.sovereign.snatcher/v1",
                "product": PRODUCT,
                "at": datetime.now(timezone.utc).isoformat(),
                "custody": str(self.custody),
                "operator": str(self.operator),
                "moved": 0,
                "copied": 0,
                "unchanged": 0,
                "skipped": 0,
                "bytes": 0,
                "skipped_reason": "disk_budget",
                "min_free_bytes": self.min_free_bytes,
                "per_source": self._empty_per_source(),
                "interval_s": self.interval_s,
                "retention_days": self.retention_days,
                "process_has_no_network_client": True,
            }
            self.write_state(report)
            report["receipt"] = str(self.write_receipt(report))
            return report
        collectors = {
            "cursor": self.collect_cursor,
            "antigravity": self.collect_antigravity,
            "kiro": self.collect_kiro,
            "codex": self.collect_codex,
            "claude": self.collect_claude,
            "ollama": self.collect_ollama,
        }
        by_source = {name: fn() for name, fn in collectors.items()}
        moved: list[dict] = []
        for rows in by_source.values():
            moved.extend(rows)
        ok = [m for m in moved if m.get("ok")]
        fail = [m for m in moved if not m.get("ok")]
        copied = [m for m in ok if m.get("action") in {"copy", "sqlite-backup"} and not m.get("unchanged")]
        moved_ok = [m for m in ok if m.get("action") == "move"]
        unchanged = [m for m in ok if m.get("unchanged")]
        pruned = self.prune_custody()
        per_source = {}
        for name, rows in by_source.items():
            src_ok = [m for m in rows if m.get("ok") and not m.get("unchanged")]
            per_source[name] = {
                "ok": len(src_ok),
                "unchanged": sum(1 for m in rows if m.get("unchanged")),
                "skipped": sum(1 for m in rows if not m.get("ok")),
                "bytes": sum(m.get("bytes") or 0 for m in src_ok),
                "disabled": not self.source_enabled(name),
            }
        report = {
            "schema": "sky.sovereign.snatcher/v1",
            "product": PRODUCT,
            "at": datetime.now(timezone.utc).isoformat(),
            "custody": str(self.custody),
            "operator": str(self.operator),
            "moved": len(moved_ok),
            "copied": len(copied),
            "unchanged": len(unchanged),
            "skipped": len(fail),
            "bytes": sum(m.get("bytes") or 0 for m in ok),
            "deduped": sum(1 for m in ok if m.get("dedup_deleted_vendor")),
            "pruned_day_buckets": pruned,
            "policy": str(self.policy_path) if self.policy_path.is_file() else None,
            "interval_s": self.interval_s,
            "retention_days": self.retention_days,
            "process_has_no_network_client": True,
            "per_source": per_source,
            "ok_sample": ok[:20],
            "skip_sample": fail[:10],
            "harden": {"policy_schema": self.policy.get("schema"), "keepalive_expected": True},
        }
        self.write_state(report)
        report["receipt"] = str(self.write_receipt(report))
        return report


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--once", action="store_true", help="single tick then exit")
    ap.add_argument("--self-check", action="store_true", help="print harden self-check JSON")
    ap.add_argument("--status", action="store_true", help="print last tick and next interval")
    ap.add_argument("--interval", type=int, default=None)
    args = ap.parse_args()
    snatcher = Snatcher()
    snatcher.ensure_tree()
    if args.self_check:
        check = snatcher.self_check()
        print(json.dumps(check, indent=2, default=str))
        return 0 if check["ok"] else 2
    if args.status:
        print(json.dumps(snatcher.status(), indent=2, default=str))
        return 0
    interval = args.interval if args.interval is not None else snatcher.interval_s
    if args.once:
        print(json.dumps(snatcher.tick(), indent=2, default=str))
        return 0
    print(
        json.dumps(
            {
                "custodian": "sovereign-snatcher",
                "product": PRODUCT,
                "interval_s": interval,
                "custody": str(snatcher.custody),
                "operator": str(snatcher.operator),
                "retention_days": snatcher.retention_days,
                "process_has_no_network_client": True,
            }
        ),
        flush=True,
    )
    while True:
        try:
            r = snatcher.tick()
            print(
                json.dumps(
                    {
                        "at": r["at"],
                        "moved": r["moved"],
                        "copied": r["copied"],
                        "unchanged": r["unchanged"],
                        "bytes": r["bytes"],
                        "skipped": r["skipped"],
                        "skipped_reason": r.get("skipped_reason"),
                    }
                ),
                flush=True,
            )
        except Exception as e:
            print(json.dumps({"error": f"{type(e).__name__}: {e}"}), flush=True)
        time.sleep(max(15, interval))


if __name__ == "__main__":
    raise SystemExit(main())
