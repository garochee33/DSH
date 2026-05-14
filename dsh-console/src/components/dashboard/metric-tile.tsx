import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Sparkline } from './sparkline'
import { cn } from '@/lib/utils'

type Props = {
  label: string
  value: string | number
  unit?: string
  hint?: string
  series?: number[]
  accent?: 'gold' | 'blue' | 'amber' | 'green' | 'cyan' | 'red'
  className?: string
}

const accentMap: Record<NonNullable<Props['accent']>, string> = {
  gold: 'text-[var(--chart-1)]',
  blue: 'text-[var(--chart-2)]',
  amber: 'text-[var(--chart-3)]',
  green: 'text-[var(--chart-4)]',
  cyan: 'text-[var(--chart-5)]',
  red: 'text-destructive',
}

export function MetricTile({ label, value, unit, hint, series, accent = 'gold', className }: Props) {
  return (
    <Card className={cn('overflow-hidden', className)}>
      <CardHeader className="pb-2">
        <CardTitle className="text-muted-foreground text-xs font-medium tracking-wide uppercase">
          {label}
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="flex items-baseline gap-1.5">
          <span className={cn('font-mono text-3xl font-semibold tabular-nums', accentMap[accent])}>
            {value}
          </span>
          {unit && <span className="text-muted-foreground font-mono text-sm">{unit}</span>}
        </div>
        {hint && (
          <p className="text-muted-foreground mt-1 font-mono text-[11px] tabular-nums">{hint}</p>
        )}
        {series && series.length > 1 && (
          <div className="mt-3 h-10">
            <Sparkline data={series} accent={accent} />
          </div>
        )}
      </CardContent>
    </Card>
  )
}
