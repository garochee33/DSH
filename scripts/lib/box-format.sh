#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════╗
# ║  Box-Drawing Format Library — Sovereign Visual Standard         ║
# ║  Source: source "$(dirname "$0")/lib/box-format.sh"             ║
# ╚══════════════════════════════════════════════════════════════════╝

BOX_WIDTH=66
ANIMATIONS_ENABLED=1
[[ ! -t 1 ]] && ANIMATIONS_ENABLED=0

# Colors (degrade gracefully)
if [[ -t 1 ]] && command -v tput >/dev/null 2>&1 && [[ "$(tput colors 2>/dev/null || echo 0)" -ge 256 ]]; then
  C_RESET="$(tput sgr0)"; C_CYAN="$(tput setaf 6)"; C_GREEN="$(tput setaf 2)"
  C_YELLOW="$(tput setaf 3)"; C_MAGENTA="$(tput setaf 178)"; C_RED="$(tput setaf 1)"
  C_DIM="$(tput dim)"; C_BOLD="$(tput bold)"
else
  C_RESET="" C_CYAN="" C_GREEN="" C_YELLOW="" C_MAGENTA="" C_RED="" C_DIM="" C_BOLD=""
fi

# ━━━ Counters ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PASS=0; FAIL=0; WARN=0
pass() { PASS=$((PASS+1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL+1)); echo "  ❌ $1"; }
warn() { WARN=$((WARN+1)); echo "  ⚠️  $1"; }

# ━━━ Box Elements ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
box_header() {
  local title="$1" subtitle="${2:-}"
  echo "${C_CYAN}╔$(printf '═%.0s' $(seq 1 $BOX_WIDTH))╗${C_RESET}"
  printf "${C_CYAN}║${C_RESET}  %-$((BOX_WIDTH-2))s${C_CYAN}║${C_RESET}\n" "$title"
  [ -n "$subtitle" ] && printf "${C_CYAN}║${C_RESET}  ${C_DIM}%-$((BOX_WIDTH-2))s${C_RESET}${C_CYAN}║${C_RESET}\n" "$subtitle"
  echo "${C_CYAN}╚$(printf '═%.0s' $(seq 1 $BOX_WIDTH))╝${C_RESET}"
}

box_footer() {
  local total=$((PASS+FAIL+WARN))
  echo "${C_CYAN}╔$(printf '═%.0s' $(seq 1 $BOX_WIDTH))╗${C_RESET}"
  printf "${C_CYAN}║${C_RESET}  PASS: ${C_GREEN}%-3d${C_RESET} │ FAIL: ${C_RED}%-3d${C_RESET} │ WARN: ${C_YELLOW}%-3d${C_RESET} │ TOTAL: %-3d          ${C_CYAN}║${C_RESET}\n" "$PASS" "$FAIL" "$WARN" "$total"
  if [ "$FAIL" -eq 0 ]; then
    echo "${C_CYAN}║${C_RESET}  ${C_GREEN}██████████████████████████████████████████████████████████████${C_RESET} ${C_CYAN}║${C_RESET}"
    echo "${C_CYAN}║${C_RESET}  ${C_GREEN}██  VERDICT: ✅ ALL CLEAR — PRODUCTION READY               ██${C_RESET} ${C_CYAN}║${C_RESET}"
    echo "${C_CYAN}║${C_RESET}  ${C_GREEN}██████████████████████████████████████████████████████████████${C_RESET} ${C_CYAN}║${C_RESET}"
  else
    printf "${C_CYAN}║${C_RESET}  ${C_RED}❌ VERDICT: %d FAILURES — REMEDIATION REQUIRED${C_RESET}              ${C_CYAN}║${C_RESET}\n" "$FAIL"
  fi
  printf "${C_CYAN}║${C_RESET}  Evidence: $(date -u +%%Y-%%m-%%dT%%H:%%M:%%SZ) │ Operator: EGD33%-$((BOX_WIDTH-52))s${C_CYAN}║${C_RESET}\n" ""
  echo "${C_CYAN}╚$(printf '═%.0s' $(seq 1 $BOX_WIDTH))╝${C_RESET}"
}

