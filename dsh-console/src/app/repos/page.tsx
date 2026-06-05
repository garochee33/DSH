import { getRepos } from '@/lib/repos'
import { ReposClient } from '@/components/repos/repos-client'

export const dynamic = 'force-dynamic'

export default async function ReposPage() {
  const initial = await getRepos()
  return <ReposClient initial={initial} />
}
