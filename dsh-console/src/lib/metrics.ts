import 'server-only'
import os from 'node:os'
import fs from 'node:fs/promises'
import path from 'node:path'
import { exec as execCb } from 'node:child_process'
import { promisify } from 'node:util'
import { getDb } from './db'
import {
  parseTopCpuPct,
  parseVmStat,
  parseDfOutput,
  parseOllamaList,
  type MacMemory,
} from './metrics-parsers'

const exec = promisify(execCb)

const HOME = os.homedir()
const DSH_ROOT = path.join(HOME, 'DSH')

export type SystemMetrics = {
  ts: number
  cpu: {
    cores: number
    model: string
    loadPct: number
    load1: number
    load5: number
    load15: number
  }
  memory: {
    totalGB: number
    usedGB: number
    availableGB: number
    usedPct: number
  }
  disk: {
    totalGB: number
    usedGB: number
    freeGB: number
    usedPct: number
  } | null
  databases: Array<{ name: string; sizeMB: number; path: string }>
  agents: { claude: number; kiro: number; total: number }
  ollama: { available: boolean; models: Array<{ name: string; sizeGB: number }> }
  contacts: { total: number; tagged: number; withNotes: number; recentInteractions: number }
  uptime: { systemHours: number; loadPctRolling: number[] }
}

async function getSystemCpuPct(): Promise<number> {
  try {
    const { stdout } = await exec('top -l 2 -n 0 -s 1', { timeout: 2500 })
    return parseTopCpuPct(stdout)
  } catch {
    const [load1] = os.loadavg()
    return Math.max(0, Math.min(100, (load1 / os.cpus().length) * 100))
  }
}

async function getMacMemory(): Promise<MacMemory> {
  const total = os.totalmem()
  try {
    const { stdout } = await exec('vm_stat', { timeout: 2000 })
    return parseVmStat(stdout, total)
  } catch {
    const free = os.freemem()
    return {
      totalGB: total / 1024 ** 3,
      usedGB: (total - free) / 1024 ** 3,
      availableGB: free / 1024 ** 3,
      usedPct: ((total - free) / total) * 100,
    }
  }
}

async function safeStat(p: string): Promise<number | null> {
  try {
    const s = await fs.stat(p)
    if (s.isDirectory()) {
      // Recursive size for chroma dir
      let total = 0
      const entries = await fs.readdir(p, { withFileTypes: true })
      for (const e of entries) {
        const full = path.join(p, e.name)
        const sub = await safeStat(full)
        if (sub != null) total += sub
      }
      return total
    }
    return s.size
  } catch {
    return null
  }
}

async function getDiskUsage(): Promise<SystemMetrics['disk']> {
  try {
    const { stdout } = await exec(`df -k ${HOME}`)
    return parseDfOutput(stdout)
  } catch {
    return null
  }
}

async function getOllama(): Promise<SystemMetrics['ollama']> {
  try {
    const { stdout } = await exec('ollama list', { timeout: 2000 })
    return { available: true, models: parseOllamaList(stdout) }
  } catch {
    return { available: false, models: [] }
  }
}

async function countAgents(dir: string, ext = '.json'): Promise<number> {
  try {
    const entries = await fs.readdir(dir)
    return entries.filter((e) => e.endsWith(ext) && !e.includes('example')).length
  } catch {
    return 0
  }
}

async function getDatabaseSizes(): Promise<SystemMetrics['databases']> {
  const candidates = [
    { name: 'dsh.db', path: path.join(DSH_ROOT, 'db', 'dsh.db') },
    { name: 'episodic.db', path: path.join(DSH_ROOT, 'db', 'episodic.db') },
    { name: 'chroma', path: path.join(DSH_ROOT, 'db', 'chroma') },
  ]
  const out: SystemMetrics['databases'] = []
  for (const c of candidates) {
    const size = await safeStat(c.path)
    if (size != null) out.push({ name: c.name, sizeMB: size / 1024 / 1024, path: c.path })
  }
  return out
}

function getContactStats(): SystemMetrics['contacts'] {
  const db = getDb()
  const total = (db.prepare('SELECT COUNT(*) AS n FROM contacts').get() as { n: number }).n
  const tagged = (db.prepare('SELECT COUNT(DISTINCT contact_id) AS n FROM contact_tags').get() as { n: number }).n
  const withNotes = (db.prepare('SELECT COUNT(DISTINCT contact_id) AS n FROM contact_notes').get() as { n: number }).n
  const recentInteractions = (
    db
      .prepare("SELECT COUNT(*) AS n FROM interactions WHERE occurred_at >= datetime('now','-7 days')")
      .get() as { n: number }
  ).n
  return { total, tagged, withNotes, recentInteractions }
}

const cpuRolling: number[] = []

export async function getMetrics(): Promise<SystemMetrics> {
  const [load1, load5, load15] = os.loadavg()

  const [loadPct, memory, disk, ollama, databases, claudeAgents, kiroAgents] = await Promise.all([
    getSystemCpuPct(),
    getMacMemory(),
    getDiskUsage(),
    getOllama(),
    getDatabaseSizes(),
    countAgents(path.join(HOME, '.claude', 'agents'), '.json'),
    countAgents(path.join(DSH_ROOT, 'home', '.kiro', 'agents'), '.json'),
  ])

  cpuRolling.push(loadPct)
  if (cpuRolling.length > 60) cpuRolling.shift()

  return {
    ts: Date.now(),
    cpu: {
      cores: os.cpus().length,
      model: os.cpus()[0]?.model ?? 'unknown',
      loadPct,
      load1,
      load5,
      load15,
    },
    memory,
    disk,
    databases,
    agents: { claude: claudeAgents, kiro: kiroAgents, total: claudeAgents + kiroAgents },
    ollama,
    contacts: getContactStats(),
    uptime: {
      systemHours: os.uptime() / 3600,
      loadPctRolling: [...cpuRolling],
    },
  }
}
