import Badge, { validationTone } from '../ui/Badge'
import Card, { CardBody } from '../ui/Card'

export default function ConfidenceMeter({
  overallScore = 0,
  decision = 'REVIEW',
  validationStatus = 'Validated',
}) {
  const value = Math.max(0, Math.min(100, Number(overallScore) || 0))
  const radius = 54
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (value / 100) * circumference

  const decisionColor =
    decision === 'HIGH'
      ? 'border-ok/30 bg-ok/10 text-ok'
      : decision === 'REVIEW'
      ? 'border-warn/30 bg-warn/10 text-warn'
      : 'border-bad/30 bg-bad/10 text-bad'

  return (
    <Card>
      <CardBody className="flex flex-col items-center py-6">
        <p className="text-xs font-medium tracking-wide text-muted uppercase">Overall confidence</p>
        <div className="relative mt-4 h-36 w-36">
          <svg viewBox="0 0 128 128" className="h-full w-full -rotate-90">
            <circle cx="64" cy="64" r={radius} fill="none" stroke="var(--color-line)" strokeWidth="10" />
            <circle
              cx="64"
              cy="64"
              r={radius}
              fill="none"
              stroke="var(--color-accent)"
              strokeWidth="10"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-3xl font-semibold tabular-nums text-fg">{value}%</span>
            <span className={`mt-0.5 rounded px-2 py-0.5 text-[11px] font-semibold uppercase ${decisionColor}`}>
              {decision}
            </span>
          </div>
        </div>
        <div className="mt-4">
          <Badge tone={validationTone(validationStatus)}>
            Validation: {validationStatus}
          </Badge>
        </div>
      </CardBody>
    </Card>
  )
}
