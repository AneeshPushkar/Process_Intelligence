import { useCallback, useEffect } from 'react'
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  addEdge,
  useEdgesState,
  useNodesState,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { nodeTypes } from './ProcessNodes'

const defaultEdgeOptions = {
  type: 'smoothstep',
  animated: false,
  style: { stroke: '#71717a', strokeWidth: 2 },
  labelStyle: { fill: '#38bdf8', fontSize: 11, fontWeight: 700 },
  labelBgStyle: { fill: '#18181b', stroke: '#38bdf8', strokeWidth: 1.5 },
  labelBgPadding: [8, 4],
  labelBgBorderRadius: 6,
}

export default function ProcessFlow({ model, onNodeClick }) {
  const initialNodes = model?.nodes || []
  const initialEdges = model?.edges || []

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)

  useEffect(() => {
    if (model?.nodes) setNodes(model.nodes)
    if (model?.edges) setEdges(model.edges)
  }, [model, setNodes, setEdges])

  const onConnect = useCallback((connection) => setEdges((eds) => addEdge(connection, eds)), [setEdges])

  return (
    <div className="h-[min(70vh,720px)] min-h-[440px] w-full overflow-hidden rounded-xl border border-line bg-surface relative">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        defaultEdgeOptions={defaultEdgeOptions}
        fitView
        proOptions={{ hideAttribution: true }}
        minZoom={0.2}
        maxZoom={1.8}
      >
        <Background color="#27272a" gap={20} size={1} />
        <Controls showInteractive={false} className="!bg-elevated !border-line !fill-fg" />
        <MiniMap
          pannable
          zoomable
          nodeColor={(node) => {
            if (node.type === 'gateway') return '#fbbf24'
            if (node.type === 'event' || node.type === 'start' || node.type === 'end') return '#14b8a6'
            return '#3f3f46'
          }}
          maskColor="rgba(9,9,11,0.75)"
          className="!bg-surface !border-line rounded-lg"
        />
      </ReactFlow>
    </div>
  )
}
