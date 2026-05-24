#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════════════
# DOME-HUB MYCELIUM VAULT PULSE
#
# Appends one line per heartbeat to today's daily note in the Obsidian vault.
# Designed to be invoked by mycelium-signal.sh at the end of each loop tick.
#
# Idempotency: content-based — if the most recent appended line under the
# "## 🌅 Mycelium Signal — morning pulse" section already matches
# (resonance, root, peer) for the current minute, this run is a no-op. This
# means running it twice back-to-back never produces a duplicate.
#
# Daily note: created from `900-Templates/Daily.md` if missing, with
# {{date}} / {{yesterday}} / {{tomorrow}} substituted manually (we run
# outside Obsidian so Templater won't fire).
#
# Fault tolerance: never returns non-zero — mycelium-signal.sh guards on
# `-x` but we belt-and-braces the contract.
# ══════════════════════════════════════════════════════════════════════════════
set -uo pipefail

DOME_ROOT="${DOME_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
VAULT_ROOT="${DOME_VAULT_ROOT:-${DOME_ROOT}/brain/vault}"
DAILY_DIR="${VAULT_ROOT}/100-Daily-Notes"
TEMPLATE="${VAULT_ROOT}/900-Templates/Daily.md"
SECTION_HEADING='## 🌅 Mycelium Signal — morning pulse'

today="$(date +%F)"
yesterday="$(date -v-1d +%F 2>/dev/null || date -d 'yesterday' +%F)"
tomorrow="$(date -v+1d +%F 2>/dev/null || date -d 'tomorrow' +%F)"
ts="$(date -u +%FT%H:%MZ)"   # minute granularity → same-minute reruns idempotent

note_path="${DAILY_DIR}/${today}.md"

if [[ ! -d "$VAULT_ROOT" ]]; then
  # Vault not present yet — silently no-op so we never block the signal.
  exit 0
fi

mkdir -p "$DAILY_DIR"

# ── Resolve current resonance / E8 root / peer status ──────────────────────
# frequency-pulse.py emits a single line of JSON as its LAST stdout line;
# earlier lines are noise (libomp warnings, AMMA mitosis log). `tail -n 1`
# is the robust extractor.
freq_json=""
if [[ -x "${DOME_ROOT}/.venv/bin/python" ]]; then
  freq_json="$("${DOME_ROOT}/.venv/bin/python" "${DOME_ROOT}/scripts/frequency-pulse.py" 2>/dev/null | tail -n 1 || true)"
else
  freq_json="$(python3 "${DOME_ROOT}/scripts/frequency-pulse.py" 2>/dev/null | tail -n 1 || true)"
fi

