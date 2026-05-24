#!/usr/bin/env bash
# fractalmap-generate.sh — tiered structural map generator for fractalmap-registered repos.
# Reads ~/DOME-HUB/config/fractalmap-repos.yaml and writes <repo>/.fractalmap/{L0.md, L1/*.md, tree-full.txt, manifest.json}.
set -euo pipefail

REGISTRY="${FRACTALMAP_REGISTRY:-$HOME/DOME-HUB/config/fractalmap-repos.yaml}"
EXCLUDE_DEFAULT='node_modules|.git|.venv|venv|.venv-coreml|__pycache__|dist|build|.next|.turbo|.cache|.mypy_cache|.pytest_cache|.ruff_cache|.tox|.DS_Store|.fractalmap|deps|coverage|htmlcov|out|.output|storybook-static|playwright-report|.pnpm-store|.parcel-cache|.vite|.gradle|Pods|bower_components'

usage() {
  cat <<'USAGE'
fractalmap-generate.sh — tiered repo map generator

Usage:
  fractalmap-generate.sh <repo-name>     Generate maps for one registered repo
  fractalmap-generate.sh --all           Generate maps for every registered repo
  fractalmap-generate.sh --list          List registered repos and exit
  fractalmap-generate.sh --help          Show this help

Outputs <repo>/.fractalmap/{L0.md, L1/<subdir>.md, tree-full.txt, manifest.json}.
USAGE
}

# ---------- registry ----------

registry_names()       { yq -r '.repos[].name' "$REGISTRY"; }
registry_path()        { yq -r ".repos[] | select(.name == \"$1\") | .path" "$REGISTRY"; }
registry_description() { yq -r ".repos[] | select(.name == \"$1\") | .description // \"\"" "$REGISTRY"; }

# ---------- helpers ----------

