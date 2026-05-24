"""
╔══════════════════════════════════════════════════════════════════╗
║  Box-Drawing Format Library — Sovereign Visual Standard         ║
║  Usage: from lib.box_format import *                            ║
╚══════════════════════════════════════════════════════════════════╝
"""
import sys
import time
from datetime import datetime, timezone

BOX_WIDTH = 66
ANIMATIONS = sys.stdout.isatty()

# ━━━ Colors ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if sys.stdout.isatty():
    CYAN = "\033[36m"; GREEN = "\033[32m"; YELLOW = "\033[33m"
    MAGENTA = "\033[38;5;178m"; RED = "\033[31m"; DIM = "\033[2m"
    BOLD = "\033[1m"; RESET = "\033[0m"
else:
    CYAN = GREEN = YELLOW = MAGENTA = RED = DIM = BOLD = RESET = ""


# ━━━ Box Elements ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def box_header(title: str, subtitle: str = "") -> str:
    w = BOX_WIDTH
    lines = [f"{CYAN}╔{'═'*w}╗{RESET}",
             f"{CYAN}║{RESET}  {title:<{w-2}}{CYAN}║{RESET}"]
    if subtitle:
        lines.append(f"{CYAN}║{RESET}  {DIM}{subtitle:<{w-2}}{RESET}{CYAN}║{RESET}")
    lines.append(f"{CYAN}╚{'═'*w}╝{RESET}")
    return "\n".join(lines)


def box_footer(passed: int, failed: int, warned: int = 0) -> str:
    total = passed + failed + warned
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [f"{CYAN}╔{'═'*BOX_WIDTH}╗{RESET}"]
    lines.append(f"{CYAN}║{RESET}  PASS: {GREEN}{passed:<3}{RESET} │ FAIL: {RED}{failed:<3}{RESET} │ WARN: {YELLOW}{warned:<3}{RESET} │ TOTAL: {total:<3}          {CYAN}║{RESET}")
    if failed == 0:
        lines.append(f"{CYAN}║{RESET}  {GREEN}{'█'*62}{RESET} {CYAN}║{RESET}")
        lines.append(f"{CYAN}║{RESET}  {GREEN}██  VERDICT: ✅ ALL CLEAR — PRODUCTION READY               ██{RESET} {CYAN}║{RESET}")
        lines.append(f"{CYAN}║{RESET}  {GREEN}{'█'*62}{RESET} {CYAN}║{RESET}")
    else:
        lines.append(f"{CYAN}║{RESET}  {RED}❌ VERDICT: {failed} FAILURES — REMEDIATION REQUIRED{RESET}              {CYAN}║{RESET}")
    lines.append(f"{CYAN}║{RESET}  Evidence: {ts} │ Operator: EGD33{' '*(BOX_WIDTH-52)}{CYAN}║{RESET}")
    lines.append(f"{CYAN}╚{'═'*BOX_WIDTH}╝{RESET}")
    return "\n".join(lines)


def section(num: int, title: str) -> str:
    prefix = f"━━━ §{num} {title} "
    return f"\n{BOLD}{prefix}{'━' * (70 - len(prefix))}{RESET}"


# ━━━ Progress ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def progress_bar(step: int, total: int, width: int = 34) -> str:
    filled = step * width // total
    empty = width - filled
    pct = step * 100 // total
    return f"{DIM}    ▐{GREEN}{'█'*filled}{DIM}{'░'*empty}▌ {pct:3d}%{RESET}"


def phase_box(step: int, total: int, title: str) -> str:
    lines = [
        f"\n{CYAN}    ┌─────────────────────────────────────────────┐{RESET}",
        f"{CYAN}    │  ▶  [{step}/{total}]  {title:<33.33}│{RESET}",
        f"{CYAN}    └─────────────────────────────────────────────┘{RESET}",
        progress_bar(step, total),
    ]
    return "\n".join(lines)