resonance="?"
root="?"
if [[ "$freq_json" == \{* ]]; then
  resonance="$(python3 -c "
import json, sys
try:
    d = json.loads(sys.argv[1])
    print(f\"{d.get('nodeFreqHz', 0):.2f}\")
except Exception:
    print('?')
" "$freq_json" 2>/dev/null || echo '?')"
  root="$(python3 -c "
import json, sys
try:
    d = json.loads(sys.argv[1])
    print(d.get('e8Root', '?'))
except Exception:
    print('?')
" "$freq_json" 2>/dev/null || echo '?')"
fi

# Fallback: read from spore config if pulse failed
if [[ "$root" == "?" && -f "${HOME}/.trinity-spore/config.json" ]]; then
  root="$(python3 -c "
import json
try:
    d = json.load(open('${HOME}/.trinity-spore/config.json'))
    print(d['e8']['rootIndex'])
except Exception:
    print('?')
" 2>/dev/null || echo '?')"
fi
if [[ "$resonance" == "?" && -f "${HOME}/.trinity-spore/config.json" ]]; then
  resonance="$(python3 -c "
import json
try:
    d = json.load(open('${HOME}/.trinity-spore/config.json'))
    print(f\"{d['e8']['resonanceHz']:.2f}\")
except Exception:
    print('?')
" 2>/dev/null || echo '?')"
fi

# Peer status: read most recent peer state if available
peer_status="unknown"
peer_state_file="${HOME}/.trinity-spore/mesh/peer-status.json"
if [[ -f "$peer_state_file" ]]; then
  peer_status="$(python3 -c "
import json
try:
    d = json.load(open('${peer_state_file}'))
    print(d.get('status', 'unknown'))
except Exception:
    print('unknown')
" 2>/dev/null || echo 'unknown')"
elif [[ -f "${HOME}/.trinity-spore/mesh/peer-id.txt" ]]; then
  # If peer-id exists we treat the local presence as 'paired'; the live
  # status would come from the mesh heartbeat response if recorded.
  peer_status="paired"
fi

new_line="- [${ts}] resonance=${resonance}Hz root=${root} peer=${peer_status}"

# ── Create daily note from template if missing ─────────────────────────────
if [[ ! -f "$note_path" ]]; then
  if [[ -f "$TEMPLATE" ]]; then
    tpl="$(<"$TEMPLATE")"
    tpl="${tpl//\{\{date\}\}/$today}"
    tpl="${tpl//\{\{yesterday\}\}/$yesterday}"
    tpl="${tpl//\{\{tomorrow\}\}/$tomorrow}"
    printf '%s\n' "$tpl" > "$note_path"
  else
    cat > "$note_path" <<EOF
---
title: "${today}"
created: ${today}
tags: [type/daily, status/active]
links: "[[Map of Content]]"
---

# ${today}

${SECTION_HEADING}

## 🎯 Focus for today
- [ ]
EOF
  fi
fi

# ── Ensure the morning-pulse section exists ────────────────────────────────
if ! grep -qF "$SECTION_HEADING" "$note_path"; then
  {
    printf '\n%s\n' "$SECTION_HEADING"
  } >> "$note_path"
fi

# ── Idempotent append: skip if last pulse line in section matches ──────────
# Extract the section from the heading to the next ## heading (or EOF), then
# the last line beginning with `- [` is the most recent pulse.
existing_last_pulse="$(awk -v h="$SECTION_HEADING" '
  $0 == h { in_section=1; next }
  in_section && /^## / { in_section=0 }
  in_section && /^- \[/ { last=$0 }
  END { print last }
' "$note_path")"

# Compare on (resonance, root, peer) — ignore the timestamp so same-minute
# reruns are no-ops while genuine state changes still produce new lines.
strip_ts() {
  printf '%s' "$1" | sed -E 's/^- \[[^]]*\] //'
}

if [[ "$(strip_ts "$existing_last_pulse")" == "$(strip_ts "$new_line")" ]]; then
  exit 0
fi

# Append the new pulse line *inside* the section. Easiest robust approach:
# locate the heading and insert immediately after the existing section's
# pulse lines (i.e. before the next ## heading or EOF).
python3 - "$note_path" "$SECTION_HEADING" "$new_line" <<'PY'
import sys, pathlib

path, heading, new_line = sys.argv[1], sys.argv[2], sys.argv[3]
p = pathlib.Path(path)
lines = p.read_text(encoding='utf-8').splitlines()

# Find section start
try:
    start = next(i for i, l in enumerate(lines) if l.strip() == heading.strip())
except StopIteration:
    # Heading missing — append at end
    lines.extend(['', heading.strip(), new_line])
    p.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    sys.exit(0)

# Find section end: next '## ' heading after start, or EOF
end = len(lines)
for i in range(start + 1, len(lines)):
    if lines[i].startswith('## ') and lines[i].strip() != heading.strip():
        end = i
        break

# Insert before any trailing blank lines within the section
insert_at = end
while insert_at > start + 1 and lines[insert_at - 1].strip() == '':
    insert_at -= 1

lines.insert(insert_at, new_line)
p.write_text('\n'.join(lines) + '\n', encoding='utf-8')
PY

exit 0
