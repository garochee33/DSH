import { NextResponse } from 'next/server'
import { getMetrics } from '@/lib/metrics'

export const dynamic = 'force-dynamic'

export async function GET() {
  const m = await getMetrics()
  return NextResponse.json(m, {
    headers: { 'cache-control': 'no-store' },
  })
}
