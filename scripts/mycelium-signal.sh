#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════════════
# DOME-HUB MYCELIUM SIGNAL — Production-grade Trinity mesh peer
#
# Pairs with spore.sh v3.1: spore still emits ~/.trinity-spore/mycelium-mesh.sh for baseline
# heartbeats; this script is the hardened replacement (HMAC, retries, DOME_ROOT .env).
#
# Hardening over the spore-generated script:
#   - HMAC-SHA256 auth for /api/mesh/peer/* (Method 1, most secure)
#   - Bearer sporeToken auth for /api/compute/* + /api/ssii/*
#   - Retry with exponential backoff on 5xx / network errors
#   - Rate-limit awareness (parses Retry-After, sleeps appropriately)
#   - Robust JSON parsing via python3 (not brittle grep)
#   - SIGTERM / SIGINT graceful shutdown
#   - Idempotent: refuses to start if another instance is already running
#   - Structured timestamped logs with severity
#
# Auth secrets:
#   sporeToken  — for compute/ssii calls (rotates with spore)
#   HUB_API_SECRET — shared with trinity-consortium MESH_PEER_SECRET (HMAC key)
#
# Paths:
#   DOME_ROOT — optional; defaults to parent of this script (repo root). Used for `.env` (HUB_API_SECRET).
# Lifecycle:
#   - launchd-managed via ~/Library/LaunchAgents/com.dome.mycelium-signal.plist
#   - Auto-restart on crash (KeepAlive=true)
#   - Logs rotate at ~10 MB to ~/.trinity-spore/logs/
# ══════════════════════════════════════════════════════════════════════════════
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOME_ROOT="${DOME_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"

SPORE_DIR="${HOME}/.trinity-spore"
CONFIG="${SPORE_DIR}/config.json"
DOME_ENV="${DOME_ROOT}/.env"
LOG_DIR="${SPORE_DIR}/logs"
LOG_FILE="${LOG_DIR}/mycelium-signal.log"
PID_FILE="${SPORE_DIR}/mycelium-mesh.pid"
SPORE_DB="${SPORE_DIR}/mempalace.db"
MERKLE_DIR="${SPORE_DIR}/fractal-memory/merkle"
MANIFEST="${MERKLE_DIR}/manifest.json"
MESH_DIR="${SPORE_DIR}/mesh"

mkdir -p "$LOG_DIR" "$MERKLE_DIR" "$MESH_DIR"

# ── Logging ─────────────────────────────────────────────────────────────────
LOG_MAX_BYTES=$((10 * 1024 * 1024))  # 10 MB

log() {
  local level="${1:-INFO}"; shift
  local ts; ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf '[%s] [%s] %s\n' "$ts" "$level" "$*" | tee -a "$LOG_FILE" >&2
}

rotate_log_if_needed() {
  if [[ -f "$LOG_FILE" ]]; then
    local size=0
    if [[ "$(uname -s)" == "Darwin" ]]; then
      size=$(wc -c < "$LOG_FILE" 2>/dev/null || echo 0)
    else
      size=$(stat -c%s "$LOG_FILE" 2>/dev/null || echo 0)
    fi
    if (( size > LOG_MAX_BYTES )); then
      mv "$LOG_FILE" "${LOG_FILE}.$(date -u +%Y%m%dT%H%M%SZ)"
      : > "$LOG_FILE"
      log INFO "log rotated; previous logs kept under $LOG_DIR"
    fi
  fi
}

# ── Config parsing (robust) ─────────────────────────────────────────────────
require_config() {
  [[ -f "$CONFIG" ]] || { log FATAL "config not found at $CONFIG — run spore.sh first"; exit 1; }
}

parse_json() {
  # parse_json <key.path>  e.g.  parse_json e8.rootIndex
  python3 -c "
import json, sys
d = json.load(open('$CONFIG'))
v = d
for k in '$1'.split('.'):
    v = v[k]
print(v)
" 2>/dev/null
}

