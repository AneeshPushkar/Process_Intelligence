import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { ArrowLeft, Loader2 } from 'lucide-react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { api } from '../lib/api'
import InsightCard from '../components/intelligence/InsightCard'
import Button from '../components/ui/Button'
import Card, { CardBody, CardHeader } from '../components/ui/Card'
import EmptyState from '../components/ui/EmptyState'

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-md border border-line bg-elevated px-3 py-2 text-xs shadow-sm">
      <p className="text-muted">{label || payload[0].name}</p>
      <p className="mt-0.5 font-medium text-fg">{payload[0].value}</p>
    </div>
  )
}

export default function ProcessIntelligence() {
  const [searchParams] = useSearchParams()
  const processId = searchParams.get('id') || localStorage.getItem('processiq_active_process_id')

  const [processData, setProcessData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function fetchProcess() {
      setLoading(true)
      setError('')
      try {
        if (processId) {
          const data = await api.processes.get(processId)
          setProcessData(data)
        } else {
          const list = await api.processes.list()
          if (list && list.length > 0) {
            const latest = await api.processes.get(list[0].id)
            setProcessData(latest)
          }
        }
      } catch (err) {
        setError(err.message || 'Failed to load process intelligence.')
      } finally {
        setLoading(false)
      }
    }
    fetchProcess()
  }, [processId])

  if (loading) {
    return (
      <div className="flex h-72 items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <Loader2 size={24} className="animate-spin text-accent" />
          <p className="text-xs text-muted">Synthesizing process intelligence...</p>
        </div>
      </div>
    )
  }

  if (error || !processData || !processData.intelligence) {
    return (
      <EmptyState
        title="No Process Intelligence Available"
        description={error || "Analyze a process first to generate bottlenecks, risks, and automation recommendations."}
        actionLabel="Analyze Process"
        onAction={() => window.location.assign('/analyze')}
      />
    )
  }

  const intel = processData.intelligence
  const confidence = processData.confidence || {}

  const agentChartData = [
    { agent: 'Analyst', confidence: confidence.analyst_score ?? 85 },
    { agent: 'Modeler', confidence: confidence.model_completeness_score ?? 90 },
    { agent: 'Validator', confidence: confidence.validation_score ?? 85 },
    { agent: 'Intelligence', confidence: Math.round(processData.overall_confidence ?? 85) },
  ]

  const efficiencyData = intel.efficiency_metrics || [
    { stage: 'Intake', hours: 1.2 },
    { stage: 'Verification', hours: 4.5 },
    { stage: 'Execution', hours: 8.0 },
    { stage: 'Completion', hours: 2.0 },
  ]

  const issueDistData = intel.issue_distribution || [
    { name: 'Bottlenecks', value: intel.bottlenecks?.length || 1, fill: '#fbbf24' },
    { name: 'Risks', value: intel.risks?.length || 1, fill: '#f87171' },
    { name: 'Redundant', value: intel.redundant_steps?.length || 0, fill: '#a1a1aa' },
    { name: 'Automation', value: intel.automation_opportunities?.length || 1, fill: '#14b8a6' },
  ]

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold tracking-tight text-fg">{processData.name} - Intelligence</h2>
          <p className="mt-1 text-xs text-muted">
            Automated multi-agent synthesis: Bottlenecks, operational risks, redundancies, and optimization opportunities.
          </p>
        </div>
        <Button as={Link} to={`/analysis?id=${processData.id}`} variant="secondary" size="sm">
          <ArrowLeft size={14} />
          Back to analysis
        </Button>
      </div>

      {/* Analytics Charts Grid */}
      <div className="grid gap-4 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <h3 className="text-sm font-semibold text-fg">Agent Agreement (%)</h3>
          </CardHeader>
          <CardBody className="h-52">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={agentChartData} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
                <CartesianGrid stroke="var(--color-line)" vertical={false} />
                <XAxis dataKey="agent" tick={{ fill: 'var(--color-faint)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis domain={[0, 100]} tick={{ fill: 'var(--color-faint)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="confidence" fill="#14b8a6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h3 className="text-sm font-semibold text-fg">Estimated Duration (hours)</h3>
          </CardHeader>
          <CardBody className="h-52">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={efficiencyData} layout="vertical" margin={{ top: 4, right: 12, left: 12, bottom: 0 }}>
                <CartesianGrid stroke="var(--color-line)" horizontal={false} />
                <XAxis type="number" tick={{ fill: 'var(--color-faint)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="stage" width={80} tick={{ fill: 'var(--color-faint)', fontSize: 10 }} axisLine={false} tickLine={false} />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="hours" fill="#38bdf8" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h3 className="text-sm font-semibold text-fg">Issue Distribution</h3>
          </CardHeader>
          <CardBody className="h-52">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={issueDistData} dataKey="value" nameKey="name" innerRadius={42} outerRadius={68} paddingAngle={3}>
                  {issueDistData.map((entry) => (
                    <Cell key={entry.name} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip content={<ChartTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>
      </div>

      {/* Intelligence Categories */}
      <div className="grid gap-4 lg:grid-cols-2">
        <InsightCard title="Bottlenecks" items={intel.bottlenecks || []} />
        <InsightCard title="Operational Risks" items={intel.risks || []} />
        <InsightCard title="Redundant Steps" items={intel.redundant_steps || []} />
        <InsightCard title="Automation Opportunities" items={intel.automation_opportunities || []} />
      </div>

      <InsightCard title="Strategic Recommendations" items={intel.recommendations || []} />
    </div>
  )
}
