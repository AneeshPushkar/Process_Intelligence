import { NavLink } from 'react-router-dom'
import {
  Brain,
  FolderKanban,
  LayoutDashboard,
  ScanSearch,
  Settings,
  X,
} from 'lucide-react'
import { cn } from '../../lib/utils'

const links = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/analyze', label: 'Analyze Process', icon: ScanSearch },
  { to: '/processes', label: 'Processes', icon: FolderKanban },
  { to: '/intelligence', label: 'Intelligence', icon: Brain },
  { to: '/settings', label: 'Settings', icon: Settings },
]

export default function Sidebar({ open, onClose }) {
  return (
    <>
      <div
        className={cn(
          'fixed inset-0 z-30 bg-black/50 transition-opacity lg:hidden',
          open ? 'opacity-100' : 'pointer-events-none opacity-0',
        )}
        onClick={onClose}
      />
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-line bg-surface transition-transform lg:static lg:translate-x-0',
          open ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        <div className="flex h-16 items-center justify-between border-b border-line px-5">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-accent/30 bg-accent/10 font-semibold text-accent">
              IQ
            </div>
            <div>
              <p className="text-sm font-semibold tracking-tight text-fg">ProcessIQ</p>
              <p className="text-[11px] text-faint">Process Intelligence</p>
            </div>
          </div>
          <button
            type="button"
            className="rounded-md p-1 text-muted hover:bg-elevated hover:text-fg lg:hidden"
            onClick={onClose}
            aria-label="Close navigation"
          >
            <X size={16} />
          </button>
        </div>

        <nav className="flex-1 space-y-0.5 p-3">
          {links.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={onClose}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors',
                  isActive
                    ? 'bg-elevated text-fg border border-line'
                    : 'text-muted hover:bg-elevated/70 hover:text-fg border border-transparent',
                )
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-line px-5 py-4">
          <p className="text-[11px] font-medium text-muted">ProcessIQ Enterprise AI</p>
          <p className="mt-0.5 text-[11px] text-faint">Multi-Agent Intelligence v1.0.0</p>
        </div>
      </aside>
    </>
  )
}
