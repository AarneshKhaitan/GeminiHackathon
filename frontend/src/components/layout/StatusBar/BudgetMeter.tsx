import { useStore } from '../../../store'

export function BudgetMeter() {
  const pct = useStore((s) => s.budgetUsedPercent)

  const barColor = pct > 80 ? '#D14B35' : pct > 60 ? '#D4651A' : '#2E9E72'

  return (
    <div className="flex items-center gap-2">
      <span className="text-[9px] font-mono tracking-wider" style={{ color: '#4A3D2A' }}>BUDGET</span>
      <div
        className="relative w-14 overflow-hidden"
        style={{ height: '3px', backgroundColor: '#2E2820' }}
      >
        <div
          className="absolute top-0 left-0 h-full transition-all duration-500 ease-out"
          style={{ width: `${pct}%`, backgroundColor: barColor }}
        />
      </div>
      <span
        className="text-[9px] font-mono tabular-nums"
        style={{ color: barColor }}
      >
        {pct}%
      </span>
    </div>
  )
}
