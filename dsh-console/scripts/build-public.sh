#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# build-public.sh — Generate sanitized DSH public build from dome-console
# ─────────────────────────────────────────────────────────────────────────────
# Usage: ./scripts/build-public.sh [TARGET_DIR]
# Default target: ~/DSH/dsh-console
#
# What this does:
#   1. Copies dome-console source → target (excluding private features)
#   2. Swaps branding: dome-console → dsh-console, Fira → Inter, green → gold
#   3. Replaces port 3737 → 4747
#   4. Strips private modules (CRM, agents panel, models viewer, repos monitor)
#   5. Replaces active nav items with "coming soon" placeholders
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

# ─── Private features to exclude ────────────────────────────────────────────
PRIVATE_DIRS=(
    "src/app/crm"
    "src/app/agents"
    "src/app/models"
    "src/app/repos"
    "src/app/api/agents"
    "src/app/api/models"
    "src/app/api/repos"
    "src/components/agents"
    "src/components/crm"
    "src/components/models"
    "src/components/repos"
    "src/lib/agents.ts"
    "src/lib/contacts.ts"
    "src/lib/repos.ts"
    "src/lib/db.ts"
    "src/test"
    "scripts/import-contacts.ts"
    "data"
    "CLAUDE.md"
    "FILE_TREE.md"
    "docs"
)

# ─── Step 1: Sync files (rsync, exclude private) ────────────────────────────
echo "  [1/5] Syncing files (excluding private features)..."

EXCLUDE_ARGS=()
for dir in "${PRIVATE_DIRS[@]}"; do
    EXCLUDE_ARGS+=(--exclude "$dir")
done

rsync -a --delete \
    --exclude "node_modules" \
    --exclude ".next" \
    --exclude ".git" \
    --exclude "pnpm-lock.yaml" \
    "${EXCLUDE_ARGS[@]}" \
    "$DOME_ROOT/" "$TARGET/"

echo "    ✓ Files synced"

# ─── Step 2: Swap layout.tsx (fonts + metadata) ─────────────────────────────
echo "  [2/5] Swapping branding (fonts, title, description)..."

cat > "$TARGET/src/app/layout.tsx" << 'EOF'
import { Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'
import { ThemeProvider } from 'next-themes'
import { AppSidebar } from '@/components/app-sidebar'
import { SidebarProvider, SidebarInset } from '@/components/ui/sidebar'
import { Toaster } from '@/components/ui/sonner'
import { SWVersionDisplay } from '@/components/sw-version-display'

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
          <SWVersionDisplay />
        </ThemeProvider>
      </body>
    </html>
  )
}
EOF

echo "    ✓ Layout: Inter/JetBrains Mono, port 4747, DSH branding"

# ─── Step 3: Swap port in package.json ──────────────────────────────────────
echo "  [3/5] Setting port 4747, removing private deps..."

cd "$TARGET"
# Port swap
sed -i '' 's/3737/4747/g' package.json 2>/dev/null || sed -i 's/3737/4747/g' package.json
# Title swap
sed -i '' 's/"name": "dome-console"/"name": "dsh-console"/g' package.json 2>/dev/null || sed -i 's/"name": "dome-console"/"name": "dsh-console"/g' package.json
# Remove private-only deps
python3 -c "
import json
with open('package.json') as f:
    data = json.load(f)
private_deps = ['better-sqlite3', '@types/better-sqlite3', '@hookform/resolvers',
                'react-hook-form', 'zod', '@tanstack/react-virtual', 'cmdk', 'date-fns']
for dep in private_deps:
    data.get('dependencies', {}).pop(dep, None)
    data.get('devDependencies', {}).pop(dep, None)
# Remove db scripts
scripts = data.get('scripts', {})
for k in list(scripts.keys()):
    if 'db:' in k or 'import' in k:
        del scripts[k]
with open('package.json', 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
"

echo "    ✓ package.json patched"

# ─── Step 4: Replace globals.css dark theme (green → gold) ──────────────────
echo "  [4/5] Swapping color palette (green → DSH gold)..."

# Replace the dome-console dark palette with DSH gold palette
python3 -c "
import re

with open('src/app/globals.css') as f:
    css = f.read()

# Replace dome palette comment + green primary
css = css.replace('dome-console palette: slate-deep + green-500 accent', 'dsh-console palette: dark slate + DSH gold accent (#D7AF00)')
# Green primary → Gold primary
css = re.sub(r'--primary: oklch\(0\.72 0\.187 144\).*', '--primary: oklch(0.78 0.16 95);             /* #D7AF00 gold — CTA */', css)
# Ring
css = re.sub(r'--ring: oklch\(0\.72 0\.187 144[^)]*\)', '--ring: oklch(0.78 0.16 95 / 60%)', css)
# Chart-1 green → gold
css = re.sub(r'--chart-1: oklch\(0\.72 0\.187 144\).*', '--chart-1: oklch(0.78 0.16 95);             /* gold */', css)

with open('src/app/globals.css', 'w') as f:
    f.write(css)
print('    ✓ Colors: green → gold')
"

# ─── Step 5: Patch sidebar (disable private nav items) ──────────────────────
echo "  [5/5] Patching sidebar (private features → coming soon)..."

# Replace active CRM/Agents/Models/Repos links with disabled placeholders
if [ -f "src/components/app-sidebar.tsx" ]; then
    python3 -c "
import re

with open('src/components/app-sidebar.tsx') as f:
    content = f.read()

# Remove imports for private feature icons if they reference private paths
# Replace nav items that link to /crm, /agents, /models, /repos with disabled versions
for route in ['/crm', '/agents', '/models', '/repos']:
    # Match href=\\\"/crm\\\" and make it disabled
    content = content.replace(f'href=\"{route}\"', f'href=\"#\" aria-disabled=\"true\" title=\"Coming soon\"')

with open('src/components/app-sidebar.tsx', 'w') as f:
    f.write(content)
print('    ✓ Sidebar: private routes disabled')
"
fi

# ─── Done ────────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════"
echo "  ✅ Public build complete"
echo "  Target: $TARGET"
echo "  Excluded: ${#PRIVATE_DIRS[@]} private paths"
echo "  Branding: Inter/JetBrains Mono • Gold • Port 4747"
echo "═══════════════════════════════════════════════════"
echo ""
echo "  Next: cd $TARGET && pnpm install && pnpm dev"
