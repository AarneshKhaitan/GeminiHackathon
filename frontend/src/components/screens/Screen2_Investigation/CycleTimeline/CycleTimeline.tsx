import { useStore } from '../../../../store'
import { CycleNode } from './CycleNode'

export function CycleTimeline() {
  const cycles = useStore((s) => s.cycles)
  const currentCycle = useStore((s) => s.currentCycle)
  const maxCycles = useStore((s) => s.maxCycles)
  const status = useStore((s) => s.systemStatus)
  const hypotheses = useStore((s) => s.hypotheses)

  const totalEliminated = hypotheses.filter((h) => h.status === 'eliminated').length
  const totalSurviving = hypotheses.filter((h) => h.status === 'surviving').length

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
    <div className="flex flex-col h-full">
      {/* Header */}
      <div
        className="shrink-0 px-3 py-2 flex items-center gap-2"
        style={{ borderBottom: '1px solid #1C1C1C' }}
      >
        <div style={{ width: '2px', height: '12px', backgroundColor: '#333333' }} />
        <span className="text-[9px] font-mono tracking-[0.2em] text-[#555555]">CYCLE TIMELINE</span>
      </div>

      {/* Summary stats */}
      <div className="shrink-0 grid grid-cols-2" style={{ borderBottom: '1px solid #1C1C1C' }}>
        <div className="px-3 py-2" style={{ borderRight: '1px solid #1C1C1C' }}>
          <div className="text-[8px] font-mono text-[#333333] tracking-wider">ELIMINATED</div>
          <div className="text-base font-mono font-medium text-[#FF3333]">{totalEliminated}</div>
        </div>
        <div className="px-3 py-2">
          <div className="text-[8px] font-mono text-[#333333] tracking-wider">SURVIVING</div>
          <div className="text-base font-mono font-medium text-[#00C27A]">{totalSurviving}</div>
        </div>
      </div>

      {/* Timeline */}
      <div className="flex-1 overflow-y-auto">
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

      {/* Compression indicator */}
      {status === 'INVESTIGATING' && (
        <div
          className="shrink-0 px-3 py-2"
          style={{ borderTop: '1px solid #1C1C1C' }}
        >
          <div className="text-[8px] font-mono text-[#8B5CF6] tracking-wider">CONTEXT COMPRESSION</div>
          <div className="text-[8px] font-mono text-[#333333] mt-0.5">
            Prior cycles compressed to reasoning traces
          </div>
        </div>
      )}
    </div>
  )
}
