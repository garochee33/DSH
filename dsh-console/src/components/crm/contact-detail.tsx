'use client'

import { useState, useTransition } from 'react'
import Link from 'next/link'
import { ArrowLeft, Phone, Mail, Plus, X, Tag as TagIcon } from 'lucide-react'
import { format, formatDistanceToNow } from 'date-fns'
import { toast } from 'sonner'
import type { ContactDetail } from '@/lib/contacts'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { addTag, removeTag, addNote, deleteNote, logInteraction } from '@/app/crm/actions'

const INTERACTION_KINDS = ['call', 'email', 'meeting', 'message', 'event', 'other'] as const

export function ContactDetailView({ contact }: { contact: ContactDetail }) {
  const [, startTransition] = useTransition()
  const [tagInput, setTagInput] = useState('')
  const [noteInput, setNoteInput] = useState('')
  const [interactionKind, setInteractionKind] = useState<(typeof INTERACTION_KINDS)[number]>('call')
  const [interactionSummary, setInteractionSummary] = useState('')

  const handleAddTag = () => {
    const t = tagInput.trim()
    if (!t) return
    startTransition(async () => {
      const r = await addTag(contact.id, t)
      if (r.ok) {
        setTagInput('')
        toast.success(`Tagged "${t}"`)
      } else {
        toast.error(r.error ?? 'Failed to add tag')
      }
    })
  }

  const handleRemoveTag = (tag: string) => {
    startTransition(async () => {
      await removeTag(contact.id, tag)
      toast.success(`Removed "${tag}"`)
    })
  }

  const handleAddNote = () => {
    const text = noteInput.trim()
    if (!text) return
    startTransition(async () => {
      const r = await addNote(contact.id, text)
      if (r.ok) {
        setNoteInput('')
        toast.success('Note saved')
      } else {
        toast.error(r.error ?? 'Failed to save note')
      }
    })
  }

  const handleLogInteraction = () => {
    const text = interactionSummary.trim()
    if (!text) return
    startTransition(async () => {
      const r = await logInteraction(contact.id, interactionKind, text)
      if (r.ok) {
        setInteractionSummary('')
        toast.success(`Logged ${interactionKind}`)
      } else {
        toast.error(r.error ?? 'Failed to log interaction')
      }
    })
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" render={<Link href="/crm" />}>
          <ArrowLeft className="size-4" />
          Back to CRM
        </Button>
      </div>

      <header className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h1 className="font-mono text-2xl font-semibold">{contact.name}</h1>
          <div className="text-muted-foreground mt-2 flex flex-wrap gap-4 font-mono text-xs">
            {contact.first_phone && (
              <span className="flex items-center gap-1.5">
                <Phone className="size-3" />
                {contact.first_phone}
              </span>
            )}
            {contact.first_email && (
              <span className="flex items-center gap-1.5">
                <Mail className="size-3" />
                {contact.first_email}
              </span>
            )}
            <span>
              ID #{contact.id} · imported {format(new Date(contact.created_at), 'yyyy-MM-dd')}
            </span>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {contact.tags.map((t) => (
            <Badge key={t} variant="secondary" className="font-mono text-xs">
              <TagIcon className="mr-1 size-3" />
              {t}
              <button
                type="button"
                onClick={() => handleRemoveTag(t)}
                className="hover:text-destructive ml-1"
                aria-label={`Remove tag ${t}`}
              >
                <X className="size-3" />
              </button>
            </Badge>
          ))}
          <div className="flex items-center gap-1">
            <Input
              placeholder="add tag…"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAddTag()}
              className="h-7 w-28 font-mono text-xs"
            />
            <Button size="sm" variant="outline" onClick={handleAddTag} className="h-7 px-2">
              <Plus className="size-3" />
            </Button>
          </div>
        </div>
      </header>

      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="notes">Notes ({contact.notes.length})</TabsTrigger>
          <TabsTrigger value="interactions">Interactions ({contact.interactions.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="font-mono text-sm">Phones</CardTitle>
            </CardHeader>
            <CardContent>
              {contact.phones.length === 0 ? (
                <p className="text-muted-foreground text-sm">No phones.</p>
              ) : (
                <ul className="space-y-1 font-mono text-sm">
                  {contact.phones.map((p, i) => (
                    <li key={i}>{p}</li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="font-mono text-sm">Emails</CardTitle>
            </CardHeader>
            <CardContent>
              {contact.emails.length === 0 ? (
                <p className="text-muted-foreground text-sm">No emails.</p>
              ) : (
                <ul className="space-y-1 font-mono text-sm break-all">
                  {contact.emails.map((e, i) => (
                    <li key={i}>{e}</li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notes" className="flex flex-col gap-4">
          <Card>
            <CardContent className="pt-6">
              <Textarea
                placeholder="Write a note…"
                value={noteInput}
                onChange={(e) => setNoteInput(e.target.value)}
                rows={3}
                className="font-mono text-sm"
              />
              <div className="mt-2 flex justify-end">
                <Button onClick={handleAddNote} size="sm">
                  Add note
                </Button>
              </div>
            </CardContent>
          </Card>
          {contact.notes.length === 0 ? (
            <p className="text-muted-foreground text-sm">No notes yet.</p>
          ) : (
            <ul className="space-y-3">
              {contact.notes.map((n) => (
                <li key={n.id}>
                  <Card>
                    <CardContent className="flex items-start justify-between gap-3 pt-6">
                      <div className="flex-1">
                        <p className="text-sm whitespace-pre-wrap">{n.body}</p>
                        <p className="text-muted-foreground mt-2 font-mono text-[11px]">
                          {format(new Date(n.created_at), 'yyyy-MM-dd HH:mm')} ·{' '}
                          {formatDistanceToNow(new Date(n.created_at), { addSuffix: true })}
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() =>
                          startTransition(async () => {
                            await deleteNote(n.id)
                            toast.success('Deleted')
                          })
                        }
                      >
                        <X className="size-3" />
                      </Button>
                    </CardContent>
                  </Card>
                </li>
              ))}
            </ul>
          )}
        </TabsContent>

        <TabsContent value="interactions" className="flex flex-col gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col gap-2">
                <div className="flex gap-2">
                  <DropdownMenu>
                    <DropdownMenuTrigger
                      render={
                        <Button variant="outline" size="sm" className="font-mono">
                          {interactionKind}
                        </Button>
                      }
                    />
                    <DropdownMenuContent>
                      {INTERACTION_KINDS.map((k) => (
                        <DropdownMenuItem key={k} onClick={() => setInteractionKind(k)} className="font-mono">
                          {k}
                        </DropdownMenuItem>
                      ))}
                    </DropdownMenuContent>
                  </DropdownMenu>
                  <Input
                    placeholder="Summary…"
                    value={interactionSummary}
                    onChange={(e) => setInteractionSummary(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleLogInteraction()}
                    className="font-mono text-sm"
                  />
                  <Button onClick={handleLogInteraction} size="sm">
                    Log
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
          {contact.interactions.length === 0 ? (
            <p className="text-muted-foreground text-sm">No interactions logged.</p>
          ) : (
            <ul className="space-y-2">
              {contact.interactions.map((it) => (
                <li
                  key={it.id}
                  className="border-border/50 flex items-start justify-between gap-3 rounded-lg border p-3"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="font-mono text-[10px]">
                        {it.kind}
                      </Badge>
                      <span className="text-muted-foreground font-mono text-[11px]">
                        {format(new Date(it.occurred_at), 'yyyy-MM-dd HH:mm')}
                      </span>
                    </div>
                    <p className="mt-1 text-sm whitespace-pre-wrap">{it.summary}</p>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
