#!/usr/bin/env bash
# Install Sovereign Log Snatcher — KeepAlive gather of vendor logs into runtime custody.
set -euo pipefail
BUNDLE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="${SKY_HUB_ROOT:-$BUNDLE_ROOT}"
if [[ "$ROOT" != "$BUNDLE_ROOT" ]]; then
  mkdir -p "$ROOT/scripts" "$ROOT/config" "$ROOT/db"
  cp -f "$BUNDLE_ROOT/scripts/sovereign-snatcher.py" "$ROOT/scripts/sovereign-snatcher.py"
  cp -f "$BUNDLE_ROOT/scripts/sovereign-snatcher-harden.py" "$ROOT/scripts/sovereign-snatcher-harden.py" 2>/dev/null || true
  cp -f "$BUNDLE_ROOT/scripts/install-sovereign-snatcher.sh" "$ROOT/scripts/install-sovereign-snatcher.sh"
  if [[ -f "$BUNDLE_ROOT/config/sovereign-snatcher-policy.json" ]]; then
    cp -f "$BUNDLE_ROOT/config/sovereign-snatcher-policy.json" "$ROOT/config/sovereign-snatcher-policy.json"
    cp -f "$BUNDLE_ROOT/config/sovereign-snatcher-policy.json" "$ROOT/db/sovereign-snatcher-policy.json"
  fi
fi
SOVEREIGN_ROOT="$(cd "${SOVEREIGN_ROOT:-$ROOT/..}" && pwd -P)"
LABEL="com.skyhub.sovereign-snatcher"
OLD_LABEL="com.skyhub.cursor-log-custodian"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
CUSTODY="$SOVEREIGN_ROOT/runtime/sovereign-snatcher"
OPERATOR="$SOVEREIGN_ROOT/Sovereign Snatcher"
OLD_CURSOR="$SOVEREIGN_ROOT/runtime/agents/cursor/records/logs/cursor-app"
LOG_DIR="$CUSTODY"
mkdir -p "$HOME/Library/LaunchAgents" "$CUSTODY" "$CUSTODY/cursor" "$OPERATOR/scripts" "$OPERATOR/launchd"
chmod 700 "$SOVEREIGN_ROOT/runtime" "$CUSTODY" "$OPERATOR" 2>/dev/null || true
touch "$LOG_DIR/snatcher-stdout.log" "$LOG_DIR/snatcher-stderr.log"
chmod 600 "$LOG_DIR/snatcher-stdout.log" "$LOG_DIR/snatcher-stderr.log"

