import 'server-only'
import { getDb, rowToContact, type Contact, type ContactRow } from './db'

export type ContactListItem = {
  id: number
  name: string
  first_phone: string | null
  first_email: string | null
  tag_count: number
  has_notes: 0 | 1
}

export type ContactDetail = Contact & {
  tags: string[]
  notes: Array<{ id: number; body: string; created_at: string }>
  interactions: Array<{
    id: number
    kind: string
    summary: string
    occurred_at: string
    created_at: string
  }>
}

export function listContacts(query?: string, limit = 5000): ContactListItem[] {
  const db = getDb()
  const q = (query ?? '').trim()

  const baseSelect = `
    SELECT
      c.id, c.name, c.first_phone, c.first_email,
      (SELECT COUNT(*) FROM contact_tags t WHERE t.contact_id = c.id) AS tag_count,
      CASE WHEN EXISTS (SELECT 1 FROM contact_notes n WHERE n.contact_id = c.id) THEN 1 ELSE 0 END AS has_notes
    FROM contacts c
  `

  if (q.length === 0) {
    return db.prepare(`${baseSelect} ORDER BY c.name COLLATE NOCASE LIMIT ?`).all(limit) as ContactListItem[]
  }

  const like = `%${q}%`
  return db
    .prepare(
      `${baseSelect}
       WHERE c.name LIKE ? COLLATE NOCASE
          OR c.first_phone LIKE ?
          OR c.first_email LIKE ? COLLATE NOCASE
          OR c.phones LIKE ? COLLATE NOCASE
          OR c.emails LIKE ? COLLATE NOCASE
       ORDER BY c.name COLLATE NOCASE
       LIMIT ?`,
    )
    .all(like, like, like, like, like, limit) as ContactListItem[]
}

export function getContactDetail(id: number): ContactDetail | null {
  const db = getDb()
  const row = db.prepare('SELECT * FROM contacts WHERE id = ?').get(id) as ContactRow | undefined
  if (!row) return null
  const contact = rowToContact(row)
  const tags = (
    db.prepare('SELECT tag FROM contact_tags WHERE contact_id = ? ORDER BY tag').all(id) as { tag: string }[]
  ).map((r) => r.tag)
  const notes = db
    .prepare('SELECT id, body, created_at FROM contact_notes WHERE contact_id = ? ORDER BY created_at DESC')
    .all(id) as ContactDetail['notes']
  const interactions = db
    .prepare(
      'SELECT id, kind, summary, occurred_at, created_at FROM interactions WHERE contact_id = ? ORDER BY occurred_at DESC',
    )
    .all(id) as ContactDetail['interactions']
  return { ...contact, tags, notes, interactions }
}

export function listAllTags(): Array<{ tag: string; count: number }> {
  const db = getDb()
  return db
    .prepare('SELECT tag, COUNT(*) AS count FROM contact_tags GROUP BY tag ORDER BY count DESC, tag')
    .all() as Array<{ tag: string; count: number }>
}
