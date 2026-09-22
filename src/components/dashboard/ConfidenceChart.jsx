import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import Card, { CardBody, CardHeader } from '../ui/Card'

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-md border border-line bg-elevated px-3 py-2 text-xs shadow-sm">
      <p className="text-muted">{label}</p>
      <p className="mt-0.5 font-medium text-fg">{payload[0].value}% confidence</p>
    </div>
  )
}

export default function ConfidenceChart({ data = [] }) {
  const hasData = data && data.length > 0

  return (
    <Card className="h-full">
      <CardHeader>
        <h2 className="text-sm font-semibold text-fg">Confidence trend</h2>
        <p className="mt-0.5 text-xs text-muted">Real confidence scores from your analyzed workflows</p>
      </CardHeader>
      <CardBody className="h-56">
        {hasData ? (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="confidenceFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#14b8a6" stopOpacity={0.28} />
                  <stop offset="100%" stopColor="#14b8a6" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="var(--color-line)" vertical={false} />
              <XAxis dataKey="month" tick={{ fill: 'var(--color-faint)', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis domain={[0, 100]} tick={{ fill: 'var(--color-faint)', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip content={<ChartTooltip />} />
              <Area type="monotone" dataKey="confidence" stroke="#14b8a6" strokeWidth={2} fill="url(#confidenceFill)" />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex h-full flex-col items-center justify-center text-center text-xs text-muted">
            <p>No confidence data yet.</p>
            <p className="mt-1 text-faint">Analyze a process to see confidence trends here.</p>
          </div>
        )}
      </CardBody>
    </Card>
  )
}
