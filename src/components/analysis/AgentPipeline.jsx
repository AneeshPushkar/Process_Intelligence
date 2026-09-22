import { CheckCircle2 } from 'lucide-react'
import ConfidenceBar from '../ui/ConfidenceBar'
import Card, { CardBody, CardHeader } from '../ui/Card'

export default function AgentPipeline({ agents = [] }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {agents.map((agent, index) => (
        <div key={agent.id} className="relative">
          <Card className="h-full">
            <CardBody>
              <div className="flex items-start justify-between gap-2">
                <p className="text-[11px] font-medium tracking-wide text-faint uppercase">
                  Agent {index + 1}
                </p>
                <span className="inline-flex items-center gap-1 text-[11px] text-ok">
                  <CheckCircle2 size={12} />
                  {agent.status || 'Complete'}
                </span>
              </div>
              <h3 className="mt-2 text-sm font-semibold text-fg">{agent.name}</h3>
              <p className="mt-1 text-xs leading-5 text-muted">{agent.role}</p>
              <div className="mt-4">
                <div className="flex justify-between text-[11px] text-faint mb-1.5">
                  <span>Confidence</span>
                  <span className="tabular-nums font-medium text-fg">{agent.confidence}%</span>
                </div>
                <ConfidenceBar value={agent.confidence} />
              </div>
            </CardBody>
          </Card>
        </div>
      ))}
    </div>
  )
}

export function AgentResults({ agents = [] }) {
  return (
    <div className="space-y-3">
      {agents.map((agent) => (
        <Card key={agent.id}>
          <CardHeader className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-fg">{agent.name}</h3>
            <p className="text-xs tabular-nums text-muted">{agent.confidence}% confidence</p>
          </CardHeader>
          <CardBody>
            <p className="text-sm leading-6 text-muted">{agent.findings}</p>
          </CardBody>
        </Card>
      ))}
    </div>
  )
}
