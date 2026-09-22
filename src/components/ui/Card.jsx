import { cn } from '../../lib/utils'

export default function Card({ className, hover = false, children, ...props }) {
  return (
    <div
      className={cn(
        'rounded-xl border border-line bg-elevated',
        hover && 'transition-colors hover:border-line-strong',
        className,
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export function CardHeader({ className, children }) {
  return <div className={cn('border-b border-line px-5 py-4', className)}>{children}</div>
}

export function CardBody({ className, children }) {
  return <div className={cn('px-5 py-4', className)}>{children}</div>
}
