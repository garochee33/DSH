#!/usr/bin/env bash
# Validate DOME-HUB secret posture for the selected provider mode.
# Modes:
#   local  -> no cloud keys required
#   mixed  -> Anthropic key required (cloud fallback path)
#   claude -> Anthropic key required (all agents on Claude)
set -euo pipefail

DOME_ROOT="${DOME_ROOT:-$HOME/DOME-HUB}"
MODE="${1:-}"
if [[ -z "$MODE" ]]; then
  MODE="$(awk -F= '$1=="DOME_PROVIDER"{print $2}' "$DOME_ROOT/.env" 2>/dev/null || true)"
fi
MODE="${MODE:-mixed}"

exists_keychain() {
  local service="$1"
  security find-generic-password -s "$service" >/dev/null 2>&1
}

print_fix() {
  local service="$1"
  local key="${service#dome/}"
  cat <<EOF
  fix:
    security add-generic-password -a "\$USER" -s "$service" -w '<VALUE>' -U
EOF
}

echo "DOME-HUB secrets doctor"
echo "root: $DOME_ROOT"
echo "mode: $MODE"
echo

missing=0

check_optional() {
  local service="$1"
  if exists_keychain "$service"; then
    echo "  [ok] optional: $service"
  else
    echo "  [--] optional: $service (not set)"
  fi
}

check_required() {
  local service="$1"
  if exists_keychain "$service"; then
    echo "  [ok] required: $service"
  else
    echo "  [!!] required: $service (missing)"
    print_fix "$service"
    missing=$((missing + 1))
  fi
}

# Always required for Trinity service-secret auth path.
check_required "dome/HUB_API_SECRET"

case "$MODE" in
  local)
    echo "  [ok] local mode selected: cloud provider keys not required"
    ;;
  mixed|claude)
    check_required "dome/ANTHROPIC_API_KEY"
    ;;
  *)
    echo "  [!!] unknown mode '$MODE' (expected: local|mixed|claude)"
    echo "  fix:"
    echo "    set DOME_PROVIDER in .env to one of: local, mixed, claude"
    missing=$((missing + 1))
    ;;
esac

# Optional integrations
check_optional "dome/GITHUB_PERSONAL_ACCESS_TOKEN"
check_optional "dome/TRINITY_JWT"
check_optional "dome/ELEVENLABS_API_KEY"

echo
if [[ "$missing" -eq 0 ]]; then
  echo "✅ secrets-doctor: healthy"
else
  echo "❌ secrets-doctor: $missing required item(s) missing"
  exit 2
fi
