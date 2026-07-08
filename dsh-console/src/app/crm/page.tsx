import { listContacts } from '@/lib/contacts'
import { ContactList } from '@/components/crm/contact-list'

export const dynamic = 'force-dynamic'

export default async function CrmPage() {
  const contacts = listContacts(undefined, 5000)
  return <ContactList contacts={contacts} />
}
