import { Link } from 'react-router-dom'
import { ArrowUpRight } from 'lucide-react'
import { formatDate } from '../../lib/utils'
import Badge, { validationTone } from '../ui/Badge'
import Card, { CardBody, CardHeader } from '../ui/Card'
import ConfidenceChart from './ConfidenceChart'

export default function StatsGrid({ stats }) {
  const statItems = [
    {
      id: 'analyzed',
      label: 'Processes Analyzed',
      value: stats ? String(stats.total_processes) : '0',
      hint: 'In your private workspace',
    },
    {
      id: 'confidence',
      label: 'Average Confidence',
      value: stats && stats.total_processes > 0 ? `${stats.average_confidence}%` : '—',
      hint: 'Authoritative backend score',
    },
    {
      id: 'validated',
      label: 'Validated Processes',
      value: stats ? String(stats.validated_count) : '0',
      hint: 'Passed structural checks',
    },
    {
      id: 'insights',
      label: 'Insights Generated',
      value: stats ? String(stats.insights_generated_count) : '0',
      hint: 'Bottlenecks, risks, opportunities',
    },
  ]

  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {statItems.map((stat) => (
        <Card key={stat.id} hover>
          <CardBody>
            <p className="text-xs text-muted">{stat.label}</p>
            <p className="mt-2 text-2xl font-semibold tracking-tight text-fg">{stat.value}</p>
            <p className="mt-1 text-xs text-faint">{stat.hint}</p>
          </CardBody>
        </Card>
      ))}
    </div>
  )
}

export function RecentProcesses({ processes = [] }) {
  return (
    <Card>
      <CardHeader className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-fg">Recent processes</h2>
          <p className="mt-0.5 text-xs text-muted">Latest analyses in this workspace</p>
        </div>
        <Link to="/processes" className="text-xs font-medium text-accent hover:underline">
          View all
        </Link>
      </CardHeader>
      <CardBody className="p-0">
        {processes.length === 0 ? (
          <div className="py-8 text-center text-xs text-muted">
            <p>No processes analyzed yet.</p>
            <p className="mt-1 text-faint">
              Go to{' '}
              <Link to="/analyze" className="text-accent hover:underline">
                Analyze Process
              </Link>{' '}
              to start your first workflow evaluation.
            </p>
          </div>
        ) : (
          <ul className="divide-y divide-line">
            {processes.map((item) => (
              <li key={item.id}>
                <Link
                  to={`/analysis?id=${item.id}`}
                  className="flex items-center gap-4 px-5 py-3.5 transition-colors hover:bg-surface"
                >
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-fg">{item.name}</p>
                    <p className="mt-0.5 text-xs text-muted">{formatDate(item.created_at)}</p>
                  </div>
                  <div className="hidden text-right sm:block">
                    <p className="text-xs tabular-nums text-fg">
                      {item.overall_confidence !== null ? `${item.overall_confidence}%` : '—'}
                    </p>
                    <p className="text-[11px] text-faint">Confidence</p>
                  </div>
                  <Badge tone={validationTone(item.validation_status || 'Pending')}>
                    {item.validation_status || 'Pending'}
                  </Badge>
                  <ArrowUpRight size={14} className="text-faint" />
                </Link>
              </li>
            ))}
          </ul>
        )}
      </CardBody>
    </Card>
  )
}

export { ConfidenceChart }
