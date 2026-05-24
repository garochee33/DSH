# Formatting Protocol — Sovereign Visual Standard

**Version:** 1.0.0  
**Scope:** All repos, agents, scripts, logs, reports, protocols, dashboards  
**Effective:** 2026-05-23

---

## Purpose

Standardize terminal and markdown output formatting using Unicode box-drawing, 3D ASCII art, and cinematic animations for:
- Instant visual scanning of pass/fail/status
- Professional, sovereign aesthetic across all outputs
- Consistent branding across 461 skills, 97 engines, 20+ repos

---

## §1 Box Characters Reference

| Char | Name | Use |
|------|------|-----|
| ╔ ╗ ╚ ╝ | Double corners | Report headers/footers |
| ║ | Double vertical | Side borders |
| ═ | Double horizontal | Top/bottom borders |
| ┌ ┐ └ ┘ | Light corners | Phase/step boxes |
| │ | Light vertical | Phase borders |
| ─ | Light horizontal | Phase borders |
| ━ | Heavy horizontal | Section dividers |
| ┃ | Heavy vertical | Emphasis |
| ┏ ┓ ┗ ┛ | Heavy corners | Agent output headers |
| ┣ ┫ | Heavy T-junctions | Sub-sections |

---

## §2 Report Header

```
╔══════════════════════════════════════════════════════════════════════╗
║  TITLE — Subtitle                                                  ║
║  Date: YYYY-MM-DDTHH:MM:SSZ | Scope: description                  ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## §3 Section Divider

```
━━━ §N SECTION TITLE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## §4 Result Footer

```
╔══════════════════════════════════════════════════════════════════════╗
║  PASS: NN  │ FAIL: NN  │ WARN: NN  │ TOTAL: NN                    ║
║  ██████████████████████████████████████████████████████████████████ ║
║  ██  VERDICT: ✅ ALL CLEAR — PRODUCTION READY                   ██ ║
║  ██████████████████████████████████████████████████████████████████ ║
║  Evidence: Run #N │ timestamp │ Operator: EGD33                    ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## §5 Phase/Step Box (from DSH setup)

```
    ┌─────────────────────────────────────────────┐
    │  ▶  [3/21]  Security Hardening              │
    └─────────────────────────────────────────────┘
    ▐████████████░░░░░░░░░░░░░░░░░░░░░░▌  35%
```

---

## §6 Status Indicators

```
✅ Pass / Success / Active / Complete
❌ Fail / Error / Missing / Blocked
⚠️  Warning / Degraded / Partial
🔄 In Progress / Pending
🚫 Disabled / Severed
✦  Phase complete (cinematic)
▸  Info / action item
●  Pulse dot (animated)
```

---

## §7 3D ASCII Art — Sacred Geometry Scenes

### 7.1 Merkaba (Star Tetrahedron)
```
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
```

### 7.2 E8 Lattice Node
```
        ◆───◆───◆───◆───◆
       ╱ ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱ ╲
      ◆───◆───◆───◆───◆───◆
       ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱
        ◆───◆───◆───◆───◆
       ╱ ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱ ╲
      ◆───◆───◆───◆───◆───◆
       ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱
        ◆───◆───◆───◆───◆
```

### 7.3 Flower of Life
```
           ╭───╮
        ╭──┤   ├──╮
     ╭──┤  ╰─┬─╯  ├──╮
     │  ╰──┬─┼─┬──╯  │
     ╰──┬──╯ │ ╰──┬──╯
        ╰──┬─┼─┬──╯
           ╰─┴─╯
```

### 7.4 Torus Field
```
          ╭━━━━━━━━━━━╮
       ╭━━╯  ╭─────╮  ╰━━╮
     ╭━╯   ╭─╯     ╰─╮   ╰━╮
    ━╯    ╭─╯    ◆    ╰─╮    ╰━
    ━╮    ╰─╮         ╭─╯    ╭━
     ╰━╮   ╰─╮     ╭─╯   ╭━╯
       ╰━━╮  ╰─────╯  ╭━━╯
          ╰━━━━━━━━━━━╯
```

### 7.5 Cube / Metatron Frame
```
        ┌───────────────┐
       ╱│              ╱│
      ╱ │             ╱ │
     ┌───────────────┐  │
     │  │            │  │
     │  └────────────│──┘
     │ ╱             │ ╱
     │╱              │╱
     └───────────────┘
```

### 7.6 Vesica Piscis
```
       ╭━━━━━━╮╭━━━━━━╮
      ╱        ╲╲       ╲
     │    ◯    ││   ◯    │
      ╲       ╱╱        ╱
       ╰━━━━━━╯╰━━━━━━╯
