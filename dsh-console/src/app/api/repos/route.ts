import { NextResponse } from 'next/server'
import { getRepos } from '@/lib/repos'

export const dynamic = 'force-dynamic'

export async function GET() {
  const repos = await getRepos()
  return NextResponse.json(repos, { headers: { 'Cache-Control': 'no-store' } })
}
