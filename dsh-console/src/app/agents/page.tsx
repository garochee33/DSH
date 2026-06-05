import { getAgentSnapshot } from '@/lib/agents'
import { AgentsClient } from '@/components/agents/agents-client'

export const dynamic = 'force-dynamic'

export default async function AgentsPage() {
  const initial = await getAgentSnapshot()
  return <AgentsClient initial={initial} />
}
