import 'server-only'
import { exec as execCb } from 'node:child_process'
import { promisify } from 'node:util'

const exec = promisify(execCb)

export type OllamaModel = {
  name: string
  sizeGB: number
  modified: string | null
}

export type OllamaRunning = {
  name: string
  processor: string
  context: number | null
  until: string | null
}

export type OllamaSnapshot = {
  ts: number
  available: boolean
  models: OllamaModel[]
  running: OllamaRunning[]
  totalSizeGB: number
  error: string | null
}

const SIZE_UNIT: Record<string, number> = {
  KB: 1 / 1024 / 1024,
  MB: 1 / 1024,
  GB: 1,
  TB: 1024,
}

function parseSize(token: string, unit: string): number {
  const n = Number(token)
  if (!Number.isFinite(n)) return 0
  return n * (SIZE_UNIT[unit.toUpperCase()] ?? 1)
}

function parseList(stdout: string): OllamaModel[] {
  const out: OllamaModel[] = []
  const lines = stdout.split('\n').map((l) => l.trim()).filter(Boolean)
  for (const line of lines) {
    if (line.toUpperCase().startsWith('NAME')) continue
    const parts = line.split(/\s{2,}|\t/).filter(Boolean)
    if (parts.length < 3) {
      const m = line.match(/^(\S+)\s+\S+\s+([\d.]+)\s*(KB|MB|GB|TB)/i)
      if (m) out.push({ name: m[1], sizeGB: parseSize(m[2], m[3]), modified: null })
      continue
    }
    const [name, , sizeRaw, ...rest] = parts
    const sizeMatch = sizeRaw.match(/([\d.]+)\s*(KB|MB|GB|TB)/i)
    const sizeGB = sizeMatch ? parseSize(sizeMatch[1], sizeMatch[2]) : 0
    out.push({ name, sizeGB, modified: rest.join(' ') || null })
  }
  return out
}

function parseRunning(stdout: string): OllamaRunning[] {
  const out: OllamaRunning[] = []
  const lines = stdout.split('\n').map((l) => l.trim()).filter(Boolean)
  for (const line of lines) {
    if (line.toUpperCase().startsWith('NAME')) continue
    const parts = line.split(/\s{2,}|\t/).filter(Boolean)
    if (parts.length < 2) continue
    const name = parts[0]
    const processor = parts.find((p) => /(cpu|gpu|metal|mps)/i.test(p)) ?? '—'
    const ctxStr = parts.find((p) => /context/i.test(p)) ?? null
    const context = ctxStr ? Number(ctxStr.replace(/\D/g, '')) || null : null
    const until = parts[parts.length - 1] ?? null
    out.push({ name, processor, context, until })
  }
  return out
}

export async function getOllamaSnapshot(): Promise<OllamaSnapshot> {
  let models: OllamaModel[] = []
  let running: OllamaRunning[] = []
  let available = false
  let error: string | null = null
  try {
    const { stdout } = await exec('ollama list', { timeout: 3000 })
    models = parseList(stdout)
    available = true
  } catch (err) {
    error = err instanceof Error ? err.message : String(err)
  }
  if (available) {
    try {
      const { stdout } = await exec('ollama ps', { timeout: 3000 })
      running = parseRunning(stdout)
    } catch {
      // ollama ps unavailable on older versions — ignore
    }
  }
  const totalSizeGB = models.reduce((acc, m) => acc + m.sizeGB, 0)
  return { ts: Date.now(), available, models, running, totalSizeGB, error }
}
