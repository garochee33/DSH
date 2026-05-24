#!/usr/bin/env bash
# Pull API keys from Trinity Consortium settings DB into local env.
# Run before starting DOME API, or source in shell profile.
# Single source of truth: the consortium's encrypted settings store.

CONSORTIUM_URL="${TRINITY_CONSORTIUM_URL:-http://localhost:5055}"
ENDPOINT="$CONSORTIUM_URL/api/settings/export/dotenv?profile=local"

echo "[key-sync] Pulling keys from $CONSORTIUM_URL..."

RESPONSE=$(curl -sf -H "X-Confirm-Secret-Export: true" "$ENDPOINT" 2>/dev/null)

if [ $? -ne 0 ] || [ -z "$RESPONSE" ]; then
  echo "[key-sync] ⚠ Consortium not reachable — using local .env fallback"
  exit 0
fi

# Extract key values and export them
for KEY in ANTHROPIC_API_KEY OPENAI_API_KEY AI_INTEGRATIONS_OPENROUTER_API_KEY; do
  VAL=$(echo "$RESPONSE" | grep "^${KEY}=" | head -1 | cut -d= -f2-)
  if [ -n "$VAL" ]; then
    export "$KEY=$VAL"
    echo "[key-sync] ✓ $KEY synced"
  fi
done

echo "[key-sync] Done. Keys loaded from consortium vault."
