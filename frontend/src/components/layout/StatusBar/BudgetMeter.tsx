import { useStore } from '../../../store'

export function BudgetMeter() {
  const pct = useStore((s) => s.budgetUsedPercent)

  const barColor = pct > 80 ? '#FF3333' : pct > 60 ? '#F59E0B' : '#00C27A'

  return (
    <div className="flex items-center gap-2">
      <span className="text-[9px] font-mono text-[#333333] tracking-wider">BUDGET</span>
      <div
        className="relative w-14 overflow-hidden"
        style={{ height: '3px', backgroundColor: '#1C1C1C' }}
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
