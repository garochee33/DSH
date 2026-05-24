#!/usr/bin/env bash
# Annual (or on-demand) language-landscape KB rollover + optional vector ingest.
# Cron example (Jan 1, 08:00):
#   0 8 1 1 * /bin/bash -lc '$HOME/DOME-HUB/scripts/rollover-language-landscape.sh'
set -euo pipefail
ROOT="${DOME_ROOT:-${HOME}/DOME-HUB}"
cd "$ROOT"
if [[ ! -f .venv/bin/activate ]]; then
  echo "error: no venv at $ROOT/.venv — run setup first" >&2
  exit 1
fi
# shellcheck source=/dev/null
source .venv/bin/activate
exec python3 scripts/rollover-language-landscape.py --ingest "$@"
