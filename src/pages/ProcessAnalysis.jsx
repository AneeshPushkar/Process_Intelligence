import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { AlertCircle, AlertTriangle, ArrowRight, CheckCircle2, Cpu, FileText, Info, Loader2, RefreshCw } from 'lucide-react'
import { api } from '../lib/api'
import { cn, formatDate } from '../lib/utils'
import AgentPipeline, { AgentResults } from '../components/analysis/AgentPipeline'
import ConfidenceMeter from '../components/analysis/ConfidenceMeter'
import ConfidenceBar from '../components/ui/ConfidenceBar'
import Button from '../components/ui/Button'
import Card, { CardBody, CardHeader } from '../components/ui/Card'
import EmptyState from '../components/ui/EmptyState'

const tabs = [
  { id: 'overview', label: 'Overview' },
  { id: 'confidence', label: 'Confidence Breakdown' },
  { id: 'agents', label: 'Agent Pipeline' },
  { id: 'validation', label: 'Validation Checks' },
]

export default function ProcessAnalysis() {
  const [searchParams] = useSearchParams()
  const processId = searchParams.get('id') || localStorage.getItem('processiq_active_process_id')

  const [processData, setProcessData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [tab, setTab] = useState('overview')

  async function fetchProcess() {
    setLoading(true)
    setError('')
    try {
      if (processId) {
        const data = await api.processes.get(processId)
        setProcessData(data)
      } else {
        // Fallback to most recent analyzed process
        const list = await api.processes.list()
        if (list && list.length > 0) {
          const latest = await api.processes.get(list[0].id)
          setProcessData(latest)
        }
      }
    } catch (err) {
      setError(err.message || 'Failed to load process analysis.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProcess()
  }, [processId])

  if (loading) {
    return (
      <div className="flex h-72 items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <Loader2 size={24} className="animate-spin text-accent" />
          <p className="text-xs text-muted">Loading process analysis...</p>
        </div>
      </div>
    )
  }

  if (error || !processData) {
    return (
      <EmptyState
        title="No Process Found"
        description={error || "You haven't analyzed a process yet. Enter your workflow description to generate intelligence."}
        actionLabel="Analyze a Process"
        onAction={() => window.location.assign('/analyze')}
      />
    )
  }

  const analysis = processData.analysis || {}
  const model = processData.model || {}
  const validation = processData.validation || {}
  const confidence = processData.confidence || {}
  const intelligence = processData.intelligence || {}

  const overallScore = processData.overall_confidence ?? confidence.overall_score ?? 0
  const decision = processData.confidence_decision ?? confidence.decision ?? 'REVIEW'
  const validationStatus = processData.validation_status || validation.display_status || 'Validated'
  const analysisMode = analysis.provider_name || 'Local Fallback'

  const actors = analysis.actors || []
  const activities = analysis.activities || []
  const decisions = analysis.decisions || []
  const dependencies = analysis.dependencies || []
  const assumptions = analysis.assumptions || []
  const ambiguities = analysis.ambiguities || []

  // Dynamic agent results
  const agentResults = [
    {
      id: 'analyst',
      name: 'Process Analyst',
      role: 'Interprets natural-language descriptions into structured activities, actors, and decision points.',
      status: 'Complete',
      confidence: confidence.analyst_score ?? Math.round(analysis.analyst_confidence || 85),
      findings: `Identified ${activities.length} activity step(s), ${actors.length} actor(s) (${actors.join(', ')}), ${decisions.length} decision gateway(s), and ${dependencies.length} dependency relation(s).`,
    },
    {
      id: 'modeler',
      name: 'Process Modeler',
      role: 'Constructs the hierarchical React Flow graph, topological ordering, and branch routing.',
      status: 'Complete',
      confidence: confidence.model_completeness_score ?? 90,
      findings: `Mapped ${model.nodes?.length || activities.length + 2} graph nodes and ${model.edges?.length || activities.length + 1} directed transitions. Coordinates calculated for visual rendering.`,
    },
    {
      id: 'validator',
      name: 'Validation Agent',
      role: 'Checks structural soundness, reachability, dead-end states, gateway branches, and contradictions.',
      status: validationStatus === 'PASS' || validationStatus === 'Validated' ? 'Complete' : 'Review Needed',
      confidence: confidence.validation_score ?? Math.round(validation.validation_score || 85),
      findings: `Validation status: ${validationStatus}. Process score: ${validation.validation_score ?? 85}%. Checked ${validation.checks?.length || 6} structural rules. Flagged ${validation.issues?.length || 0} issue(s).`,
    },
    {
      id: 'intelligence',
      name: 'Process Intelligence',
      role: 'Evaluates throughput bottlenecks, operational risks, redundancies, and automation opportunities.',
      status: 'Complete',
      confidence: Math.round(overallScore),
      findings: `Generated ${intelligence.bottlenecks?.length || 0} bottleneck(s), ${intelligence.risks?.length || 0} risk(s), ${intelligence.automation_opportunities?.length || 0} automation candidate(s), and ${intelligence.recommendations?.length || 0} recommendation(s).`,
    },
  ]

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      {/* Header & Mode Banner */}
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="inline-flex items-center gap-1.5 rounded-md border border-accent/30 bg-accent/10 px-2.5 py-0.5 text-xs font-medium text-accent">
              <Cpu size={13} />
              Analysis Mode: {analysisMode}
            </span>
            <span className="text-xs text-faint">
              Domain: <strong className="text-muted">{analysis.domain || 'General'}</strong>
            </span>
          </div>
          <h2 className="text-xl font-semibold tracking-tight text-fg">{processData.name}</h2>
          <p className="mt-1 text-xs text-muted">
            Analyzed {formatDate(processData.created_at)} · {activities.length} activities · {decisions.length} gateway(s) · {actors.length} actor(s)
          </p>
        </div>
        <div className="flex gap-2">
          <Button as={Link} to={`/process-model?id=${processData.id}`} variant="secondary" size="sm">
            Open process model
          </Button>
          <Button as={Link} to={`/intelligence?id=${processData.id}`} size="sm">
            View intelligence
          </Button>
        </div>
      </div>

      <AgentPipeline agents={agentResults} />

      {/* Summary and Confidence Meter */}
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card className="h-full">
            <CardHeader>
              <h3 className="text-sm font-semibold text-fg">Process Summary</h3>
            </CardHeader>
            <CardBody className="space-y-4">
              <p className="text-sm leading-6 text-muted">
                {analysis.summary || processData.description}
              </p>

              <div>
                <p className="text-xs font-medium text-faint mb-2">Identified Actors</p>
                <div className="flex flex-wrap gap-2">
                  {actors.length > 0 ? (
                    actors.map((actor) => (
                      <span
                        key={actor}
                        className="rounded-md border border-line bg-surface px-2.5 py-1 text-xs font-medium text-muted"
                      >
                        {actor}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-faint">No specific actors identified</span>
                  )}
                </div>
              </div>

              {ambiguities.length > 0 && (
                <div className="rounded-lg border border-warn/30 bg-warn/10 p-3 space-y-1">
                  <div className="flex items-center gap-1.5 text-xs font-semibold text-warn">
                    <AlertTriangle size={14} />
                    <span>Ambiguities & Vagueness Flagged</span>
                  </div>
                  <ul className="list-disc list-inside text-xs text-muted space-y-0.5">
                    {ambiguities.map((amb, idx) => (
                      <li key={idx}>{amb}</li>
                    ))}
                  </ul>
                </div>
              )}
            </CardBody>
          </Card>
        </div>

        <ConfidenceMeter
          overallScore={overallScore}
          decision={decision}
          validationStatus={validationStatus}
        />
      </div>

      {/* Navigation Tabs */}
      <div className="flex gap-1 rounded-lg border border-line bg-elevated p-1">
        {tabs.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => setTab(item.id)}
            className={cn(
              'flex-1 rounded-md px-3 py-2 text-xs sm:text-sm font-medium transition-colors',
              tab === item.id ? 'bg-surface text-fg shadow-sm' : 'text-muted hover:text-fg',
            )}
          >
            {item.label}
          </button>
        ))}
      </div>

      {/* Tab 1: Overview */}
      {tab === 'overview' && (
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <h3 className="text-sm font-semibold text-fg">Extracted Activities ({activities.length})</h3>
            </CardHeader>
            <CardBody className="p-0">
              <ul className="divide-y divide-line">
                {activities.map((act, index) => (
                  <li key={act.id || index} className="px-5 py-3 flex items-start gap-3">
                    <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-line bg-surface text-[10px] text-faint">
                      {index + 1}
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-fg">{act.name}</p>
                      <p className="text-xs text-faint">
                        Actor: <strong className="text-muted">{act.actor || 'Unassigned'}</strong>
                      </p>
                      {act.description && (
                        <p className="mt-0.5 text-xs text-muted leading-relaxed">{act.description}</p>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h3 className="text-sm font-semibold text-fg">Decisions & Dependencies</h3>
            </CardHeader>
            <CardBody className="space-y-4">
              <div>
                <p className="text-xs font-medium text-faint mb-2">Decisions & Gateways ({decisions.length})</p>
                {decisions.length > 0 ? (
                  <div className="space-y-2">
                    {decisions.map((dec, i) => (
                      <div key={dec.id || i} className="rounded-lg border border-line bg-surface p-2.5 text-xs">
                        <p className="font-semibold text-fg">{dec.condition}</p>
                        <p className="text-faint mt-0.5">{dec.sentence || 'Branching evaluation point'}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-muted">No explicit conditional branches detected (sequential flow).</p>
                )}
              </div>

              <div>
                <p className="text-xs font-medium text-faint mb-2">Process Boundaries</p>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="rounded-lg border border-line bg-surface p-2.5">
                    <span className="text-[10px] font-semibold text-accent uppercase tracking-wide">Start Event</span>
                    <p className="font-medium text-fg mt-1">{analysis.start_event?.name || 'Process Initiated'}</p>
                  </div>
                  <div className="rounded-lg border border-line bg-surface p-2.5">
                    <span className="text-[10px] font-semibold text-faint uppercase tracking-wide">End Event</span>
                    <p className="font-medium text-fg mt-1">{analysis.end_event?.name || 'Process Completed'}</p>
                  </div>
                </div>
              </div>

              {assumptions.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-faint mb-1.5">Assumptions</p>
                  <ul className="list-disc list-inside text-xs text-muted space-y-0.5">
                    {assumptions.map((ass, i) => (
                      <li key={i}>{ass}</li>
                    ))}
                  </ul>
                </div>
              )}
            </CardBody>
          </Card>
        </div>
      )}

      {/* Tab 2: Authoritative Confidence Breakdown */}
      {tab === 'confidence' && (
        <div className="space-y-4">
          <Card>
            <CardHeader className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-fg">Authoritative 5-Component Confidence Formula</h3>
                <p className="mt-0.5 text-xs text-muted">
                  overall = 0.25*Analyst + 0.20*Model + 0.25*Validation + 0.15*Sequence + 0.15*Gateway
                </p>
              </div>
              <div className="text-right">
                <span className="text-2xl font-bold tabular-nums text-fg">{overallScore}%</span>
                <p className="text-[10px] text-faint">Authoritative Score ({decision})</p>
              </div>
            </CardHeader>
            <CardBody className="space-y-5">
              <div className="grid gap-3 sm:grid-cols-5">
                <div className="rounded-lg border border-line bg-surface p-3">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-muted font-medium">Analyst (25%)</span>
                    <span className="font-semibold text-fg">{confidence.analyst_score ?? 0}%</span>
                  </div>
                  <ConfidenceBar value={confidence.analyst_score ?? 0} />
                  <p className="mt-2 text-[10px] text-faint leading-relaxed">Entity extraction, clarity, and actor coverage.</p>
                </div>

                <div className="rounded-lg border border-line bg-surface p-3">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-muted font-medium">Model (20%)</span>
                    <span className="font-semibold text-fg">{confidence.model_completeness_score ?? 0}%</span>
                  </div>
                  <ConfidenceBar value={confidence.model_completeness_score ?? 0} />
                  <p className="mt-2 text-[10px] text-faint leading-relaxed">Nodes, edges, start/end completeness, layout.</p>
                </div>

                <div className="rounded-lg border border-line bg-surface p-3">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-muted font-medium">Validation (25%)</span>
                    <span className="font-semibold text-fg">{confidence.validation_score ?? 0}%</span>
                  </div>
                  <ConfidenceBar value={confidence.validation_score ?? 0} />
                  <p className="mt-2 text-[10px] text-faint leading-relaxed">Structural soundness, defects, and contradictions.</p>
                </div>

                <div className="rounded-lg border border-line bg-surface p-3">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-muted font-medium">Sequence (15%)</span>
                    <span className="font-semibold text-fg">{confidence.sequence_consistency_score ?? 0}%</span>
                  </div>
                  <ConfidenceBar value={confidence.sequence_consistency_score ?? 0} />
                  <p className="mt-2 text-[10px] text-faint leading-relaxed">Reachability, dead-end absence, forward flow.</p>
                </div>

                <div className="rounded-lg border border-line bg-surface p-3">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-muted font-medium">Gateway (15%)</span>
                    <span className="font-semibold text-fg">{confidence.gateway_consistency_score ?? 0}%</span>
                  </div>
                  <ConfidenceBar value={confidence.gateway_consistency_score ?? 0} />
                  <p className="mt-2 text-[10px] text-faint leading-relaxed">Branch completeness or linear flow policy.</p>
                </div>
              </div>

              {confidence.explanation && (
                <div className="rounded-lg border border-accent/20 bg-accent/5 p-4 text-xs text-muted leading-relaxed">
                  <strong className="text-fg block mb-1">Authoritative Explanation:</strong>
                  {confidence.explanation}
                </div>
              )}

              {confidence.reasons && confidence.reasons.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-fg mb-2">Scoring Rationales:</h4>
                  <ul className="space-y-1 text-xs text-muted">
                    {confidence.reasons.map((r, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <Info size={13} className="text-accent mt-0.5 shrink-0" />
                        <span>{r}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardBody>
          </Card>
        </div>
      )}

      {/* Tab 3: Agent Results */}
      {tab === 'agents' && <AgentResults agents={agentResults} />}

      {/* Tab 4: Validation */}
      {tab === 'validation' && (
        <Card>
          <CardHeader className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-fg">Deterministic Validation Report</h3>
              <p className="mt-0.5 text-xs text-muted">Evaluated on the generated process graph and dependency logic</p>
            </div>
            <span
              className={cn(
                'rounded-md px-2.5 py-1 text-xs font-semibold uppercase',
                validationStatus === 'PASS' || validationStatus === 'Validated'
                  ? 'border border-ok/30 bg-ok/10 text-ok'
                  : 'border border-warn/30 bg-warn/10 text-warn',
              )}
            >
              {validationStatus}
            </span>
          </CardHeader>
          <CardBody className="divide-y divide-line p-0">
            {validation.checks?.map((check) => (
              <div key={check.id} className="flex flex-col gap-1 px-5 py-4 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p className="text-sm font-medium text-fg">{check.label}</p>
                  <p className="mt-1 text-xs text-muted leading-relaxed">{check.detail}</p>
                </div>
                <span
                  className={cn(
                    'mt-2 text-xs font-semibold sm:mt-0 uppercase',
                    check.result === 'Pass' ? 'text-ok' : check.result === 'Review' ? 'text-warn' : 'text-bad',
                  )}
                >
                  {check.result}
                </span>
              </div>
            ))}

            {validation.issues && validation.issues.length > 0 && (
              <div className="p-5 space-y-2">
                <p className="text-xs font-semibold text-fg">Issues Detected ({validation.issues.length}):</p>
                {validation.issues.map((iss, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-xs text-warn bg-warn/10 border border-warn/20 rounded p-2.5">
                    <AlertCircle size={14} className="mt-0.5 shrink-0 text-warn" />
                    <div>
                      <span className="font-semibold uppercase text-[10px] tracking-wide mr-1.5">[{iss.severity}]</span>
                      <span>{iss.message}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardBody>
        </Card>
      )}
    </div>
  )
}
