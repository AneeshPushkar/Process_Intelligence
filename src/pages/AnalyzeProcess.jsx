import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlertCircle, CheckCircle2, Eraser, Loader2, Sparkles } from 'lucide-react'
import { api } from '../lib/api'
import Button from '../components/ui/Button'
import Card, { CardBody } from '../components/ui/Card'

const BENCHMARK_SAMPLES = [
  {
    id: 'order',
    label: 'Order Fulfillment',
    name: 'Order Fulfillment Process',
    desc: 'A customer places an order. The system checks inventory. If the product is available, payment is processed and the order is shipped. If the product is unavailable, the customer is notified.',
  },
  {
    id: 'onboarding',
    label: 'Employee Onboarding',
    name: 'Employee Onboarding Workflow',
    desc: 'HR receives a new employee application. HR verifies the documents. If the documents are valid, an employee account is created and onboarding begins. If the documents are incomplete, HR requests the missing documents.',
  },
  {
    id: 'loan',
    label: 'Loan Approval',
    name: 'Loan Approval Process',
    desc: 'A customer submits a loan application. The bank verifies the documents and checks the credit score. If the application is approved, the loan is processed. If it is rejected, the customer is notified.',
  },
  {
    id: 'support',
    label: 'Customer Support',
    name: 'Customer Support Resolution',
    desc: 'A customer submits a support request. The support team reviews the issue. If the issue is simple, the support team resolves it. If the issue is complex, it is escalated to a specialist.',
  },
]

const agentSteps = [
  { step: 1, title: 'Process Analyst Agent', desc: 'Extracting activities, actors, decisions, and dependencies' },
  { step: 2, title: 'Process Modeler Agent', desc: 'Synthesizing React Flow graph and topological layout' },
  { step: 3, title: 'Validation Agent', desc: 'Testing workflow soundness, reachability, and branch completeness' },
  { step: 4, title: 'Process Intelligence Agent', desc: 'Detecting bottlenecks, risks, redundancies, and automation' },
  { step: 5, title: 'Confidence Engine', desc: 'Computing explainable 5-component authoritative confidence score' },
]

