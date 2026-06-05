'use client'

import { useEffect, useState } from 'react'
import type { SystemMetrics } from '@/lib/metrics'
import { MetricTile } from './metric-tile'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

const REFRESH_MS = 5000

function fmtBytes(gb: number): string {
  if (gb >= 1024) return `${(gb / 1024).toFixed(1)} TB`
  if (gb >= 1) return `${gb.toFixed(1)} GB`
  if (gb >= 0.001) return `${(gb * 1024).toFixed(0)} MB`
  return `${(gb * 1024 * 1024).toFixed(0)} KB`
}

export function DashboardClient({ initial }: { initial: SystemMetrics }) {
  const [metrics, setMetrics] = useState<SystemMetrics>(initial)
  const [stale, setStale] = useState(false)

  useEffect(() => {
    const tick = async () => {
      try {
        const res = await fetch('/api/metrics', { cache: 'no-store' })
        if (!res.ok) throw new Error(String(res.status))
        const m = (await res.json()) as SystemMetrics
        setMetrics(m)
        setStale(false)
      } catch {
        setStale(true)
      }
    }
    const id = setInterval(tick, REFRESH_MS)
    return () => clearInterval(id)
  }, [])

  const m = metrics

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-mono text-2xl font-semibold">System Dashboard</h1>
          <p className="text-muted-foreground font-mono text-xs">
            {m.cpu.cores}-core · {m.cpu.model} · uptime {m.uptime.systemHours.toFixed(1)}h
          </p>
        </div>
        <Badge variant={stale ? 'destructive' : 'outline'} className="font-mono text-[10px]">
          {stale ? 'STALE' : 'LIVE'} · {(REFRESH_MS / 1000).toFixed(0)}s
        </Badge>
      </div>

      <section className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <MetricTile
          label="CPU"
          value={m.cpu.loadPct.toFixed(1)}
          unit="%"
          hint={`load 1m ${m.cpu.load1.toFixed(2)} · 5m ${m.cpu.load5.toFixed(2)}`}
          series={m.uptime.loadPctRolling}
          accent="green"
        />
        <MetricTile
          label="Memory"
          value={m.memory.usedGB.toFixed(1)}
          unit={`/ ${m.memory.totalGB.toFixed(0)} GB`}
          hint={`${m.memory.usedPct.toFixed(0)}% used · ${m.memory.availableGB.toFixed(1)} GB available`}
          accent="blue"
        />
        <MetricTile
          label="Disk"
          value={m.disk ? m.disk.usedGB.toFixed(0) : '—'}
          unit={m.disk ? `/ ${m.disk.totalGB.toFixed(0)} GB` : ''}
          hint={m.disk ? `${m.disk.usedPct.toFixed(0)}% used · ${m.disk.freeGB.toFixed(0)} GB free` : 'unavailable'}
          accent="amber"
        />
        <MetricTile
          label="Contacts"
          value={m.contacts.total.toLocaleString()}
          hint={`${m.contacts.tagged} tagged · ${m.contacts.withNotes} with notes · ${m.contacts.recentInteractions} interactions /7d`}
          accent="cyan"
        />
      </section>

      <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="font-mono text-sm">Databases</CardTitle>
          </CardHeader>
          <CardContent>
            {m.databases.length === 0 ? (
              <p className="text-muted-foreground text-sm">No databases found.</p>
            ) : (
              <ul className="divide-border/50 divide-y font-mono text-sm">
                {m.databases.map((d) => (
                  <li key={d.path} className="flex items-center justify-between py-2">
                    <span>{d.name}</span>
                    <span className="text-muted-foreground tabular-nums">{fmtBytes(d.sizeMB / 1024)}</span>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="font-mono text-sm">Agents</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="divide-border/50 divide-y font-mono text-sm">
              <li className="flex items-center justify-between py-2">
                <span>Claude</span>
                <span className="text-muted-foreground tabular-nums">{m.agents.claude}</span>
              </li>
              <li className="flex items-center justify-between py-2">
                <span>Kiro</span>
                <span className="text-muted-foreground tabular-nums">{m.agents.kiro}</span>
              </li>
              <li className="flex items-center justify-between py-2">
                <span className="font-semibold">Total</span>
                <span className="text-primary font-semibold tabular-nums">{m.agents.total}</span>
              </li>
            </ul>
          </CardContent>
        </Card>
      </section>

      <section>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="font-mono text-sm">Ollama Models</CardTitle>
            <Badge variant={m.ollama.available ? 'outline' : 'secondary'} className="font-mono text-[10px]">
              {m.ollama.available ? `online · ${m.ollama.models.length}` : 'offline'}
            </Badge>
          </CardHeader>
          <CardContent>
            {!m.ollama.available ? (
              <p className="text-muted-foreground text-sm">
                Ollama not running. Start with{' '}
                <code className="bg-muted rounded px-1 py-0.5 font-mono text-xs">ollama serve</code>.
              </p>
            ) : m.ollama.models.length === 0 ? (
              <p className="text-muted-foreground text-sm">No models pulled. Try `ollama pull llama3.1:8b`.</p>
            ) : (
              <ul className="grid grid-cols-1 gap-2 font-mono text-sm md:grid-cols-2 lg:grid-cols-3">
                {m.ollama.models.map((md) => (
                  <li key={md.name} className="border-border/50 flex items-center justify-between rounded border px-3 py-2">
                    <span className="truncate">{md.name}</span>
                    <span className="text-muted-foreground tabular-nums">{md.sizeGB.toFixed(1)} GB</span>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </section>
    </div>
  )
}