build_excludes() {
  local repo_path="$1"
  local pat="$EXCLUDE_DEFAULT"
  local custom="$repo_path/.fractalmapignore"
  if [[ -f "$custom" ]]; then
    while IFS= read -r line; do
      [[ -z "$line" || "$line" =~ ^# ]] && continue
      pat="$pat|$line"
    done < "$custom"
  fi
  printf '%s' "$pat"
}

sha256_file() { shasum -a 256 "$1" | awk '{print $1}'; }

file_size() {
  if stat -f%z "$1" >/dev/null 2>&1; then stat -f%z "$1"; else stat -c%s "$1"; fi
}

git_or() {
  local dir="$1" cmd="$2" fallback="$3"
  ( cd "$dir" && eval "git $cmd" ) 2>/dev/null || printf '%s' "$fallback"
}

is_excluded() {
  local name="$1" excludes="$2"
  local IFS='|'
  local p
  for p in $excludes; do
    [[ "$name" == "$p" ]] && return 0
  done
  return 1
}

now_utc() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

# ---------- L0 ----------

generate_l0() {
  local repo_path="$1" repo_name="$2" desc="$3" excludes="$4" out="$5"
  local sha branch generated
  sha=$(git_or "$repo_path" "rev-parse HEAD" "no-git")
  branch=$(git_or "$repo_path" "rev-parse --abbrev-ref HEAD" "no-git")
  generated=$(now_utc)

  {
    printf '# fractalmap L0 — %s\n\n' "$repo_name"
    printf '**Path:** `%s`  \n' "$repo_path"
    printf '**Branch:** `%s`  \n' "$branch"
    printf '**Git SHA:** `%s`  \n' "$sha"
    printf '**Generated:** `%s`\n\n' "$generated"
    if [[ -n "$desc" ]]; then
      printf '## Purpose\n\n%s\n\n' "$desc"
    fi
    printf '## Top-level layout (depth 2)\n\n'
    printf '```\n'
    tree -a -L 2 -I "$excludes" "$repo_path" 2>/dev/null | head -300
    printf '```\n\n'
    printf '## Top-level entries (file counts, recursive)\n\n'
    printf '| Entry | Type | Files |\n'
    printf '|---|---|---|\n'
    while IFS= read -r entry; do
      [[ -z "$entry" ]] && continue
      local base
      base="$(basename "$entry")"
      is_excluded "$base" "$excludes" && continue
      if [[ -d "$entry" ]]; then
        local count
        # Cap depth to avoid hanging on huge overlay dirs (e.g. home/ with 2M files)
        count=$(find "$entry" -maxdepth 3 -type f 2>/dev/null | wc -l | tr -d ' ')
        printf '| `%s/` | dir | %s |\n' "$base" "$count"
      elif [[ -f "$entry" ]]; then
        printf '| `%s` | file | — |\n' "$base"
      fi
    done < <(find "$repo_path" -mindepth 1 -maxdepth 1 2>/dev/null | sort)
    printf '\n'
    if [[ -f "$repo_path/README.md" ]]; then
      printf '## README excerpt\n\n'
      head -40 "$repo_path/README.md"
      printf '\n'
    fi
  } > "$out"
}

# ---------- L1 ----------

generate_l1_for_subdir() {
  local repo_path="$1" subdir="$2" excludes="$3" out="$4"
  local full="$repo_path/$subdir"
  local generated file_count size
  generated=$(now_utc)
  # Cap depth to avoid hanging on huge subtrees
  file_count=$(find "$full" -maxdepth 4 -type f 2>/dev/null | wc -l | tr -d ' ')
  size=$(du -sh "$full" 2>/dev/null | awk '{print $1}')
  {
    printf '# fractalmap L1 — %s/\n\n' "$subdir"
    printf '**Subtree:** `%s`  \n' "$subdir"
    printf '**Files (depth≤4):** `%s`  \n' "$file_count"
    printf '**Size:** `%s`  \n' "$size"
    printf '**Generated:** `%s`\n\n' "$generated"
    printf '## Tree (depth 4)\n\n'
    printf '```\n'
    { tree -a -L 4 -I "$excludes" "$full" 2>/dev/null || true; } | head -800 || true
    printf '```\n\n'
    printf '## Markdown documents in this subtree\n\n'
    local found_md=0
    local md_list
    # Collect up to 50 md files, capped at depth 5, excluding noise dirs
    md_list=$(find "$full" -maxdepth 5 -type f -name '*.md' \
      -not -path '*/node_modules/*' -not -path '*/.git/*' \
      -not -path '*/deps/*' -not -path '*/vendor/*' \
      2>/dev/null | sort | head -50 || true)
    while IFS= read -r md; do
      [[ -z "$md" ]] && continue
      local rel head1
      rel="${md#$full/}"
      head1=$(grep -m1 -E '^# ' "$md" 2>/dev/null | sed 's/^# *//' || true)
      [[ -z "$head1" ]] && head1='(no H1)'
      printf '%s\n' "- \`$rel\` — $head1"
      found_md=1
    done <<< "$md_list"
    [[ "$found_md" -eq 0 ]] && printf '_None._\n'
    printf '\n'
  } > "$out"
}

# ---------- tree-full ----------

generate_tree_full() {
  local repo_path="$1" excludes="$2" out="$3" repo_name="${4:-$(basename "$repo_path")}"
  local generated sha branch tree_ver
  generated=$(now_utc)
  sha=$(git_or "$repo_path" "rev-parse --short HEAD" "no-git")
  branch=$(git_or "$repo_path" "rev-parse --abbrev-ref HEAD" "no-git")
  tree_ver=$(tree --version 2>/dev/null | head -1 || printf 'tree (unknown)')

  {
    printf '%s\n' "================================================================================"
    printf '%s\n' "${repo_name} fractalmap — FULL STACK + REPOSITORY TREE (tree-full.txt)"
    printf '%s\n' "================================================================================"
    printf '%s\n' ""
    if [[ "$repo_name" == "dome-hub" ]]; then
      printf '%s\n' "Canonical architecture: docs/DOME-HUB-ARCHITECTURE.md"
      printf '%s\n' "Index: INDEX.md | Skills: kb/skills/INDEX.md | Protocols: PROTOCOLS.md"
    else
      printf '%s\n' "Parent registry: ~/DOME-HUB/config/fractalmap-repos.yaml"
    fi
    printf '%s\n' ""
    if [[ "$repo_name" == "dome-hub" ]]; then
      printf '%s\n' "---- LAYER MAP (sovereign node) ------------------------------------------------"
      printf '%s\n' "L0  Apple Silicon UMA — CPU 8P+4E | MPS GPU | Neural Engine via ONNX→CoreML EP"
      printf '%s\n' "     (agents/core/memory/vector.py) | MLX/Metal LLMs (mlx_lm, agents/core/stream.py)"
      printf '%s\n' "     Optional Trinity MLX HTTP: scripts/mlx-neural-bridge.sh → nexus-core/mlx-neural-bridge.py"
      printf '%s\n' "L1  QuantumDome — compute/quantum_dome/ (scheduler, pool, memory, profiler)"
      printf '%s\n' "L2  Agents + API — agents/ (FastAPI :8001), voice, workers, registry (Ollama/MLX/Claude/OpenAI)"
      printf '%s\n' "L3  Memory — db/episodic.db, db/chroma/, Akashic, mesh queue (mempalace.db)"
      printf '%s\n' "L4  Knowledge — kb/trinity-unified-ai (Mycelium KB), kb/skills, kb/claude"
      printf '%s\n' "L5  Trinity mirror — home/projects/trinity-consortium/ (engines, LAVA Loihi sidecar, nexus-core, E8-240 AMMA)"
      printf '%s\n' "L6  Neuromorphic — canonical scripts/e8_240_with_amma_lens.py (real E8 k-NN + heterogeneous LIF + AMMA 8-band projection lens, Lava Loihi 2); legacy: python/lava/coherence_optimizer.py (Py3.10), compute/sim_*.py, julia/neuromorphic.jl"
      printf '%s\n' "L7  Mesh / scripts — spore.sh, scripts/mycelium-signal.sh, scripts/machine-probe.py"
    else
      printf '%s\n' "---- STACK --------------------------------------------------------------------"
      printf '%s\n' "See this repository README and parent DOME-HUB docs for cross-repo context."
    fi
    printf '%s\n' ""
    printf '%s\n' "---- TREE EXCLUDES (basename pattern for tree -I) ------------------------------"
    printf '%s\n' "$excludes"
    printf '%s\n' ""
    printf '%s\n' "---- METADATA ------------------------------------------------------------------"
    printf 'Generated (UTC): %s\n' "$generated"
    printf 'Repo path:       %s\n' "$repo_path"
    printf 'Git branch:      %s\n' "$branch"
    printf 'Git SHA:         %s\n' "$sha"
    printf '%s\n' "$tree_ver"
    printf '%s\n' "================================================================================"
    printf '%s\n' ""
  } > "$out"

  { tree -a -I "$excludes" "$repo_path" 2>/dev/null || true; } >> "$out"
}

# ---------- manifest ----------

generate_manifest() {
  local repo_path="$1" repo_name="$2" map_dir="$3" excludes="$4"
  local sha branch generated
  sha=$(git_or "$repo_path" "rev-parse HEAD" "no-git")
  branch=$(git_or "$repo_path" "rev-parse --abbrev-ref HEAD" "no-git")
  generated=$(now_utc)

  local l1_entries='[]'
  if [[ -d "$map_dir/L1" ]]; then
    l1_entries=$(
      find "$map_dir/L1" -maxdepth 1 -type f -name '*.md' 2>/dev/null | sort | while IFS= read -r f; do
        local name size sum
        name="$(basename "$f" .md)"
        size=$(file_size "$f")
        sum=$(sha256_file "$f")
        jq -nc --arg name "$name" --arg path "L1/$(basename "$f")" \
          --argjson size "$size" --arg sum "$sum" \
          '{name:$name, path:$path, size:$size, checksum:("sha256:" + $sum)}'
      done | jq -sc '.'
    )
    [[ -z "$l1_entries" ]] && l1_entries='[]'
  fi

  local l0_size l0_sum tree_size tree_sum
  l0_size=$(file_size "$map_dir/L0.md")
  l0_sum=$(sha256_file "$map_dir/L0.md")
  tree_size=$(file_size "$map_dir/tree-full.txt")
  tree_sum=$(sha256_file "$map_dir/tree-full.txt")

  jq -n \
    --arg repo_name "$repo_name" \
    --arg repo_path "$repo_path" \
    --arg generated "$generated" \
    --arg sha "$sha" \
    --arg branch "$branch" \
    --arg excludes "$excludes" \
    --argjson l0_size "$l0_size" --arg l0_sum "$l0_sum" \
    --argjson tree_size "$tree_size" --arg tree_sum "$tree_sum" \
    --argjson l1 "$l1_entries" \
    '{
      version: 1,
      repo_name: $repo_name,
      repo_path: $repo_path,
      generated_at: $generated,
      git_sha: $sha,
      git_branch: $branch,
      excluded_pattern: $excludes,
      tiers: {
        L0:   {path: "L0.md",         size: $l0_size,   checksum: ("sha256:" + $l0_sum)},
        L1:   $l1,
        tree: {path: "tree-full.txt", size: $tree_size, checksum: ("sha256:" + $tree_sum)}
      }
    }' > "$map_dir/manifest.json"
}

# ---------- per-repo orchestration ----------

generate_repo() {
  local repo_name="$1"
  local repo_path; repo_path="$(registry_path "$repo_name")"
  if [[ -z "$repo_path" || "$repo_path" == "null" ]]; then
    printf 'fractalmap: unknown repo: %s\n' "$repo_name" >&2; return 1
  fi
  if [[ ! -d "$repo_path" ]]; then
    printf 'fractalmap: repo path missing: %s\n' "$repo_path" >&2; return 1
  fi
  local desc;     desc="$(registry_description "$repo_name")"
  local excludes; excludes="$(build_excludes "$repo_path")"
  local map_dir="$repo_path/.fractalmap"
  mkdir -p "$map_dir/L1"

  printf '[fractalmap] %s — %s\n' "$repo_name" "$repo_path"

  generate_l0 "$repo_path" "$repo_name" "$desc" "$excludes" "$map_dir/L0.md"

  # Clear stale L1 entries so deleted subdirs don't leave orphan maps.
  find "$map_dir/L1" -maxdepth 1 -type f -name '*.md' -delete 2>/dev/null || true

  while IFS= read -r entry; do
    [[ -z "$entry" ]] && continue
    local base; base="$(basename "$entry")"
    is_excluded "$base" "$excludes" && continue
    [[ -d "$entry" ]] || continue
    generate_l1_for_subdir "$repo_path" "$base" "$excludes" "$map_dir/L1/$base.md"
  done < <(find "$repo_path" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort)

  generate_tree_full "$repo_path" "$excludes" "$map_dir/tree-full.txt" "$repo_name"
  generate_manifest "$repo_path" "$repo_name" "$map_dir" "$excludes"

  local total_size
  total_size=$(du -sh "$map_dir" 2>/dev/null | awk '{print $1}')
  printf '[fractalmap] %s done — %s (%s)\n' "$repo_name" "$map_dir" "$total_size"
}

# ---------- main ----------

main() {
  if [[ $# -eq 0 ]]; then usage; exit 1; fi
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --list)    registry_names ;;
    --all)
      while IFS= read -r name; do
        [[ -z "$name" ]] && continue
        generate_repo "$name" || printf '[fractalmap] WARNING: %s failed\n' "$name" >&2
      done < <(registry_names)
      ;;
    -*)
      printf 'fractalmap: unknown flag: %s\n' "$1" >&2
      usage; exit 1
      ;;
    *) generate_repo "$1" ;;
  esac
}

main "$@"
