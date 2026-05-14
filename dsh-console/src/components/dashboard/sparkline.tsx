'use client'

import { Area, AreaChart, ResponsiveContainer } from 'recharts'

const accentVar: Record<string, string> = {
  gold: 'var(--chart-1)',
  blue: 'var(--chart-2)',
  amber: 'var(--chart-3)',
  green: 'var(--chart-4)',
  cyan: 'var(--chart-5)',
}

export function Sparkline({ data, accent = 'gold' }: { data: number[]; accent?: string }) {
  const stroke = accentVar[accent] ?? accentVar.gold
  const series = data.map((v, i) => ({ i, v }))
  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={series} margin={{ top: 2, right: 2, bottom: 2, left: 2 }}>
        <defs>
          <linearGradient id={`spark-${accent}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={stroke} stopOpacity={0.4} />
            <stop offset="100%" stopColor={stroke} stopOpacity={0} />
          </linearGradient>
        </defs>
        <Area
          type="monotone"
          dataKey="v"
          stroke={stroke}
          strokeWidth={1.5}
          fill={`url(#spark-${accent})`}
          isAnimationActive={false}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
