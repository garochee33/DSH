import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import os from 'node:os'
import path from 'node:path'
import fs from 'node:fs'

const tmpDb = path.join(os.tmpdir(), `dome-test-actions-${Date.now()}-${Math.random().toString(36).slice(2)}.db`)
process.env.DOME_DB_PATH = tmpDb

vi.mock('next/cache', () => ({
  revalidatePath: vi.fn(),
}))

import { __resetDbForTests, getDb } from '@/lib/db'
import { addTag, removeTag, addNote, deleteNote, logInteraction } from './actions'

function seedOne(): number {
  const r = getDb()
    .prepare(
      `INSERT INTO contacts (name, phones, emails, first_phone, first_email)
       VALUES ('Test User', '[]', '[]', null, null)`,
    )
    .run()
  return Number(r.lastInsertRowid)
}

let id: number

beforeEach(() => {
  __resetDbForTests()
  if (fs.existsSync(tmpDb)) fs.unlinkSync(tmpDb)
  id = seedOne()
})

afterEach(() => {
  __resetDbForTests()
  if (fs.existsSync(tmpDb)) fs.unlinkSync(tmpDb)
})

describe('addTag', () => {
  it('inserts a normalized (lowercase, trimmed) tag', async () => {
    const r = await addTag(id, '  Mykonos  ')
    expect(r.ok).toBe(true)
    const tags = getDb().prepare('SELECT tag FROM contact_tags WHERE contact_id=?').all(id) as { tag: string }[]
    expect(tags).toEqual([{ tag: 'mykonos' }])
  })

  it('is idempotent (no error or duplicate on second call)', async () => {
    await addTag(id, 'family')
    const r = await addTag(id, 'family')
    expect(r.ok).toBe(true)
    const count = (getDb().prepare('SELECT COUNT(*) AS n FROM contact_tags WHERE contact_id=?').get(id) as {
      n: number
    }).n
    expect(count).toBe(1)
  })

  it('rejects empty tags', async () => {
    expect((await addTag(id, '')).ok).toBe(false)
    expect((await addTag(id, '   ')).ok).toBe(false)
  })

  it('rejects tags > 64 chars', async () => {
    const long = 'x'.repeat(65)
    const r = await addTag(id, long)
    expect(r.ok).toBe(false)
  })

  it('throws on non-positive contact id', async () => {
    await expect(addTag(0, 'x')).rejects.toThrow()
    await expect(addTag(-1, 'x')).rejects.toThrow()
  })
})

describe('removeTag', () => {
  it('removes an existing tag', async () => {
    await addTag(id, 'family')
    await removeTag(id, 'family')
    const tags = getDb().prepare('SELECT tag FROM contact_tags WHERE contact_id=?').all(id)
    expect(tags).toEqual([])
  })

  it('is a noop when tag doesn\'t exist', async () => {
    const r = await removeTag(id, 'nonexistent')
    expect(r.ok).toBe(true)
  })
})

describe('addNote / deleteNote', () => {
  it('adds a note', async () => {
    const r = await addNote(id, 'Sent the contract')
    expect(r.ok).toBe(true)
    const notes = getDb().prepare('SELECT body FROM contact_notes WHERE contact_id=?').all(id) as {
      body: string
    }[]
    expect(notes).toHaveLength(1)
    expect(notes[0].body).toBe('Sent the contract')
  })

  it('rejects empty notes', async () => {
    expect((await addNote(id, '')).ok).toBe(false)
    expect((await addNote(id, '   ')).ok).toBe(false)
  })

  it('rejects notes > 10000 chars', async () => {
    const huge = 'x'.repeat(10_001)
    expect((await addNote(id, huge)).ok).toBe(false)
  })

  it('deletes by note id', async () => {
    await addNote(id, 'note A')
    const noteId = (getDb().prepare('SELECT id FROM contact_notes ORDER BY id DESC LIMIT 1').get() as {
      id: number
    }).id
    await deleteNote(noteId)
    const remaining = getDb().prepare('SELECT COUNT(*) AS n FROM contact_notes WHERE contact_id=?').get(id) as {
      n: number
    }
    expect(remaining.n).toBe(0)
  })
})

describe('logInteraction', () => {
  it('inserts with valid kind + summary', async () => {
    const r = await logInteraction(id, 'call', 'Quick chat')
    expect(r.ok).toBe(true)
    const rows = getDb().prepare('SELECT kind, summary FROM interactions WHERE contact_id=?').all(id)
    expect(rows).toEqual([{ kind: 'call', summary: 'Quick chat' }])
  })

  it('respects an explicit occurred_at', async () => {
    await logInteraction(id, 'meeting', 'Property tour', '2026-05-10 14:30:00')
    const row = getDb().prepare('SELECT occurred_at FROM interactions WHERE contact_id=?').get(id) as {
      occurred_at: string
    }
    expect(row.occurred_at).toBe('2026-05-10 14:30:00')
  })

  it('rejects empty summary', async () => {
    expect((await logInteraction(id, 'call', '')).ok).toBe(false)
  })

  it('rejects an invalid kind', async () => {
    // @ts-expect-error testing runtime validation
    await expect(logInteraction(id, 'fax', 'irrelevant')).rejects.toThrow()
  })

  it('enforces FK: deleting a contact cascades to interactions', async () => {
    await logInteraction(id, 'call', 'Test')
    getDb().prepare('DELETE FROM contacts WHERE id=?').run(id)
    const remaining = (getDb().prepare('SELECT COUNT(*) AS n FROM interactions').get() as { n: number }).n
    expect(remaining).toBe(0)
  })
})
