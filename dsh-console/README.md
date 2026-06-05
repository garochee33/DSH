# dsh-console

Open-source sovereign-node control panel for DSH (Dome Sovereign Hub). System dashboard with real-time metrics. Localhost only.

> ⚠️ **This is a generated build.** Do not edit directly. Source: [dome-console](https://github.com/garochee33/dome-console) (private).

## Stack

- Next.js 16 (App Router, Turbopack, RSC)
- TypeScript, Tailwind v4, shadcn/ui, Recharts
- Inter + JetBrains Mono, dark-only OLED palette, slate base + DSH gold accent
- 127.0.0.1:4747, no auth (sovereign by isolation)

## Features

- **/** — System Dashboard. CPU / memory / disk tiles with sparklines. 5s auto-refresh.
- Additional modules coming soon.

## Setup

```bash
pnpm install
pnpm dev
# → http://127.0.0.1:4747
```

## Relationship to dome-console

This directory is auto-generated from the private `dome-console` repo via:

```bash
# In dome-console:
./scripts/build-public.sh ~/DSH/dsh-console
```

The script strips private features (CRM, agent panel, model viewer, repo monitor), swaps branding (Fira→Inter, green→gold, 3737→4747), and creates public-safe stubs.

**Do not commit changes here directly.** All changes flow from dome-console.

## License

MIT — Trinity Consortium / Enzo Garoche
