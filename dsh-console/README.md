# dsh-console

Sovereign-node control panel for [DSH](https://github.com/garochee33/DSH). A small, local-only web app that surfaces what your sovereign node is actually doing right now: CPU load, memory pressure, disk capacity, and the local Ollama models you have available.

Localhost only. No telemetry. Sovereign by isolation.

## What it shows

- **CPU** — system-wide percentage (parsed from `top -l 2 -n 0 -s 1`, not the misleading process-CPU you get from Node's `process.cpuUsage`)
- **Memory** — used / available / total, computed from `vm_stat` (matches Activity Monitor's "Memory Pressure" definition; not the `os.freemem()` fiction that reports ~99% used on idle macOS)
- **Disk** — used / free for your home volume
- **Ollama** — available models with size, or a clear offline state with start instructions

## Stack

- Next.js 16 (App Router, Turbopack) + React 19.2 + TypeScript strict
- Tailwind v4 + shadcn/ui (Base UI render-prop pattern)
- Recharts (sparklines)
- Vitest (unit + parser tests) + Playwright (E2E in chromium)
- Dark-only OLED palette with DSH gold accent

## Requirements

- macOS (the parsers target `top`, `vm_stat`, `df` output as found on Darwin)
- Node 22+
- pnpm
- Optional: [Ollama](https://ollama.com) running locally — the dashboard works without it (shows `offline`)

## Run

```bash
pnpm install
pnpm dev          # http://127.0.0.1:4747 (Turbopack, hot reload)
pnpm build
pnpm start        # production server, also localhost-only on 4747
pnpm lint
pnpm test         # unit + parser tests
pnpm test:e2e     # build + Playwright (chromium)
pnpm validate     # full gate: lint + tests + e2e
```

## Why localhost only

This panel reads system telemetry (memory pages, CPU, disk, model registry). It is never bound to a public interface — `next dev` and `next start` are both pinned to `127.0.0.1`. If you need to access it from another device on your trusted LAN, set up an SSH tunnel; do not flip the bind address.

## Architecture

```
src/
├── app/
│   ├── api/metrics/route.ts   # GET → SystemMetrics JSON
│   ├── layout.tsx             # sidebar + main shell
│   └── page.tsx               # dashboard (RSC; first render is fresh metrics)
├── components/
│   ├── app-sidebar.tsx        # nav (Dashboard active; Agents/KB/Mesh roadmap)
│   ├── dashboard/             # MetricTile, Sparkline, DashboardClient (5s refresh)
│   └── ui/                    # shadcn primitives
└── lib/
    ├── metrics.ts             # IO orchestration (server-only, calls parsers)
    └── metrics-parsers.ts     # PURE parsers (no IO; safe to test directly)
```

The split between `metrics.ts` (IO) and `metrics-parsers.ts` (pure) is deliberate so the parsers can be tested against fixture strings — see `src/lib/metrics-parsers.test.ts` (16 tests against real `vm_stat` / `top` / `ollama list` output).

## Roadmap

The sidebar shows greyed-out destinations for the next iterations:

- Agents (list of registered agents on the node)
- Knowledge (KB / docs browser)
- Database (sqlite browsers)
- Models (pull / remove local models)
- Mesh (Trinity Mycelium connectivity, when applicable)
- Logs (audit + session)

PRs welcome.

## License

MIT — same as DSH.
