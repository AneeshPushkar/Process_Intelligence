import { useEffect, useState } from 'react'
import { CheckCircle2, Cpu, Database, Info, ShieldCheck, User } from 'lucide-react'
import { api } from '../lib/api'
import { useAuth } from '../hooks/useAuth'
import { useTheme } from '../hooks/useTheme'
import Card, { CardBody, CardHeader } from '../components/ui/Card'

export default function Settings() {
  const { theme, setTheme } = useTheme()
  const { user } = useAuth()
  const [health, setHealth] = useState(null)
  const [loadingHealth, setLoadingHealth] = useState(true)

  useEffect(() => {
    async function checkHealth() {
      try {
        const h = await api.health.get()
        setHealth(h)
      } catch {
        setHealth({ status: 'offline', database: 'Unknown', llm_provider: 'Local Fallback' })
      } finally {
        setLoadingHealth(false)
      }
    }
    checkHealth()
  }, [])

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      {/* User Profile */}
      <Card>
        <CardHeader className="flex items-center gap-2">
          <User size={16} className="text-accent" />
          <h2 className="text-sm font-semibold text-fg">User Profile & Tenant Isolation</h2>
        </CardHeader>
        <CardBody className="space-y-4">
          <p className="text-xs text-muted">
            All workflows, models, and dashboard metrics in this session belong exclusively to your user ID.
          </p>
          <div className="grid gap-3 sm:grid-cols-3 text-xs">
            <div className="rounded-lg border border-line bg-canvas p-3">
              <span className="text-faint text-[10px] uppercase font-semibold">Full Name</span>
              <p className="font-medium text-fg mt-0.5">{user?.full_name || '—'}</p>
            </div>
            <div className="rounded-lg border border-line bg-canvas p-3">
              <span className="text-faint text-[10px] uppercase font-semibold">Email Address</span>
              <p className="font-medium text-fg mt-0.5">{user?.email || '—'}</p>
            </div>
            <div className="rounded-lg border border-line bg-canvas p-3">
              <span className="text-faint text-[10px] uppercase font-semibold">Organization</span>
              <p className="font-medium text-fg mt-0.5">{user?.organization || 'Individual Workspace'}</p>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Backend & LLM Runtime Configuration */}
      <Card>
        <CardHeader className="flex items-center gap-2">
          <Cpu size={16} className="text-accent" />
          <h2 className="text-sm font-semibold text-fg">AI Multi-Agent & Backend Runtime</h2>
        </CardHeader>
        <CardBody className="space-y-4">
          <div className="grid gap-3 sm:grid-cols-3 text-xs">
            <div className="rounded-lg border border-line bg-canvas p-3">
              <span className="text-faint text-[10px] uppercase font-semibold">LLM Provider</span>
              <p className="font-medium text-fg mt-0.5">{health?.llm_provider || 'Local Fallback'}</p>
              <span className="text-[10px] text-accent font-medium">Deterministic Rule-Based NLP</span>
            </div>

            <div className="rounded-lg border border-line bg-canvas p-3">
              <span className="text-faint text-[10px] uppercase font-semibold">Database Engine</span>
              <div className="flex items-center gap-1.5 mt-0.5">
                <Database size={13} className="text-ok" />
                <p className="font-medium text-fg">{health?.database || 'SQLite (Local)'}</p>
              </div>
              <span className="text-[10px] text-faint">SQLAlchemy + Alembic</span>
            </div>

            <div className="rounded-lg border border-line bg-canvas p-3">
              <span className="text-faint text-[10px] uppercase font-semibold">Backend Health</span>
              <div className="flex items-center gap-1.5 mt-0.5">
                <CheckCircle2 size={13} className="text-ok" />
                <p className="font-medium text-ok uppercase">{health?.status || 'Active'}</p>
              </div>
              <span className="text-[10px] text-faint">FastAPI / Uvicorn</span>
            </div>
          </div>

          <div className="rounded-lg border border-line bg-surface p-3 text-xs text-muted flex items-start gap-2">
            <ShieldCheck size={16} className="text-accent shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-fg">Security Architecture</p>
              <p className="mt-0.5 text-[11px] leading-relaxed">
                API secrets and credentials are fully isolated on the server side and never exposed to the browser.
                When no external API key is present, the system runs locally in Local Fallback mode with zero external dependency.
              </p>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Confidence Thresholds */}
      <Card>
        <CardHeader className="flex items-center gap-2">
          <Info size={16} className="text-accent" />
          <h2 className="text-sm font-semibold text-fg">Confidence Score Thresholds</h2>
        </CardHeader>
        <CardBody className="space-y-3">
          <p className="text-xs text-muted">
            The project confidence engine calculates the authoritative score using the weighted formula:
          </p>
          <div className="rounded-lg border border-line bg-canvas p-3 font-mono text-xs text-fg">
            overall = 0.25*Analyst + 0.20*Model + 0.25*Validation + 0.15*Sequence + 0.15*Gateway
          </div>
          <div className="grid grid-cols-3 gap-3 text-xs pt-1">
            <div className="rounded border border-ok/30 bg-ok/10 p-2.5 text-center">
              <span className="font-bold text-ok block text-sm">HIGH</span>
              <span className="text-[11px] text-muted">&gt;= 85.0%</span>
            </div>
            <div className="rounded border border-warn/30 bg-warn/10 p-2.5 text-center">
              <span className="font-bold text-warn block text-sm">REVIEW</span>
              <span className="text-[11px] text-muted">60.0% – 84.9%</span>
            </div>
            <div className="rounded border border-bad/30 bg-bad/10 p-2.5 text-center">
              <span className="font-bold text-bad block text-sm">LOW</span>
              <span className="text-[11px] text-muted">&lt; 60.0%</span>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Appearance */}
      <Card>
        <CardHeader>
          <h2 className="text-sm font-semibold text-fg">Appearance</h2>
        </CardHeader>
        <CardBody>
          <p className="mb-3 text-xs text-muted">Theme preference for this browser session. Dark is the product default.</p>
          <div className="grid grid-cols-2 gap-2 max-w-xs">
            {[
              { id: 'dark', label: 'Dark' },
              { id: 'light', label: 'Light' },
            ].map((option) => (
              <button
                key={option.id}
                type="button"
                onClick={() => setTheme(option.id)}
                className={`rounded-lg border px-4 py-2.5 text-xs font-medium transition-colors ${
                  theme === option.id
                    ? 'border-accent/40 bg-accent/10 text-fg'
                    : 'border-line bg-canvas text-muted hover:text-fg'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </CardBody>
      </Card>
    </div>
  )
}
