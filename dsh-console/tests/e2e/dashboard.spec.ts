import { test, expect } from '@playwright/test'

test.describe('dsh-console dashboard', () => {
  test('renders with live system metrics', async ({ page }) => {
    await page.goto('/')

    // h1
    await expect(page.getByRole('heading', { name: 'Sovereign Node' })).toBeVisible()

    // KPI tile labels
    await expect(page.getByText('CPU', { exact: true })).toBeVisible()
    await expect(page.getByText('Memory', { exact: true })).toBeVisible()
    await expect(page.getByText('Disk', { exact: true })).toBeVisible()

    // Live indicator
    await expect(page.getByText(/LIVE|STALE/)).toBeVisible()

    // Ollama section
    await expect(page.getByText(/Local Models/)).toBeVisible()
  })

  test('/api/metrics returns shape and bug-fix regression guards', async ({ request }) => {
    const res = await request.get('/api/metrics')
    expect(res.status()).toBe(200)
    const m = await res.json()

    // CPU shape + sanity
    expect(m).toHaveProperty('cpu')
    expect(m.cpu.cores).toBeGreaterThan(0)
    expect(m.cpu.loadPct).toBeGreaterThanOrEqual(0)
    expect(m.cpu.loadPct).toBeLessThanOrEqual(100)
    // CPU should track load average within a reasonable band
    // (would catch a regression to process.cpuUsage which decouples from load avg)
    const expectedFromLoad = (m.cpu.load1 / m.cpu.cores) * 100
    expect(Math.abs(m.cpu.loadPct - expectedFromLoad)).toBeLessThan(50)

    // Memory shape + sanity (would catch a regression to os.freemem reporting ~99%)
    expect(m).toHaveProperty('memory')
    expect(m.memory.totalGB).toBeGreaterThan(0)
    expect(m.memory.usedGB).toBeGreaterThan(0)
    expect(m.memory.availableGB).toBeGreaterThan(0)
    expect(m.memory.usedPct).toBeLessThan(95)

    // Disk + Ollama present (Ollama may be available:false on a clean machine)
    expect(m).toHaveProperty('disk')
    expect(m).toHaveProperty('ollama')
  })
})
