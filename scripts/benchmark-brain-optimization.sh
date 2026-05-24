#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# BRAIN OPTIMIZATION BENCHMARK — Before/After Production Measurement
# ═══════════════════════════════════════════════════════════════════════════════
# Hits real production endpoints and captures latency, status, and quality metrics.
# Run BEFORE deploy (baseline) and AFTER deploy (optimized) then compare.
#
# Usage:
#   ./scripts/benchmark-brain-optimization.sh baseline
#   ./scripts/benchmark-brain-optimization.sh optimized
#   ./scripts/benchmark-brain-optimization.sh compare
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

PROD_URL="${TRINITY_MESH_API_URL:-https://trinity-consortium.com}"
RESULTS_DIR="${HOME}/DOME-HUB/logs/benchmarks"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
REPS=5  # Number of repetitions per endpoint

# Auth — use HUB_API_SECRET for HMAC or a JWT token
source "${HOME}/DOME-HUB/.env" 2>/dev/null || true
AUTH_HEADER=""
if [[ -n "${TRINITY_JWT:-}" ]]; then
  AUTH_HEADER="Authorization: Bearer ${TRINITY_JWT}"
elif [[ -n "${HUB_API_SECRET:-}" ]]; then
  # Generate HMAC signature for mesh endpoints
  AUTH_HEADER="X-Hub-Secret: ${HUB_API_SECRET}"
fi

# ─── Helpers ──────────────────────────────────────────────────────────────────

mkdir -p "$RESULTS_DIR"

