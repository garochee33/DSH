#!/bin/bash
# DOME-HUB Daemon Watchdog
# Monitors LaunchAgents/Daemons and kills unauthorized ones
# Run: bash scripts/daemon-watch.sh (or add to cron)

LOG="$HOME/DOME-HUB/logs/daemon-watch.log"
mkdir -p "$(dirname $LOG)"

# Approved daemons (whitelist)
APPROVED=(
  "homebrew.mxcl.postgresql"
  "homebrew.mxcl.redis"
  "homebrew.mxcl.dnscrypt-proxy"
  "com.apple."
  "com.openssh."
  "org.cups."
)

is_approved() {
  local name=$1
  for pattern in "${APPROVED[@]}"; do
    [[ "$name" == *"$pattern"* ]] && return 0
  done
  return 1
}

echo "=== DOME-HUB Daemon Watchdog ===" | tee -a "$LOG"
echo "Date: $(date)" | tee -a "$LOG"
echo ""

# Check user LaunchAgents
for plist in ~/Library/LaunchAgents/*.plist; do
  name=$(basename "$plist" .plist)
  if is_approved "$name"; then
    echo "✅ $name"
  else
    echo "⚠️  UNAUTHORIZED: $name" | tee -a "$LOG"
    echo "   → Unloading..."
    launchctl unload -w "$plist" 2>/dev/null && \
      echo "   → Disabled. Requires dome-approve to re-enable." | tee -a "$LOG"
  fi
done

# Check system LaunchDaemons
for plist in /Library/LaunchDaemons/*.plist; do
  name=$(basename "$plist" .plist)
  if is_approved "$name"; then
    echo "✅ $name"
  else
    echo "⚠️  UNAUTHORIZED DAEMON: $name" | tee -a "$LOG"
  fi
done

echo ""
echo "Log: $LOG"
