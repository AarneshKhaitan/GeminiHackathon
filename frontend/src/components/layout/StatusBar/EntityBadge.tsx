import { useStore } from '../../../store'

export function EntityBadge() {
  const entity = useStore((s) => s.entityName)
  const ticker = useStore((s) => s.ticker)

  if (!entity) {
    return (
      <span className="text-[10px] font-mono tracking-wider" style={{ color: '#4A3D2A' }}>
        — NO ENTITY —
      </span>
    )
  }

  return (
    <div className="flex items-center gap-2">
      <div
        className="px-2 py-0.5"
        style={{ border: '1px solid #3D3529', backgroundColor: '#1E1B15' }}
      >
        <span className="text-[10px] font-mono font-medium tracking-wider" style={{ color: '#EDE4D4' }}>
          {ticker}
        </span>
      </div>
      <span className="text-[10px] font-mono truncate max-w-[140px]" style={{ color: '#8C7A5E' }}>
        {entity}
      </span>
    </div>
  )
}
