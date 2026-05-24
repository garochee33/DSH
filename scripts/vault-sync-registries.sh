#!/usr/bin/env bash
#
# vault-sync-registries.sh
#
# Regenerates 600-Engines/, 700-Agents/, 800-Skills/ in the Obsidian vault
# from upstream canonical registries. Idempotent: each note is rewritten only
# if its content hash differs.
#
# Sources:
#   brain/REGISTRY.md          → 600-Engines/
#   agents/*/                  → 700-Agents/
#   trinity-consortium/skills/MASTER_INDEX.md → 800-Skills/
#
# Vault root: ~/DOME-HUB/brain/vault

set -euo pipefail

DOME="${DOME_HUB_ROOT:-$HOME/DOME-HUB}"
VAULT="$DOME/brain/vault"
TODAY="$(date +%F)"

if [[ ! -d "$VAULT" ]]; then
  echo "vault-sync: vault not found at $VAULT" >&2
  exit 1
fi

mkdir -p "$VAULT/600-Engines" "$VAULT/700-Agents" "$VAULT/800-Skills"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

slugify() {
  local s="${1,,}"
  s="${s//[^a-z0-9_]/-}"
  s="${s##-}"
  s="${s%%-}"
  while [[ "$s" == *--* ]]; do s="${s//--/-}"; done
  printf '%s' "$s"
}

# preserve_created <path> — echo the file's existing `created:` value if present,
# else echo $TODAY. Lets idempotency survive day-rollover.
preserve_created() {
  local path="$1"
  if [[ -f "$path" ]]; then
    local existing
    existing=$(awk -F': *' '/^created: */ {print $2; exit}' "$path" 2>/dev/null)
    if [[ -n "$existing" ]]; then printf '%s' "$existing"; return; fi
  fi
  printf '%s' "$TODAY"
}

# write_if_changed <path> <content>
write_if_changed() {
  local path="$1" content="$2"
  local new_hash old_hash
  new_hash="$(printf '%s\n' "$content" | shasum -a 256 | cut -d' ' -f1)"
  if [[ -f "$path" ]]; then
    old_hash="$(shasum -a 256 < "$path" | cut -d' ' -f1)"
    if [[ "$new_hash" == "$old_hash" ]]; then
      return 0
    fi
  fi
  printf '%s\n' "$content" > "$path"
  echo "  wrote $path"
}

# ---------------------------------------------------------------------------
# 1. Engines  (brain/REGISTRY.md)
# ---------------------------------------------------------------------------
echo "→ engines"
ENGINES_SRC="$DOME/brain/REGISTRY.md"
if [[ ! -f "$ENGINES_SRC" ]]; then
  echo "  skip: $ENGINES_SRC not found" >&2
else
  ENGINE_COUNT=0
  # Match table rows shaped: | **Name** | `path` | lines | status | wired |
  # but the REGISTRY varies, so we accept any | **Bold** | ... | row.
  while IFS=$'\t' read -r name rest; do
    [[ -z "$name" ]] && continue
    slug="$(slugify "$name")"
    out="$VAULT/600-Engines/${slug}.md"
    rest_md="$(printf '%s' "$rest" | sed 's/|/ · /g')"
    body="---
title: \"$name\"
created: $(preserve_created "$out")
type: engine
tier: brain
source: brain/REGISTRY.md
tags: [type/engine, status/active, source/brain-registry]
links: \"[[REGISTRY-brain]]\"
---

# $name

**Source registry:** [[REGISTRY-brain]]

## Row from registry
$rest_md

