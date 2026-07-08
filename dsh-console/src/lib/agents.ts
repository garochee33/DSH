import 'server-only'
import os from 'node:os'
import path from 'node:path'
import fs from 'node:fs/promises'
import { getDb } from './db'

const HOME = os.homedir()

export type AgentRow = {
  name: string
  vendor: string | null
  surface: string | null
  role: string | null
  entrypoint: string | null
  updatedAt: string | null
  lastTraceAt: number | null
  traceCount: number
  avgLatencyMs: number | null
  totalTokens: number
}

export type SessionRuntime = {
  runtime: string
  baseDir: string
  available: boolean
  sessionCount: number
  recentCount: number
  lastModifiedIso: string | null
}

export type AgentSnapshot = {
  ts: number
  registered: AgentRow[]
  runtimes: SessionRuntime[]
}

function getRegisteredAgents(): AgentRow[] {
  const db = getDb()
  const tableExists = db
    .prepare("SELECT name FROM sqlite_master WHERE type='table' AND name='agents'")
    .get() as { name: string } | undefined
  if (!tableExists) return []

  const tracesExists = db
    .prepare("SELECT name FROM sqlite_master WHERE type='table' AND name='traces'")
    .get() as { name: string } | undefined

  const rows = db
    .prepare(`
      SELECT name, vendor, surface, role, entrypoint, updated_at AS updatedAt
      FROM agents
      ORDER BY name
    `)
    .all() as Array<{
      name: string
      vendor: string | null
      surface: string | null
      role: string | null
      entrypoint: string | null
      updatedAt: string | null
    }>

  if (!tracesExists) {
    return rows.map((r) => ({ ...r, lastTraceAt: null, traceCount: 0, avgLatencyMs: null, totalTokens: 0 }))
  }

  const tStmt = db.prepare(`
    SELECT
      COUNT(*) AS traceCount,
      MAX(ended_at) AS lastTraceAt,
      AVG(latency_ms) AS avgLatencyMs,
      COALESCE(SUM(token_count), 0) AS totalTokens
    FROM traces
    WHERE agent = ?
  `)

  return rows.map((r) => {
    const t = tStmt.get(r.name) as {
      traceCount: number | null
      lastTraceAt: number | null
      avgLatencyMs: number | null
      totalTokens: number | null
    }
    return {
      ...r,
      lastTraceAt: t.lastTraceAt ?? null,
      traceCount: t.traceCount ?? 0,
      avgLatencyMs: t.avgLatencyMs ?? null,
      totalTokens: t.totalTokens ?? 0,
    }
  })
}

async function probeRuntime(runtime: string, baseDir: string, extPattern: RegExp): Promise<SessionRuntime> {
  try {
    const entries = await fs.readdir(baseDir)
    let sessionCount = 0
    let recentCount = 0
    let latestMs = 0
    const cutoff = Date.now() - 24 * 60 * 60 * 1000
    for (const e of entries) {
      if (!extPattern.test(e)) continue
      sessionCount += 1
      try {
        const s = await fs.stat(path.join(baseDir, e))
        const m = s.mtimeMs
        if (m > latestMs) latestMs = m
        if (m > cutoff) recentCount += 1
      } catch {
        // skip
      }
    }
    return {
      runtime,
      baseDir,
      available: true,
      sessionCount,
      recentCount,
      lastModifiedIso: latestMs > 0 ? new Date(latestMs).toISOString() : null,
    }
  } catch {
    return { runtime, baseDir, available: false, sessionCount: 0, recentCount: 0, lastModifiedIso: null }
  }
}

async function probeRuntimeRecursive(runtime: string, baseDir: string, extPattern: RegExp, maxDepth = 2): Promise<SessionRuntime> {
  try {
    let sessionCount = 0
    let recentCount = 0
    let latestMs = 0
    const cutoff = Date.now() - 24 * 60 * 60 * 1000

    async function walk(dir: string, depth: number): Promise<void> {
      if (depth > maxDepth) return
      const entries = await fs.readdir(dir, { withFileTypes: true })
      for (const e of entries) {
        const full = path.join(dir, e.name)
        if (e.isDirectory()) {
          if (e.name === 'node_modules' || e.name.startsWith('.')) continue
          await walk(full, depth + 1)
        } else if (extPattern.test(e.name)) {
          sessionCount += 1
          try {
            const s = await fs.stat(full)
            if (s.mtimeMs > latestMs) latestMs = s.mtimeMs
            if (s.mtimeMs > cutoff) recentCount += 1
          } catch {
            // skip
          }
        }
      }
    }

    await walk(baseDir, 0)
    return {
      runtime,
      baseDir,
      available: true,
      sessionCount,
      recentCount,
      lastModifiedIso: latestMs > 0 ? new Date(latestMs).toISOString() : null,
    }
  } catch {
    return { runtime, baseDir, available: false, sessionCount: 0, recentCount: 0, lastModifiedIso: null }
  }
}

export async function getAgentSnapshot(): Promise<AgentSnapshot> {
  const [claude, kiro, cursor, codex] = await Promise.all([
    probeRuntimeRecursive('claude', path.join(HOME, '.claude', 'projects'), /\.jsonl$/),
    probeRuntimeRecursive('kiro', path.join(HOME, '.kiro', 'sessions'), /\.(jsonl|json)$/),
    probeRuntimeRecursive('cursor', path.join(HOME, '.cursor', 'projects'), /\.(jsonl|json)$/),
    probeRuntime('codex', path.join(HOME, '.codex'), /\.(sqlite|db|jsonl)$/),
  ])

  return {
    ts: Date.now(),
    registered: getRegisteredAgents(),
    runtimes: [claude, kiro, cursor, codex],
  }
}
