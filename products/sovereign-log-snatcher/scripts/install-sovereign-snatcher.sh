#!/usr/bin/env bash
# Install Sovereign Log Snatcher — local KeepAlive gather into your custody tree.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -n "${SOVEREIGN_ROOT:-}" ]]; then
  SOVEREIGN_ROOT="$(cd "$SOVEREIGN_ROOT" && pwd -P)"
elif [[ -d "$HOME/sovereign" ]]; then
  SOVEREIGN_ROOT="$(cd "$HOME/sovereign" && pwd -P)"
else
  SOVEREIGN_ROOT="$HOME/.sovereign"
fi
LABEL="com.sovereign.log-snatcher"
LEGACY_LABELS="com.skyhub.sovereign-snatcher com.skyhub.cursor-log-custodian"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
CUSTODY="$SOVEREIGN_ROOT/runtime/sovereign-snatcher"
OPERATOR="$SOVEREIGN_ROOT/Sovereign Snatcher"
LOG_DIR="$CUSTODY"
mkdir -p "$HOME/Library/LaunchAgents" "$CUSTODY" "$CUSTODY/cursor" "$OPERATOR/scripts" "$OPERATOR/launchd"
chmod 700 "$SOVEREIGN_ROOT" "$SOVEREIGN_ROOT/runtime" "$CUSTODY" "$OPERATOR" 2>/dev/null || true
touch "$LOG_DIR/snatcher-stdout.log" "$LOG_DIR/snatcher-stderr.log"
chmod 600 "$LOG_DIR/snatcher-stdout.log" "$LOG_DIR/snatcher-stderr.log"

PY="$(command -v python3)"
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PY="$ROOT/.venv/bin/python"
elif [[ -x "$ROOT/../../.venv/bin/python" ]]; then
  PY="$ROOT/../../.venv/bin/python"
fi
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
    <key>SNATCHER_ROOT</key><string>$ROOT</string>
    <key>SOVEREIGN_ROOT</key><string>$SOVEREIGN_ROOT</string>
    <key>SOVEREIGN_SNATCHER_INTERVAL</key><string>900</string>
    <key>SOVEREIGN_SNATCHER_RETENTION_DAYS</key><string>30</string>
    <key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
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
ln -sfn "$ROOT/config/sovereign-snatcher-policy.json" "$OPERATOR/policy.json"
ln -sfn "$CUSTODY" "$OPERATOR/custody"

cat >"$OPERATOR/README.md" <<'EOF'
# Sovereign Log Snatcher

Local-only log custody for this Mac. This process has no network client.

Logs live under `runtime/sovereign-snatcher/` (mode 0700). This folder is the
operator index: policy, scripts, launchd, and a `custody` symlink.

KeepAlive agent: `com.sovereign.log-snatcher` (every 15 minutes, 30-day retention).
This process has no network client. It does not prove OS-level zero egress.
Chat history is a different store — this product does not make chat smarter.
EOF
chmod 600 "$OPERATOR/README.md"

uid="$(id -u)"
for old in $LEGACY_LABELS; do
  launchctl bootout "gui/$uid/$old" 2>/dev/null || true
done
launchctl bootout "gui/$uid/$LABEL" 2>/dev/null || true

export SNATCHER_ROOT="$ROOT"
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
