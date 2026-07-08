import Database from 'better-sqlite3'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

export const E2E_DB_PATH = path.join(os.tmpdir(), 'dome-console-e2e.db')

const SCHEMA = `
CREATE TABLE IF NOT EXISTS contacts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  phones TEXT NOT NULL DEFAULT '[]',
  emails TEXT NOT NULL DEFAULT '[]',
  source TEXT,
  first_phone TEXT,
  first_email TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_contacts_name ON contacts(name COLLATE NOCASE);
CREATE UNIQUE INDEX IF NOT EXISTS uniq_contacts_natural
  ON contacts(name, COALESCE(first_phone,''), COALESCE(first_email,''));
CREATE TABLE IF NOT EXISTS contact_tags (
  contact_id INTEGER NOT NULL, tag TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  PRIMARY KEY (contact_id, tag),
  FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS contact_notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  contact_id INTEGER NOT NULL, body TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS interactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  contact_id INTEGER NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('call','email','meeting','message','event','other')),
  summary TEXT NOT NULL,
  occurred_at TEXT NOT NULL DEFAULT (datetime('now')),
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
);
`

export function seedE2eDatabase() {
  if (fs.existsSync(E2E_DB_PATH)) fs.unlinkSync(E2E_DB_PATH)
  const db = new Database(E2E_DB_PATH)
  db.exec(SCHEMA)
  const insert = db.prepare(
    `INSERT INTO contacts (name, phones, emails, first_phone, first_email)
     VALUES (?, ?, ?, ?, ?)`,
  )
  insert.run('Aria Paradise', '["+30 690 0000 001"]', '["aria@paradise.example"]', '+30 690 0000 001', 'aria@paradise.example')
  insert.run('Beatrice Builder', '["+1 555 222 3333"]', '["b@builder.example"]', '+1 555 222 3333', 'b@builder.example')
  insert.run('Cyrus Chef', '["+30 690 0000 003"]', '[]', '+30 690 0000 003', null)
  insert.run('Dimitra Driver', '["+30 690 0000 004"]', '["d@driver.example"]', '+30 690 0000 004', 'd@driver.example')
  insert.run('Estate Mykonos Concierge', '["+30 690 0000 005"]', '["concierge@paradise.example"]', '+30 690 0000 005', 'concierge@paradise.example')
  db.close()
}
