import { test, expect } from '@playwright/test'
import path from 'node:path'
import fs from 'node:fs'

const SCREENSHOT_DIR = path.join(__dirname, '..', '..', 'docs', 'v-and-v', 'screenshots')

test.beforeAll(() => {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true })
  // DB seeding happens in playwright global-setup (before the server starts touching it).
})

test.describe('dome-console end-to-end happy path', () => {
  test('dashboard renders with live system metrics', async ({ page }) => {
    await page.goto('/')

    await expect(page.getByRole('heading', { name: 'System Dashboard' })).toBeVisible()

    // KPI tile labels
    await expect(page.getByText('CPU', { exact: true })).toBeVisible()
    await expect(page.getByText('Memory', { exact: true })).toBeVisible()
    await expect(page.getByText('Disk', { exact: true })).toBeVisible()
    await expect(page.getByText('Contacts', { exact: true })).toBeVisible()

    // The contacts tile should show the seeded count (5)
    await expect(page.getByText('5', { exact: true }).first()).toBeVisible()

    // Live indicator
    await expect(page.getByText(/LIVE|STALE/)).toBeVisible()

    // Section card titles (CardTitle renders as div, not <h*>)
    await expect(page.getByText('Databases', { exact: true })).toBeVisible()
    await expect(page.getByText('Agents', { exact: true }).first()).toBeVisible()
    await expect(page.getByText('Ollama Models', { exact: true })).toBeVisible()

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '01-dashboard.png'), fullPage: true })
  })

  test('CRM list virtualizes, searches, navigates to detail', async ({ page }) => {
    await page.goto('/crm')

    await expect(page.getByRole('heading', { name: 'CRM' })).toBeVisible()
    // 5 of 5 contacts when no filter
    await expect(page.getByText(/5 of 5 contacts/)).toBeVisible()

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '02-crm-list.png'), fullPage: true })

    // Search filters
    await page.getByPlaceholder(/Search by name/).fill('paradise')
    await expect(page.getByText(/2 of 5 contacts/)).toBeVisible() // Aria Paradise + Estate Mykonos Concierge (paradise.example email)

    // Click first matching contact
    await page.getByRole('link', { name: /Aria Paradise/ }).click()
    await expect(page).toHaveURL(/\/crm\/\d+$/)
    await expect(page.getByRole('heading', { name: 'Aria Paradise' })).toBeVisible()
  })

  test('add tag → log interaction → both visible (full server-action round-trip)', async ({ page }) => {
    // Find Aria's id
    await page.goto('/crm')
    await page.getByPlaceholder(/Search by name/).fill('Aria')
    const link = page.getByRole('link', { name: /Aria Paradise/ })
    await link.click()
    await expect(page).toHaveURL(/\/crm\/\d+$/)

    // Add a tag
    const tagInput = page.getByPlaceholder('add tag…')
    await tagInput.fill('paradise-vip')
    await tagInput.press('Enter')

    // Wait for the BADGE specifically (toast also says "paradise-vip" — disambiguate via badge data-slot).
    await expect(page.locator('[data-slot="badge"]').filter({ hasText: 'paradise-vip' })).toBeVisible({
      timeout: 5_000,
    })

    // Switch to interactions tab and log one
    await page.getByRole('tab', { name: /Interactions/ }).click()

    // Open kind dropdown, pick 'meeting'
    await page.getByRole('button', { name: 'call', exact: true }).click()
    await page.getByRole('menuitem', { name: 'meeting' }).click()
    await expect(page.getByRole('button', { name: 'meeting' })).toBeVisible()

    await page.getByPlaceholder('Summary…').fill('Property tour at Paradise Estate')
    await page.getByRole('button', { name: 'Log', exact: true }).click()

    await expect(page.getByText('Property tour at Paradise Estate')).toBeVisible({ timeout: 5_000 })
    await expect(page.getByText(/Interactions \(1\)/)).toBeVisible()

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '03-contact-detail.png'), fullPage: true })

    // Add a note via Notes tab
    await page.getByRole('tab', { name: /Notes/ }).click()
    await page.getByPlaceholder('Write a note…').fill('Confirmed booking for July 15-22')
    await page.getByRole('button', { name: 'Add note' }).click()
    await expect(page.getByText('Confirmed booking for July 15-22')).toBeVisible({ timeout: 5_000 })

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '04-contact-notes.png'), fullPage: true })

    // Cross-validate: navigate back to /crm; the contact should now show tag count + note marker
    await page.goto('/crm')
    await page.getByPlaceholder(/Search by name/).fill('Aria')
    const ariaRow = page.getByRole('link', { name: /Aria Paradise/ })
    await expect(ariaRow).toBeVisible()
    // Tag count badge (scope to badge data-slot to avoid matching the phone number)
    await expect(ariaRow.locator('[data-slot="badge"]').filter({ hasText: '1' })).toBeVisible()
  })

  test('/api/metrics returns correct shape and matches seeded contact count', async ({ request }) => {
    const res = await request.get('/api/metrics')
    expect(res.status()).toBe(200)
    const m = await res.json()

    expect(m).toHaveProperty('cpu')
    expect(m.cpu.cores).toBeGreaterThan(0)
    expect(m.cpu.loadPct).toBeGreaterThanOrEqual(0)
    expect(m.cpu.loadPct).toBeLessThanOrEqual(100)

    expect(m).toHaveProperty('memory')
    expect(m.memory.totalGB).toBeGreaterThan(0)
    expect(m.memory.usedGB).toBeGreaterThan(0)
    expect(m.memory.availableGB).toBeGreaterThan(0)
    // Tighter guard: original os.freemem() bug reported ~99% on this M4 Pro.
    // vm_stat-derived used% sits in the 50-90 band on a normally loaded machine.
    expect(m.memory.usedPct).toBeLessThan(95)
    // CPU sanity: process-CPU bug (the previous regression) returned a near-zero idle
    // process number. System CPU should be reasonably correlated with load average.
    const expectedFromLoad = (m.cpu.load1 / m.cpu.cores) * 100
    expect(Math.abs(m.cpu.loadPct - expectedFromLoad)).toBeLessThan(50)

    expect(m.contacts.total).toBe(5)
  })
})
