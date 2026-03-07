import { useStore } from '../../../store'
import { ContextWindowBar } from '../../layout/StatusBar/ContextWindowBar'
import { MonoValue } from '../../shared/MonoValue'
import { fmt } from '../../../utils/format'

export function ContextBreathingChart() {
  const cycles = useStore((s) => s.cycles)
  const liveCtx = useStore((s) => s.contextWindow)
  const currentCycle = useStore((s) => s.currentCycle)
  const isCompressing = useStore((s) => s.isCompressing)
  const status = useStore((s) => s.systemStatus)

  const isLiveActive = status === 'INVESTIGATING' || status === 'CONVERGING'

  return (
    <div className="p-3" style={{ backgroundColor: '#000000' }}>
      {/* Header row */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-[9px] font-mono text-[#333333] tracking-widest">
          CONTEXT WINDOW — BREATHING PATTERN
        </span>
        <div className="flex items-center gap-3 text-[8px] font-mono">
          <span className="flex items-center gap-1.5">
            <span className="inline-block w-2 h-1" style={{ backgroundColor: '#3B82F6' }} />
            <span className="text-[#333333]">REASONING</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="inline-block w-2 h-1" style={{ backgroundColor: '#00C27A' }} />
            <span className="text-[#333333]">EVIDENCE</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="inline-block w-2 h-1" style={{ backgroundColor: '#8B5CF6' }} />
            <span className="text-[#333333]">COMPRESSED</span>
          </span>
        </div>
      </div>

      {/* Per-cycle rows */}
      <div className="space-y-1.5">
        {cycles
          .filter((c) => c.status === 'completed')
          .map((cycle) => {
            const total = cycle.contextSnapshot.totalCapacity
            const used =
              cycle.contextSnapshot.reasoningTokens +
              cycle.contextSnapshot.evidenceTokens +
              cycle.contextSnapshot.compressedTokens
            const usedPct = Math.round((used / total) * 100)

            return (
              <div key={cycle.cycleNumber} className="flex items-center gap-2">
                <span className="text-[8px] font-mono text-[#333333] w-4 shrink-0">
                  C{cycle.cycleNumber}
                </span>
                <div className="flex-1">
                  <ContextWindowBar height={6} snapshot={cycle.contextSnapshot} />
                </div>
                <MonoValue color="#333333" size="xs" className="w-7 text-right">
                  {usedPct}%
                </MonoValue>
              </div>
            )
          })}

        {/* Live / active cycle row */}
        {isLiveActive && currentCycle > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-[8px] font-mono text-[#3B82F6] w-4 shrink-0">
              C{currentCycle}
            </span>
            <div className="flex-1 relative">
              <ContextWindowBar height={8} />
              {/* Live pulse dot */}
              <div
                className="absolute right-0 top-1/2 -translate-y-1/2"
                style={{
                  width: '4px',
                  height: '4px',
                  backgroundColor: '#3B82F6',
                  animation: 'pulse-dot 0.8s ease-in-out infinite',
                }}
              />
            </div>
            <div className="w-7 flex items-center justify-end">
              {isCompressing ? (
                <span className="text-[8px] font-mono text-[#8B5CF6]" style={{ animation: 'blink 0.5s step-end infinite' }}>
                  CMPR
                </span>
              ) : (
                <span className="text-[8px] font-mono text-[#3B82F6]" style={{ animation: 'blink 1s step-end infinite' }}>
                  LIVE
                </span>
              )}
            </div>
          </div>
        )}

        {/* Empty state */}
        {cycles.length === 0 && !isLiveActive && (
          <div className="flex items-center justify-center h-6">
            <span className="text-[9px] font-mono text-[#333333] tracking-wider">
              CONTEXT WINDOW IDLE — 1M TOKENS AVAILABLE
            </span>
          </div>
        )}
      </div>

      {/* Token summary */}
      {isLiveActive && (
        <div
          className="mt-2 pt-2 flex gap-4 text-[8px] font-mono"
          style={{ borderTop: '1px solid #1C1C1C' }}
        >
          <span className="text-[#333333]">REASONING: <span className="text-[#3B82F6]">{fmt(liveCtx.reasoningTokens)}</span></span>
          <span className="text-[#333333]">EVIDENCE: <span className="text-[#00C27A]">{fmt(liveCtx.evidenceTokens)}</span></span>
          <span className="text-[#333333]">COMPRESSED: <span className="text-[#8B5CF6]">{fmt(liveCtx.compressedTokens)}</span></span>
          <span className="ml-auto text-[#333333]">CAPACITY: <span className="text-[#333333]">{fmt(liveCtx.totalCapacity)}</span></span>
        </div>
      )}
    </div>
  )
}
