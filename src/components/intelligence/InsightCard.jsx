import Badge, { severityTone } from '../ui/Badge'
import Card, { CardBody, CardHeader } from '../ui/Card'

export default function InsightCard({ title, items = [] }) {
  return (
    <Card className="h-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-fg">{title}</h2>
          <span className="text-xs text-faint font-medium">({items.length})</span>
        </div>
      </CardHeader>
      <CardBody className="space-y-3.5">
        {items.length === 0 ? (
          <p className="text-xs text-faint py-3 text-center">No items identified in this category.</p>
        ) : (
          items.map((item) => (
            <div key={item.id} className="rounded-lg border border-line bg-surface p-3 space-y-2">
              <div className="flex items-start justify-between gap-3">
                <p className="text-sm font-medium text-fg">{item.title}</p>
                <div className="flex items-center gap-1.5 shrink-0">
                  {item.priority && (
                    <span className="rounded bg-elevated px-1.5 py-0.5 text-[10px] font-semibold text-muted border border-line">
                      {item.priority}
                    </span>
                  )}
                  {item.severity && <Badge tone={severityTone(item.severity)}>{item.severity}</Badge>}
                </div>
              </div>

              <p className="text-xs leading-relaxed text-muted">{item.description || item.detail}</p>

              {item.recommendation && (
                <div className="rounded bg-accent/5 border border-accent/20 p-2 text-xs text-muted">
                  <span className="font-medium text-accent block text-[11px] mb-0.5">Recommendation:</span>
                  {item.recommendation}
                </div>
              )}

              {item.related_node_ids && item.related_node_ids.length > 0 && (
                <div className="flex items-center gap-1 text-[10px] text-faint">
                  <span>Related nodes:</span>
                  {item.related_node_ids.map((nid) => (
                    <span key={nid} className="font-mono bg-elevated px-1 rounded border border-line">
                      {nid}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
      </CardBody>
    </Card>
  )
}
