'use client'

import { useDeferredValue, useMemo, useRef, useState } from 'react'
import Link from 'next/link'
import { useVirtualizer } from '@tanstack/react-virtual'
import { Search, MessageSquareText, Tag } from 'lucide-react'
import type { ContactListItem } from '@/lib/contacts'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

const ROW_HEIGHT = 56

export function ContactList({ contacts }: { contacts: ContactListItem[] }) {
  const [query, setQuery] = useState('')
  const deferredQuery = useDeferredValue(query)

  const filtered = useMemo(() => {
    const q = deferredQuery.trim().toLowerCase()
    if (q.length === 0) return contacts
    return contacts.filter(
      (c) =>
        c.name.toLowerCase().includes(q) ||
        (c.first_phone ?? '').toLowerCase().includes(q) ||
        (c.first_email ?? '').toLowerCase().includes(q),
    )
  }, [contacts, deferredQuery])

  const parentRef = useRef<HTMLDivElement>(null)
  // eslint-disable-next-line react-hooks/incompatible-library
  const rowVirtualizer = useVirtualizer({
    count: filtered.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => ROW_HEIGHT,
    overscan: 12,
  })

  return (
    <div className="flex h-full flex-col gap-4">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="font-mono text-2xl font-semibold">CRM</h1>
          <p className="text-muted-foreground font-mono text-xs">
            {filtered.length.toLocaleString()} of {contacts.length.toLocaleString()} contacts
          </p>
        </div>
      </div>

      <div className="relative">
        <Search className="text-muted-foreground absolute top-1/2 left-3 size-4 -translate-y-1/2" />
        <Input
          placeholder="Search by name, phone, or email…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="pl-9 font-mono text-sm"
          autoFocus
        />
      </div>

      <div
        ref={parentRef}
        className="border-border/50 relative h-[calc(100vh-220px)] overflow-auto rounded-lg border"
      >
        <div style={{ height: `${rowVirtualizer.getTotalSize()}px`, width: '100%', position: 'relative' }}>
          {rowVirtualizer.getVirtualItems().map((virtualRow) => {
            const c = filtered[virtualRow.index]
            return (
              <Link
                key={c.id}
                href={`/crm/${c.id}`}
                className={cn(
                  'border-border/30 hover:bg-accent absolute top-0 left-0 flex w-full items-center justify-between gap-4 border-b px-4 py-3 transition-colors',
                )}
                style={{
                  height: `${virtualRow.size}px`,
                  transform: `translateY(${virtualRow.start}px)`,
                }}
              >
                <div className="flex min-w-0 flex-1 flex-col">
                  <span className="truncate font-medium">{c.name}</span>
                  <span className="text-muted-foreground truncate font-mono text-xs">
                    {c.first_phone ?? c.first_email ?? '—'}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  {c.has_notes ? (
                    <MessageSquareText className="text-muted-foreground size-3.5" />
                  ) : null}
                  {c.tag_count > 0 ? (
                    <Badge variant="outline" className="font-mono text-[10px]">
                      <Tag className="mr-1 size-3" />
                      {c.tag_count}
                    </Badge>
                  ) : null}
                </div>
              </Link>
            )
          })}
        </div>
      </div>
    </div>
  )
}
