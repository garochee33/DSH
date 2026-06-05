import { notFound } from 'next/navigation'
import { getContactDetail } from '@/lib/contacts'
import { ContactDetailView } from '@/components/crm/contact-detail'

export const dynamic = 'force-dynamic'

export default async function ContactPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const contactId = Number(id)
  if (!Number.isFinite(contactId)) notFound()
  const contact = getContactDetail(contactId)
  if (!contact) notFound()
  return <ContactDetailView contact={contact} />
}
