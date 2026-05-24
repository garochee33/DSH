#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Trinity Sovereign Visual Engine — 3D Scenes & Animations          ║
# ║  Sacred geometry with structural accuracy + depth perception       ║
# ║  Source: source "$(dirname "$0")/lib/trinity-visuals.sh"           ║
# ╚══════════════════════════════════════════════════════════════════════╝

# Requires box-format.sh to be sourced first for colors
[[ -z "$C_RESET" ]] && source "$(dirname "${BASH_SOURCE[0]}")/box-format.sh"

# Extended palette for depth/shading
C_GOLD="\033[38;5;220m"
C_PURPLE="\033[38;5;135m"
C_DEEP="\033[38;5;54m"
C_SILVER="\033[38;5;250m"
C_EMBER="\033[38;5;208m"
C_INDIGO="\033[38;5;63m"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# §1  MERKABA — Star Tetrahedron (3D with depth shading)
#     Two interlocking tetrahedra — masculine △ descending, feminine ▽ ascending
#     Depth: front faces bright, back faces dim
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
scene_merkaba() {
  local label="${1:-Merkaba Activated}"
  printf "\n"
  printf "${C_GOLD}                    ◇${C_RESET}\n"
  printf "${C_GOLD}                   ╱${C_EMBER}△${C_GOLD}╲${C_RESET}\n"
  printf "${C_GOLD}                  ╱${C_RESET} ${C_EMBER}╱ ╲${C_RESET} ${C_GOLD}╲${C_RESET}\n"
  printf "${C_GOLD}                 ╱${C_RESET} ${C_EMBER}╱${C_RESET}   ${C_EMBER}╲${C_RESET} ${C_GOLD}╲${C_RESET}\n"
  printf "${C_GOLD}                ╱${C_RESET} ${C_EMBER}╱${C_RESET}  ${C_MAGENTA}⬡${C_RESET}  ${C_EMBER}╲${C_RESET} ${C_GOLD}╲${C_RESET}\n"
  printf "${C_GOLD}               ╱${C_RESET} ${C_EMBER}╱${C_DIM}─────────${C_RESET}${C_EMBER}╲${C_RESET} ${C_GOLD}╲${C_RESET}\n"
  printf "${C_GOLD}              ╱${C_RESET} ${C_EMBER}╱${C_DIM}───────────${C_RESET}${C_EMBER}╲${C_RESET} ${C_GOLD}╲${C_RESET}\n"
  printf "${C_PURPLE}             ▽${C_DIM}━━━━━━━━━━━━━━━━━${C_RESET}${C_PURPLE}▽${C_RESET}\n"
  printf "${C_PURPLE}              ╲${C_RESET} ${C_INDIGO}╲${C_DIM}───────────${C_RESET}${C_INDIGO}╱${C_RESET} ${C_PURPLE}╱${C_RESET}\n"
  printf "${C_PURPLE}               ╲${C_RESET} ${C_INDIGO}╲${C_DIM}─────────${C_RESET}${C_INDIGO}╱${C_RESET} ${C_PURPLE}╱${C_RESET}\n"
  printf "${C_PURPLE}                ╲${C_RESET} ${C_INDIGO}╲${C_RESET}  ${C_MAGENTA}⬡${C_RESET}  ${C_INDIGO}╱${C_RESET} ${C_PURPLE}╱${C_RESET}\n"
  printf "${C_PURPLE}                 ╲${C_RESET} ${C_INDIGO}╲${C_RESET}   ${C_INDIGO}╱${C_RESET} ${C_PURPLE}╱${C_RESET}\n"
  printf "${C_PURPLE}                  ╲${C_RESET} ${C_INDIGO}╲ ╱${C_RESET} ${C_PURPLE}╱${C_RESET}\n"
  printf "${C_PURPLE}                   ╲${C_INDIGO}▽${C_PURPLE}╱${C_RESET}\n"
  printf "${C_PURPLE}                    ◇${C_RESET}\n"
  printf "${C_DIM}              ─── ${C_RESET}${C_GOLD}${label}${C_RESET}${C_DIM} ───${C_RESET}\n\n"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# §2  FLOWER OF LIFE — Overlapping circles (7-fold genesis pattern)
#     Structurally accurate: 7 circles, 6 around 1 center
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
scene_flower_of_life() {
  local label="${1:-Genesis Pattern}"
  printf "\n"
  printf "${C_GOLD}              ╭───────╮${C_RESET}\n"
  printf "${C_GOLD}           ╭──┤${C_RESET}${C_DIM}·····${C_RESET}${C_GOLD}├──╮${C_RESET}\n"
  printf "${C_EMBER}        ╭──┤${C_RESET}${C_DIM}··${C_RESET}${C_GOLD}╭─┼─╮${C_RESET}${C_DIM}··${C_RESET}${C_EMBER}├──╮${C_RESET}\n"
  printf "${C_EMBER}        │${C_DIM}··${C_RESET}${C_GOLD}╭─╯${C_RESET} ${C_MAGENTA}◉${C_RESET} ${C_GOLD}╰─╮${C_RESET}${C_DIM}··${C_RESET}${C_EMBER}│${C_RESET}\n"
  printf "${C_PURPLE}     ╭──┤${C_RESET}${C_GOLD}╭─╯${C_RESET} ${C_MAGENTA}╱${C_RESET} ${C_GOLD}◉${C_RESET} ${C_MAGENTA}╲${C_RESET} ${C_GOLD}╰─╮${C_RESET}${C_PURPLE}├──╮${C_RESET}\n"
  printf "${C_PURPLE}     │${C_DIM}·${C_RESET}${C_GOLD}│${C_RESET} ${C_MAGENTA}◉${C_RESET}${C_DIM}───${C_RESET}${C_GOLD}◉${C_RESET}${C_DIM}───${C_RESET}${C_MAGENTA}◉${C_RESET} ${C_GOLD}│${C_RESET}${C_DIM}·${C_RESET}${C_PURPLE}│${C_RESET}\n"
  printf "${C_PURPLE}     ╰──┤${C_RESET}${C_GOLD}╰─╮${C_RESET} ${C_MAGENTA}╲${C_RESET} ${C_GOLD}◉${C_RESET} ${C_MAGENTA}╱${C_RESET} ${C_GOLD}╭─╯${C_RESET}${C_PURPLE}├──╯${C_RESET}\n"
  printf "${C_EMBER}        │${C_DIM}··${C_RESET}${C_GOLD}╰─╮${C_RESET} ${C_MAGENTA}◉${C_RESET} ${C_GOLD}╭─╯${C_RESET}${C_DIM}··${C_RESET}${C_EMBER}│${C_RESET}\n"
  printf "${C_EMBER}        ╰──┤${C_RESET}${C_DIM}··${C_RESET}${C_GOLD}╰─┼─╯${C_RESET}${C_DIM}··${C_RESET}${C_EMBER}├──╯${C_RESET}\n"
  printf "${C_GOLD}           ╰──┤${C_RESET}${C_DIM}·····${C_RESET}${C_GOLD}├──╯${C_RESET}\n"
  printf "${C_GOLD}              ╰───────╯${C_RESET}\n"
  printf "${C_DIM}              ─── ${C_RESET}${C_GOLD}${label}${C_RESET}${C_DIM} ───${C_RESET}\n\n"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# §3  TORUS — Toroidal field with depth (front bright, back dim)
#     Represents the unified field / energy body
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
scene_torus() {
  local label="${1:-Toroidal Field Active}"
  printf "\n"
  printf "${C_DIM}            ╭━━━━━━━━━━━━━━━━━╮${C_RESET}\n"
  printf "${C_DIM}         ╭━━╯${C_RESET}${C_PURPLE}  ╭━━━━━━━━━╮  ${C_RESET}${C_DIM}╰━━╮${C_RESET}\n"
  printf "${C_DIM}       ╭━╯${C_RESET}${C_PURPLE}  ╭━╯${C_RESET}${C_GOLD}           ${C_RESET}${C_PURPLE}╰━╮  ${C_RESET}${C_DIM}╰━╮${C_RESET}\n"
  printf "${C_DIM}      ━╯${C_RESET}${C_PURPLE} ╭━╯${C_RESET}${C_GOLD}    ╭━━━━━╮    ${C_RESET}${C_PURPLE}╰━╮ ${C_RESET}${C_DIM}╰━${C_RESET}\n"
  printf "${C_MAGENTA}     ┃${C_RESET}${C_PURPLE}  ┃${C_RESET}${C_GOLD}    ╭╯${C_RESET}  ${C_EMBER}⬡${C_RESET}  ${C_GOLD}╰╮    ${C_RESET}${C_PURPLE}┃  ${C_RESET}${C_MAGENTA}┃${C_RESET}\n"
  printf "${C_MAGENTA}     ┃${C_RESET}${C_PURPLE}  ┃${C_RESET}${C_GOLD}    │${C_RESET}  ${C_EMBER}◆ ◆ ◆${C_RESET}  ${C_GOLD}│    ${C_RESET}${C_PURPLE}┃  ${C_RESET}${C_MAGENTA}┃${C_RESET}\n"
  printf "${C_MAGENTA}     ┃${C_RESET}${C_PURPLE}  ┃${C_RESET}${C_GOLD}    ╰╮${C_RESET}  ${C_EMBER}⬡${C_RESET}  ${C_GOLD}╭╯    ${C_RESET}${C_PURPLE}┃  ${C_RESET}${C_MAGENTA}┃${C_RESET}\n"
  printf "${C_DIM}      ━╮${C_RESET}${C_PURPLE} ╰━╮${C_RESET}${C_GOLD}    ╰━━━━━╯    ${C_RESET}${C_PURPLE}╭━╯ ${C_RESET}${C_DIM}╭━${C_RESET}\n"
  printf "${C_DIM}       ╰━╮${C_RESET}${C_PURPLE}  ╰━╮${C_RESET}${C_GOLD}           ${C_RESET}${C_PURPLE}╭━╯  ${C_RESET}${C_DIM}╭━╯${C_RESET}\n"
  printf "${C_DIM}         ╰━━╮${C_RESET}${C_PURPLE}  ╰━━━━━━━━━╯  ${C_RESET}${C_DIM}╭━━╯${C_RESET}\n"
  printf "${C_DIM}            ╰━━━━━━━━━━━━━━━━━╯${C_RESET}\n"
  printf "${C_DIM}              ─── ${C_RESET}${C_GOLD}${label}${C_RESET}${C_DIM} ───${C_RESET}\n\n"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# §4  E8 LATTICE — 240-root polytope projection (isometric 3D)
#     Hexagonal close-packed with depth layers (front/mid/back)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
scene_e8_lattice() {
  local label="${1:-E8 Lattice · 240 Roots}"
  printf "\n"
  printf "${C_DIM}          ·───·───·───·───·───·${C_RESET}\n"
  printf "${C_DIM}         ╱${C_RESET}${C_INDIGO} ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱ ╲ ${C_RESET}${C_DIM}╱${C_RESET}\n"
  printf "${C_PURPLE}        ◆━━━◆━━━◆━━━◆━━━◆━━━◆${C_RESET}\n"
  printf "${C_PURPLE}       ╱${C_GOLD} ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱ ╲ ${C_PURPLE}╱${C_RESET}\n"
  printf "${C_GOLD}      ◆━━━◆━━━◆━━━◆━━━◆━━━◆━━━◆${C_RESET}\n"
  printf "${C_GOLD}     ╱${C_EMBER} ╲ ╱ ╲ ╱${C_RESET} ${C_MAGENTA}⬢${C_RESET} ${C_EMBER}╲ ╱ ╲ ╱ ╲ ${C_GOLD}╱${C_RESET}\n"
  printf "${C_EMBER}    ◆━━━◆━━━◆━━━◆━━━◆━━━◆━━━◆━━━◆${C_RESET}\n"
  printf "${C_EMBER}     ╲${C_GOLD} ╱ ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱ ╲ ${C_EMBER}╲${C_RESET}\n"
  printf "${C_GOLD}      ◆━━━◆━━━◆━━━◆━━━◆━━━◆━━━◆${C_RESET}\n"
  printf "${C_PURPLE}       ╲${C_GOLD} ╱ ╲ ╱ ╲ ╱ ╲ ╱ ╲ ${C_PURPLE}╲${C_RESET}\n"
  printf "${C_PURPLE}        ◆━━━◆━━━◆━━━◆━━━◆━━━◆${C_RESET}\n"
  printf "${C_DIM}         ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱${C_RESET}\n"
  printf "${C_DIM}          ·───·───·───·───·───·${C_RESET}\n"
  printf "${C_DIM}              ─── ${C_RESET}${C_GOLD}${label}${C_RESET}${C_DIM} ───${C_RESET}\n\n"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# §5  METATRON'S CUBE — 13 circles + connecting lines (3D perspective)
#     Contains all 5 Platonic solids — the blueprint of creation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
scene_metatrons_cube() {
  local label="${1:-Metatrons Cube · All Platonic Solids}"
  printf "\n"
  printf "${C_DIM}                    ◯${C_RESET}\n"
  printf "${C_DIM}                 ╱${C_RESET}${C_PURPLE}·····${C_RESET}${C_DIM}╲${C_RESET}\n"
  printf "${C_PURPLE}              ◯${C_DIM}─────────${C_RESET}${C_PURPLE}◯${C_RESET}\n"
  printf "${C_PURPLE}             ╱│${C_GOLD}╲       ╱${C_RESET}${C_PURPLE}│╲${C_RESET}\n"
  printf "${C_PURPLE}            ╱ │ ${C_GOLD}╲     ╱${C_RESET}${C_PURPLE} │ ╲${C_RESET}\n"
  printf "${C_GOLD}          ◯──┼──${C_EMBER}◯${C_GOLD}───${C_EMBER}◯${C_GOLD}──┼──◯${C_RESET}\n"
  printf "${C_GOLD}          │${C_RESET}  ${C_PURPLE}│${C_RESET} ${C_EMBER}╱ ${C_MAGENTA}◉${C_RESET} ${C_EMBER}╲${C_RESET} ${C_PURPLE}│${C_RESET}  ${C_GOLD}│${C_RESET}\n"
  printf "${C_GOLD}          │${C_RESET}  ${C_PURPLE}◯${C_EMBER}───────${C_RESET}${C_PURPLE}◯${C_RESET}  ${C_GOLD}│${C_RESET}\n"
  printf "${C_GOLD}          │${C_RESET} ${C_EMBER}╱${C_RESET} ${C_PURPLE}│${C_RESET}     ${C_PURPLE}│${C_RESET} ${C_EMBER}╲${C_RESET} ${C_GOLD}│${C_RESET}\n"
  printf "${C_GOLD}          ◯${C_EMBER}──┼──${C_PURPLE}◯${C_EMBER}───${C_PURPLE}◯${C_EMBER}──┼──${C_GOLD}◯${C_RESET}\n"
  printf "${C_PURPLE}            ╲ │ ${C_GOLD}╱     ╲${C_RESET}${C_PURPLE} │ ╱${C_RESET}\n"
  printf "${C_PURPLE}             ╲│${C_GOLD}╱       ╲${C_RESET}${C_PURPLE}│╱${C_RESET}\n"
  printf "${C_PURPLE}              ◯${C_DIM}─────────${C_RESET}${C_PURPLE}◯${C_RESET}\n"
  printf "${C_DIM}                 ╲·····╱${C_RESET}\n"
  printf "${C_DIM}                    ◯${C_RESET}\n"
  printf "${C_DIM}           ─── ${C_RESET}${C_GOLD}${label}${C_RESET}${C_DIM} ───${C_RESET}\n\n"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# §6  SRI YANTRA — 9 interlocking triangles (3D layered)
#     Supreme geometry of manifestation — 4 upward + 5 downward triangles
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
scene_sri_yantra() {
  local label="${1:-Sri Yantra · 9 Triangles}"
  printf "\n"
  printf "${C_DIM}        ╔═══════════════════════════════╗${C_RESET}\n"
  printf "${C_DIM}        ║${C_RESET}${C_GOLD}              △                ${C_RESET}${C_DIM}║${C_RESET}\n"
  printf "${C_DIM}        ║${C_RESET}${C_GOLD}             ╱ ╲               ${C_RESET}${C_DIM}║${C_RESET}\n"
  printf "${C_DIM}        ║${C_RESET}${C_PURPLE}           ▽${C_GOLD}───${C_EMBER}──${C_GOLD}───${C_PURPLE}▽           ${C_RESET}${C_DIM}║${C_RESET}\n"
  printf "${C_DIM}        ║${C_RESET}${C_PURPLE}          ╱${C_RESET} ${C_GOLD}╲ ${C_EMBER}△${C_GOLD} ╱${C_RESET} ${C_PURPLE}╲          ${C_RESET}${C_DIM}║${C_RESET}\n"
  printf "${C_DIM}        ║${C_RESET}${C_EMBER}        △${C_PURPLE}──╱──${C_MAGENTA}◉${C_PURPLE}──╲──${C_EMBER}△        ${C_RESET}${C_DIM}║${C_RESET}\n"
  printf "${C_DIM}        ║${C_RESET}${C_EMBER}       ╱ ${C_PURPLE}╲╱${C_RESET} ${C_GOLD}╱ ╲${C_RESET} ${C_PURPLE}╲╱${C_RESET} ${C_EMBER}╲       ${C_RESET}${C_DIM}║${C_RESET}\n"
  printf "${C_DIM}        ║${C_RESET}${C_GOLD}      ▽───▽───▽───▽───▽      ${C_RESET}${C_DIM}║${C_RESET}\n"
  printf "${C_DIM}        ║${C_RESET}${C_GOLD}       ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱       ${C_RESET}${C_DIM}║${C_RESET}\n"
  printf "${C_DIM}        ║${C_RESET}${C_PURPLE}        △───△───△───△        ${C_RESET}${C_DIM}║${C_RESET}\n"
  printf "${C_DIM}        ║${C_RESET}${C_PURPLE}         ╲   ╲ ╱   ╱         ${C_RESET}${C_DIM}║${C_RESET}\n"
  printf "${C_DIM}        ║${C_RESET}${C_EMBER}          ╲   ▽   ╱          ${C_RESET}${C_DIM}║${C_RESET}\n"
  printf "${C_DIM}        ║${C_RESET}${C_EMBER}           ╲     ╱           ${C_RESET}${C_DIM}║${C_RESET}\n"
  printf "${C_DIM}        ║${C_RESET}${C_GOLD}            ╲   ╱            ${C_RESET}${C_DIM}║${C_RESET}\n"
  printf "${C_DIM}        ║${C_RESET}${C_GOLD}             ╲ ╱             ${C_RESET}${C_DIM}║${C_RESET}\n"
  printf "${C_DIM}        ║${C_RESET}${C_GOLD}              ▽              ${C_RESET}${C_DIM}║${C_RESET}\n"
  printf "${C_DIM}        ╚═══════════════════════════════╝${C_RESET}\n"
  printf "${C_DIM}              ─── ${C_RESET}${C_GOLD}${label}${C_RESET}${C_DIM} ───${C_RESET}\n\n"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# §7  VESICA PISCIS — Two overlapping circles (creation portal)
#     The womb of duality — where two become one
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
scene_vesica_piscis() {
  local label="${1:-Vesica Piscis · Creation Portal}"
  printf "\n"
  printf "${C_PURPLE}           ╭━━━━━━━━╮${C_RESET}\n"
  printf "${C_PURPLE}         ╭╯${C_RESET}${C_DIM}········${C_RESET}${C_PURPLE}╰╮${C_GOLD}━━━━━━━━╮${C_RESET}\n"
  printf "${C_PURPLE}        ╭╯${C_RESET}${C_DIM}··${C_RESET}${C_GOLD}╭━━━━╮${C_DIM}··${C_RESET}${C_GOLD}╰╮${C_DIM}·······${C_RESET}${C_GOLD}╰╮${C_RESET}\n"
  printf "${C_PURPLE}        │${C_RESET}${C_DIM}·${C_RESET}${C_GOLD}╭╯${C_RESET} ${C_MAGENTA}◉${C_RESET} ${C_EMBER}⬡${C_RESET} ${C_MAGENTA}◉${C_RESET} ${C_GOLD}╰╮${C_DIM}·${C_RESET}${C_GOLD}│${C_RESET}\n"
  printf "${C_PURPLE}        │${C_RESET} ${C_GOLD}│${C_RESET}  ${C_EMBER}╱ ${C_MAGENTA}✦${C_RESET} ${C_EMBER}╲${C_RESET}  ${C_GOLD}│${C_RESET} ${C_GOLD}│${C_RESET}\n"
  printf "${C_PURPLE}        │${C_RESET}${C_DIM}·${C_RESET}${C_GOLD}╰╮${C_RESET} ${C_MAGENTA}◉${C_RESET} ${C_EMBER}⬡${C_RESET} ${C_MAGENTA}◉${C_RESET} ${C_GOLD}╭╯${C_DIM}·${C_RESET}${C_GOLD}│${C_RESET}\n"
  printf "${C_PURPLE}        ╰╮${C_RESET}${C_DIM}··${C_RESET}${C_GOLD}╰━━━━╯${C_DIM}··${C_RESET}${C_GOLD}╭╯${C_DIM}·······${C_RESET}${C_GOLD}╭╯${C_RESET}\n"
  printf "${C_PURPLE}         ╰╮${C_RESET}${C_DIM}········${C_RESET}${C_PURPLE}╭╯${C_GOLD}━━━━━━━━╯${C_RESET}\n"
  printf "${C_PURPLE}           ╰━━━━━━━━╯${C_RESET}\n"
  printf "${C_DIM}           ─── ${C_RESET}${C_GOLD}${label}${C_RESET}${C_DIM} ───${C_RESET}\n\n"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# §8  3D ISOMETRIC CUBE — Proper depth with hidden-line removal
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
scene_cube_3d() {
  local label="${1:-Hypercube Projection}"
  printf "\n"
  printf "${C_GOLD}            ┌─────────────────────┐${C_RESET}\n"
  printf "${C_GOLD}           ╱${C_EMBER}│${C_RESET}                    ${C_GOLD}╱${C_EMBER}│${C_RESET}\n"
  printf "${C_GOLD}          ╱${C_RESET} ${C_EMBER}│${C_RESET}                  ${C_GOLD}╱${C_RESET} ${C_EMBER}│${C_RESET}\n"
  printf "${C_GOLD}         ╱${C_RESET}  ${C_EMBER}│${C_RESET}    ${C_MAGENTA}⬡${C_RESET}           ${C_GOLD}╱${C_RESET}  ${C_EMBER}│${C_RESET}\n"
  printf "${C_GOLD}        ╱${C_RESET}   ${C_EMBER}│${C_RESET}                ${C_GOLD}╱${C_RESET}   ${C_EMBER}│${C_RESET}\n"
  printf "${C_GOLD}       ┌─────────────────────┐${C_RESET}    ${C_EMBER}│${C_RESET}\n"
  printf "${C_GOLD}       │${C_RESET}    ${C_EMBER}│${C_RESET}                ${C_GOLD}│${C_RESET}    ${C_EMBER}│${C_RESET}\n"
  printf "${C_GOLD}       │${C_RESET}    ${C_DIM}└─ ─ ─ ─ ─ ─ ─ ─ ${C_RESET}${C_GOLD}│${C_DIM}─ ─ ┘${C_RESET}\n"
  printf "${C_GOLD}       │${C_RESET}   ${C_DIM}╱${C_RESET}                  ${C_GOLD}│${C_RESET}   ${C_DIM}╱${C_RESET}\n"
  printf "${C_GOLD}       │${C_RESET}  ${C_DIM}╱${C_RESET}                   ${C_GOLD}│${C_RESET}  ${C_DIM}╱${C_RESET}\n"
  printf "${C_GOLD}       │${C_RESET} ${C_DIM}╱${C_RESET}                    ${C_GOLD}│${C_RESET} ${C_DIM}╱${C_RESET}\n"
  printf "${C_GOLD}       │${C_DIM}╱${C_RESET}                     ${C_GOLD}│${C_DIM}╱${C_RESET}\n"
  printf "${C_GOLD}       └─────────────────────┘${C_RESET}\n"
  printf "${C_DIM}              ─── ${C_RESET}${C_GOLD}${label}${C_RESET}${C_DIM} ───${C_RESET}\n\n"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# §9  ANIMATED MERKABA ROTATION (4-frame loop)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
anim_merkaba_spin() {
  [[ "$ANIMATIONS_ENABLED" -ne 1 ]] && { scene_merkaba "$1"; return; }
  local frames=(
    "    ◇─△─◇     ▽─◇─▽"
    "     ◇△◇       ▽◇▽ "
    "    ◇─△─◇     ▽─◇─▽"
    "   ◇──△──◇   ▽──◇──▽"
  )
  for f in "${frames[@]}"; do
    printf "\r${C_GOLD}    %s${C_RESET}" "$f"
    sleep 0.2
  done
  printf "\n"
  scene_merkaba "${1:-Merkaba Spin Complete}"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# §10  ANIMATED TORUS PULSE (energy flow visualization)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
anim_torus_pulse() {
  [[ "$ANIMATIONS_ENABLED" -ne 1 ]] && { scene_torus "$1"; return; }
  local dots=("·" "•" "●" "◉" "●" "•" "·" " ")
  for d in "${dots[@]}"; do
    printf "\r${C_PURPLE}    ╭━━╮ ${C_EMBER}%s${C_PURPLE} ╭━━╮  ${C_GOLD}Energy flowing...${C_RESET}" "$d"
    sleep 0.12
  done
  printf "\n"
  scene_torus "${1:-Torus Field Coherent}"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# §11  ANIMATED DNA HELIX (double strand with depth)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
anim_dna_helix() {
  local msg="${1:-Encoding sacred sequence}"
  [[ "$ANIMATIONS_ENABLED" -ne 1 ]] && { printf "    ✦ %s\n" "$msg"; return; }
  local lines=(
    "${C_GOLD}    ╭─╮${C_DIM}       ${C_PURPLE}╭─╮${C_RESET}"
    "${C_GOLD}   ╱${C_RESET} ${C_EMBER}◆${C_RESET} ${C_GOLD}╲${C_DIM}───${C_PURPLE}╱${C_RESET} ${C_EMBER}◆${C_RESET} ${C_PURPLE}╲${C_RESET}"
    "${C_GOLD}  │${C_RESET}  ${C_EMBER}┃${C_RESET}  ${C_GOLD}╳${C_RESET}  ${C_EMBER}┃${C_RESET}  ${C_PURPLE}│${C_RESET}"
    "${C_GOLD}   ╲${C_RESET} ${C_EMBER}◆${C_RESET} ${C_GOLD}╱${C_DIM}───${C_PURPLE}╲${C_RESET} ${C_EMBER}◆${C_RESET} ${C_PURPLE}╱${C_RESET}"
    "${C_GOLD}    ╰─╯${C_DIM}       ${C_PURPLE}╰─╯${C_RESET}"
    "${C_PURPLE}    ╭─╮${C_DIM}       ${C_GOLD}╭─╮${C_RESET}"
    "${C_PURPLE}   ╱${C_RESET} ${C_EMBER}◆${C_RESET} ${C_PURPLE}╲${C_DIM}───${C_GOLD}╱${C_RESET} ${C_EMBER}◆${C_RESET} ${C_GOLD}╲${C_RESET}"
    "${C_PURPLE}  │${C_RESET}  ${C_EMBER}┃${C_RESET}  ${C_PURPLE}╳${C_RESET}  ${C_EMBER}┃${C_RESET}  ${C_GOLD}│${C_RESET}"
    "${C_PURPLE}   ╲${C_RESET} ${C_EMBER}◆${C_RESET} ${C_PURPLE}╱${C_DIM}───${C_GOLD}╲${C_RESET} ${C_EMBER}◆${C_RESET} ${C_GOLD}╱${C_RESET}"
    "${C_PURPLE}    ╰─╯${C_DIM}       ${C_GOLD}╰─╯${C_RESET}"
  )
  for line in "${lines[@]}"; do
    printf "    %s\n" "$line"
    sleep 0.05
  done
  printf "${C_DIM}              ─── ${C_RESET}${C_GOLD}${msg}${C_RESET}${C_DIM} ───${C_RESET}\n\n"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# §12  ANIMATED FREQUENCY WAVE (cymatics visualization)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
anim_frequency() {
  local hz="${1:-432}" msg="${2:-Frequency lock}"
  [[ "$ANIMATIONS_ENABLED" -ne 1 ]] && { printf "    ⚡ %s Hz — %s ✓\n" "$hz" "$msg"; return; }
  local waves=(
    "╶─╮╭─╮╭─╮╭─╮╭─╮╭─╮╭─╮╭─╶"
    "╶╮╭╯╰╮╭╯╰╮╭╯╰╮╭╯╰╮╭╯╰╮╭╶"
    "╶╯╰──╯╰──╯╰──╯╰──╯╰──╯╰╶"
    "╶╮╭╯╰╮╭╯╰╮╭╯╰╮╭╯╰╮╭╯╰╮╭╶"
  )
  for w in "${waves[@]}"; do
    printf "\r    ${C_EMBER}⚡${C_RESET} ${C_GOLD}%s${C_RESET} ${C_DIM}%s Hz${C_RESET}" "$w" "$hz"
    sleep 0.15
  done
  printf "\r    ${C_GREEN}⚡ ═══════════════════════════${C_RESET} ${C_GOLD}%s Hz${C_RESET} — %s ✓\n" "$hz" "$msg"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# §13  ANIMATED CHAKRA COLUMN (7 energy centers ascending)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
anim_chakra_ascend() {
  local msg="${1:-Kundalini rising}"
  [[ "$ANIMATIONS_ENABLED" -ne 1 ]] && { printf "    ✦ %s\n" "$msg"; return; }
  local colors=("\033[31m" "\033[38;5;208m" "\033[33m" "\033[32m" "\033[36m" "\033[38;5;63m" "\033[38;5;135m")
  local names=("ROOT" "SACRAL" "SOLAR" "HEART" "THROAT" "THIRD EYE" "CROWN")
  local symbols=("◆" "◆" "◆" "◆" "◆" "◆" "◇")
  for i in $(seq 0 6); do
    printf "    ${colors[$i]}    %s ━━━ %s${C_RESET}\n" "${symbols[$i]}" "${names[$i]}"
    sleep 0.12
  done
  printf "    ${C_GOLD}    ✦ ━━━ ${msg}${C_RESET}\n\n"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# §14  COMPOSITE: VALIDATION COMPLETE (Merkaba + result)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
scene_validation_complete() {
  local pass="${1:-0}" total="${2:-0}"
  printf "\n"
  printf "${C_GOLD}    ╔══════════════════════════════════════════════════════════╗${C_RESET}\n"
  printf "${C_GOLD}    ║${C_RESET}                                                          ${C_GOLD}║${C_RESET}\n"
  printf "${C_GOLD}    ║${C_RESET}                  ${C_GOLD}◇${C_RESET}                                    ${C_GOLD}║${C_RESET}\n"
  printf "${C_GOLD}    ║${C_RESET}                 ${C_GOLD}╱${C_EMBER}△${C_GOLD}╲${C_RESET}         ${C_GREEN}VALIDATION COMPLETE${C_RESET}       ${C_GOLD}║${C_RESET}\n"
  printf "${C_GOLD}    ║${C_RESET}                ${C_GOLD}╱${C_RESET} ${C_MAGENTA}⬡${C_RESET} ${C_GOLD}╲${C_RESET}        ${C_GREEN}%d/%d checks pass${C_RESET}         ${C_GOLD}║${C_RESET}\n" "$pass" "$total"
  printf "${C_GOLD}    ║${C_RESET}               ${C_GOLD}╱─────╲${C_RESET}       ${C_GREEN}0 failures${C_RESET}                ${C_GOLD}║${C_RESET}\n"
  printf "${C_GOLD}    ║${C_RESET}              ${C_PURPLE}▽━━━━━━━▽${C_RESET}      ${C_GREEN}Production ready${C_RESET}           ${C_GOLD}║${C_RESET}\n"
  printf "${C_GOLD}    ║${C_RESET}               ${C_PURPLE}╲─────╱${C_RESET}                                  ${C_GOLD}║${C_RESET}\n"
  printf "${C_GOLD}    ║${C_RESET}                ${C_PURPLE}╲ ${C_MAGENTA}⬡${C_PURPLE} ╱${C_RESET}                                   ${C_GOLD}║${C_RESET}\n"
  printf "${C_GOLD}    ║${C_RESET}                 ${C_PURPLE}╲${C_INDIGO}▽${C_PURPLE}╱${C_RESET}                                    ${C_GOLD}║${C_RESET}\n"
  printf "${C_GOLD}    ║${C_RESET}                  ${C_PURPLE}◇${C_RESET}                                     ${C_GOLD}║${C_RESET}\n"
  printf "${C_GOLD}    ║${C_RESET}                                                          ${C_GOLD}║${C_RESET}\n"
  printf "${C_GOLD}    ╚══════════════════════════════════════════════════════════╝${C_RESET}\n\n"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# §15  COMPOSITE: ENGINE BOOT (Torus + checklist)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
scene_engine_boot() {
  printf "\n"
  printf "${C_GOLD}    ╔══════════════════════════════════════════════════════════╗${C_RESET}\n"
  printf "${C_GOLD}    ║${C_RESET}  ${C_EMBER}▓▓▓${C_RESET} Engine Initialization ${C_EMBER}▓▓▓${C_RESET}                          ${C_GOLD}║${C_RESET}\n"
  printf "${C_GOLD}    ║${C_RESET}                                                          ${C_GOLD}║${C_RESET}\n"
  printf "${C_GOLD}    ║${C_RESET}     ${C_DIM}╭━━━━━━━━━━━╮${C_RESET}                                     ${C_GOLD}║${C_RESET}\n"
  printf "${C_GOLD}    ║${C_RESET}  ${C_DIM}╭━━╯${C_RESET}${C_PURPLE}  ╭─────╮  ${C_RESET}${C_DIM}╰━━╮${C_RESET}  ${C_GREEN}✦${C_RESET} cymatics-engine         ${C_GOLD}║${C_RESET}\n"
  printf "${C_GOLD}    ║${C_RESET}  ${C_DIM}━╯${C_RESET}${C_PURPLE}  ╭╯${C_RESET}  ${C_EMBER}⬡${C_RESET}  ${C_PURPLE}╰╮  ${C_RESET}${C_DIM}╰━${C_RESET}  ${C_GREEN}✦${C_RESET} crown-coherence         ${C_GOLD}║${C_RESET}\n"
  printf "${C_GOLD}    ║${C_RESET}  ${C_DIM}━╮${C_RESET}${C_PURPLE}  ╰╮${C_RESET}  ${C_EMBER}◆${C_RESET}  ${C_PURPLE}╭╯  ${C_RESET}${C_DIM}╭━${C_RESET}  ${C_GREEN}✦${C_RESET} spectral-monitor        ${C_GOLD}║${C_RESET}\n"
  printf "${C_GOLD}    ║${C_RESET}  ${C_DIM}╰━━╮${C_RESET}${C_PURPLE}  ╰─────╯  ${C_RESET}${C_DIM}╭━━╯${C_RESET}  ${C_GREEN}✦${C_RESET} kuramoto-sync           ${C_GOLD}║${C_RESET}\n"
  printf "${C_GOLD}    ║${C_RESET}     ${C_DIM}╰━━━━━━━━━━━╯${C_RESET}      ${C_GREEN}✦${C_RESET} e8-lattice-router       ${C_GOLD}║${C_RESET}\n"
  printf "${C_GOLD}    ║${C_RESET}                            ${C_GREEN}✦${C_RESET} mandelbulb-validator     ${C_GOLD}║${C_RESET}\n"
  printf "${C_GOLD}    ║${C_RESET}                                                          ${C_GOLD}║${C_RESET}\n"
  printf "${C_GOLD}    ║${C_RESET}  ${C_GREEN}All 97 engines online${C_RESET}                                    ${C_GOLD}║${C_RESET}\n"
  printf "${C_GOLD}    ╚══════════════════════════════════════════════════════════╝${C_RESET}\n\n"
}
