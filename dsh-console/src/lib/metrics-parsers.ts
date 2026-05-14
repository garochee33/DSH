// Pure parsers — no IO, no `server-only`. Safe to import in tests.
//
// Targets macOS system tools (top, vm_stat, df) and Ollama.
// All functions are total: never throw on bad input, return safe fallbacks.

export function parseTopCpuPct(stdout: string): number {
  const lines = stdout.split('\n')
  const cpuLines = lines.filter((l) => l.startsWith('CPU usage:'))
  // For two-sample top, use the second line (interval); for one sample, use what we have.
  const target = cpuLines[cpuLines.length - 1] ?? ''
  const idleMatch = target.match(/([\d.]+)%\s+idle/)
  if (!idleMatch) return 0
  const idle = parseFloat(idleMatch[1])
  return Math.max(0, Math.min(100, 100 - idle))
}

export type MacMemory = {
  totalGB: number
  usedGB: number
  availableGB: number
  usedPct: number
}

export function parseVmStat(stdout: string, totalBytes: number): MacMemory {
  const pageSizeMatch = stdout.match(/page size of (\d+) bytes/)
  const pageSize = pageSizeMatch ? parseInt(pageSizeMatch[1], 10) : 16384
  const grab = (label: string): number => {
    const re = new RegExp(`Pages ${label}[^:]*:\\s+(\\d+)`)
    const m = stdout.match(re)
    return m ? parseInt(m[1], 10) : 0
  }
  // "Available" matches Activity Monitor's definition: free + inactive (cacheable)
  // + speculative + purgeable. This is much more accurate than os.freemem(),
  // which reports only fully unmapped pages.
  const free = grab('free')
  const inactive = grab('inactive')
  const speculative = grab('speculative')
  const purgeable = grab('purgeable')
  const availablePages = free + inactive + speculative + purgeable
  const availableBytes = availablePages * pageSize
  const usedBytes = Math.max(0, totalBytes - availableBytes)
  return {
    totalGB: totalBytes / 1024 ** 3,
    usedGB: usedBytes / 1024 ** 3,
    availableGB: availableBytes / 1024 ** 3,
    usedPct: totalBytes > 0 ? (usedBytes / totalBytes) * 100 : 0,
  }
}

export type Disk = {
  totalGB: number
  usedGB: number
  freeGB: number
  usedPct: number
}

export function parseDfOutput(stdout: string): Disk | null {
  const lines = stdout.trim().split('\n')
  if (lines.length === 0) return null
  const last = lines[lines.length - 1].split(/\s+/)
  const totalKB = parseInt(last[1], 10)
  const usedKB = parseInt(last[2], 10)
  const freeKB = parseInt(last[3], 10)
  if (!Number.isFinite(totalKB) || totalKB <= 0) return null
  return {
    totalGB: totalKB / 1024 / 1024,
    usedGB: usedKB / 1024 / 1024,
    freeGB: freeKB / 1024 / 1024,
    usedPct: (usedKB / totalKB) * 100,
  }
}

export type OllamaModel = { name: string; sizeGB: number }

export function parseOllamaList(stdout: string): OllamaModel[] {
  const lines = stdout.trim().split('\n').slice(1)
  return lines
    .filter((l) => l.trim().length > 0)
    .map((l) => {
      const parts = l.split(/\s+/)
      const name = parts[0] ?? ''
      // `ollama list` size column is e.g. "4.7 GB"
      const sizeNum = parseFloat(parts[2] ?? '0')
      const unit = (parts[3] ?? '').toLowerCase()
      const sizeGB =
        unit.startsWith('gb') || unit === ''
          ? sizeNum
          : unit.startsWith('mb')
            ? sizeNum / 1024
            : unit.startsWith('tb')
              ? sizeNum * 1024
              : 0
      return { name, sizeGB }
    })
    .filter((m) => m.name.length > 0)
}
