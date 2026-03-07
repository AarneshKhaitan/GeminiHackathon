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
        style={{ borderBottom: '1px solid #2E2820', backgroundColor: '#161310' }}
      >
        <div style={{ width: '2px', height: '12px', backgroundColor: '#C8912A' }} />
        <span
          className="text-[9px] tracking-[0.2em]"
          style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, color: '#8C7A5E' }}
        >CYCLE TIMELINE</span>
      </div>

      {/* Summary stats */}
      <div className="shrink-0 grid grid-cols-2" style={{ borderBottom: '1px solid #2E2820' }}>
        <div className="px-3 py-2" style={{ borderRight: '1px solid #1C1C1C' }}>
          <div className="text-[8px] font-mono tracking-wider" style={{ color: '#4A3D2A' }}>ELIMINATED</div>
          <div className="text-base font-mono font-medium" style={{ color: '#D14B35' }}>{totalEliminated}</div>
        </div>
        <div className="px-3 py-2">
          <div className="text-[8px] font-mono tracking-wider" style={{ color: '#4A3D2A' }}>SURVIVING</div>
          <div className="text-base font-mono font-medium" style={{ color: '#2E9E72' }}>{totalSurviving}</div>
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
          <div className="text-[8px] font-mono tracking-wider" style={{ color: '#7C6DB8' }}>CONTEXT COMPRESSION</div>
          <div className="text-[8px] font-mono mt-0.5" style={{ color: '#4A3D2A' }}>
            Prior cycles compressed to reasoning traces
          </div>
        </div>
      )}
    </div>
  )
}