read_dotenv() {
  # Read a key from DOME-HUB .env (lines like KEY=value)
  [[ -f "$DOME_ENV" ]] || return 1
  local key="$1"
  awk -F= -v k="$key" '$1==k {sub(/^[^=]*=/,""); print; exit}' "$DOME_ENV"
}

require_config

API_BASE="$(parse_json apiBase)"
SPORE_TOKEN="$(parse_json sporeToken)"
NODE_ID="$(parse_json nodeId)"
E8_ROOT="$(parse_json e8.rootIndex)"
USER_ID="$(parse_json userId)"

if [[ -z "$API_BASE" || -z "$SPORE_TOKEN" || -z "$NODE_ID" || -z "$E8_ROOT" ]]; then
  log FATAL "config parse failed (api=$API_BASE node=$NODE_ID e8=$E8_ROOT token=${SPORE_TOKEN:0:20}…)"
  exit 1
fi

HUB_API_SECRET="$(read_dotenv HUB_API_SECRET || true)"
if [[ -z "$HUB_API_SECRET" ]]; then
  log WARN "HUB_API_SECRET not in ${DOME_ENV} — mesh-peer HMAC auth will fail (compute/ssii endpoints still work)"
fi

PEER_ID="$(cat "${MESH_DIR}/peer-id.txt" 2>/dev/null || echo "")"
[[ -z "$PEER_ID" ]] && log WARN "no peer-id file at ${MESH_DIR}/peer-id.txt — mesh peer heartbeats will be skipped"

# ── Tunables ────────────────────────────────────────────────────────────────
HEARTBEAT_INTERVAL="${MYCELIUM_HEARTBEAT_INTERVAL:-60}"
SYNC_INTERVAL="${MYCELIUM_SYNC_INTERVAL:-300}"
MESH_HEARTBEAT_INTERVAL="${MYCELIUM_MESH_HEARTBEAT_INTERVAL:-120}"
PHEROMONE_STRENGTH="${MYCELIUM_PHEROMONE_STRENGTH:-1.0}"
HTTP_TIMEOUT_S="${MYCELIUM_HTTP_TIMEOUT:-10}"
MAX_RETRIES="${MYCELIUM_MAX_RETRIES:-3}"
BACKOFF_BASE_S="${MYCELIUM_BACKOFF_BASE:-2}"

# ── Idempotency ─────────────────────────────────────────────────────────────
SELF_PID=$$
if [[ -f "$PID_FILE" ]]; then
  EXISTING_PID="$(cat "$PID_FILE" 2>/dev/null)"
  if [[ -n "$EXISTING_PID" && "$EXISTING_PID" != "$SELF_PID" ]] && kill -0 "$EXISTING_PID" 2>/dev/null; then
    log FATAL "another mycelium signal already running (pid=$EXISTING_PID); refusing to double-start"
    exit 1
  fi
fi
echo "$SELF_PID" > "$PID_FILE"

# ── Graceful shutdown ───────────────────────────────────────────────────────
shutdown_signal() {
  log INFO "shutdown requested — exiting cleanly"
  rm -f "$PID_FILE"
  exit 0
}
trap shutdown_signal SIGTERM SIGINT

# ── HMAC-SHA256 (for mesh-peer endpoints) ───────────────────────────────────
hmac_sha256() {
  # hmac_sha256 <secret> <payload>  →  hex digest on stdout
  # MUST use sha256 to match server-side verifyMeshHmac() in mesh-peer.service.ts
  printf '%s' "$2" | openssl dgst -sha256 -hmac "$1" -hex | awk '{print $NF}'
}