```

### 7.7 Spiral / Golden Ratio
```
     ╭━━━━━━━━━━━━━━━━━━━━━╮
     │  ╭━━━━━━━━━━━━━━╮   │
     │  │  ╭━━━━━━━╮   │   │
     │  │  │  ╭━━╮ │   │   │
     │  │  │  │◆ │ │   │   │
     │  │  │  ╰──╯ │   │   │
     │  │  ╰━━━━━━━╯   │   │
     │  ╰━━━━━━━━━━━━━━╯   │
     ╰━━━━━━━━━━━━━━━━━━━━━╯
```

---

## §8 Animation Loops (Bash)

### 8.1 Spinner
```bash
spin() {
  local frames=("◐" "◓" "◑" "◒")
  local msg="$1"
  for f in "${frames[@]}"; do
    printf "\r    %s %s" "$f" "$msg"
    sleep 0.08
  done
  printf "\r    ✦ %s done\n" "$msg"
}
```

### 8.2 Pulse Dots
```bash
pulse() {
  printf "    ▸ %s" "$1"
  for _ in 1 2 3; do printf "●"; sleep 0.15; done
  printf "\n"
}
```

### 8.3 Progress Bar
```bash
progress_bar() {
  local step=$1 total=$2 width=34
  local filled=$((step * width / total))
  local empty=$((width - filled))
  printf "    ▐%s%s▌ %3d%%" \
    "$(printf '%*s' $filled '' | tr ' ' '█')" \
    "$(printf '%*s' $empty '' | tr ' ' '░')" \
    $((step * 100 / total))
}
```

### 8.4 Waveform
```bash
wave() {
  local frames=("∿∿∿∿∿∿∿∿" "≋≋≋≋≋≋≋≋" "∿∿∿∿∿∿∿∿" "〰〰〰〰")
  for f in "${frames[@]}"; do
    printf "\r    ⚡ %s %s" "$f" "$1"
    sleep 0.12
  done
  printf "\r    ⚡ ════════ %s ✓\n" "$1"
}
```

### 8.5 DNA Helix
```bash
helix() {
  local frames=(
    "  ╭─╮   ╭─╮"
    " ╱ ╳ ╲ ╱ ╳ ╲"
    "╱─────╳─────╲"
    " ╲ ╳ ╱ ╲ ╳ ╱"
    "  ╰─╯   ╰─╯"
  )
  for line in "${frames[@]}"; do
    printf "    %s\n" "$line"
    sleep 0.06
  done
}
```

### 8.6 Orbit
```bash
orbit() {
  local frames=("◜" "◝" "◞" "◟")
  local msg="$1"; local i=0
  while [ $i -lt 8 ]; do
    printf "\r    %s %s" "${frames[$((i%4))]}" "$msg"
    sleep 0.1; i=$((i+1))
  done
  printf "\r    ◉ %s\n" "$msg"
}
```

### 8.7 3D Cube Rotation
```bash
cube_rotate() {
  local f1="    ┌──┐  " f2="    │◆ │╱ " f3="    └──┘╱  "
  local f4="     ╱┌──┐" f5="    ╱ │ ◆│" f6="     ╱└──┘"
  printf "%s\n%s\n%s\n" "$f1" "$f2" "$f3"; sleep 0.2
  printf "\033[3A"
  printf "%s\n%s\n%s\n" "$f4" "$f5" "$f6"; sleep 0.2
  printf "\033[3A"
  printf "%s\n%s\n%s\n" "$f1" "$f2" "$f3"
}
```

---

## §9 Color Palette

```bash
C_RESET="$(tput sgr0)"
C_CYAN="$(tput setaf 6)"       # Headers, info
C_GREEN="$(tput setaf 2)"      # Success, pass
C_YELLOW="$(tput setaf 3)"     # Warnings, pulse
C_MAGENTA="$(tput setaf 178)"  # Sacred geometry, spinners
C_RED="$(tput setaf 1)"        # Errors, fail
C_DIM="$(tput dim)"            # Subtitles, metadata
C_BOLD="$(tput bold)"          # Emphasis
```

---

## §10 Banner Templates

### 10.1 DSH
```
    ██████╗  ███████╗ ██╗  ██╗
    ██╔══██╗ ██╔════╝ ██║  ██║
    ██║  ██║ ███████╗ ███████║
    ██║  ██║ ╚════██║ ██╔══██║
    ██████╔╝ ███████║ ██║  ██║
    ╚═════╝  ╚══════╝ ╚═╝  ╚═╝
