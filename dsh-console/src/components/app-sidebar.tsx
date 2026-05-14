'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Activity, Database, Bot, BookOpen, Network, Cpu, ScrollText, Settings } from 'lucide-react'
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

const navMain = [{ title: 'Dashboard', href: '/', icon: Activity }]

const navFuture = [
  { title: 'Agents', href: '/agents', icon: Bot },
  { title: 'Knowledge', href: '/knowledge', icon: BookOpen },
  { title: 'Database', href: '/database', icon: Database },
  { title: 'Models', href: '/models', icon: Cpu },
  { title: 'Mesh', href: '/mesh', icon: Network },
  { title: 'Logs', href: '/logs', icon: ScrollText },
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
            <span className="text-muted-foreground font-mono text-[10px]">sovereign node</span>
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
                const active =
                  pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href))
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
          <SidebarGroupLabel>Roadmap</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navFuture.map((item) => {
                const Icon = item.icon
                return (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton disabled className="opacity-50">
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
