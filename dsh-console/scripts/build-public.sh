#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# build-public.sh — Generate public DSH Console from dome-console
# ─────────────────────────────────────────────────────────────────────────────
# Usage: ./scripts/build-public.sh [TARGET_DIR]
# Default target: ~/DSH/dsh-console
#
# Both consoles have IDENTICAL features. The only differences:
#   - Branding: dome-console → dsh-console, DSH → DSH
#   - Theme: Fira/green/3737 → Inter/gold/4747
#   - Data: personal data/scripts stripped (users start with empty state)
#   - Paths: ~/DSH → ~/DSH
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOME_ROOT="$(dirname "$SCRIPT_DIR")"
TARGET="${1:-$HOME/DSH/dsh-console}"

echo "═══════════════════════════════════════════════════"
echo "  dome-console → dsh-console (public build)"
echo "═══════════════════════════════════════════════════"
echo "  Source: $DOME_ROOT"
echo "  Target: $TARGET"
echo ""

# ─── Files to exclude (personal data only, NOT features) ────────────────────
EXCLUDE_ARGS=(
    --exclude "node_modules"
    --exclude ".next"
    --exclude ".git"
    --exclude "pnpm-lock.yaml"
    --exclude "scripts/import-contacts.ts"
    --exclude "CLAUDE.md"
    --exclude "FILE_TREE.md"
    --exclude "docs/v-and-v"
    --exclude "data"
)

# ─── Step 1: Sync all files (features included) ─────────────────────────────
echo "  [1/4] Syncing files (all features, excluding personal data)..."

rsync -a --delete "${EXCLUDE_ARGS[@]}" "$DOME_ROOT/" "$TARGET/"

echo "    ✓ Files synced (CRM, agents, models, repos — all included)"

# ─── Step 2: Swap branding and paths ────────────────────────────────────────
echo "  [2/4] Swapping branding (DSH → DSH, dome-console → dsh-console)..."

cd "$TARGET"

# Find-and-replace across all source files
find src -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i '' \
    -e 's/DSH/DSH/g' \
    -e 's/DSH/DSH_ROOT/g' \
    -e 's/dome-console/dsh-console/g' \
    -e "s/dome\.db/dsh.db/g" \
    -e "s/episodic\.db/episodic.db/g" \
    -e 's/3737/4747/g' \
    {} +

# package.json
sed -i '' -e 's/"dome-console"/"dsh-console"/g' -e 's/3737/4747/g' package.json

# Layout: swap fonts + metadata
cat > src/app/layout.tsx << 'EOF'
import { Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'
import { ThemeProvider } from 'next-themes'
import { AppSidebar } from '@/components/app-sidebar'
import { SidebarProvider, SidebarInset } from '@/components/ui/sidebar'
import { Toaster } from '@/components/ui/sonner'

const sans = Inter({
  variable: '--font-sans',
  subsets: ['latin'],
})
const mono = JetBrains_Mono({
  variable: '--font-mono',
  subsets: ['latin'],
})

export const metadata = {
  title: 'dsh-console',
  description: 'Sovereign-node control panel for DSH (Dome Sovereign Hub)',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className="bg-background text-foreground min-h-full font-sans"
            style={{ ['--font-sans' as string]: sans.style.fontFamily, ['--font-mono' as string]: mono.style.fontFamily }}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
          <SidebarProvider>
            <AppSidebar />
            <SidebarInset>
              <main className="flex-1 p-6">
                <div className="font-mono text-xs text-muted-foreground">
                  localhost:4747
                </div>
                {children}
              </main>
            </SidebarInset>
          </SidebarProvider>
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  )
}
EOF

echo "    ✓ Paths: DSH → DSH, dome.db → dsh.db, port 3737 → 4747"

# ─── Step 3: Swap color palette (green → DSH gold) ──────────────────────────
echo "  [3/4] Swapping color palette (green → DSH gold)..."

python3 -c "
import re

with open('src/app/globals.css') as f:
    css = f.read()

# Comment
css = css.replace('dome-console palette: slate-deep + green-500 accent', 'dsh-console palette: dark slate + DSH gold accent (#D7AF00)')
# Green primary → Gold
css = re.sub(r'--primary: oklch\(0\.72 0\.187 144\).*', '--primary: oklch(0.78 0.16 95);             /* #D7AF00 gold — CTA */', css)
# Ring
css = re.sub(r'--ring: oklch\(0\.72 0\.187 144[^)]*\)', '--ring: oklch(0.78 0.16 95 / 60%)', css)
# Chart-1
css = re.sub(r'--chart-1: oklch\(0\.72 0\.187 144\).*', '--chart-1: oklch(0.78 0.16 95);             /* gold */', css)

with open('src/app/globals.css', 'w') as f:
    f.write(css)
print('    ✓ Colors: green → gold')
"

# ─── Step 4: Remove private deps, keep feature deps ─────────────────────────
echo "  [4/4] Cleaning package.json (remove import scripts, keep all feature deps)..."

python3 -c "
import json
with open('package.json') as f:
    data = json.load(f)
# Remove personal data scripts only
scripts = data.get('scripts', {})
for k in list(scripts.keys()):
    if 'import' in k:
        del scripts[k]
with open('package.json', 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
print('    ✓ Removed import scripts, kept all feature deps')
"

# ─── README ──────────────────────────────────────────────────────────────────
cat > "$TARGET/README.md" << 'EOF'
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
EOF

# ─── Done ────────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════"
echo "  ✅ Public build complete (full features)"
echo "  Target: $TARGET"
echo "  Theme: Inter / JetBrains Mono • Gold • Port 4747"
echo "  Data: Empty state (users start fresh)"
echo "═══════════════════════════════════════════════════"
echo ""
echo "  Next: cd $TARGET && pnpm install && pnpm dev"
