import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import { SidebarProvider, SidebarInset, SidebarTrigger } from '@/components/ui/sidebar'
import { TooltipProvider } from '@/components/ui/tooltip'
import { Toaster } from '@/components/ui/sonner'
import { AppSidebar } from '@/components/app-sidebar'
import { Separator } from '@/components/ui/separator'
import './globals.css'

const sans = Inter({
  variable: '--font-sans',
  subsets: ['latin'],
})

const mono = JetBrains_Mono({
  variable: '--font-mono',
  subsets: ['latin'],
})

export const metadata: Metadata = {
  title: 'dsh-console',
  description: 'Sovereign-node control panel for DSH (Dome Sovereign Hub)',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${sans.variable} ${mono.variable} dark h-full antialiased`}
    >
      <body className="bg-background text-foreground min-h-full font-sans">
        <TooltipProvider>
          <SidebarProvider>
            <AppSidebar />
            <SidebarInset>
              <header className="flex h-12 shrink-0 items-center gap-2 border-b border-border/50 px-4">
                <SidebarTrigger className="-ml-1" />
                <Separator orientation="vertical" className="h-4" />
                <div className="font-mono text-xs text-muted-foreground">
                  dsh-console <span className="text-primary">●</span> 127.0.0.1:4747
                </div>
              </header>
              <main className="flex-1 p-6">{children}</main>
            </SidebarInset>
          </SidebarProvider>
          <Toaster />
        </TooltipProvider>
      </body>
    </html>
  )
}
