import Database from 'better-sqlite3'
import path from 'node:path'
import os from 'node:os'

const DEFAULT_DB_PATH = path.join(os.homedir(), 'DSH', 'db', 'dsh.db')

function resolvePath(): string {
  return process.env.DOME_DB_PATH ?? DEFAULT_DB_PATH
}

export const DB_PATH = resolvePath()

let _db: Database.Database | null = null

export function getDb(): Database.Database {
  if (_db) return _db
  const db = new Database(resolvePath())
  if (resolvePath() !== ':memory:') db.pragma('journal_mode = WAL')
  db.pragma('foreign_keys = ON')
  ensureSchema(db)
  _db = db
  return db
}

/** Test-only: close the singleton so the next getDb() rebuilds against current DOME_DB_PATH. */
export function __resetDbForTests(): void {
  if (_db) {
    try {
      _db.close()
    } catch {
      // ignore
    }
    _db = null
  }
}

function ensureSchema(db: Database.Database) {
  db.exec(`
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
    CREATE INDEX IF NOT EXISTS idx_contacts_first_phone ON contacts(first_phone);
    CREATE INDEX IF NOT EXISTS idx_contacts_first_email ON contacts(first_email);

    CREATE UNIQUE INDEX IF NOT EXISTS uniq_contacts_natural
      ON contacts(name, COALESCE(first_phone,''), COALESCE(first_email,''));

    CREATE TABLE IF NOT EXISTS contact_tags (
      contact_id INTEGER NOT NULL,
      tag TEXT NOT NULL,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      PRIMARY KEY (contact_id, tag),
      FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_contact_tags_tag ON contact_tags(tag);

    CREATE TABLE IF NOT EXISTS contact_notes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      contact_id INTEGER NOT NULL,
      body TEXT NOT NULL,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_contact_notes_contact ON contact_notes(contact_id, created_at DESC);

    CREATE TABLE IF NOT EXISTS interactions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      contact_id INTEGER NOT NULL,
      kind TEXT NOT NULL CHECK (kind IN ('call','email','meeting','message','event','other')),
      summary TEXT NOT NULL,
      occurred_at TEXT NOT NULL DEFAULT (datetime('now')),
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_interactions_contact ON interactions(contact_id, occurred_at DESC);
    CREATE INDEX IF NOT EXISTS idx_interactions_occurred ON interactions(occurred_at DESC);
  `)
}

export type ContactRow = {
  id: number
  name: string
  phones: string
  emails: string
  source: string | null
  first_phone: string | null
  first_email: string | null
  created_at: string
  updated_at: string
}

export type Contact = Omit<ContactRow, 'phones' | 'emails'> & {
  phones: string[]
  emails: string[]
}

export function rowToContact(row: ContactRow): Contact {
  return {
    ...row,
    phones: JSON.parse(row.phones || '[]'),
    emails: JSON.parse(row.emails || '[]'),
  }
}