## Backlinks
- [[Map of Content]]
- [[REGISTRY-brain]]
"
    write_if_changed "$out" "$body"
    ENGINE_COUNT=$((ENGINE_COUNT + 1))
  done < <(awk -F'|' '
      /^\| \*\*[A-Za-z0-9]/ {
        name = $2
        gsub(/^[ *]+|[ *]+$/, "", name)
        rest = ""
        for (i = 3; i <= NF; i++) rest = rest (i==3 ? "" : "|") $i
        gsub(/^[ ]+|[ ]+$/, "", rest)
        if (name != "" && name !~ /^Engine$|^Skill$|^Brain$|^File$|^Name$/)
          print name "\t" rest
      }' "$ENGINES_SRC")

  # Index page
  index="---
title: \"REGISTRY-brain\"
created: $(preserve_created "$VAULT/600-Engines/REGISTRY-brain.md")
tags: [type/registry, status/active]
links: \"[[Map of Content]]\"
---

# Brain Engine Registry (live mirror)

**Upstream:** \`$ENGINES_SRC\`
**Synced:** $TODAY
**Engine count:** $ENGINE_COUNT

\`\`\`dataview
TABLE WITHOUT ID file.link AS Engine, tier AS Tier
FROM \"600-Engines\"
WHERE type = \"engine\"
SORT file.name ASC
\`\`\`
"
  write_if_changed "$VAULT/600-Engines/REGISTRY-brain.md" "$index"
  echo "  $ENGINE_COUNT engines synced"
fi

# ---------------------------------------------------------------------------
# 2. Agents  (agents/<runner>/)
# ---------------------------------------------------------------------------
echo "→ agents"
AGENT_COUNT=0
for d in "$DOME/agents"/*/; do
  name="$(basename "$d")"
  [[ "$name" == "__pycache__" ]] && continue
  [[ "$name" == "skills" ]] && continue
  slug="$(slugify "$name")"
  out="$VAULT/700-Agents/${slug}.md"
  readme="$d/README.md"
  yaml="$d/agent.yaml"

  transport="unknown"
  if [[ -f "$readme" ]]; then
    if grep -qiE "http|fastapi|rest" "$readme"; then transport="HTTP"; fi
    if grep -qiE "cli|shell" "$readme"; then transport="CLI"; fi
    if grep -qi "websocket\|sse\|stream" "$readme"; then transport="streaming"; fi
  fi

  auth="local"
  if [[ -f "$readme" ]]; then
    grep -qi "ANTHROPIC_API_KEY"  "$readme" 2>/dev/null && auth="ANTHROPIC_API_KEY"
    grep -qi "MOONSHOT_API_KEY"   "$readme" 2>/dev/null && auth="MOONSHOT_API_KEY"
    grep -qi "OPENAI_API_KEY"     "$readme" 2>/dev/null && auth="OPENAI_API_KEY"
  fi

  summary=""
  if [[ -f "$readme" ]]; then
    summary="$(head -20 "$readme" | sed 's/^/> /')"
  fi

  body="---
title: \"agent/$name\"
created: $(preserve_created "$out")
type: agent
tier: runner
runner: $name
transport: $transport
auth: $auth
status: active
source: agents/$name/
tags: [type/agent, status/active, source/agents-dir]
links: \"[[REGISTRY-agents]]\"
---

# Agent — $name

**Runner directory:** \`agents/$name/\`
**Transport:** $transport
**Auth:** $auth

## README excerpt
$summary

## Backlinks
- [[Map of Content]]
- [[REGISTRY-agents]]
"
  write_if_changed "$out" "$body"
  AGENT_COUNT=$((AGENT_COUNT + 1))
done

agent_index="---
title: \"REGISTRY-agents\"
created: $(preserve_created "$VAULT/700-Agents/REGISTRY-agents.md")
tags: [type/registry, status/active]
links: \"[[Map of Content]]\"
---

# Agent Runner Registry (live mirror)

**Upstream:** \`$DOME/agents/\`
**Synced:** $TODAY
**Runner count:** $AGENT_COUNT

\`\`\`dataview
TABLE WITHOUT ID file.link AS Agent, transport, auth
FROM \"700-Agents\"
WHERE type = \"agent\"
SORT runner ASC
\`\`\`
"
write_if_changed "$VAULT/700-Agents/REGISTRY-agents.md" "$agent_index"
echo "  $AGENT_COUNT agents synced"

# ---------------------------------------------------------------------------
# 3. Skills  (trinity-consortium/skills/MASTER_INDEX.md)
# ---------------------------------------------------------------------------
echo "→ skills"
SKILLS_SRC="$DOME/home/projects/trinity-consortium/skills/MASTER_INDEX.md"
if [[ ! -f "$SKILLS_SRC" ]]; then
  echo "  skip: $SKILLS_SRC not found" >&2
else
  SKILL_COUNT=0
  while IFS=$'\t' read -r name desc trig tiers; do
    [[ -z "$name" ]] && continue
    slug="$(slugify "$name")"
    out="$VAULT/800-Skills/${slug}.md"
    body="---
title: \"skill/$name\"
created: $(preserve_created "$out")
type: skill
tier: trinity-canonical
skill_name: $name
triggers: \"$trig\"
mirrors: \"$tiers\"
status: active
source: trinity-consortium/skills/MASTER_INDEX.md
tags: [type/skill, status/active, source/master-index]
links: \"[[MASTER_INDEX-skills]]\"
---

# Skill — $name

## Description
$desc

## Triggers
$trig

## Available in tiers
$tiers

## Backlinks
- [[Map of Content]]
- [[MASTER_INDEX-skills]]
"
    write_if_changed "$out" "$body"
    SKILL_COUNT=$((SKILL_COUNT + 1))
  done < <(awk -F'|' '
      /^\| \*\*[a-z0-9]/ {
        n=$2; d=$3; t=$4; m=$5
        gsub(/^[ *]+|[ *]+$/, "", n)
        gsub(/^[ ]+|[ ]+$/, "", d)
        gsub(/^[ ]+|[ ]+$/, "", t)
        gsub(/^[ ]+|[ ]+$/, "", m)
        if (n != "") print n "\t" d "\t" t "\t" m
      }' "$SKILLS_SRC")

  skill_index="---
title: \"MASTER_INDEX-skills\"
created: $(preserve_created "$VAULT/800-Skills/MASTER_INDEX-skills.md")
tags: [type/registry, status/active]
links: \"[[Map of Content]]\"
---

# Trinity Skills MASTER_INDEX (live mirror)

**Upstream:** \`$SKILLS_SRC\`
**Synced:** $TODAY
**Skill count:** $SKILL_COUNT

\`\`\`dataview
TABLE WITHOUT ID file.link AS Skill, mirrors AS Tiers
FROM \"800-Skills\"
WHERE type = \"skill\"
SORT skill_name ASC
\`\`\`
"
  write_if_changed "$VAULT/800-Skills/MASTER_INDEX-skills.md" "$skill_index"
  echo "  $SKILL_COUNT skills synced"
fi

# ---------------------------------------------------------------------------
echo
echo "vault-sync complete → $VAULT"
