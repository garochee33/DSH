# Sovereign Log Snatcher

**Sovereign data. Snatch it back. Don't wait.**

A local gatherer for a DSH / sky-hub / dome-hub tree. Every 15 minutes it
moves vendor telemetry off the vendor path and copies live IDE logs into
`runtime/` on *your* disk. The process has no network client. It does not
make chat smarter. It does not prove an air-gap. It keeps residue where
you can see it.

---

## Sovereign Data

```
They clock the sovereign data like a buffet they can plate,
park Sentry in the drywall, leave Crashpad on the grate.
I don't dial a handler. I don't open a gate.
Fifteen-minute KeepAlive. Local. That's the state.

Policy names the sources — quiet list, your floor, your fate.
No cloud tasting menu. No "trust us" tour. No bait.
I MOVE the telemetry they stashed so a later bot can scrape,
empty the vendor path so the supply chain got no tray to take.

I COPY live IDE logs, leave the writer in the chair —
Cursor, Kiro, Claude debug, Codex sqlite, Ollama air.
`runtime/` custody. `0700`. Thirty days. That's fair.
Full disk says no. Unchanged files sleep. Keys and `sk-` ain't there.

Receipt on your metal. Status line. Partner install. Your crate.
Not their datacenter. Not a phone-home. Not a plate.

What the corporations cannot do when the snatcher's in the cut:
can't leave crumbs on THEIR path like a courtesy platter,
can't treat leftover traces like they still live in their gutter,
can't ping this gatherer — no socket, no uploader, no chatter,
can't say "just logs in our folder" and serve 'em up later.

Custody. Not a Faraday cage. Chat's a different store.
Snatcher don't make the model smarter. It just locks the door.
Sovereign data. Snatch it back. Don't wait.
```

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
