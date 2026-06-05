# dsh-console

Open-source sovereign-node control panel for DSH. Full-featured: Dashboard, CRM, Agents, Models, Repos. Localhost only.

> **Generated from dome-console** via `scripts/build-public.sh`. Same features, clean state.

## Stack

- Next.js 16 (App Router, Turbopack, RSC + server actions)
- TypeScript, Tailwind v4, shadcn/ui, Recharts
- SQLite via better-sqlite3 (auto-creates `~/DSH/db/dsh.db` on first run)
- Inter + JetBrains Mono, dark-only OLED palette, slate + gold accent
- 127.0.0.1:4747, no auth (sovereign by isolation)

## Modules

- **/** — System Dashboard (CPU, memory, disk, agent status, sparklines)
- **/crm** — Contact management (search, tags, notes, interactions)
- **/agents** — Registered AI agents (Claude, Kiro, etc.)
- **/models** — Ollama local model viewer
- **/repos** — Git repository monitor

## Setup

```bash
pnpm install
pnpm dev
# → http://127.0.0.1:4747
```

## License

MIT — Trinity Consortium / Enzo Garoche
