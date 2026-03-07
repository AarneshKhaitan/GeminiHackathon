import { useStore } from '../../../store'

const MAX_CYCLES = 5

export function CycleCounter() {
  const currentCycle = useStore((s) => s.currentCycle)
  const status = useStore((s) => s.systemStatus)

  const isActive = status === 'INVESTIGATING' || status === 'CONVERGING'

  return (
    <div className="flex items-center gap-1.5">
      <span className="text-[9px] font-mono text-[#333333] tracking-wider">CYC</span>
      <span
        className="text-[9px] font-mono tabular-nums"
        style={{ color: isActive ? '#3B82F6' : '#555555' }}
      >
        {currentCycle}/{MAX_CYCLES}
      </span>
    </div>
  )
}
