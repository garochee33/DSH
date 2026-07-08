'use client'

import { useEffect, useState } from 'react'
import type { AgentSnapshot } from '@/lib/agents'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

const REFRESH_MS = 10_000

function relTime(iso: string | null): string {
  if (!iso) return '—'
  const ms = Date.now() - new Date(iso).getTime()
  if (Number.isNaN(ms)) return iso
  const s = Math.floor(ms / 1000)
  if (s < 60) return `${s}s ago`
  const m = Math.floor(s / 60)
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 48) return `${h}h ago`
  const d = Math.floor(h / 24)
  return `${d}d ago`
}

function epochToIso(epoch: number | null): string | null {
  if (epoch == null) return null
  // traces table stores ended_at as REAL — could be seconds or ms; treat <1e12 as seconds.
  const ms = epoch < 1e12 ? epoch * 1000 : epoch
  return new Date(ms).toISOString()
}

export function AgentsClient({ initial }: { initial: AgentSnapshot }) {
  const [snap, setSnap] = useState<AgentSnapshot>(initial)
  const [stale, setStale] = useState(false)

  useEffect(() => {
    const tick = async () => {
      try {
        const res = await fetch('/api/agents', { cache: 'no-store' })
        if (!res.ok) throw new Error(String(res.status))
        const s = (await res.json()) as AgentSnapshot
        setSnap(s)
        setStale(false)
      } catch {
        setStale(true)
      }
    }
    const id = setInterval(tick, REFRESH_MS)
    return () => clearInterval(id)
  }, [])

  const traced = snap.registered.filter((a) => a.traceCount > 0).length
  const activeRuntimes = snap.runtimes.filter((r) => r.recentCount > 0).length

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-mono text-2xl font-semibold">Agents</h1>
          <p className="text-muted-foreground font-mono text-xs">
            {snap.registered.length} registered · {traced} with traces · {activeRuntimes}/{snap.runtimes.length} runtimes active /24h
          </p>
        </div>
        <Badge variant={stale ? 'destructive' : 'outline'} className="font-mono text-[10px]">
          {stale ? 'STALE' : 'LIVE'} · {REFRESH_MS / 1000}s
        </Badge>
      </div>

      <section>
        <Card>
          <CardHeader>
            <CardTitle className="font-mono text-sm">CLI Runtimes — last 24h activity</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="divide-border/50 grid grid-cols-1 divide-y font-mono text-sm md:grid-cols-2 md:divide-y-0">
              {snap.runtimes.map((r) => (
                <li
                  key={r.runtime}
                  className="flex items-center justify-between gap-3 border-border/50 py-2 md:border-b md:py-3 md:pr-4"
                >
                  <div className="min-w-0 flex-1">
                    <p className="flex items-center gap-2">
                      <span className="font-semibold capitalize">{r.runtime}</span>
                      {!r.available && (
                        <Badge variant="secondary" className="font-mono text-[9px]">
                          n/a
                        </Badge>
                      )}
                    </p>
                    <p className="text-muted-foreground truncate text-[10px]">{r.baseDir}</p>
                  </div>
                  <div className="text-right">
                    <p className="tabular-nums">
                      <span className={r.recentCount > 0 ? 'text-[var(--chart-1)]' : 'text-muted-foreground'}>
                        {r.recentCount}
                      </span>
                      <span className="text-muted-foreground"> / {r.sessionCount}</span>
                    </p>
                    <p className="text-muted-foreground text-[10px]">{relTime(r.lastModifiedIso)}</p>
                  </div>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </section>

      <section>
        <Card>
          <CardHeader>
            <CardTitle className="font-mono text-sm">Registered agents — dsh.db</CardTitle>
          </CardHeader>
          <CardContent>
            {snap.registered.length === 0 ? (
              <p className="text-muted-foreground text-sm">No registered agents found.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full font-mono text-xs">
                  <thead>
                    <tr className="text-muted-foreground border-b border-border/50 text-left uppercase">
                      <th className="py-2 pr-3 font-medium">Name</th>
                      <th className="py-2 pr-3 font-medium">Vendor</th>
                      <th className="py-2 pr-3 font-medium">Surface</th>
                      <th className="py-2 pr-3 font-medium">Role</th>
                      <th className="py-2 pr-3 text-right font-medium">Traces</th>
                      <th className="py-2 pr-3 text-right font-medium">Avg latency</th>
                      <th className="py-2 pr-3 text-right font-medium">Last run</th>
                    </tr>
                  </thead>
                  <tbody>
                    {snap.registered.map((a) => (
                      <tr key={a.name} className="border-b border-border/30 last:border-0">
                        <td className="py-2 pr-3 font-semibold">{a.name}</td>
                        <td className="py-2 pr-3 text-muted-foreground">{a.vendor ?? '—'}</td>
                        <td className="py-2 pr-3 text-muted-foreground">{a.surface ?? '—'}</td>
                        <td className="py-2 pr-3 text-muted-foreground">{a.role ?? '—'}</td>
                        <td className="py-2 pr-3 text-right tabular-nums">{a.traceCount}</td>
                        <td className="py-2 pr-3 text-right tabular-nums text-muted-foreground">
                          {a.avgLatencyMs == null ? '—' : `${a.avgLatencyMs.toFixed(0)} ms`}
                        </td>
                        <td className="py-2 pr-3 text-right tabular-nums text-muted-foreground">
                          {relTime(epochToIso(a.lastTraceAt))}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </section>
    </div>
  )
}
