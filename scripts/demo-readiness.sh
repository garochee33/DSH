#!/bin/bash
# Presentation readiness gate for DOME-HUB
# Usage:
#   bash scripts/demo-readiness.sh
#   bash scripts/demo-readiness.sh --strict

set -u

DOME_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STRICT=0

for arg in "$@"; do
  case "$arg" in
    --strict) STRICT=1 ;;
  esac
done

PASS=0
FAIL=0

ok() {
  echo "✅ $1"
  PASS=$((PASS + 1))
}

fail() {
  echo "❌ $1"
  FAIL=$((FAIL + 1))
}

run_check() {
  local label="$1"
  local cmd="$2"
  if eval "$cmd" >/tmp/dome-demo-check.out 2>&1; then
    ok "$label"
  else
    fail "$label"
    echo "---- ${label} output ----"
    sed -n '1,80p' /tmp/dome-demo-check.out
    echo "-------------------------"
  fi
}

echo ""
echo "=== DOME-HUB DEMO READINESS === $(date)"
echo "Root: $DOME_ROOT"
echo ""

cd "$DOME_ROOT" || exit 1

run_check "API required routes wired" "python3 scripts/api-smoke.py"
run_check "Python tests pass" "python3 -m pytest -q"
run_check "TypeScript typecheck clean" "pnpm -s typecheck"
run_check "TypeScript lint clean" "pnpm -s lint"
run_check "Voice error paths return client-safe responses" "python3 - <<'PY'
from fastapi.testclient import TestClient
from agents.api.server import app

client = TestClient(app)
for path in ('/voice/vad', '/voice/transcribe'):
    r = client.post(path, json={'audio_path': '/tmp/does-not-exist.wav'})
    if r.status_code != 400:
        raise SystemExit(f'{path} expected 400, got {r.status_code}')
print('voice error path checks passed')
PY"

if [ "$STRICT" -eq 1 ]; then
  run_check "Protocol check strict mode" "bash scripts/dome-check.sh --strict"
else
  run_check "Protocol check" "bash scripts/dome-check.sh"
fi

echo ""
echo "=== DEMO SUMMARY ==="
echo "✅ Passed: $PASS"
echo "❌ Failed: $FAIL"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "🟢 READY TO PRESENT"
  exit 0
fi

echo "🔴 NOT READY — resolve failures above"
exit 1
