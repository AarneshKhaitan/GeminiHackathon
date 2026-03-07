import { useStore } from '../../../store'

export function EntityBadge() {
  const entity = useStore((s) => s.entityName)
  const ticker = useStore((s) => s.ticker)

  if (!entity) {
    return (
      <span className="text-[10px] font-mono text-[#333333] tracking-wider">
        — NO ENTITY —
      </span>
    )
  }

  return (
    <div className="flex items-center gap-2">
      <div
        className="px-2 py-0.5"
        style={{ border: '1px solid #2D2D2D', backgroundColor: '#0A0A0A' }}
      >
        <span className="text-[10px] font-mono font-medium text-[#E8E8E8] tracking-wider">
          {ticker}
        </span>
      </div>
      <span className="text-[10px] font-mono text-[#555555] truncate max-w-[140px]">
        {entity}
      </span>
    </div>
  )
}
