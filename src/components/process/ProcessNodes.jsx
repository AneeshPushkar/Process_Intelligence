import { Handle, Position } from 'reactflow'
import { cn } from '../../lib/utils'

function HandlePair() {
  return (
    <>
      <Handle type="target" position={Position.Top} className="!h-2.5 !w-2.5 !border-line !bg-accent" />
      <Handle type="source" position={Position.Bottom} className="!h-2.5 !w-2.5 !border-line !bg-accent" />
    </>
  )
}

export function EventNode({ data }) {
  const isStart = data?.kind === 'start' || data?.type === 'start'
  return (
    <div
      className={cn(
        'flex min-h-[72px] min-w-[72px] max-w-[150px] px-2.5 flex-col items-center justify-center rounded-full border-2 bg-elevated text-center shadow-md',
        isStart ? 'border-accent text-accent' : 'border-line-strong text-fg',
      )}
    >
      <HandlePair />
      <span className="text-[9px] font-bold tracking-wide uppercase">
        {isStart ? 'Start' : 'End'}
      </span>
      <span className="text-xs font-semibold line-clamp-2">{data?.label || (isStart ? 'Start' : 'End')}</span>
    </div>
  )
}

export function TaskNode({ data }) {
  return (
    <div className="min-w-[190px] max-w-[250px] rounded-lg border border-line bg-elevated px-3.5 py-3 shadow-md hover:border-accent/60 transition-all hover:shadow-lg">
      <HandlePair />
      <p className="text-[10px] tracking-wide text-accent uppercase font-bold">{data?.actor || 'Activity'}</p>
      <p className="mt-0.5 text-sm font-semibold text-fg leading-tight">{data?.label}</p>
      {data?.description && (
        <p className="mt-1 text-[11px] text-muted line-clamp-2 leading-relaxed">{data.description}</p>
      )}
    </div>
  )
}

export function GatewayNode({ data }) {
  return (
    <div className="flex h-[96px] w-[96px] items-center justify-center relative">
      <HandlePair />
      <div className="flex h-20 w-20 rotate-45 items-center justify-center border-2 border-warn/70 bg-warn/20 shadow-md transition-transform hover:scale-105">
        <span className="-rotate-45 px-1.5 text-center text-[10px] font-bold leading-tight text-fg drop-shadow-sm">
          {data?.label || 'Decision?'}
        </span>
      </div>
    </div>
  )
}

export const nodeTypes = {
  event: EventNode,
  task: TaskNode,
  gateway: GatewayNode,
  start: EventNode,
  end: EventNode,
  activity: TaskNode,
}
