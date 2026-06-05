'use server'

import { revalidatePath } from 'next/cache'
import { z } from 'zod'
import { getDb } from '@/lib/db'

const idSchema = z.number().int().positive()

export async function addTag(contactId: number, tag: string) {
  const id = idSchema.parse(contactId)
  const t = tag.trim().toLowerCase()
  if (t.length === 0 || t.length > 64) return { ok: false, error: 'tag must be 1-64 chars' }
  const db = getDb()
  db.prepare('INSERT OR IGNORE INTO contact_tags (contact_id, tag) VALUES (?, ?)').run(id, t)
  revalidatePath('/crm')
  revalidatePath(`/crm/${id}`)
  return { ok: true }
}

export async function removeTag(contactId: number, tag: string) {
  const id = idSchema.parse(contactId)
  const db = getDb()
  db.prepare('DELETE FROM contact_tags WHERE contact_id = ? AND tag = ?').run(id, tag.trim().toLowerCase())
  revalidatePath('/crm')
  revalidatePath(`/crm/${id}`)
  return { ok: true }
}

export async function addNote(contactId: number, body: string) {
  const id = idSchema.parse(contactId)
  const text = body.trim()
  if (text.length === 0) return { ok: false, error: 'note cannot be empty' }
  if (text.length > 10_000) return { ok: false, error: 'note too long' }
  const db = getDb()
  db.prepare('INSERT INTO contact_notes (contact_id, body) VALUES (?, ?)').run(id, text)
  revalidatePath(`/crm/${id}`)
  return { ok: true }
}

export async function deleteNote(noteId: number) {
  const id = idSchema.parse(noteId)
  const db = getDb()
  const row = db.prepare('SELECT contact_id FROM contact_notes WHERE id = ?').get(id) as
    | { contact_id: number }
    | undefined
  db.prepare('DELETE FROM contact_notes WHERE id = ?').run(id)
  if (row) revalidatePath(`/crm/${row.contact_id}`)
  return { ok: true }
}

const interactionKindSchema = z.enum(['call', 'email', 'meeting', 'message', 'event', 'other'])

export async function logInteraction(
  contactId: number,
  kind: z.infer<typeof interactionKindSchema>,
  summary: string,
  occurredAt?: string,
) {
  const id = idSchema.parse(contactId)
  const k = interactionKindSchema.parse(kind)
  const text = summary.trim()
  if (text.length === 0) return { ok: false, error: 'summary cannot be empty' }
  if (text.length > 10_000) return { ok: false, error: 'summary too long' }
  const db = getDb()
  if (occurredAt) {
    db.prepare('INSERT INTO interactions (contact_id, kind, summary, occurred_at) VALUES (?, ?, ?, ?)').run(
      id,
      k,
      text,
      occurredAt,
    )
  } else {
    db.prepare('INSERT INTO interactions (contact_id, kind, summary) VALUES (?, ?, ?)').run(id, k, text)
  }
  revalidatePath(`/crm/${id}`)
  return { ok: true }
}
