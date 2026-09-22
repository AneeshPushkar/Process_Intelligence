import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlertCircle, Loader2, Plus, Search, Trash2 } from 'lucide-react'
import { api } from '../lib/api'
import { formatDate } from '../lib/utils'
import Badge, { statusTone, validationTone } from '../components/ui/Badge'
import Button from '../components/ui/Button'
import ConfidenceBar from '../components/ui/ConfidenceBar'
import EmptyState from '../components/ui/EmptyState'

export default function ProcessHistory() {
  const [processes, setProcesses] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [validationFilter, setValidationFilter] = useState('all')
  const [error, setError] = useState('')
  const [deletingId, setDeletingId] = useState(null)

  const navigate = useNavigate()

  async function loadProcesses() {
    setLoading(true)
    setError('')
    try {
      const data = await api.processes.list({
        search,
        status: statusFilter,
        validation: validationFilter,
      })
      setProcesses(data || [])
    } catch (err) {
      setError(err.message || 'Failed to fetch process history.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadProcesses()
  }, [search, statusFilter, validationFilter])

  async function handleDelete(id, name, e) {
    e.stopPropagation()
    if (!window.confirm(`Are you sure you want to delete "${name}"?`)) return

    setDeletingId(id)
    try {
      await api.processes.delete(id)
      setProcesses((prev) => prev.filter((p) => p.id !== id))
    } catch (err) {
      alert(err.message || 'Failed to delete process.')
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="mx-auto max-w-6xl space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex min-w-0 flex-1 items-center gap-2 rounded-lg border border-line bg-elevated px-3">
          <Search size={16} className="text-faint" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search processes by name or description..."
            className="h-10 w-full bg-transparent text-sm text-fg outline-none placeholder:text-faint"
          />
        </div>

        <div className="flex flex-wrap gap-2">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="h-10 rounded-lg border border-line bg-elevated px-3 text-sm text-fg"
          >
            <option value="all">All Statuses</option>
            <option value="Completed">Completed</option>
            <option value="Draft">Draft</option>
            <option value="Analyzing">Analyzing</option>
            <option value="Failed">Failed</option>
          </select>

          <select
            value={validationFilter}
            onChange={(e) => setValidationFilter(e.target.value)}
            className="h-10 rounded-lg border border-line bg-elevated px-3 text-sm text-fg"
          >
            <option value="all">All Validation</option>
            <option value="Validated">Validated</option>
            <option value="Needs review">Needs review</option>
            <option value="Failed">Failed</option>
          </select>

          <Button size="sm" onClick={() => navigate('/analyze')} className="h-10">
            <Plus size={15} />
            New
          </Button>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-warn/30 bg-warn/10 p-3 text-xs text-warn">
          <AlertCircle size={15} />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="flex h-48 items-center justify-center">
          <Loader2 size={24} className="animate-spin text-accent" />
        </div>
      ) : processes.length === 0 ? (
        <EmptyState
          title="No processes match these filters"
          description="Try adjusting your search query or reset your filters."
          actionLabel="Analyze New Process"
          onAction={() => navigate('/analyze')}
        />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-line">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="border-b border-line bg-elevated text-xs text-muted">
              <tr>
                <th className="px-4 py-3 font-medium">Process Name</th>
                <th className="px-4 py-3 font-medium">Analyzed At</th>
                <th className="px-4 py-3 font-medium">Confidence</th>
                <th className="px-4 py-3 font-medium">Validation</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line bg-surface">
              {processes.map((item) => (
                <tr
                  key={item.id}
                  onClick={() => navigate(`/analysis?id=${item.id}`)}
                  className="cursor-pointer hover:bg-elevated/60 transition-colors"
                >
                  <td className="px-4 py-3">
                    <p className="font-medium text-fg">{item.name}</p>
                    <p className="text-xs text-faint">Domain: {item.domain || 'General'}</p>
                  </td>
                  <td className="px-4 py-3 text-xs text-muted">{formatDate(item.created_at)}</td>
                  <td className="px-4 py-3">
                    {item.overall_confidence !== null ? (
                      <div className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="font-medium text-fg">{item.overall_confidence}%</span>
                          <span className="text-[10px] text-faint uppercase font-medium">
                            {item.confidence_decision}
                          </span>
                        </div>
                        <ConfidenceBar value={item.overall_confidence} className="min-w-[120px]" />
                      </div>
                    ) : (
                      <span className="text-xs text-faint">Not Analyzed</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <Badge tone={validationTone(item.validation_status || 'Pending')}>
                      {item.validation_status || 'Pending'}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">
                    <Badge tone={statusTone(item.status)}>{item.status}</Badge>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2" onClick={(e) => e.stopPropagation()}>
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => navigate(`/analysis?id=${item.id}`)}
                      >
                        View
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="text-warn hover:bg-warn/10"
                        disabled={deletingId === item.id}
                        onClick={(e) => handleDelete(item.id, item.name, e)}
                        title="Delete process"
                      >
                        <Trash2 size={14} />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
