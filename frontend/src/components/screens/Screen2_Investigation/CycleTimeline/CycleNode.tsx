import { MonoValue } from '../../../shared/MonoValue'
import type { Cycle } from '../../../../types/investigation'

interface CycleNodeProps {
  cycle: Cycle
  isActive: boolean
}

export function CycleNode({ cycle, isActive }: CycleNodeProps) {
  const isCompleted = cycle.status === 'completed'
  const isPending = cycle.status === 'pending'

  const nodeColor = isActive ? '#C8912A' : isCompleted ? '#2E9E72' : '#2E2820'
  const nodeTextColor = isActive ? '#C8912A' : isCompleted ? '#2E9E72' : '#4A3D2A'

  return (
    <div
      className="flex items-start gap-3 px-3 py-2"
      style={{ borderBottom: '1px solid #2E2820' }}
    >
      {/* Node indicator — square, no glow */}
      <div className="shrink-0 mt-0.5">
        <div
          className="w-5 h-5 flex items-center justify-center text-[8px] font-mono font-medium"
          style={{
            border: `1px solid ${nodeColor}`,
            backgroundColor: isActive ? '#2D1E07' : isCompleted ? '#0A2D1E' : '#161310',
            color: nodeTextColor,
          }}
        >
          {cycle.cycleNumber}
        </div>
      </div>

      {/* Content */}
      <div className="flex flex-col gap-0.5 flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-[9px] font-mono font-medium tracking-wider" style={{ color: nodeTextColor }}>
            CYCLE {cycle.cycleNumber}
          </span>
          {isActive && (
            <span className="text-[8px] font-mono" style={{ color: '#C8912A', animation: 'blink 1s step-end infinite' }}>
              ●
            </span>
          )}
          {isPending && (
            <span className="text-[8px] font-mono" style={{ color: '#4A3D2A' }}>PENDING</span>
          )}
        </div>

        {isCompleted && (
          <>
            <div className="flex items-center gap-1.5">
              <MonoValue color="#E8E8E8" size="xs">{cycle.hypothesesStart}</MonoValue>
              <span className="text-[8px] font-mono" style={{ color: '#4A3D2A' }}>→</span>
              <MonoValue color="#2E9E72" size="xs">{cycle.hypothesesEnd}</MonoValue>
              <span className="text-[8px] font-mono" style={{ color: '#4A3D2A' }}>hyp</span>
            </div>

            {cycle.eliminations.length > 0 && (
              <span className="text-[8px] font-mono" style={{ color: '#8C7A5E' }}>
                −{cycle.eliminations.length} eliminated
              </span>
            )}

            <MonoValue color="#333333" size="xs">
              {(cycle.durationMs / 1000).toFixed(1)}s
            </MonoValue>

            {/* Mini context snapshot bar */}
            {cycle.contextSnapshot && (
              <div className="mt-0.5 w-full h-px flex overflow-hidden" style={{ backgroundColor: '#2E2820' }}>
                <div
                  style={{
                    width: `${(cycle.contextSnapshot.compressedTokens / cycle.contextSnapshot.totalCapacity) * 100}%`,
                    backgroundColor: '#7C6DB8',
                    height: '100%',
                  }}
                />
                <div
                  style={{
                    width: `${(cycle.contextSnapshot.evidenceTokens / cycle.contextSnapshot.totalCapacity) * 100}%`,
                    backgroundColor: '#2E9E72',
                    height: '100%',
                  }}
                />
                <div
                  style={{
                    width: `${(cycle.contextSnapshot.reasoningTokens / cycle.contextSnapshot.totalCapacity) * 100}%`,
                    backgroundColor: '#C8912A',
                    height: '100%',
                  }}
                />
              </div>
            )}
          </>
        )}

        {isActive && (
          <div className="text-[8px] font-mono" style={{ color: '#C8912A', animation: 'blink 1s step-end infinite' }}>
            REASONING...
          </div>
        )}
      </div>
    </div>
  )
}