# ── HTTP with retry + backoff ───────────────────────────────────────────────
# Args: <method> <url> <auth_header_string> <body_string>
# Echoes: <http_code>\n<body>
http_call() {
  local method="$1" url="$2" body="${3:-}"
  shift 3 || true
  local extra_headers=("$@")

  local attempt=0 code body_file resp_code retry_after
  body_file="$(mktemp)"
  while (( attempt < MAX_RETRIES )); do
    attempt=$(( attempt + 1 ))
    local curl_args=(
      -sS -X "$method"
      -o "$body_file"
      -w '%{http_code}'
      --max-time "$HTTP_TIMEOUT_S"
    )
    for h in "${extra_headers[@]}"; do curl_args+=(-H "$h"); done
    if [[ -n "$body" ]]; then
      curl_args+=(-H "Content-Type: application/json" --data "$body")
    fi
    code="$(curl "${curl_args[@]}" "$url" 2>/dev/null || echo 000)"
    if [[ "$code" =~ ^2[0-9]{2}$ ]]; then
      cat "$body_file"; rm -f "$body_file"
      printf '\n%s\n' "$code"
      return 0
    fi
    if [[ "$code" == "429" ]]; then
      retry_after="$(grep -oE '"retryAfter":[0-9]+' "$body_file" | head -1 | cut -d: -f2 || true)"
      retry_after="${retry_after:-30}"
      log WARN "rate limited on $url — sleeping ${retry_after}s"
      sleep "$retry_after"
      continue
    fi
    # 4xx (other than 429): no retry, return
    if [[ "$code" =~ ^4[0-9]{2}$ ]]; then
      cat "$body_file"; rm -f "$body_file"
      printf '\n%s\n' "$code"
      return 0
    fi
    # 5xx or network error: exponential backoff
    local delay=$(( BACKOFF_BASE_S ** attempt ))
    log WARN "http $code on $url — retry ${attempt}/${MAX_RETRIES} after ${delay}s"
    sleep "$delay"
  done
  cat "$body_file"; rm -f "$body_file"
  printf '\n%s\n' "$code"
  return 1
}

# ── Heartbeats ──────────────────────────────────────────────────────────────
heartbeat_compute() {
  local out code
  out="$(http_call POST "${API_BASE}/api/compute/nodes/${NODE_ID}/heartbeat" "" \
    "Authorization: Bearer ${SPORE_TOKEN}")"
  code="${out##*$'\n'}"
  if [[ "$code" =~ ^2 ]]; then
    log INFO "♡ compute heartbeat ok"
  elif [[ "$code" == "401" ]]; then
    : # Expected for sovereign-local nodes (JWT required, HMAC mesh is the correct path)
  else
    log WARN "♡ compute heartbeat failed (status=$code)"
  fi
}

heartbeat_mesh_peer() {
  [[ -z "$PEER_ID" || -z "$HUB_API_SECRET" ]] && return 0
  local ts payload sig out code freq_pulse
  ts="$(date +%s)000"
  payload="${PEER_ID}:${ts}"
  sig="$(hmac_sha256 "$HUB_API_SECRET" "$payload")"

  # Compute E8 frequency harmonic pulse for node synchronization
  freq_pulse="$(python3 "${DOME_ROOT}/scripts/frequency-pulse.py" 2>/dev/null || echo '{}')"

  # Check if GOD_MODE brain optimization is active
  local god_mode_active="false"
  [[ -f "${DOME_ROOT}/.god-mode-active" ]] && god_mode_active="true"

  out="$(http_call POST "${API_BASE}/api/mesh/peer/heartbeat" \
    "{\"peerId\":\"${PEER_ID}\",\"pulse\":${freq_pulse},\"godMode\":${god_mode_active},\"brainOptimization\":\"v3-2026-05-20\"}" \
    "X-Mesh-Peer-Id: ${PEER_ID}" \
    "X-Mesh-Timestamp: ${ts}" \
    "X-Mesh-Signature: ${sig}")"
  code="${out##*$'\n'}"
  if [[ "$code" =~ ^2 ]]; then
    log INFO "⬡ mesh peer heartbeat ok (freq=$(echo "$freq_pulse" | python3 -c "import sys,json;d=json.load(sys.stdin);print(f'{d.get(\"nodeFreqHz\",0):.1f}Hz')" 2>/dev/null || echo '?'))"
  else
    log WARN "⬡ mesh peer heartbeat failed (status=$code)"
  fi
}