section() {
  local num="$1" title="$2"
  local prefix="━━━ §$num $title "
  local remaining=$((70-${#prefix}))
  printf "\n${C_BOLD}%s$(printf '━%.0s' $(seq 1 $remaining))${C_RESET}\n" "$prefix"
}

# ━━━ Phase Box ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
phase_box() {
  local step="$1" total="$2" title="$3"
  printf "\n${C_CYAN}    ┌─────────────────────────────────────────────┐${C_RESET}\n"
  printf "${C_CYAN}    │  ▶  [%d/%d]  %-33.33s│${C_RESET}\n" "$step" "$total" "$title"
  printf "${C_CYAN}    └─────────────────────────────────────────────┘${C_RESET}\n"
  progress_bar "$step" "$total"
  echo
}

# ━━━ Progress Bar ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
progress_bar() {
  local step=$1 total=$2 width=34
  local filled=$((step * width / total))
  local empty=$((width - filled))
  local pct=$((step * 100 / total))
  printf "${C_DIM}    ▐${C_GREEN}%s${C_DIM}%s▌ %3d%%${C_RESET}\n" \
    "$(printf '%*s' $filled '' | tr ' ' '█')" \
    "$(printf '%*s' $empty '' | tr ' ' '░')" \
    "$pct"
}

# ━━━ Animations ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
spin() {
  local msg="$1"
  if [[ "$ANIMATIONS_ENABLED" -ne 1 ]]; then printf "    ✦ %s\n" "$msg"; return; fi
  local frames=("◐" "◓" "◑" "◒")
  for f in "${frames[@]}"; do
    printf "\r    ${C_MAGENTA}%s${C_RESET} %s" "$f" "$msg"; sleep 0.08
  done
  printf "\r    ${C_GREEN}✦${C_RESET} %s done\n" "$msg"
}

pulse() {
  local msg="$1"
  if [[ "$ANIMATIONS_ENABLED" -ne 1 ]]; then printf "    ▸ %s\n" "$msg"; return; fi
  printf "    ${C_YELLOW}▸ %s${C_RESET}" "$msg"
  for _ in 1 2 3; do printf "${C_MAGENTA}●${C_RESET}"; sleep 0.15; done
  printf "\n"
}

wave() {
  local msg="$1"
  if [[ "$ANIMATIONS_ENABLED" -ne 1 ]]; then printf "    ⚡ %s ✓\n" "$msg"; return; fi
  local frames=("∿∿∿∿∿∿∿∿" "≋≋≋≋≋≋≋≋" "∿∿∿∿∿∿∿∿" "〰〰〰〰")
  for f in "${frames[@]}"; do
    printf "\r    ${C_MAGENTA}⚡ %s${C_RESET} %s" "$f" "$msg"; sleep 0.12
  done
  printf "\r    ${C_GREEN}⚡ ════════${C_RESET} %s ✓\n" "$msg"
}

orbit() {
  local msg="$1"
  if [[ "$ANIMATIONS_ENABLED" -ne 1 ]]; then printf "    ◉ %s\n" "$msg"; return; fi
  local frames=("◜" "◝" "◞" "◟") i=0
  while [ $i -lt 8 ]; do
    printf "\r    ${C_MAGENTA}%s${C_RESET} %s" "${frames[$((i%4))]}" "$msg"
    sleep 0.1; i=$((i+1))
  done
  printf "\r    ${C_GREEN}◉${C_RESET} %s\n" "$msg"
}

# ━━━ 3D Scenes ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
scene_merkaba() {
  printf "${C_MAGENTA}"
  cat << 'EOF'
              △
             ╱ ╲
            ╱   ╲
           ╱  ◆  ╲
          ╱ ╱   ╲ ╲
         ╱ ╱     ╲ ╲
        ▽━━━━━━━━━━━▽
         ╲ ╲     ╱ ╱
          ╲ ╲   ╱ ╱
           ╲  ◆  ╱
            ╲   ╱
             ╲ ╱
              ▽
EOF
  printf "${C_RESET}"
}

scene_lattice() {
  local label="${1:-E8 Lattice}"
  printf "${C_MAGENTA}"
  printf '    ╔══════════════════════════════════════════════════════════╗\n'
  printf '    ║  ▓▓▓ Sacred Geometry Mesh ▓▓▓                          ║\n'
  printf '    ║                                                        ║\n'
  printf '    ║       ◆───◆───◆───◆───◆                                ║\n'
  printf '    ║      ╱ ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱ ╲                              ║\n'
  printf '    ║     ◆───◆───◆───◆───◆───◆                              ║\n'
  printf '    ║      ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱                              ║\n'
  printf '    ║       ◆───◆───◆───◆───◆                                ║\n'
  printf '    ║                                                        ║\n'
  printf "    ║  %-54.54s  ║\n" "$label"
  printf '    ╚══════════════════════════════════════════════════════════╝\n'
  printf "${C_RESET}"
}

scene_torus() {
  printf "${C_MAGENTA}"
  cat << 'EOF'
          ╭━━━━━━━━━━━╮
       ╭━━╯  ╭─────╮  ╰━━╮
     ╭━╯   ╭─╯     ╰─╮   ╰━╮
    ━╯    ╭─╯    ◆    ╰─╮    ╰━
    ━╮    ╰─╮         ╭─╯    ╭━
     ╰━╮   ╰─╮     ╭─╯   ╭━╯
       ╰━━╮  ╰─────╯  ╭━━╯
          ╰━━━━━━━━━━━╯
EOF
  printf "${C_RESET}"
}

scene_cube() {
  printf "${C_MAGENTA}"
  cat << 'EOF'
        ┌───────────────┐
       ╱│              ╱│
      ╱ │             ╱ │
     ┌───────────────┐  │
     │  │            │  │
     │  └────────────│──┘
     │ ╱             │ ╱
     │╱              │╱
     └───────────────┘
EOF
  printf "${C_RESET}"
}

# ━━━ Banners ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
banner_dsh() {
  printf "${C_MAGENTA}"
  cat << 'EOF'
    ██████╗  ███████╗ ██╗  ██╗
    ██╔══██╗ ██╔════╝ ██║  ██║
    ██║  ██║ ███████╗ ███████║
    ██║  ██║ ╚════██║ ██╔══██║
    ██████╔╝ ███████║ ██║  ██║
    ╚═════╝  ╚══════╝ ╚═╝  ╚═╝
EOF
  printf "${C_RESET}"
  printf "${C_CYAN}    ═══ D O M E   S O V E R E I G N   H U B ═══${C_RESET}\n"
}

banner_trinity() {
  printf "${C_MAGENTA}"
  cat << 'EOF'
    ████████╗██████╗ ██╗███╗   ██╗██╗████████╗██╗   ██╗
    ╚══██╔══╝██╔══██╗██║████╗  ██║██║╚══██╔══╝╚██╗ ██╔╝
       ██║   ██████╔╝██║██╔██╗ ██║██║   ██║    ╚████╔╝
       ██║   ██╔══██╗██║██║╚██╗██║██║   ██║     ╚██╔╝
       ██║   ██║  ██║██║██║ ╚████║██║   ██║      ██║
       ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚═╝   ╚═╝      ╚═╝
EOF
  printf "${C_RESET}"
}
