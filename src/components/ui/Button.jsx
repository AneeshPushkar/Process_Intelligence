import { cn } from '../../lib/utils'

const variants = {
  primary:
    'bg-accent text-accent-fg hover:brightness-110 focus-visible:outline-accent',
  secondary:
    'bg-elevated text-fg border border-line hover:border-line-strong hover:bg-surface',
  ghost: 'text-muted hover:text-fg hover:bg-elevated',
}

const sizes = {
  sm: 'h-8 px-3 text-xs',
  md: 'h-10 px-4 text-sm',
  lg: 'h-11 px-5 text-sm',
}

export default function Button({
  as: Comp = 'button',
  variant = 'primary',
  size = 'md',
  className,
  type,
  ...props
}) {
  return (
    <Comp
      type={Comp === 'button' ? type || 'button' : type}
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors disabled:pointer-events-none disabled:opacity-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2',
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    />
  )
}
