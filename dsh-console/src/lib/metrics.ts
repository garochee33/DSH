import 'server-only'
import os from 'node:os'
import { exec as execCb } from 'node:child_process'
import { promisify } from 'node:util'
import {
  parseTopCpuPct,
  parseVmStat,
  parseDfOutput,
  parseOllamaList,
  type MacMemory,
} from './metrics-parsers'

const exec = promisify(execCb)

const HOME = os.homedir()

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
  memory: MacMemory
  disk: {
    totalGB: number
    usedGB: number
    freeGB: number
    usedPct: number
  } | null
  ollama: { available: boolean; models: Array<{ name: string; sizeGB: number }> }
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

const cpuRolling: number[] = []

export async function getMetrics(): Promise<SystemMetrics> {
  const [load1, load5, load15] = os.loadavg()

  const [loadPct, memory, disk, ollama] = await Promise.all([
    getSystemCpuPct(),
    getMacMemory(),
    getDiskUsage(),
    getOllama(),
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
    ollama,
    uptime: {
      systemHours: os.uptime() / 3600,
      loadPctRolling: [...cpuRolling],
    },
  }
}
