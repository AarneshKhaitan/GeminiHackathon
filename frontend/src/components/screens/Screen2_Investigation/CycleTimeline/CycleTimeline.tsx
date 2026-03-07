import { useStore } from '../../../../store'
import { CycleNode } from './CycleNode'
import { SectionLabel } from '../../../shared/SectionLabel'

export function CycleTimeline() {
  const cycles = useStore((s) => s.cycles)
  const currentCycle = useStore((s) => s.currentCycle)
  const maxCycles = useStore((s) => s.maxCycles)
  const status = useStore((s) => s.systemStatus)
  const hypotheses = useStore((s) => s.hypotheses)

  const totalEliminated = hypotheses.filter((h) => h.status === 'eliminated').length
  const totalSurviving = hypotheses.filter((h) => h.status === 'surviving').length

  // Add pending cycles for the ones not yet started
  const allCycles = [...cycles]
  for (let i = cycles.length + 1; i <= maxCycles; i++) {
    allCycles.push({
      cycleNumber: i,
      status: 'pending',
      hypothesesStart: 0,
      hypothesesEnd: 0,
      eliminations: [],
      contradictionsFound: 0,
      durationMs: 0,
      contextSnapshot: {
        cycleNumber: i,
        reasoningTokens: 0,
        evidenceTokens: 0,
        compressedTokens: 0,
        totalCapacity: 1_000_000,
      },
    })
  }

  return (
    <div className="flex flex-col h-full p-3 gap-3">
      <SectionLabel accent="#334155">CYCLE TIMELINE</SectionLabel>

      {/* Summary stats */}
      <div className="grid grid-cols-2 gap-2">
        <div className="px-2 py-1.5 rounded border border-[#1E293B] bg-[#0D1526]">
          <div className="text-[9px] font-terminal text-[#334155] tracking-wider">ELIMINATED</div>
          <div className="text-base font-terminal font-bold text-[#DC2626]">{totalEliminated}</div>
        </div>
        <div className="px-2 py-1.5 rounded border border-[#1E293B] bg-[#0D1526]">
          <div className="text-[9px] font-terminal text-[#334155] tracking-wider">SURVIVING</div>
          <div className="text-base font-terminal font-bold text-[#059669]">{totalSurviving}</div>
        </div>
      </div>

      {/* Timeline */}
      <div className="flex-1 overflow-y-auto">
        <div className="relative">
          {/* Vertical line */}
          <div
            className="absolute left-3 top-1 bottom-0 w-px"
            style={{ backgroundColor: '#1E293B' }}
          />
          <div className="space-y-0">
            {allCycles.map((cycle) => (
              <CycleNode
                key={cycle.cycleNumber}
                cycle={cycle}
                isActive={
                  cycle.cycleNumber === currentCycle &&
                  (status === 'INVESTIGATING' || status === 'CONVERGING')
                }
              />
            ))}
          </div>
        </div>
      </div>

      {/* Compression indicator */}
      {status === 'INVESTIGATING' && (
        <div className="px-2 py-1.5 rounded border border-[#7C3AED]/20 bg-[#1E293B]">
          <div className="text-[9px] font-terminal text-[#7C3AED] tracking-wider">CONTEXT COMPRESSION</div>
          <div className="text-[9px] font-terminal text-[#475569] mt-0.5">
            Prior cycles compressed to reasoning traces
          </div>
        </div>
      )}
    </div>
  )
}
