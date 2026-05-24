#!/usr/bin/env bash
#
# vault-emerge.sh
#
# Cross-reference vault for emergent patterns:
#   - Tag co-occurrence across folders (notes sharing tags but not linked)
#   - Tag frequency (top 20)
#   - Orphan candidates (no inbound links)
#
# Read-only; emits a report to stdout.

set -euo pipefail
DOME="${DOME_HUB_ROOT:-$HOME/DOME-HUB}"
VAULT="$DOME/brain/vault"

echo "# vault-emerge — $(date +'%F %T')"
echo

echo "## Top 20 tags"
grep -hE "^tags: \[" "$VAULT"/*/*.md 2>/dev/null \
  | sed -E 's/^tags: \[([^]]*)\].*/\1/' \
  | tr ',' '\n' \
  | sed -E 's/^[ ]+|[ ]+$//g' \
  | grep -v '^$' \
  | sort | uniq -c | sort -rn | head -20
echo

echo "## Notes by folder"
for d in 000-Inbox 100-Daily-Notes 200-Projects 300-Areas 400-Resources 500-Archive 600-Engines 700-Agents 800-Skills; do
  n=$(ls "$VAULT/$d"/*.md 2>/dev/null | wc -l | tr -d ' ')
  printf '  %-20s %s\n' "$d" "$n"
done
echo

echo "## Cross-domain mentions (engine ↔ agent ↔ skill)"
echo "Notes referencing multiple top-level concepts:"
for f in "$VAULT"/{200-Projects,100-Daily-Notes,400-Resources}/*.md; do
  [[ -e "$f" ]] || continue
  hits=0
  grep -qi "engine\|brain"  "$f" && hits=$((hits+1))
  grep -qi "agent\|runner"  "$f" && hits=$((hits+1))
  grep -qi "skill"          "$f" && hits=$((hits+1))
  if (( hits >= 2 )); then
    echo "  $(basename "$f")"
  fi
done
echo

echo "## Orphan candidates (notes nobody links to)"
# crude: filenames whose stems do not appear in any other file
all_md=( "$VAULT"/*/*.md )
for f in "${all_md[@]}"; do
  stem="$(basename "$f" .md)"
  # skip indexes
  case "$stem" in README|"Map of Content"|REGISTRY-brain|REGISTRY-agents|MASTER_INDEX-skills) continue ;; esac
  if ! grep -rqF "[[$stem]]" "$VAULT" --include="*.md" --exclude="$(basename "$f")" 2>/dev/null; then
    echo "  $stem"
  fi
done | head -25
