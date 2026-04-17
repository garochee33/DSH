#!/usr/bin/env bash
# Engage spore lockdown — blocks all outbound provider calls (Anthropic, OpenAI)
# Source this file: source scripts/spore-lock.sh
export SPORE_GERMINATING=1
echo "[LOCKDOWN] Spore lockdown ENGAGED — outbound AI providers blocked"
echo "           Node is air-gapped. Only local/MLX inference allowed."
echo "           Run: source scripts/spore-unlock.sh  to release after germination"