export default function AnalyzeProcess() {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [error, setError] = useState('')

  const navigate = useNavigate()

  function handleSelectSample(sample) {
    setName(sample.name)
    setDescription(sample.desc)
    setError('')
  }

  function handleFillExample() {
    handleSelectSample(BENCHMARK_SAMPLES[0])
  }

  function handleClear() {
    setName('')
    setDescription('')
    setError('')
  }

  async function handleAnalyze() {
    if (!description.trim()) return
    setError('')
    setAnalyzing(true)
    setCurrentStepIndex(0)

    try {
      // 1. Create process record
      const processName = name.trim() || 'Business Workflow'
      const created = await api.processes.create({
        name: processName,
        description: description.trim(),
      })

      // Simulate progression state visual indicators during real call
      const interval = setInterval(() => {
        setCurrentStepIndex((prev) => (prev < agentSteps.length - 1 ? prev + 1 : prev))
      }, 700)

      // 2. Trigger real backend LangGraph analysis
      const analyzed = await api.processes.analyze(created.id)
      clearInterval(interval)

      // Cache selected process id for immediate navigation
      localStorage.setItem('processiq_active_process_id', analyzed.id)
      navigate(`/analysis?id=${analyzed.id}`)
    } catch (err) {
      setError(err.message || 'Analysis failed. Please ensure the backend is running.')
      setAnalyzing(false)
    }
  }

  return (
    <div className="mx-auto grid max-w-6xl gap-6 lg:grid-cols-5">
      <section className="lg:col-span-3 space-y-4">
        <div>
          <h2 className="text-xl font-semibold tracking-tight text-fg">Analyze a Business Process</h2>
          <p className="mt-1 text-sm text-muted">
            Describe your workflow in natural language. ProcessIQ's multi-agent workflow will extract, model,
            validate, score, and generate intelligence for it.
          </p>
        </div>

        {error && (
          <div className="flex items-start gap-2.5 rounded-lg border border-warn/30 bg-warn/10 p-3 text-xs text-warn">
            <AlertCircle size={15} className="mt-0.5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Benchmark Test Scenarios */}
        <div className="space-y-2 rounded-xl border border-line bg-surface p-3.5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-fg">Benchmark Test Scenarios</span>
            <span className="text-[11px] text-muted">Click any scenario to prefill the form</span>
          </div>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            {BENCHMARK_SAMPLES.map((sample) => (
              <button
                key={sample.id}
                type="button"
                onClick={() => handleSelectSample(sample)}
                disabled={analyzing}
                className="group flex flex-col items-start rounded-lg border border-line bg-elevated/70 p-2.5 text-left transition hover:border-accent/50 hover:bg-elevated focus:outline-none focus:ring-1 focus:ring-accent disabled:opacity-50"
              >
                <span className="text-xs font-semibold text-fg group-hover:text-accent transition-colors">
                  {sample.label}
                </span>
                <span className="line-clamp-2 mt-1 text-[11px] text-muted">
                  {sample.desc}
                </span>
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-3 rounded-xl border border-line bg-elevated p-4">
          <div className="space-y-1">
            <label htmlFor="processName" className="text-xs font-medium text-muted">
              Process Name
            </label>
            <input
              id="processName"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Employee Onboarding, Order Fulfillment, Loan Approval..."
              disabled={analyzing}
              className="h-10 w-full rounded-lg border border-line bg-canvas px-3 text-sm text-fg outline-none focus:border-accent"
            />
          </div>

          <div className="space-y-1">
            <label htmlFor="processDescription" className="text-xs font-medium text-muted">
              Process Description
            </label>
            <textarea
              id="processDescription"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={11}
              disabled={analyzing}
              placeholder="Describe what each participant does in the workflow. Include conditional steps (e.g. 'If documents are incomplete...')..."
              className="w-full resize-y rounded-lg border border-line bg-canvas p-3 text-sm leading-6 text-fg outline-none focus:border-accent placeholder:text-faint"
            />
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3 border-t border-line pt-3">
            <p className="text-xs tabular-nums text-faint">{description.length} characters</p>
            <div className="flex flex-wrap gap-2">
              <Button variant="secondary" size="sm" onClick={handleFillExample} disabled={analyzing}>
                <Sparkles size={14} />
                Example process
              </Button>
              <Button variant="ghost" size="sm" onClick={handleClear} disabled={analyzing}>
                <Eraser size={14} />
                Clear
              </Button>
              <Button size="sm" onClick={handleAnalyze} disabled={!description.trim() || analyzing}>
                {analyzing ? (
                  <>
                    <Loader2 size={14} className="animate-spin" />
                    Analyzing Workflow...
                  </>
                ) : (
                  'Analyze Process'
                )}
              </Button>
            </div>
          </div>
        </div>

        {analyzing && (
          <div className="rounded-xl border border-line bg-surface p-4 space-y-3">
            <p className="text-xs font-semibold text-fg">Multi-Agent Pipeline Execution</p>
            <div className="space-y-2">
              {agentSteps.map((st, idx) => {
                const isDone = idx < currentStepIndex
                const isCurrent = idx === currentStepIndex
                return (
                  <div
                    key={st.step}
                    className={`flex items-center gap-3 rounded-lg border p-2.5 text-xs transition-colors ${
                      isCurrent
                        ? 'border-accent/40 bg-accent/10 text-fg'
                        : isDone
                        ? 'border-line bg-elevated/40 text-muted'
                        : 'border-transparent text-faint'
                    }`}
                  >
                    {isDone ? (
                      <CheckCircle2 size={14} className="text-ok shrink-0" />
                    ) : isCurrent ? (
                      <Loader2 size={14} className="animate-spin text-accent shrink-0" />
                    ) : (
                      <span className="flex h-3.5 w-3.5 items-center justify-center rounded-full border border-line text-[9px]">
                        {st.step}
                      </span>
                    )}
                    <div>
                      <p className="font-medium text-fg">{st.title}</p>
                      <p className="text-[11px] text-faint">{st.desc}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </section>

      <aside className="lg:col-span-2 space-y-4">
        <div>
          <h3 className="text-sm font-semibold text-fg">How ProcessIQ Works</h3>
          <p className="mt-1 text-xs text-muted">A coordinated five-agent LangGraph workflow running on the real backend.</p>
        </div>

        <div className="space-y-3">
          {agentSteps.map((item) => (
            <Card key={item.step}>
              <CardBody className="flex gap-3">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-line bg-surface text-xs font-semibold text-accent">
                  {item.step}
                </div>
                <div>
                  <p className="text-sm font-medium text-fg">{item.title}</p>
                  <p className="mt-1 text-xs leading-5 text-muted">{item.desc}</p>
                </div>
              </CardBody>
            </Card>
          ))}
        </div>
      </aside>
    </div>
  )
}
