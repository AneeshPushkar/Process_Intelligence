import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, RefreshCw } from 'lucide-react'
import { api } from '../lib/api'
import Button from '../components/ui/Button'
import StatsGrid, { ConfidenceChart, RecentProcesses } from '../components/dashboard/StatsGrid'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function fetchStats() {
    setLoading(true)
    setError('')
    try {
      const data = await api.dashboard.getStats()
      setStats(data)
    } catch (err) {
      setError(err.message || 'Failed to load workspace dashboard.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStats()
  }, [])

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <section className="overflow-hidden rounded-xl border border-line bg-elevated">
        <div className="relative px-6 py-8 sm:px-8 sm:py-10">
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,rgba(20,184,166,0.12),transparent_50%)]" />
          <div className="relative max-w-2xl">
            <p className="text-xs font-medium tracking-wide text-accent uppercase">ProcessIQ</p>
            <h2 className="mt-2 text-2xl font-semibold tracking-tight text-fg sm:text-3xl">
              AI-Powered Enterprise Process Intelligence
            </h2>
            <p className="mt-3 max-w-xl text-sm leading-6 text-muted">
              Transform natural-language business processes into validated, intelligent process models
              using a coordinated multi-agent workflow — analyst, modeler, validator, confidence, and intelligence.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Button as={Link} to="/analyze">
                Analyze a Process
                <ArrowRight size={16} />
              </Button>
              <Button variant="secondary" onClick={fetchStats} disabled={loading}>
                <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
                Refresh
              </Button>
            </div>
          </div>
        </div>
      </section>

      {error && (
        <div className="rounded-lg border border-warn/30 bg-warn/10 p-4 text-xs text-warn">
          {error}
        </div>
      )}

      <StatsGrid stats={stats} />

      <div className="grid gap-4 lg:grid-cols-5">
        <div className="lg:col-span-3">
          <RecentProcesses processes={stats?.recent_processes || []} />
        </div>
        <div className="lg:col-span-2">
          <ConfidenceChart data={stats?.confidence_trend || []} />
        </div>
      </div>
    </div>
  )
}
