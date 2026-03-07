import { useStore } from '../../../store'
import { MonoValue } from '../../shared/MonoValue'

export function BudgetMeter() {
  const pct = useStore((s) => s.budgetUsedPercent)

  const barColor = pct > 80 ? '#DC2626' : pct > 60 ? '#D97706' : '#059669'

  return (
    <div className="flex items-center gap-2">
      <span className="text-[9px] font-terminal text-[#334155] tracking-wider">BUDGET</span>
      <div className="relative w-16 h-1.5 bg-[#1E293B] rounded-full overflow-hidden">
        <div
          className="absolute top-0 left-0 h-full rounded-full transition-all duration-500 ease-out"
          style={{ width: `${pct}%`, backgroundColor: barColor }}
        />
      </div>
      <MonoValue color={barColor} size="xs">
        {pct}%
      </MonoValue>
    </div>
  )
}