# Fold existing Cursor snatcher files into the shared custody tree.
if [[ -d "$OLD_CURSOR" && ! -L "$OLD_CURSOR" ]]; then
  mkdir -p "$CUSTODY/cursor"
  chmod 700 "$CUSTODY/cursor"
  if [[ -n "$(ls -A "$OLD_CURSOR" 2>/dev/null || true)" ]]; then
    mv "$OLD_CURSOR"/* "$CUSTODY/cursor/" 2>/dev/null || true
  fi
  rmdir "$OLD_CURSOR" 2>/dev/null || true
fi
if [[ ! -e "$OLD_CURSOR" || -L "$OLD_CURSOR" ]]; then
  mkdir -p "$(dirname "$OLD_CURSOR")"
  ln -sfn "$CUSTODY/cursor" "$OLD_CURSOR"
fi

PY="$ROOT/.venv/bin/python"
[[ -x "$PY" ]] || PY="$(command -v python3)"
SNATCHER="$ROOT/scripts/sovereign-snatcher.py"

cat >"$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array>
    <string>$PY</string>
    <string>$SNATCHER</string>
  </array>
  <key>EnvironmentVariables</key><dict>
    <key>SKY_HUB_ROOT</key><string>$ROOT</string>
    <key>SOVEREIGN_ROOT</key><string>$SOVEREIGN_ROOT</string>
    <key>SOVEREIGN_SNATCHER_INTERVAL</key><string>900</string>
    <key>SOVEREIGN_SNATCHER_RETENTION_DAYS</key><string>30</string>
    <key>PATH</key><string>$ROOT/.venv/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
    <key>DISABLE_TELEMETRY</key><string>1</string>
    <key>DO_NOT_TRACK</key><string>1</string>
    <key>PYTHONUNBUFFERED</key><string>1</string>
  </dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ProcessType</key><string>Background</string>
  <key>LowPriorityIO</key><true/>
  <key>Umask</key><integer>63</integer>
  <key>StandardOutPath</key><string>$LOG_DIR/snatcher-stdout.log</string>
  <key>StandardErrorPath</key><string>$LOG_DIR/snatcher-stderr.log</string>
  <key>WorkingDirectory</key><string>$ROOT</string>
</dict></plist>
EOF
chmod 600 "$PLIST"
cp -f "$PLIST" "$OPERATOR/launchd/$LABEL.plist"
chmod 600 "$OPERATOR/launchd/$LABEL.plist"
plutil -lint "$PLIST"

ln -sfn "$SNATCHER" "$OPERATOR/scripts/sovereign-snatcher.py"
ln -sfn "$ROOT/scripts/install-sovereign-snatcher.sh" "$OPERATOR/scripts/install-sovereign-snatcher.sh"
if [[ -f "$ROOT/db/sovereign-snatcher-policy.json" ]]; then
  ln -sfn "$ROOT/db/sovereign-snatcher-policy.json" "$OPERATOR/policy.json"
else
  ln -sfn "$ROOT/config/sovereign-snatcher-policy.json" "$OPERATOR/policy.json"
fi
ln -sfn "$CUSTODY" "$OPERATOR/custody"

cat >"$OPERATOR/README.md" <<'EOF'
# Sovereign Log Snatcher

Local-only log custody for this Mac. This process has no network client.

Logs live under `runtime/sovereign-snatcher/` (mode 0700). This folder is the
operator index: policy, scripts, launchd, and a `custody` symlink.

| Bucket | What |
|--------|------|
| `cursor/` | Existing Cursor snatcher files + IDE logs (copy) + telemetry (move) |
| `antigravity/` | Antigravity logs + Crashpad |
| `kiro/` | Kiro / Amazon Q logs + telemetryCache (copy) |
| `codex/` | `logs_2.sqlite` backup (vendor file stays) |
| `claude/` | `debug/` + `daemon.log` (copy) |
| `ollama/` | Homebrew `ollama.log` (copy) |

KeepAlive agent: `com.skyhub.sovereign-snatcher` (every 15 minutes, 30-day retention).
This process has no network client. It does not prove OS-level zero egress.
Chat history is a different store — this product does not make chat smarter.
EOF
chmod 600 "$OPERATOR/README.md"

uid="$(id -u)"
launchctl bootout "gui/$uid/$OLD_LABEL" 2>/dev/null || true
launchctl bootout "gui/$uid/$LABEL" 2>/dev/null || true

export SKY_HUB_ROOT="$ROOT"
export SOVEREIGN_ROOT="$SOVEREIGN_ROOT"
if [[ "${SOVEREIGN_SNATCHER_SKIP_ONCE:-}" != "1" ]]; then
  echo "first gather (may take several minutes; ~1 GB on a full node)..."
  "$PY" "$SNATCHER" --once
else
  echo "skipped first --once (SOVEREIGN_SNATCHER_SKIP_ONCE=1)"
fi

launchctl bootstrap "gui/$uid" "$PLIST"
launchctl enable "gui/$uid/$LABEL" 2>/dev/null || true
launchctl kickstart -k "gui/$uid/$LABEL" 2>/dev/null || launchctl kickstart "gui/$uid/$LABEL"

echo
echo "installed Sovereign Log Snatcher ($LABEL)"
echo "operator: $OPERATOR"
echo "custody:  $CUSTODY"
echo "state:    $CUSTODY/state.json"