# ━━━ Animations ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def spin(msg: str):
    if not ANIMATIONS:
        print(f"    ✦ {msg}"); return
    for f in ("◐", "◓", "◑", "◒"):
        print(f"\r    {MAGENTA}{f}{RESET} {msg}", end="", flush=True)
        time.sleep(0.08)
    print(f"\r    {GREEN}✦{RESET} {msg} done")


def pulse(msg: str):
    if not ANIMATIONS:
        print(f"    ▸ {msg}"); return
    print(f"    {YELLOW}▸ {msg}{RESET}", end="", flush=True)
    for _ in range(3):
        print(f"{MAGENTA}●{RESET}", end="", flush=True)
        time.sleep(0.15)
    print()


def wave(msg: str):
    if not ANIMATIONS:
        print(f"    ⚡ {msg} ✓"); return
    for f in ("∿∿∿∿∿∿∿∿", "≋≋≋≋≋≋≋≋", "∿∿∿∿∿∿∿∿", "〰〰〰〰"):
        print(f"\r    {MAGENTA}⚡ {f}{RESET} {msg}", end="", flush=True)
        time.sleep(0.12)
    print(f"\r    {GREEN}⚡ ════════{RESET} {msg} ✓")


def orbit(msg: str):
    if not ANIMATIONS:
        print(f"    ◉ {msg}"); return
    for i in range(8):
        f = ("◜", "◝", "◞", "◟")[i % 4]
        print(f"\r    {MAGENTA}{f}{RESET} {msg}", end="", flush=True)
        time.sleep(0.1)
    print(f"\r    {GREEN}◉{RESET} {msg}")


# ━━━ 3D Scenes ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MERKABA = f"""{MAGENTA}
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
{RESET}"""

TORUS = f"""{MAGENTA}
          ╭━━━━━━━━━━━╮
       ╭━━╯  ╭─────╮  ╰━━╮
     ╭━╯   ╭─╯     ╰─╮   ╰━╮
    ━╯    ╭─╯    ◆    ╰─╮    ╰━
    ━╮    ╰─╮         ╭─╯    ╭━
     ╰━╮   ╰─╮     ╭─╯   ╭━╯
       ╰━━╮  ╰─────╯  ╭━━╯
          ╰━━━━━━━━━━━╯
{RESET}"""

LATTICE = f"""{MAGENTA}
        ◆───◆───◆───◆───◆
       ╱ ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱ ╲
      ◆───◆───◆───◆───◆───◆
       ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱
        ◆───◆───◆───◆───◆
       ╱ ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱ ╲
      ◆───◆───◆───◆───◆───◆
       ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱
        ◆───◆───◆───◆───◆
{RESET}"""

CUBE = f"""{MAGENTA}
        ┌───────────────┐
       ╱│              ╱│
      ╱ │             ╱ │
     ┌───────────────┐  │
     │  │            │  │
     │  └────────────│──┘
     │ ╱             │ ╱
     │╱              │╱
     └───────────────┘
{RESET}"""

SPIRAL = f"""{MAGENTA}
     ╭━━━━━━━━━━━━━━━━━━━━━╮
     │  ╭━━━━━━━━━━━━━━╮   │
     │  │  ╭━━━━━━━╮   │   │
     │  │  │  ╭━━╮ │   │   │
     │  │  │  │◆ │ │   │   │
     │  │  │  ╰──╯ │   │   │
     │  │  ╰━━━━━━━╯   │   │
     │  ╰━━━━━━━━━━━━━━╯   │
     ╰━━━━━━━━━━━━━━━━━━━━━╯
{RESET}"""


# ━━━ Validation Counter ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class V:
    """Validation counter with pass/fail/warn tracking."""
    def __init__(self):
        self.passed = self.failed = self.warned = 0

    def ok(self, msg: str):
        self.passed += 1; print(f"  ✅ {msg}")

    def fail(self, msg: str):
        self.failed += 1; print(f"  ❌ {msg}")

    def warn(self, msg: str):
        self.warned += 1; print(f"  ⚠️  {msg}")

    def summary(self) -> str:
        return box_footer(self.passed, self.failed, self.warned)
