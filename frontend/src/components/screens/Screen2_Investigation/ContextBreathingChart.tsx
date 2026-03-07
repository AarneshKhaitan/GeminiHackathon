import { useStore } from '../../../store'
import { ContextWindowBar } from '../../layout/StatusBar/ContextWindowBar'
import { MonoValue } from '../../shared/MonoValue'

function fmt(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(2)}M`
  if (n >= 1000) return `${(n / 1000).toFixed(0)}K`
  return `${n}`
}

export function ContextBreathingChart() {
  const cycles = useStore((s) => s.cycles)
  const liveCtx = useStore((s) => s.contextWindow)
  const currentCycle = useStore((s) => s.currentCycle)
  const isCompressing = useStore((s) => s.isCompressing)
  const status = useStore((s) => s.systemStatus)

  const isLiveActive = status === 'INVESTIGATING' || status === 'CONVERGING'

  return (
    <div className="border-t border-[#1E293B] p-3">
      {/* Header row */}
      <div className="flex items-center justify-between mb-2">
        <div className="text-[9px] font-terminal text-[#273548] tracking-widest">
          CONTEXT WINDOW — BREATHING PATTERN
        </div>
        <div className="flex items-center gap-3 text-[8px] font-terminal">
          <span className="flex items-center gap-1">
            <span className="w-2 h-1.5 rounded-sm inline-block bg-[#2563EB]" />
            <span className="text-[#475569]">REASONING</span>
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-1.5 rounded-sm inline-block bg-[#10B981]" />
            <span className="text-[#475569]">EVIDENCE</span>
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-1.5 rounded-sm inline-block bg-[#7C3AED]" />
            <span className="text-[#475569]">COMPRESSED</span>
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
                <span className="text-[8px] font-terminal text-[#334155] w-4 shrink-0">
                  C{cycle.cycleNumber}
                </span>
                <div className="flex-1">
                  <ContextWindowBar height={6} snapshot={cycle.contextSnapshot} />
                </div>
                <MonoValue color="#273548" size="xs" className="w-7 text-right">
                  {usedPct}%
                </MonoValue>
              </div>
            )
          })}

        {/* Live / active cycle row */}
        {isLiveActive && currentCycle > 0 && (
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1 w-4 shrink-0">
              <span className="text-[8px] font-terminal text-[#3B82F6]">
                C{currentCycle}
              </span>
            </div>
            <div className="flex-1 relative">
              <ContextWindowBar height={8} />
              {/* Live indicator */}
              <div
                className="absolute right-0 top-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-[#3B82F6]"
                style={{ animation: 'pulse-dot 0.8s ease-in-out infinite' }}
              />
            </div>
            <div className="w-7 flex items-center justify-end">
              {isCompressing ? (
                <span className="text-[8px] font-terminal text-[#7C3AED] animate-[blink_0.5s_step-end_infinite]">
                  CMPR
                </span>
              ) : (
                <span className="text-[8px] font-terminal text-[#3B82F6] animate-[blink_1s_step-end_infinite]">
                  LIVE
                </span>
              )}
            </div>
          </div>
        )}

        {/* Empty state */}
        {cycles.length === 0 && !isLiveActive && (
          <div className="flex items-center justify-center h-8">
            <span className="text-[9px] font-terminal text-[#1E293B] tracking-wider">
              CONTEXT WINDOW IDLE — 1M TOKENS AVAILABLE
            </span>
          </div>
        )}
      </div>

      {/* Token summary */}
      {isLiveActive && (
        <div className="mt-2 pt-2 border-t border-[#1E293B] flex gap-4 text-[8px] font-terminal text-[#273548]">
          <span>REASONING: <span className="text-[#2563EB]">{fmt(liveCtx.reasoningTokens)}</span></span>
          <span>EVIDENCE: <span className="text-[#10B981]">{fmt(liveCtx.evidenceTokens)}</span></span>
          <span>COMPRESSED: <span className="text-[#7C3AED]">{fmt(liveCtx.compressedTokens)}</span></span>
          <span className="ml-auto">CAPACITY: <span className="text-[#334155]">{fmt(liveCtx.totalCapacity)}</span></span>
        </div>
      )}
    </div>
  )
}
