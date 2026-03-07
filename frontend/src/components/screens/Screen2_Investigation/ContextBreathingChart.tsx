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
    <div className="p-3" style={{ backgroundColor: '#161310' }}>
      {/* Header row */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-[9px] font-mono tracking-widest" style={{ color: '#4A3D2A' }}>
          CONTEXT WINDOW — BREATHING PATTERN
        </span>
        <div className="flex items-center gap-3 text-[8px] font-mono">
          <span className="flex items-center gap-1.5">
            <span className="inline-block w-2 h-1" style={{ backgroundColor: '#C8912A' }} />
            <span style={{ color: '#4A3D2A' }}>REASONING</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="inline-block w-2 h-1" style={{ backgroundColor: '#2E9E72' }} />
            <span style={{ color: '#4A3D2A' }}>EVIDENCE</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="inline-block w-2 h-1" style={{ backgroundColor: '#7C6DB8' }} />
            <span style={{ color: '#4A3D2A' }}>COMPRESSED</span>
          </span>
        </div>
      </div>

      {/* Workspace label */}
      <div className="mb-2 text-[8px] font-mono" style={{ color: '#4A3D2A' }}>
        Context window as workspace — each cycle loads fresh evidence into a clean window
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
                <span className="text-[8px] font-mono w-4 shrink-0" style={{ color: '#4A3D2A' }}>
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
            <span className="text-[8px] font-mono w-4 shrink-0" style={{ color: '#C8912A' }}>
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
                  backgroundColor: '#C8912A',
                  animation: 'pulse-dot 0.8s ease-in-out infinite',
                }}
              />
            </div>
            <div className="w-7 flex items-center justify-end">
              {isCompressing ? (
                <span className="text-[8px] font-mono" style={{ color: '#7C6DB8', animation: 'blink 0.5s step-end infinite' }}>
                  CMPR
                </span>
              ) : (
                <span className="text-[8px] font-mono" style={{ color: '#C8912A', animation: 'blink 1s step-end infinite' }}>
                  LIVE
                </span>
              )}
            </div>
          </div>
        )}

        {/* Empty state */}
        {cycles.length === 0 && !isLiveActive && (
          <div className="flex items-center justify-center h-6">
            <span className="text-[9px] font-mono tracking-wider" style={{ color: '#4A3D2A' }}>
              CONTEXT WINDOW IDLE — 1M TOKENS AVAILABLE
            </span>
          </div>
        )}
      </div>

      {/* Token summary */}
      {isLiveActive && (
        <div
          className="mt-2 pt-2 flex gap-4 text-[8px] font-mono"
          style={{ borderTop: '1px solid #2E2820' }}
        >
          <span style={{ color: '#4A3D2A' }}>REASONING: <span style={{ color: '#C8912A' }}>{fmt(liveCtx.reasoningTokens)}</span></span>
          <span style={{ color: '#4A3D2A' }}>EVIDENCE: <span style={{ color: '#2E9E72' }}>{fmt(liveCtx.evidenceTokens)}</span></span>
          <span style={{ color: '#4A3D2A' }}>COMPRESSED: <span style={{ color: '#7C6DB8' }}>{fmt(liveCtx.compressedTokens)}</span></span>
          <span className="ml-auto" style={{ color: '#4A3D2A' }}>CAPACITY: <span style={{ color: '#8C7A5E' }}>{fmt(liveCtx.totalCapacity)}</span></span>
        </div>
      )}
    </div>
  )
}
