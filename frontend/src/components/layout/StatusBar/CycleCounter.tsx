import { useStore } from '../../../store'

const MAX_CYCLES = 5

export function CycleCounter() {
  const currentCycle = useStore((s) => s.currentCycle)
  const status = useStore((s) => s.systemStatus)

  const isActive = status === 'INVESTIGATING' || status === 'CONVERGING'

  return (
    <div className="flex items-center gap-1.5">
      <span className="text-[9px] font-mono tracking-wider" style={{ color: '#4A3D2A' }}>CYC</span>
      <span
        className="text-[9px] font-mono tabular-nums"
        style={{ color: isActive ? '#C8912A' : '#8C7A5E' }}
      >
        {currentCycle}/{MAX_CYCLES}
      </span>
    </div>
  )
}
