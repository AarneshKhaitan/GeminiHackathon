import { useStore } from '../../../store'
import { MonoValue } from '../../shared/MonoValue'

// Tier-aware max cycles per the architecture spec:
// Tier 3: Initial investigation — 1-2 quick cycles
// Tier 4: Full investigation — 4-5 deep cycles
function getMaxCycles(tier: number | null): number {
  if (tier === 3) return 2
  if (tier === 4) return 5
  return 5
}

export function CycleCounter() {
  const currentCycle = useStore((s) => s.currentCycle)
  const currentTier = useStore((s) => s.currentTier)
  const status = useStore((s) => s.systemStatus)

  const maxCycles = getMaxCycles(currentTier)
  const isActive = status === 'INVESTIGATING' || status === 'CONVERGING'

  // Tier-relative cycle: for T4, cycles continue from where T3 left off
  // so we show the cycle within-tier context for T4
  const tierLabel = currentTier === 3 ? 'INITIAL' : currentTier === 4 ? 'FULL' : null

  return (
    <div className="flex flex-col leading-none gap-0.5">
      <div className="flex items-center gap-1">
        <span className="text-[9px] font-terminal text-[#334155] tracking-wider">CYC</span>
        <MonoValue color={isActive ? '#3B82F6' : '#475569'} size="sm">
          {currentCycle}
        </MonoValue>
        <span className="text-[9px] font-terminal text-[#273548]">/</span>
        <MonoValue color="#334155" size="sm">
          {maxCycles}
        </MonoValue>
      </div>
      {tierLabel && (
        <span className="text-[7px] font-terminal text-[#273548] tracking-wider">
          {tierLabel} PASS
        </span>
      )}
    </div>
  )
}