measure() {
  local name="$1" method="$2" url="$3" body="${4:-}"
  local times=() statuses=() sizes=()

  for i in $(seq 1 $REPS); do
    local result
    if [[ "$method" == "GET" ]]; then
      result=$(curl -s -o /tmp/bench_body -w "%{http_code} %{time_total} %{size_download}" \
        -H "Content-Type: application/json" \
        ${AUTH_HEADER:+-H "$AUTH_HEADER"} \
        "$url" 2>/dev/null)
    else
      result=$(curl -s -o /tmp/bench_body -w "%{http_code} %{time_total} %{size_download}" \
        -X POST -H "Content-Type: application/json" \
        ${AUTH_HEADER:+-H "$AUTH_HEADER"} \
        -d "$body" \
        "$url" 2>/dev/null)
    fi
    local code=$(echo "$result" | awk '{print $1}')
    local time_s=$(echo "$result" | awk '{print $2}')
    local size=$(echo "$result" | awk '{print $3}')
    local time_ms=$(echo "$time_s" | awk '{printf "%.1f", $1 * 1000}')

    times+=("$time_ms")
    statuses+=("$code")
    sizes+=("$size")
  done

  # Compute p50, p95, avg
  local sorted=($(printf '%s\n' "${times[@]}" | sort -n))
  local count=${#sorted[@]}
  local p50=${sorted[$((count/2))]}
  local p95=${sorted[$((count * 95 / 100))]}
  local avg=$(printf '%s\n' "${times[@]}" | awk '{s+=$1} END {printf "%.1f", s/NR}')
  local last_status=${statuses[-1]}
  local last_size=${sizes[-1]}

  echo "${name}|${last_status}|${avg}|${p50}|${p95}|${last_size}"
}

# ─── Benchmark Suite ──────────────────────────────────────────────────────────

run_benchmark() {
  local label="$1"
  local outfile="${RESULTS_DIR}/benchmark-${label}-${TIMESTAMP}.csv"

  echo "═══════════════════════════════════════════════════════════════"
  echo "  BRAIN OPTIMIZATION BENCHMARK — ${label^^}"
  echo "  Target: ${PROD_URL}"
  echo "  Reps: ${REPS} per endpoint"
  echo "  Time: $(date)"
  echo "═══════════════════════════════════════════════════════════════"
  echo ""

  # CSV header
  echo "endpoint|status|avg_ms|p50_ms|p95_ms|bytes" > "$outfile"

  # 1. Health check (baseline latency)
  echo -n "  [1/10] Health check... "
  local r=$(measure "health" GET "${PROD_URL}/api/health")
  echo "$r" >> "$outfile"; echo "$r" | awk -F'|' '{printf "%s %sms (p50=%s p95=%s)\n", $2, $3, $4, $5}'

  # 2. AMMA health
  echo -n "  [2/10] AMMA health... "
  r=$(measure "amma_health" GET "${PROD_URL}/api/amma/health")
  echo "$r" >> "$outfile"; echo "$r" | awk -F'|' '{printf "%s %sms (p50=%s p95=%s)\n", $2, $3, $4, $5}'

  # 3. Brain status (neuromorphic)
  echo -n "  [3/10] Brain status... "
  r=$(measure "brain_status" GET "${PROD_URL}/api/brain/status")
  echo "$r" >> "$outfile"; echo "$r" | awk -F'|' '{printf "%s %sms (p50=%s p95=%s)\n", $2, $3, $4, $5}'

  # 4. E8 compute status
  echo -n "  [4/10] E8 compute... "
  r=$(measure "e8_compute" GET "${PROD_URL}/api/e8-compute/status")
  echo "$r" >> "$outfile"; echo "$r" | awk -F'|' '{printf "%s %sms (p50=%s p95=%s)\n", $2, $3, $4, $5}'

  # 5. Fractal memory recall (quality test)
  echo -n "  [5/10] Fractal recall... "
  r=$(measure "fractal_recall" POST "${PROD_URL}/api/vault/fractal-memory/recall" \
    '{"query":"E8 lattice coherence optimization","limit":5}')
  echo "$r" >> "$outfile"; echo "$r" | awk -F'|' '{printf "%s %sms (p50=%s p95=%s) %sb\n", $2, $3, $4, $5, $6}'

  # 6. Brain recall (neuromorphic memory)
  echo -n "  [6/10] Brain recall... "
  r=$(measure "brain_recall" POST "${PROD_URL}/api/brain/recall" \
    '{"query":"system coherence and healing","limit":3}')
  echo "$r" >> "$outfile"; echo "$r" | awk -F'|' '{printf "%s %sms (p50=%s p95=%s)\n", $2, $3, $4, $5}'

  # 7. Mesh peer heartbeat latency
  echo -n "  [7/10] Mesh heartbeat... "
  r=$(measure "mesh_heartbeat" GET "${PROD_URL}/api/mesh/peer/status")
  echo "$r" >> "$outfile"; echo "$r" | awk -F'|' '{printf "%s %sms (p50=%s p95=%s)\n", $2, $3, $4, $5}'

  # 8. GOD_MODE protocols
  echo -n "  [8/10] GOD_MODE protocols... "
  r=$(measure "god_protocols" GET "${PROD_URL}/api/protocols/god-mode")
  echo "$r" >> "$outfile"; echo "$r" | awk -F'|' '{printf "%s %sms (p50=%s p95=%s)\n", $2, $3, $4, $5}'

  # 9. Holographic state
  echo -n "  [9/10] Holographic state... "
  r=$(measure "holographic" GET "${PROD_URL}/api/holographic")
  echo "$r" >> "$outfile"; echo "$r" | awk -F'|' '{printf "%s %sms (p50=%s p95=%s)\n", $2, $3, $4, $5}'

  # 10. AI agent routing (full pipeline)
  echo -n "  [10/10] Agent routing... "
  r=$(measure "agent_route" POST "${PROD_URL}/api/ai/chat" \
    '{"message":"What is the current system coherence?","agentId":"oracle"}')
  echo "$r" >> "$outfile"; echo "$r" | awk -F'|' '{printf "%s %sms (p50=%s p95=%s) %sb\n", $2, $3, $4, $5, $6}'

  echo ""
  echo "  Results saved: ${outfile}"
  echo ""

  # Print summary table
  echo "┌────────────────────┬────────┬─────────┬─────────┬─────────┬─────────┐"
  echo "│ Endpoint           │ Status │ Avg(ms) │ P50(ms) │ P95(ms) │ Bytes   │"
  echo "├────────────────────┼────────┼─────────┼─────────┼─────────┼─────────┤"
  tail -n +2 "$outfile" | while IFS='|' read -r name status avg p50 p95 bytes; do
    printf "│ %-18s │ %6s │ %7s │ %7s │ %7s │ %7s │\n" "$name" "$status" "$avg" "$p50" "$p95" "$bytes"
  done
  echo "└────────────────────┴────────┴─────────┴─────────┴─────────┴─────────┘"
}

# ─── Compare Mode ─────────────────────────────────────────────────────────────

compare_results() {
  local baseline=$(ls -t "${RESULTS_DIR}"/benchmark-baseline-*.csv 2>/dev/null | head -1)
  local optimized=$(ls -t "${RESULTS_DIR}"/benchmark-optimized-*.csv 2>/dev/null | head -1)

  if [[ -z "$baseline" || -z "$optimized" ]]; then
    echo "ERROR: Need both baseline and optimized results."
    echo "  Baseline: ${baseline:-NOT FOUND}"
    echo "  Optimized: ${optimized:-NOT FOUND}"
    exit 1
  fi

  echo "═══════════════════════════════════════════════════════════════"
  echo "  BEFORE/AFTER COMPARISON"
  echo "  Baseline:  ${baseline}"
  echo "  Optimized: ${optimized}"
  echo "═══════════════════════════════════════════════════════════════"
  echo ""
  echo "┌────────────────────┬───────────────┬───────────────┬──────────────┐"
  echo "│ Endpoint           │ Before (avg)  │ After (avg)   │ Δ Change     │"
  echo "├────────────────────┼───────────────┼───────────────┼──────────────┤"

  paste -d'@' <(tail -n +2 "$baseline") <(tail -n +2 "$optimized") | while IFS='@' read -r before after; do
    local name=$(echo "$before" | cut -d'|' -f1)
    local before_avg=$(echo "$before" | cut -d'|' -f3)
    local after_avg=$(echo "$after" | cut -d'|' -f3)
    local delta=$(echo "$before_avg $after_avg" | awk '{d=$2-$1; pct=($1>0)?(d/$1*100):0; printf "%+.1fms (%+.1f%%)", d, pct}')
    printf "│ %-18s │ %11sms │ %11sms │ %12s │\n" "$name" "$before_avg" "$after_avg" "$delta"
  done

  echo "└────────────────────┴───────────────┴───────────────┴──────────────┘"
}

# ─── Main ─────────────────────────────────────────────────────────────────────

case "${1:-help}" in
  baseline)   run_benchmark "baseline" ;;
  optimized)  run_benchmark "optimized" ;;
  compare)    compare_results ;;
  *)
    echo "Usage: $0 {baseline|optimized|compare}"
    echo "  baseline  — Run before deploying optimization"
    echo "  optimized — Run after deploying optimization"
    echo "  compare   — Show before/after delta"
    exit 1
    ;;
esac