```

### 10.2 TRINITY
```
    ████████╗██████╗ ██╗███╗   ██╗██╗████████╗██╗   ██╗
    ╚══██╔══╝██╔══██╗██║████╗  ██║██║╚══██╔══╝╚██╗ ██╔╝
       ██║   ██████╔╝██║██╔██╗ ██║██║   ██║    ╚████╔╝
       ██║   ██╔══██╗██║██║╚██╗██║██║   ██║     ╚██╔╝
       ██║   ██║  ██║██║██║ ╚████║██║   ██║      ██║
       ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚═╝   ╚═╝      ╚═╝
```

### 10.3 E8
```
    ███████╗ █████╗
    ██╔════╝██╔══██╗
    █████╗  ╚█████╔╝
    ██╔══╝  ██╔══██╗
    ███████╗╚█████╔╝
    ╚══════╝ ╚════╝
```

### 10.4 AMMA
```
     █████╗ ███╗   ███╗███╗   ███╗ █████╗
    ██╔══██╗████╗ ████║████╗ ████║██╔══██╗
    ███████║██╔████╔██║██╔████╔██║███████║
    ██╔══██║██║╚██╔╝██║██║╚██╔╝██║██╔══██║
    ██║  ██║██║ ╚═╝ ██║██║ ╚═╝ ██║██║  ██║
    ╚═╝  ╚═╝╚═╝     ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝
```

---

## §11 Composite Scene Templates

### 11.1 Validation Complete
```
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║              △                                             ║
    ║             ╱ ╲          VALIDATION COMPLETE               ║
    ║            ╱ ✦ ╲         62/62 checks pass                 ║
    ║           ╱─────╲        0 failures                        ║
    ║          ▽━━━━━━━▽       Production ready                  ║
    ║                                                            ║
    ╚══════════════════════════════════════════════════════════════╝
```

### 11.2 Phase Transition
```
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃  ◆───◆───◆───◆───◆                                       ┃
    ┃   ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱   PHASE 3 → PHASE 4                   ┃
    ┃  ◆───◆───◆───◆───◆   Lattice harmonics aligned           ┃
    ┃                                                           ┃
    ┃  ▐████████████████████████████░░░░░░░░░░▌  71%            ┃
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### 11.3 Engine Boot
```
    ╔══════════════════════════════════════════════════════════════╗
    ║  ▓▓▓ Engine Initialization ▓▓▓                             ║
    ║                                                            ║
    ║     ╭━━━━━━━━━━━╮                                         ║
    ║  ╭━━╯  ╭─────╮  ╰━━╮    cymatics-engine ........... ✦    ║
    ║  ━╯   ╭╯  ◆  ╰╮   ╰━   crown-coherence ........... ✦    ║
    ║  ━╮   ╰╮     ╭╯   ╭━   spectral-monitor ........... ✦    ║
    ║  ╰━━╮  ╰─────╯  ╭━━╯    kuramoto-sync ............. ✦    ║
    ║     ╰━━━━━━━━━━━╯                                         ║
    ║                                                            ║
    ║  All 97 engines online                                     ║
    ╚══════════════════════════════════════════════════════════════╝
```

---

## §12 Rules

1. **All validation scripts** MUST use Report Header + Section Divider + Result Footer
2. **All session logs** MUST start with Session Header box
3. **Phase transitions** SHOULD include a sacred geometry scene
4. **Completion states** SHOULD show the Merkaba or Validation Complete scene
5. **Engine boots** SHOULD show the Torus + engine checklist
6. **Section numbers** use `§N` prefix
7. **Tables** use standard markdown `|` pipes — no box-drawing in tables
8. **Width** standardize at 66 chars inside box (68 total with borders)
9. **Timestamps** always UTC ISO-8601 in headers
10. **Pass/Fail** always use ✅/❌ emoji
11. **Animations** only in interactive TTY (check `[[ -t 1 ]]`)
12. **Colors** degrade gracefully (check `tput colors`)

---

## §13 Adoption Matrix

| Scope | Status |
|-------|--------|
| Trinity Consortium (CTO validation) | ✅ Active |
| DSH sovereign-setup-mac.sh | ✅ Active |
| DSH sovereign audit | ✅ Active |
| Akashic session logs | ✅ Active |
| LAVA simulation outputs | 🔄 Adopt |
| Agent skill outputs | 🔄 Adopt |
| Paradise Estate reports | 🔄 Adopt |
| S3XYVERSE reports | 🔄 Adopt |
| All Kiro CLI sessions | ✅ Active |
| Income Loops reports | 🔄 Adopt |

---

*Maintained by: EGD33 | Last updated: 2026-05-23*
