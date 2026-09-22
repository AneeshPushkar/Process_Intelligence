import { LogOut, Menu, User as UserIcon } from 'lucide-react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

const meta = {
  '/': {
    title: 'Dashboard',
    description: 'Workspace overview of analyzed processes, confidence, and recent activity.',
  },
  '/dashboard': {
    title: 'Dashboard',
    description: 'Workspace overview of analyzed processes, confidence, and recent activity.',
  },
  '/analyze': {
    title: 'Analyze Process',
    description: 'Describe a business process in natural language to generate a model.',
  },
  '/analysis': {
    title: 'Process Analysis',
    description: 'Multi-agent results, confidence, and validation for the current process.',
  },
  '/process-analysis': {
    title: 'Process Analysis',
    description: 'Multi-agent results, confidence, and validation for the current process.',
  },
  '/process-model': {
    title: 'Process Model',
    description: 'Interactive graph of activities, decisions, and terminal events.',
  },
  '/intelligence': {
    title: 'Process Intelligence',
    description: 'Bottlenecks, risks, redundancy, and recommended optimizations.',
  },
  '/process-intelligence': {
    title: 'Process Intelligence',
    description: 'Bottlenecks, risks, redundancy, and recommended optimizations.',
  },
  '/processes': {
    title: 'Process History',
    description: 'Search and filter previously analyzed processes in this workspace.',
  },
  '/history': {
    title: 'Process History',
    description: 'Search and filter previously analyzed processes in this workspace.',
  },
  '/settings': {
    title: 'Settings',
    description: 'Workspace preferences and AI runtime configuration.',
  },
}

export default function Header({ onMenu }) {
  const { pathname } = useLocation()
  const page = meta[pathname] ?? { title: 'ProcessIQ', description: '' }
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const displayName = user?.full_name || 'User'
  const organization = user?.organization || user?.email || 'ProcessIQ'

  const initials = displayName
    .split(' ')
    .filter(Boolean)
    .map((w) => w[0])
    .slice(0, 2)
    .join('')
    .toUpperCase() || 'IQ'

  async function handleLogout() {
    await logout()
    navigate('/login')
  }

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center gap-4 border-b border-line bg-surface/90 px-4 backdrop-blur sm:px-6">
      <button
        type="button"
        className="rounded-md p-2 text-muted hover:bg-elevated hover:text-fg lg:hidden"
        onClick={onMenu}
        aria-label="Open navigation"
      >
        <Menu size={18} />
      </button>

      <div className="min-w-0 flex-1">
        <h1 className="truncate text-sm font-semibold text-fg">{page.title}</h1>
        {page.description && (
          <p className="hidden truncate text-xs text-muted sm:block">{page.description}</p>
        )}
      </div>

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 rounded-lg border border-line bg-elevated py-1 pr-3 pl-1.5">
          <div className="flex h-7 w-7 items-center justify-center rounded-md bg-accent/15 text-xs font-semibold text-accent">
            {initials}
          </div>
          <div className="hidden sm:block text-left">
            <p className="truncate text-xs font-medium text-fg max-w-[140px]">{displayName}</p>
            <p className="truncate text-[10px] text-faint max-w-[140px]">{organization}</p>
          </div>
        </div>

        <button
          type="button"
          onClick={handleLogout}
          title="Sign out"
          className="flex h-8 w-8 items-center justify-center rounded-lg border border-line bg-canvas text-muted transition-colors hover:bg-elevated hover:text-warn"
        >
          <LogOut size={15} />
        </button>
      </div>
    </header>
  )
}
