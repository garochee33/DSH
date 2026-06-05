import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock all external dependencies before importing
type ExecCallback = (err: Error | null, result?: { stdout: string }) => void
vi.mock('node:child_process', () => ({
  exec: vi.fn((cmd: string, _opts: unknown, cb: ExecCallback) => {
    if (cmd.includes('top -l')) cb(null, { stdout: 'CPU usage: 12.5% user, 5.0% sys, 82.5% idle' })
    else if (cmd.includes('vm_stat')) cb(null, { stdout: 'Pages free: 100000.\nPages active: 200000.\nPages inactive: 50000.\nPages speculative: 10000.\nPages wired down: 80000.\n' })
    else if (cmd.includes('df -k')) cb(null, { stdout: 'Filesystem 1024-blocks Used Available Capacity\n/dev/disk1s1 976000000 500000000 476000000 52%\n' })
    else if (cmd.includes('ollama list')) cb(null, { stdout: 'NAME SIZE\nllama3:8b 4.7 GB\n' })
    else cb(new Error('unknown cmd'))
  }),
}))

vi.mock('server-only', () => ({}))

vi.mock('./db', () => ({
  getDb: () => ({
    prepare: () => ({ get: () => ({ n: 5 }) }),
  }),
}))

vi.mock('node:fs/promises', () => ({
  default: {
    stat: vi.fn().mockResolvedValue({ isDirectory: () => false, size: 1048576 }),
    readdir: vi.fn().mockResolvedValue([]),
  },
}))

describe('metrics', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('getMetrics returns complete SystemMetrics shape', async () => {
    const { getMetrics } = await import('./metrics')
    const m = await getMetrics()

    expect(m).toHaveProperty('ts')
    expect(m).toHaveProperty('cpu')
    expect(m.cpu).toHaveProperty('cores')
    expect(m.cpu).toHaveProperty('loadPct')
    expect(m.cpu.cores).toBeGreaterThan(0)

    expect(m).toHaveProperty('memory')
    expect(m.memory.totalGB).toBeGreaterThan(0)
    expect(m.memory.usedPct).toBeGreaterThanOrEqual(0)
    expect(m.memory.usedPct).toBeLessThanOrEqual(100)

    expect(m).toHaveProperty('databases')
    expect(Array.isArray(m.databases)).toBe(true)

    expect(m).toHaveProperty('agents')
    expect(m.agents).toHaveProperty('total')

    expect(m).toHaveProperty('ollama')
    expect(m).toHaveProperty('contacts')
    expect(m.contacts).toHaveProperty('total')

    expect(m).toHaveProperty('uptime')
    expect(m.uptime.systemHours).toBeGreaterThan(0)
  })

  it('cpu loadPct is between 0 and 100', async () => {
    const { getMetrics } = await import('./metrics')
    const m = await getMetrics()
    expect(m.cpu.loadPct).toBeGreaterThanOrEqual(0)
    expect(m.cpu.loadPct).toBeLessThanOrEqual(100)
  })

  it('contacts returns numeric values', async () => {
    const { getMetrics } = await import('./metrics')
    const m = await getMetrics()
    expect(typeof m.contacts.total).toBe('number')
    expect(typeof m.contacts.tagged).toBe('number')
    expect(typeof m.contacts.withNotes).toBe('number')
    expect(typeof m.contacts.recentInteractions).toBe('number')
  })
})
