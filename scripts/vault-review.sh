#!/usr/bin/env bash
#
# vault-review.sh
#
# Synthesize past 7 daily notes into a weekly review note.
#
# Default = stdout preview.
# `--write` saves to 100-Daily-Notes/Weekly-Review-YYYY-[W]WW.md

set -euo pipefail
DOME="${DSH_ROOT:-$HOME/DSH}"
VAULT="$DOME/brain/vault"
WRITE=0
[[ "${1:-}" == "--write" ]] && WRITE=1

today="$(date +%F)"
isoweek="$(date +'%G-W%V')"

# Collect last 7 daily notes
files=()
for i in 0 1 2 3 4 5 6; do
  d="$(date -v -${i}d +%F 2>/dev/null || date -d "$i days ago" +%F)"
  f="$VAULT/100-Daily-Notes/$d.md"
  [[ -f "$f" ]] && files+=("$f")
done

if (( ${#files[@]} == 0 )); then
  echo "vault-review: no daily notes in past 7 days under $VAULT/100-Daily-Notes/"
  exit 0
fi

render() {
  cat <<EOF
---
title: "Weekly Review — $isoweek"
created: $today
tags: [type/review, status/active]
links: "[[Map of Content]]"
period: "$(date -v -6d +%F 2>/dev/null || date -d '6 days ago' +%F)..$today"
---

# Weekly Review — $isoweek

**Daily notes reviewed:** ${#files[@]}

## Completion log (MERKABA Signals)
$(grep -hA1 -i "MERKABA Signal" "${files[@]}" 2>/dev/null | grep -E "^- " | sort -u || echo "_(none captured)_")

## Open loops
$(grep -hE "^- \[ \]" "${files[@]}" 2>/dev/null | sort -u || echo "_(none)_")

## Drift / friction
$(grep -hA1 -i "Drift / friction" "${files[@]}" 2>/dev/null | grep -E "^- " | sort -u || echo "_(none captured)_")

## Inbox captures (raw)
$(grep -hA1 -i "Inbox captures" "${files[@]}" 2>/dev/null | grep -E "^- " | sort -u || echo "_(none)_")

## Daily notes
$(for f in "${files[@]}"; do echo "- [[$(basename "$f" .md)]]"; done)
EOF
}

if (( WRITE )); then
  out="$VAULT/100-Daily-Notes/Weekly-Review-$isoweek.md"
  render > "$out"
  echo "vault-review: wrote $out"
else
  render
  echo
  echo "# (preview only — re-run with --write to save)"
fi
