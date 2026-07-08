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
