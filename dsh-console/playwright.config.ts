import { defineConfig, devices } from '@playwright/test'
import os from 'node:os'
import path from 'node:path'

const E2E_DB_PATH = path.join(os.tmpdir(), 'dome-console-e2e.db')

export default defineConfig({
  testDir: './tests/e2e',
  outputDir: './test-results',
  globalSetup: './tests/e2e/global-setup.ts',
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
  ],
  use: {
    baseURL: 'http://127.0.0.1:3737',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'off',
  },
  webServer: {
    // Production build (run `pnpm build` first).
    // We hit a static favicon URL so the server doesn't open the DB
    // before tests have finished seeding.
    command: 'pnpm start',
    url: 'http://127.0.0.1:3737/favicon.ico',
    reuseExistingServer: false,
    timeout: 60_000,
    env: {
      DOME_DB_PATH: E2E_DB_PATH,
      NODE_ENV: 'production',
    },
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
})

export const E2E_DB = E2E_DB_PATH
