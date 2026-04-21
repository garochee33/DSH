#!/bin/bash
# DSH — Ollama initialization
# Detects hardware tier and pulls the right local models.
# Safe to re-run: already-installed models are skipped.
set -euo pipefail

DOME_ROOT="${DOME_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

echo "==> DSH Ollama init"

if ! command -v ollama >/dev/null 2>&1; then
  echo "    ollama not installed. Install via:"
  echo "    brew install ollama"
  echo "    brew services start ollama"
  exit 1
fi

if ! pgrep -x ollama >/dev/null 2>&1; then
  echo "    ollama not running — starting service..."
  brew services start ollama 2>/dev/null || {
    echo "    failed to start ollama via brew services"
    echo "    try: ollama serve &"
    exit 1
  }
  sleep 2
fi

# ── Detect RAM tier ──────────────────────────────────────────────────────────
if [[ "$(uname)" == "Darwin" ]]; then
  RAM_GB=$(( $(sysctl -n hw.memsize) / 1024 / 1024 / 1024 ))
else
  RAM_GB=$(awk '/^MemTotal/ {printf "%d", $2/1024/1024}' /proc/meminfo)
fi

echo "    RAM detected: ${RAM_GB} GB"

# ── Pick models per tier ─────────────────────────────────────────────────────
# Tiers are conservative — leave headroom for agents + ChromaDB + editor.
MODELS=()
MODELS+=("nomic-embed-text")  # ~274MB — always useful for local embeddings

if   (( RAM_GB >= 64 )); then
  TIER="workstation"
  MODELS+=("qwen2.5-coder:32b" "llama3.1:70b" "mistral:7b")
elif (( RAM_GB >= 32 )); then
  TIER="heavy"
  MODELS+=("qwen2.5-coder:14b" "llama3.1:8b" "mistral:7b")
elif (( RAM_GB >= 18 )); then
  TIER="sovereign"
  MODELS+=("qwen2.5-coder:14b" "llama3.1:8b")
elif (( RAM_GB >= 12 )); then
  TIER="guardian"
  MODELS+=("llama3.1:8b" "phi3:medium")
elif (( RAM_GB >= 8 )); then
  TIER="scout"
  MODELS+=("llama3.1:8b")
else
  TIER="seed"
  MODELS+=("phi3:mini")
fi

echo "    Tier: $TIER"
echo "    Models to pull: ${MODELS[*]}"
echo ""

# ── Pull ─────────────────────────────────────────────────────────────────────
INSTALLED=$(ollama list 2>/dev/null | awk 'NR>1 {print $1}')

for m in "${MODELS[@]}"; do
  if echo "$INSTALLED" | grep -qxF "$m" || echo "$INSTALLED" | grep -qxF "$m:latest"; then
    echo "  ✓ $m (already installed)"
  else
    echo "  ↓ pulling $m ..."
    ollama pull "$m"
  fi
done

echo ""
echo "✅ Ollama init complete"
echo "   Default local model (DOME_LOCAL_MODEL): set in .env"
echo "   Test: ollama run ${MODELS[1]:-llama3.1:8b} 'hello'"
