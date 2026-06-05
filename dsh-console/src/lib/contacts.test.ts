import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import os from 'node:os'
import path from 'node:path'
import fs from 'node:fs'

// CRITICAL: set the env var BEFORE importing modules that read it.
const tmpDb = path.join(os.tmpdir(), `dome-test-contacts-${Date.now()}-${Math.random().toString(36).slice(2)}.db`)
process.env.DOME_DB_PATH = tmpDb

// Stub revalidatePath which next/cache exposes
vi.mock('next/cache', () => ({
  revalidatePath: vi.fn(),
}))

import { __resetDbForTests, getDb } from './db'
import { listContacts, getContactDetail, listAllTags } from './contacts'
import { addTag, addNote, logInteraction } from '@/app/crm/actions'

function seed() {
  const db = getDb()
  db.prepare(
    `INSERT INTO contacts (name, phones, emails, first_phone, first_email)
     VALUES (?, ?, ?, ?, ?)`,
  ).run('Alice Anderson', '["555-1000"]', '["alice@example.com"]', '555-1000', 'alice@example.com')
  db.prepare(
    `INSERT INTO contacts (name, phones, emails, first_phone, first_email)
     VALUES (?, ?, ?, ?, ?)`,
  ).run('Bob Builder', '["555-2000"]', '["bob@example.com"]', '555-2000', 'bob@example.com')
  db.prepare(
    `INSERT INTO contacts (name, phones, emails, first_phone, first_email)
     VALUES (?, ?, ?, ?, ?)`,
  ).run('Charlie Chaplin', '[]', '[]', null, null)
}

beforeEach(() => {
  __resetDbForTests()
  if (fs.existsSync(tmpDb)) fs.unlinkSync(tmpDb)
  seed()
})

afterEach(() => {
  __resetDbForTests()
  if (fs.existsSync(tmpDb)) fs.unlinkSync(tmpDb)
})

describe('listContacts', () => {
  it('returns all contacts when query is empty', () => {
    const all = listContacts(undefined, 1000)
    expect(all).toHaveLength(3)
    expect(all.map((c) => c.name)).toEqual(['Alice Anderson', 'Bob Builder', 'Charlie Chaplin'])
  })

  it('filters by name (case-insensitive substring)', () => {
    const r = listContacts('alice')
    expect(r).toHaveLength(1)
    expect(r[0].name).toBe('Alice Anderson')
  })

  it('filters by phone', () => {
    const r = listContacts('555-2000')
    expect(r).toHaveLength(1)
    expect(r[0].name).toBe('Bob Builder')
  })

  it('filters by email substring', () => {
    const r = listContacts('bob@')
    expect(r).toHaveLength(1)
    expect(r[0].name).toBe('Bob Builder')
  })

  it('respects limit', () => {
    const r = listContacts(undefined, 2)
    expect(r).toHaveLength(2)
  })

  it('reports tag_count and has_notes correctly', async () => {
    await addTag(1, 'family')
    await addTag(1, 'mykonos')
    await addNote(2, 'A note')
    const list = listContacts()
    const alice = list.find((c) => c.id === 1)!
    const bob = list.find((c) => c.id === 2)!
    expect(alice.tag_count).toBe(2)
    expect(alice.has_notes).toBe(0)
    expect(bob.tag_count).toBe(0)
    expect(bob.has_notes).toBe(1)
  })
})

describe('getContactDetail', () => {
  it('returns full detail with parsed arrays + tags + notes + interactions', async () => {
    await addTag(1, 'paradise-guest')
    await addNote(1, 'First call went well')
    await logInteraction(1, 'call', 'Discussed availability', '2026-05-01 10:00:00')
    const c = getContactDetail(1)!
    expect(c).not.toBeNull()
    expect(c.name).toBe('Alice Anderson')
    expect(c.phones).toEqual(['555-1000'])
    expect(c.emails).toEqual(['alice@example.com'])
    expect(c.tags).toEqual(['paradise-guest'])
    expect(c.notes).toHaveLength(1)
    expect(c.notes[0].body).toBe('First call went well')
    expect(c.interactions).toHaveLength(1)
    expect(c.interactions[0].kind).toBe('call')
    expect(c.interactions[0].summary).toBe('Discussed availability')
  })

  it('returns null for nonexistent id', () => {
    expect(getContactDetail(99999)).toBeNull()
  })

  it('handles contact with no phones/emails', () => {
    const c = getContactDetail(3)!
    expect(c.name).toBe('Charlie Chaplin')
    expect(c.phones).toEqual([])
    expect(c.emails).toEqual([])
  })
})

describe('listAllTags', () => {
  it('returns tag→count rows ordered by count desc', async () => {
    await addTag(1, 'mykonos')
    await addTag(2, 'mykonos')
    await addTag(1, 'family')
    const tags = listAllTags()
    expect(tags).toHaveLength(2)
    expect(tags[0]).toEqual({ tag: 'mykonos', count: 2 })
    expect(tags[1]).toEqual({ tag: 'family', count: 1 })
  })
})
