import { NextResponse } from 'next/server'
import { getAgentSnapshot } from '@/lib/agents'

export const dynamic = 'force-dynamic'

export async function GET() {
  const snap = await getAgentSnapshot()
  return NextResponse.json(snap, { headers: { 'Cache-Control': 'no-store' } })
}
