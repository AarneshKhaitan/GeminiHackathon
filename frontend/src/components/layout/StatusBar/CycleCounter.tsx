import { useStore } from '../../../store'
import { MonoValue } from '../../shared/MonoValue'

export function CycleCounter() {
  const currentCycle = useStore((s) => s.currentCycle)
  const maxCycles = useStore((s) => s.maxCycles)
  const status = useStore((s) => s.systemStatus)

  const isActive = status === 'INVESTIGATING' || status === 'CONVERGING'

  return (
    <div className="flex items-center gap-1">
      <span className="text-[9px] font-terminal text-[#334155] tracking-wider">CYCLE</span>
      <MonoValue color={isActive ? '#3B82F6' : '#475569'} size="sm">
        {currentCycle}
      </MonoValue>
      <span className="text-[9px] font-terminal text-[#273548]">/</span>
      <MonoValue color="#334155" size="sm">
        {maxCycles}
      </MonoValue>
    </div>
  )
}
