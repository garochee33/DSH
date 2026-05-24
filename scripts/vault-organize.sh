#!/usr/bin/env bash
#
# vault-organize.sh
#
# Process everything in 000-Inbox/. For each .md file:
#   1. If missing YAML frontmatter → add it
#   2. Infer tags from content (project/area/resource heuristics)
#   3. Suggest target folder; --apply moves it
#
# Default = dry run (suggests, does not move).
# `--apply` actually moves files.

set -euo pipefail

DOME="${DOME_HUB_ROOT:-$HOME/DOME-HUB}"
VAULT="$DOME/brain/vault"
INBOX="$VAULT/000-Inbox"
APPLY=0

[[ "${1:-}" == "--apply" ]] && APPLY=1

today="$(date +%F)"

infer_dest() {
  local file="$1"
  local lower
  lower="$(tr '[:upper:]' '[:lower:]' < "$file")"
  if grep -qE "deadline|milestone|sprint|launch" <<< "$lower"; then
    echo "200-Projects"
  elif grep -qE "habit|finances?|health|review|monthly|yearly|ongoing" <<< "$lower"; then
    echo "300-Areas"
  elif grep -qE "paper|book|reference|snippet|cheat *sheet|api docs?" <<< "$lower"; then
    echo "400-Resources"
  elif grep -qE "agent|engine|trinity|brain|skill|mycelium|merkaba" <<< "$lower"; then
    echo "400-Resources"
  else
    echo "400-Resources"
  fi
}

infer_tags() {
  local file="$1" tags="type/note"
  grep -qiE "project" "$file" && tags="$tags, type/project"
  grep -qiE "agent|trinity"  "$file" && tags="$tags, area/trinity"
  grep -qiE "engine|brain"   "$file" && tags="$tags, area/brain"
  grep -qiE "mycelium|merkaba|pheromone" "$file" && tags="$tags, lang/trinity-vocab"
  echo "$tags"
}

has_frontmatter() {
  head -1 "$1" 2>/dev/null | grep -q "^---$"
}

if ! compgen -G "$INBOX/*.md" > /dev/null; then
  echo "vault-organize: inbox empty ($INBOX)"
  exit 0
fi

for f in "$INBOX"/*.md; do
  name="$(basename "$f")"
  dest="$(infer_dest "$f")"
  tags="$(infer_tags "$f")"
  title="${name%.md}"

  if has_frontmatter "$f"; then
    echo "  has frontmatter: $name → suggest $dest"
  else
    # Prepend frontmatter
    tmp="$(mktemp)"
    {
      printf '%s\n' "---"
      printf 'title: "%s"\n' "$title"
      printf 'created: %s\n' "$today"
      printf 'tags: [%s]\n'  "$tags"
      printf 'links: "[[Map of Content]]"\n'
      printf 'status: inbox\n'
      printf '%s\n\n'        "---"
      cat "$f"
    } > "$tmp"
    if (( APPLY )); then
      mv "$tmp" "$f"
      mv "$f" "$VAULT/$dest/$name"
      echo "  moved: $name → $dest/  (frontmatter added)"
    else
      rm "$tmp"
      echo "  WOULD add frontmatter + move: $name → $dest/"
    fi
  fi
done

if (( ! APPLY )); then
  echo
  echo "Dry run. Re-run with --apply to perform the moves."
fi
