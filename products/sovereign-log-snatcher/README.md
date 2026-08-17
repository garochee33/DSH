# Sovereign Log Snatcher

**Keep your data sovereign. Don't let the vendors cater.**

A local gatherer for a DSH / sky-hub / dome-hub tree. Every 15 minutes it
moves vendor telemetry off the vendor path and copies live IDE logs into
`runtime/` on *your* disk. The process has no network client. It does not
make chat smarter. It does not prove an air-gap. It keeps residue where
you can see it.

---

## The Ballad of Sovereign Data

They want your **data sovereign** — not plated by a waiter,  
not boxed for a boardroom, not sold to a dictator.  
So we snatch the logs they leave behind, and we snatch them **later**,  
before a corporate caterer turns your crumbs into something greater  
for *them* — and smaller for the only **creator**: you.

**Step one.** A policy names the sources. Local. Quiet. Yours.  
No cloud menu. No "trust us" tour of other people's doors.

**Step two.** A fifteen-minute tick. KeepAlive. No open ports to flatter.  
This process has no network client — it does not phone a handler.

**Step three.** We *move* the telemetry they stashed to scoop you later:  
Sentry, Crashpad, the vendor-path platter.  
Empty that house so they cannot keep a ready-made crater  
of your residue sitting in *their* folders, waiting for a traitor  
in the supply chain to pick it up and cater.

**Step four.** We *copy* live IDE logs — leave the writer in its chair.  
Cursor traces, Kiro, Claude debug, Codex sqlite, Ollama's air.  
Custody under `runtime/sovereign-snatcher/`, locked `0700` there.  
Thirty days. Unchanged files sleep. Full disks refuse the errand, fair.

**Step five.** Skip the keys, the cookies, the `sk-` shaped traitor.  
That is a guardrail, not a church of DLP. We do not copy the detonator.

**Step six.** A receipt. A status line. Your hub, your floor, your equator.  
Partner install. Your metal. Not their datacenter.

### What the corporations cannot do — when this is used

They cannot leave Sentry and Crashpad **on the vendor path** as a courtesy platter.  
They cannot treat your leftover traces as still living in *their* Application gutter.  
They cannot call this gatherer from the outside — it has no socket, no uploader, no chatter.  
They cannot pretend those crumbs are still "just logs in our folder" for a later caterer.

### What this does not claim (so the verse stays honest)

The live app may still talk if the OS lets it.  
This is **custody**, not a Faraday cage, not a courtroom later.  
Chat history is a different store. Snatcher does not make the model greater.

**Keep your data sovereign. Snatch the logs. Don't wait for the waiter.**

---

## Install

```bash
# From a DSH / sky-hub / dome-hub tree
export SKY_HUB_ROOT="${SKY_HUB_ROOT:-$PWD}"
# or: export SKY_HUB_ROOT="$HOME/sovereign/sky-hub"

# First gather on a full node can be ~1 GB.
# SOVEREIGN_SNATCHER_SKIP_ONCE=1 to install the agent only.
bash products/sovereign-log-snatcher/scripts/install-sovereign-snatcher.sh
```

If you copied this folder into a hub `scripts/` layout, the install script
seeds `$SKY_HUB_ROOT` and writes launchd `com.skyhub.sovereign-snatcher`.

```bash
python3 products/sovereign-log-snatcher/scripts/sovereign-snatcher.py --self-check
python3 products/sovereign-log-snatcher/scripts/sovereign-snatcher.py --status
```

## What it gathers

| Source | Action |
|--------|--------|
| Cursor | Move telemetry / Sentry / Crashpad; copy IDE logs |
| Antigravity | Move crash/telemetry; copy logs |
| Kiro | Copy Amazon Q logs + telemetryCache |
| Codex | Copy `logs_2.sqlite` (vendor file stays) |
| Claude | Copy `debug/` + `daemon.log` |
| Ollama | Copy Homebrew `ollama.log` |

Chat composer DBs and session JSONL are **out of scope**.

## Claims lock

Allowed: local-only process, no upload code path, custody under sovereign
`runtime/`, 15-minute tick, 30-day retention.

Forbidden: "zero telemetry," "zero egress," "makes the AI smarter,"
"captures all chat history."
