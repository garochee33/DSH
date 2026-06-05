import { seedE2eDatabase, E2E_DB_PATH } from './setup'

export default async function globalSetup() {
  seedE2eDatabase()
  process.stdout.write(`[playwright] seeded e2e database at ${E2E_DB_PATH}\n`)
}
