'use client'

import { useEffect, useState } from 'react'
import type { RepoStatus } from '@/lib/repos'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

const REFRESH_MS = 10_000

function relTime(iso: string): string {
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

function stompTone(risk: RepoStatus['stompRisk']): 'outline' | 'secondary' | 'destructive' {
  if (risk === 'high') return 'destructive'
  if (risk === 'low') return 'secondary'
  return 'outline'
}

function dirtyTotal(r: RepoStatus): number {
  return r.uncommitted + r.staged + r.untracked
}

export function ReposClient({ initial }: { initial: RepoStatus[] }) {
  const [repos, setRepos] = useState<RepoStatus[]>(initial)
  const [stale, setStale] = useState(false)

  useEffect(() => {
    const tick = async () => {
      try {
        const res = await fetch('/api/repos', { cache: 'no-store' })
        if (!res.ok) throw new Error(String(res.status))
        const r = (await res.json()) as RepoStatus[]
        setRepos(r)
        setStale(false)
      } catch {
        setStale(true)
      }
    }
    const id = setInterval(tick, REFRESH_MS)
    return () => clearInterval(id)
  }, [])

  const dirtyCount = repos.filter((r) => dirtyTotal(r) > 0).length
  const stompCount = repos.filter((r) => r.stompRisk !== 'none').length

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-mono text-2xl font-semibold">5-Repo Git Grid</h1>
          <p className="text-muted-foreground font-mono text-xs">
            {dirtyCount}/{repos.length} dirty · {stompCount} with stomp risk
          </p>
        </div>
        <Badge variant={stale ? 'destructive' : 'outline'} className="font-mono text-[10px]">
          {stale ? 'STALE' : 'LIVE'} · {REFRESH_MS / 1000}s
        </Badge>
      </div>

      <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {repos.map((r) => {
          const dirty = dirtyTotal(r)
          return (
            <Card key={r.path} className="overflow-hidden">
              <CardHeader className="flex flex-row items-start justify-between gap-2 pb-3">
                <div className="min-w-0">
                  <CardTitle className="font-mono text-sm">{r.name}</CardTitle>
                  <p className="text-muted-foreground truncate font-mono text-[10px]">{r.path}</p>
                </div>
                <Badge variant={dirty > 0 ? 'secondary' : 'outline'} className="font-mono text-[10px]">
                  {r.branch ?? 'no-branch'}
                </Badge>
              </CardHeader>
              <CardContent className="pt-0">
                {r.error ? (
                  <p className="text-destructive font-mono text-xs">{r.error}</p>
                ) : (
                  <>
                    <div className="grid grid-cols-5 gap-2 text-center font-mono text-[10px]">
                      <Stat label="staged" value={r.staged} accent={r.staged > 0 ? 'text-[var(--chart-1)]' : ''} />
                      <Stat label="unstaged" value={r.uncommitted} accent={r.uncommitted > 0 ? 'text-[var(--chart-3)]' : ''} />
                      <Stat label="untracked" value={r.untracked} accent={r.untracked > 0 ? 'text-[var(--chart-2)]' : ''} />
                      <Stat label="ahead" value={r.ahead} accent={r.ahead > 0 ? 'text-[var(--chart-5)]' : ''} />
                      <Stat label="behind" value={r.behind} accent={r.behind > 0 ? 'text-destructive' : ''} />
                    </div>
                    {r.lastCommit && (
                      <div className="mt-3 border-t border-border/50 pt-3 font-mono text-[11px]">
                        <p className="truncate">
                          <span className="text-muted-foreground">{r.lastCommit.sha.slice(0, 7)}</span>{' '}
                          {r.lastCommit.subject}
                        </p>
                        <p className="text-muted-foreground mt-0.5 text-[10px]">
                          {r.lastCommit.author} · {relTime(r.lastCommit.iso)}
                        </p>
                      </div>
                    )}
                    {r.stompRisk !== 'none' && r.stompReason && (
                      <div className="mt-3 border-t border-border/50 pt-3">
                        <Badge variant={stompTone(r.stompRisk)} className="font-mono text-[10px]">
                          ⚠ STOMP {r.stompRisk.toUpperCase()}
                        </Badge>
                        <p className="text-muted-foreground mt-1 font-mono text-[10px]">{r.stompReason}</p>
                      </div>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          )
        })}
      </section>
    </div>
  )
}

function Stat({ label, value, accent }: { label: string; value: number; accent?: string }) {
  return (
    <div className="flex flex-col items-center justify-center rounded border border-border/40 py-2">
      <span className={`text-sm font-semibold tabular-nums ${accent ?? ''}`}>{value}</span>
      <span className="text-muted-foreground mt-0.5 text-[9px] uppercase tracking-wide">{label}</span>
    </div>
  )
}
