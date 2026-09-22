import { cn } from '../../lib/utils'

const tones = {
  ok: 'bg-ok/10 text-ok border-ok/20',
  warn: 'bg-warn/10 text-warn border-warn/20',
  danger: 'bg-danger/10 text-danger border-danger/20',
  muted: 'bg-surface text-muted border-line',
  accent: 'bg-accent/10 text-accent border-accent/20',
}

export default function Badge({ tone = 'muted', className, children }) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-md border px-2 py-0.5 text-[11px] font-medium tracking-wide',
        tones[tone],
        className,
      )}
    >
      {children}
    </span>
  )
}

export function validationTone(status) {
  if (status === 'Validated') return 'ok'
  if (status === 'Needs review') return 'warn'
  return 'muted'
}

export function statusTone(status) {
  if (status === 'Complete') return 'accent'
  if (status === 'Draft') return 'muted'
  return 'warn'
}

export function severityTone(severity) {
  if (severity === 'High') return 'danger'
  if (severity === 'Medium') return 'warn'
  return 'muted'
}
