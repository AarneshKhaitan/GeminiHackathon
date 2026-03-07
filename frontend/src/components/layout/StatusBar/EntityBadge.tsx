import { useStore } from '../../../store'

export function EntityBadge() {
  const entity = useStore((s) => s.entityName)
  const ticker = useStore((s) => s.ticker)

  if (!entity) {
    return (
      <div className="flex items-center gap-1.5">
        <span className="text-[11px] font-terminal text-[#273548] tracking-widest">— NO ENTITY —</span>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-2">
      <div className="px-2 py-0.5 rounded border border-[#334155] bg-[#1E293B]">
        <span className="text-[10px] font-terminal font-bold text-[#E2E8F0] tracking-widest">
          {ticker}
        </span>
      </div>
      <span className="text-[11px] font-display font-medium text-[#94A3B8] truncate max-w-[140px]">
        {entity}
      </span>
    </div>
  )
}
