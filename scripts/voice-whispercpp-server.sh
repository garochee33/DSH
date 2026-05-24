#!/usr/bin/env bash
set -euo pipefail

DOME_ROOT="${DOME_ROOT:-$HOME/DOME-HUB}"
WHISPER_CPP_DIR="${DOME_WHISPER_CPP_DIR:-$DOME_ROOT/deps/whisper.cpp}"
HOST="${DOME_WHISPER_CPP_HOST:-127.0.0.1}"
PORT="${DOME_WHISPER_CPP_PORT:-8082}"
MODEL="${DOME_WHISPER_CPP_MODEL:-$DOME_ROOT/models/asr/whisper/ggml-base.bin}"
TMP_DIR="${DOME_WHISPER_CPP_TMP_DIR:-/tmp}"
PID_FILE="$DOME_ROOT/logs/voice/whisper-server-$PORT.pid"
LOG_FILE="$DOME_ROOT/logs/voice/whisper-server-$PORT.log"
PLIST="$HOME/Library/LaunchAgents/com.dome.whispercpp.$PORT.plist"
LABEL="com.dome.whispercpp.$PORT"

server_bin="$WHISPER_CPP_DIR/build/bin/whisper-server"

is_running() {
  lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1
}

wait_until_healthy() {
  for _ in $(seq 1 90); do
    if curl -fsS "http://$HOST:$PORT/health" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  return 1
}

write_plist() {
  mkdir -p "$HOME/Library/LaunchAgents" "$DOME_ROOT/logs/voice"
  cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$LABEL</string>
  <key>WorkingDirectory</key>
  <string>$WHISPER_CPP_DIR</string>
  <key>ProgramArguments</key>
  <array>
    <string>$server_bin</string>
    <string>-m</string>
    <string>$MODEL</string>
    <string>--host</string>
    <string>$HOST</string>
    <string>--port</string>
    <string>$PORT</string>
    <string>--convert</string>
    <string>--tmp-dir</string>
    <string>$TMP_DIR</string>
    <string>-l</string>
    <string>en</string>
    <string>-nt</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
  </dict>
  <key>StandardOutPath</key>
  <string>$LOG_FILE</string>
  <key>StandardErrorPath</key>
  <string>$LOG_FILE</string>
</dict>
</plist>
PLIST
}

start() {
  if is_running; then
    echo "whisper.cpp server already running: url=http://$HOST:$PORT"
    return 0
  fi
  if [[ ! -x "$server_bin" ]]; then
    echo "missing server binary: $server_bin" >&2
    exit 1
  fi
  if [[ ! -f "$MODEL" ]]; then
    echo "missing model: $MODEL" >&2
    exit 1
  fi

  write_plist
  launchctl bootout "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true
  launchctl bootstrap "gui/$(id -u)" "$PLIST"
  launchctl kickstart -k "gui/$(id -u)/$LABEL"
  if wait_until_healthy; then
    echo "started whisper.cpp server: url=http://$HOST:$PORT"
  else
    echo "server did not become healthy; see $LOG_FILE" >&2
    exit 1
  fi
}

stop() {
  launchctl bootout "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true
  rm -f "$PID_FILE"
  echo "stopped whisper.cpp server"
}

status() {
  if is_running; then
    echo "running url=http://$HOST:$PORT"
  else
    echo "stopped"
  fi
}

case "${1:-status}" in
  start) start ;;
  stop) stop ;;
  restart) stop; start ;;
  status) status ;;
  *)
    echo "usage: $0 {start|stop|restart|status}" >&2
    exit 2
    ;;
esac
