import { getMetrics } from '@/lib/metrics'
import { DashboardClient } from '@/components/dashboard/dashboard-client'

export const dynamic = 'force-dynamic'

export default async function DashboardPage() {
  const initial = await getMetrics()
  return <DashboardClient initial={initial} />
}