deposit_pheromone() {
  http_call POST "${API_BASE}/api/ssii/state" \
    "{\"action\":\"deposit\",\"rootIndex\":${E8_ROOT},\"strength\":${PHEROMONE_STRENGTH}}" \
    "Authorization: Bearer ${SPORE_TOKEN}" >/dev/null 2>&1 || true
}

sync_memories() {
  command -v sqlite3 >/dev/null 2>&1 || return 0
  [[ -f "$SPORE_DB" ]] || return 0
  local UNSYNCED COUNT=0 mem_id content tags RESP E8_IDX HRR
  UNSYNCED="$(sqlite3 "$SPORE_DB" \
    "SELECT id, content, tags FROM mempalace_memories WHERE synced_at IS NULL LIMIT 10;" 2>/dev/null || true)"
  [[ -z "$UNSYNCED" ]] && return 0
  while IFS='|' read -r mem_id content tags; do
    [[ -z "$mem_id" ]] && continue
    local body
    body="$(python3 -c "import json,sys; print(json.dumps({'memoryId': sys.argv[1], 'content': sys.argv[2], 'userId': sys.argv[3], 'e8RootIndex': int(sys.argv[4])}))" \
      "$mem_id" "$content" "$USER_ID" "$E8_ROOT")"
    RESP="$(http_call POST "${API_BASE}/api/ssii/ingest" "$body" \
      "Authorization: Bearer ${SPORE_TOKEN}" 2>/dev/null || true)"
    if [[ -n "$RESP" ]]; then
      E8_IDX="$(echo "$RESP" | grep -oE '"e8RootIndex":[0-9]+' | cut -d: -f2 | head -1 || echo "$E8_ROOT")"
      HRR="$(echo "$RESP" | grep -oE '"hrrSignature":"[^"]*"' | cut -d'"' -f4 || echo "")"
      # Sanitize server-returned values to prevent SQL injection
      E8_IDX="$(echo "$E8_IDX" | tr -cd '0-9')"
      HRR="$(echo "$HRR" | tr -cd 'a-zA-Z0-9_-')"
      [[ -z "$E8_IDX" ]] && E8_IDX="$E8_ROOT"
      sqlite3 "$SPORE_DB" \
        "UPDATE mempalace_memories SET e8_root_index=${E8_IDX:-$E8_ROOT}, hrr_signature='${HRR}', synced_at=datetime('now') WHERE id='${mem_id}';" 2>/dev/null || true
      COUNT=$(( COUNT + 1 ))
    fi
  done <<< "$UNSYNCED"
  (( COUNT > 0 )) && log INFO "⟳ synced ${COUNT} memories → Trinity SSII (E8 root #${E8_ROOT})"
}

# ── Main loop ───────────────────────────────────────────────────────────────
log INFO "🌱 Mycelium Signal v3.1-prod starting (node=${NODE_ID}, E8 root=${E8_ROOT}, peer=${PEER_ID:-none})"

LAST_SYNC=0
LAST_MESH_HB=0

while true; do
  rotate_log_if_needed
  heartbeat_compute

  NOW="$(date +%s)"
  if (( NOW - LAST_SYNC >= SYNC_INTERVAL )); then
    sync_memories
    deposit_pheromone
    LAST_SYNC=$NOW
  fi
  if (( NOW - LAST_MESH_HB >= MESH_HEARTBEAT_INTERVAL )); then
    heartbeat_mesh_peer
    LAST_MESH_HB=$NOW
  fi

  # Vault pulse — append one line per heartbeat to today's daily note.
  # Guarded so a missing/non-exec script never blocks the signal.
  [[ -x "${DOME_ROOT}/scripts/mycelium-vault-pulse.sh" ]] && \
    "${DOME_ROOT}/scripts/mycelium-vault-pulse.sh" >/dev/null 2>&1 || true

  sleep "$HEARTBEAT_INTERVAL"
done
