#!/bin/bash
# Render .env from .env.template, resolving {{keychain:SERVICE}} markers via
# the macOS Keychain (`security find-generic-password`).
# Output is mode 600, gitignored. Compatible with python-dotenv / uvicorn / any loader.
#
# Backward compatible: {{pass:dome/KEY}} markers are also resolved via pass if available,
# so the template works for either backend.

set -euo pipefail

DOME_ROOT="${DOME_ROOT:-$HOME/DSH}"
TPL="$DOME_ROOT/.env.template"
OUT="$DOME_ROOT/.env"

[ -f "$TPL" ] || { echo "error: template not found: $TPL" >&2; exit 1; }

TMP="$(mktemp "$DOME_ROOT/.env.render.XXXXXX")"
chmod 600 "$TMP"
trap 'rm -f "$TMP"' EXIT

resolved=0
missing=0
while IFS= read -r line; do
  # {{keychain:service-name}}
  while [[ "$line" =~ \{\{keychain:([^}]+)\}\} ]]; do
    svc="${BASH_REMATCH[1]}"
    if val="$(security find-generic-password -s "$svc" -w 2>/dev/null)"; then
      line="${line//\{\{keychain:$svc\}\}/$val}"
      resolved=$((resolved+1))
    else
      line="${line//\{\{keychain:$svc\}\}/}"
      missing=$((missing+1))
      echo "  warn: keychain entry '$svc' not found (left blank)" >&2
    fi
  done
  # {{pass:dome/KEY}}  (legacy, only works if pass+gpg are unlocked)
  while [[ "$line" =~ \{\{pass:([^}]+)\}\} ]]; do
    key="${BASH_REMATCH[1]}"
    if command -v pass >/dev/null 2>&1 && val="$(pass show "$key" 2>/dev/null)"; then
      line="${line//\{\{pass:$key\}\}/$val}"
      resolved=$((resolved+1))
    else
      line="${line//\{\{pass:$key\}\}/}"
      missing=$((missing+1))
      echo "  warn: pass entry '$key' not available (left blank)" >&2
    fi
  done
  printf '%s\n' "$line" >>"$TMP"
done <"$TPL"

mv "$TMP" "$OUT"
chmod 600 "$OUT"
trap - EXIT

echo "✓ rendered: $OUT  (mode 600, $resolved resolved, $missing missing)"
