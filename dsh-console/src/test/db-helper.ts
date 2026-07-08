import Database from 'better-sqlite3'

/**
 * Build an in-memory SQLite db with the same schema as production.
 * Mirrors src/lib/db.ts ensureSchema().
 */
export function makeTestDb(): Database.Database {
  const db = new Database(':memory:')
  db.pragma('foreign_keys = ON')
  db.exec(`
    CREATE TABLE contacts (
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
    CREATE INDEX idx_contacts_name ON contacts(name COLLATE NOCASE);
    CREATE UNIQUE INDEX uniq_contacts_natural
      ON contacts(name, COALESCE(first_phone,''), COALESCE(first_email,''));

    CREATE TABLE contact_tags (
      contact_id INTEGER NOT NULL,
      tag TEXT NOT NULL,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      PRIMARY KEY (contact_id, tag),
      FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
    );

    CREATE TABLE contact_notes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      contact_id INTEGER NOT NULL,
      body TEXT NOT NULL,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
    );

    CREATE TABLE interactions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      contact_id INTEGER NOT NULL,
      kind TEXT NOT NULL CHECK (kind IN ('call','email','meeting','message','event','other')),
      summary TEXT NOT NULL,
      occurred_at TEXT NOT NULL DEFAULT (datetime('now')),
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
    );
  `)
  return db
}

export function seedContact(db: Database.Database, name: string, phone?: string, email?: string): number {
  const r = db
    .prepare(
      `INSERT INTO contacts (name, phones, emails, first_phone, first_email)
       VALUES (?, ?, ?, ?, ?)`,
    )
    .run(
      name,
      JSON.stringify(phone ? [phone] : []),
      JSON.stringify(email ? [email] : []),
      phone ?? null,
      email ?? null,
    )
  return Number(r.lastInsertRowid)
}
