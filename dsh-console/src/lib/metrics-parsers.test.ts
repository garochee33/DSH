import { describe, it, expect } from 'vitest'
import {
  parseTopCpuPct,
  parseVmStat,
  parseDfOutput,
  parseOllamaList,
} from './metrics-parsers'

describe('parseTopCpuPct', () => {
  it('returns 100 - idle% from a single sample', () => {
    const stdout = `Load Avg: 1.20, 1.10, 1.05
CPU usage: 15.13% user, 11.39% sys, 73.46% idle`
    expect(parseTopCpuPct(stdout)).toBeCloseTo(26.54, 1)
  })

  it('uses the SECOND CPU usage line when top reports two samples', () => {
    const stdout = `CPU usage: 5.0% user, 3.0% sys, 92.0% idle
CPU usage: 20.0% user, 10.0% sys, 70.0% idle`
    expect(parseTopCpuPct(stdout)).toBeCloseTo(30.0, 1)
  })

  it('returns 0 when no CPU line present', () => {
    expect(parseTopCpuPct('')).toBe(0)
    expect(parseTopCpuPct('garbage output')).toBe(0)
  })

  it('clamps to 0..100 even with absurd input', () => {
    expect(parseTopCpuPct('CPU usage: 0% user, 0% sys, -50% idle')).toBeLessThanOrEqual(100)
    expect(parseTopCpuPct('CPU usage: 0% user, 0% sys, 200% idle')).toBeGreaterThanOrEqual(0)
  })
})

describe('parseVmStat', () => {
  const VM_STAT = `Mach Virtual Memory Statistics: (page size of 16384 bytes)
Pages free:                              289457.
Pages active:                            384702.
Pages inactive:                          363573.
Pages speculative:                        28257.
Pages throttled:                              0.
Pages wired down:                        199215.
Pages purgeable:                           7833.`

  it('parses available pages and returns Activity Monitor-style memory', () => {
    const total = 24 * 1024 ** 3
    const m = parseVmStat(VM_STAT, total)
    expect(m.totalGB).toBeCloseTo(24, 1)
    expect(m.availableGB).toBeCloseTo(10.51, 1)
    expect(m.usedGB).toBeCloseTo(13.49, 1)
    expect(m.usedPct).toBeGreaterThan(50)
    expect(m.usedPct).toBeLessThan(60)
  })

  it('handles a different page size (4 KB)', () => {
    const stdout = VM_STAT.replace('page size of 16384', 'page size of 4096')
    const m = parseVmStat(stdout, 24 * 1024 ** 3)
    expect(m.availableGB).toBeLessThan(5)
  })

  it('returns total used = total when vm_stat is empty', () => {
    const total = 16 * 1024 ** 3
    const m = parseVmStat('', total)
    expect(m.totalGB).toBe(16)
    expect(m.availableGB).toBe(0)
    expect(m.usedGB).toBe(16)
    expect(m.usedPct).toBe(100)
  })

  it('never produces negative usedBytes', () => {
    const m = parseVmStat(VM_STAT, 1024) // tiny "total" relative to available
    expect(m.usedGB).toBeGreaterThanOrEqual(0)
    expect(m.usedPct).toBeGreaterThanOrEqual(0)
  })
})

describe('parseDfOutput', () => {
  it('parses macOS df -k output (last line wins)', () => {
    const stdout = `Filesystem  1024-blocks      Used Available Capacity iused      ifree %iused  Mounted on
/dev/disk3s1s1  482568628 369821112 110747516    78%  551250 1107475160    0%   /System/Volumes/Data`
    const d = parseDfOutput(stdout)!
    expect(d).not.toBeNull()
    expect(d.totalGB).toBeCloseTo(460.2, 0)
    expect(d.usedGB).toBeCloseTo(352.7, 0)
    expect(d.freeGB).toBeCloseTo(105.6, 0)
    expect(d.usedPct).toBeCloseTo(76.6, 0)
  })

  it('returns null when df failed / empty', () => {
    expect(parseDfOutput('')).toBeNull()
    expect(parseDfOutput('not a df output')).toBeNull()
  })
})

describe('parseOllamaList', () => {
  it('parses standard ollama list output', () => {
    const stdout = `NAME                ID              SIZE      MODIFIED
llama3.1:8b         42182419e950    4.7 GB    2 days ago
qwen2.5-coder:14b   abc123          9.0 GB    1 week ago
nomic-embed-text    def456          274 MB    3 weeks ago`
    const models = parseOllamaList(stdout)
    expect(models).toHaveLength(3)
    expect(models[0]).toEqual({ name: 'llama3.1:8b', sizeGB: 4.7 })
    expect(models[1]).toEqual({ name: 'qwen2.5-coder:14b', sizeGB: 9.0 })
    expect(models[2].name).toBe('nomic-embed-text')
    expect(models[2].sizeGB).toBeCloseTo(0.267, 2)
  })

  it('returns empty array when only header present', () => {
    expect(parseOllamaList('NAME ID SIZE MODIFIED')).toEqual([])
  })

  it('returns empty array for empty input', () => {
    expect(parseOllamaList('')).toEqual([])
  })
})
