'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  Activity,
  Users,
  Database,
  Bot,
  BookOpen,
  Network,
  Cpu,
  ScrollText,
  Settings,
  GitBranch,
} from 'lucide-react'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from '@/components/ui/sidebar'

const navMain = [
  { title: 'Dashboard', href: '/', icon: Activity },
  { title: 'CRM', href: '/crm', icon: Users },
  { title: 'Agents', href: '/agents', icon: Bot },
  { title: 'Models', href: '/models', icon: Cpu },
  { title: 'Repos', href: '/repos', icon: GitBranch },
]

const navSystem = [
  { title: 'Knowledge', href: '/knowledge', icon: BookOpen, disabled: true },
  { title: 'Database', href: '/database', icon: Database, disabled: true },
  { title: 'Mesh', href: '/mesh', icon: Network, disabled: true },
  { title: 'Logs', href: '/logs', icon: ScrollText, disabled: true },
]

export function AppSidebar() {
  const pathname = usePathname()
  return (
    <Sidebar>
      <SidebarHeader>
        <div className="flex items-center gap-2 px-2 py-3">
          <div className="bg-primary text-primary-foreground flex aspect-square size-8 items-center justify-center rounded-md font-mono text-xs font-bold">
            ●
          </div>
          <div className="flex flex-col leading-tight">
            <span className="font-mono text-sm font-semibold">dsh-console</span>
            <span className="text-muted-foreground font-mono text-[10px]">M4 Pro · sovereign</span>
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Active</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navMain.map((item) => {
                const Icon = item.icon
                const active = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href))
                return (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton isActive={active} render={<Link href={item.href} />}>
                      <Icon className="size-4" />
                      <span>{item.title}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                )
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
        <SidebarGroup>
          <SidebarGroupLabel>Coming soon</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navSystem.map((item) => {
                const Icon = item.icon
                return (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton disabled={item.disabled} className="opacity-50">
                      <Icon className="size-4" />
                      <span>{item.title}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                )
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton disabled className="opacity-50">
              <Settings className="size-4" />
              <span>Settings</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  )
}
