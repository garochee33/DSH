#!/usr/bin/env bash
# Rotate local DOME-HUB secrets in macOS Keychain (personal machine).
# Does not touch git config or remote state.
set -euo pipefail

DOME_ROOT="${DOME_ROOT:-$HOME/DSH}"

rotate_hub_secret() {
  local value
  value="$(openssl rand -hex 48)"
  security add-generic-password -a "${USER:-dome}" -s "dome/HUB_API_SECRET" -w "$value" -U >/dev/null
  echo "rotated: dome/HUB_API_SECRET"
}

seed_if_present() {
  local key="$1"
  local env_file="$DOME_ROOT/.env.pre-rotate.latest"
  [[ -f "$env_file" ]] || return 0
  local value
  value="$(awk -F= -v k="$key" '$1==k {sub(/^[^=]*=/,""); print; exit}' "$env_file")"
  [[ -n "${value:-}" ]] || return 0
  security add-generic-password -a "${USER:-dome}" -s "dome/$key" -w "$value" -U >/dev/null
  echo "seeded: dome/$key"
}

main() {
  echo "DOME-HUB keychain rotation (local machine)"
  rotate_hub_secret

  # Optional seeds from the last backup snapshot if present.
  seed_if_present "ANTHROPIC_API_KEY"
  seed_if_present "GITHUB_PERSONAL_ACCESS_TOKEN"
  seed_if_present "ELEVENLABS_API_KEY"
  seed_if_present "TRINITY_JWT"

  echo "done. render plaintext runtime file only when needed:"
  echo "  bash \"$DOME_ROOT/scripts/render-env.sh\""
}

main "$@"
