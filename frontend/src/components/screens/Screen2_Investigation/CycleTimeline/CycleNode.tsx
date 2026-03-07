import { MonoValue } from '../../../shared/MonoValue'
import type { Cycle } from '../../../../types/investigation'

interface CycleNodeProps {
  cycle: Cycle
  isActive: boolean
}

export function CycleNode({ cycle, isActive }: CycleNodeProps) {
  const isCompleted = cycle.status === 'completed'
  const isPending = cycle.status === 'pending'

  const nodeColor = isActive ? '#3B82F6' : isCompleted ? '#00C27A' : '#1C1C1C'
  const nodeTextColor = isActive ? '#3B82F6' : isCompleted ? '#00C27A' : '#333333'

  return (
    <div
      className="flex items-start gap-3 px-3 py-2"
      style={{ borderBottom: '1px solid #1C1C1C' }}
    >
      {/* Node indicator — square, no glow */}
      <div className="shrink-0 mt-0.5">
        <div
          className="w-5 h-5 flex items-center justify-center text-[8px] font-mono font-medium"
          style={{
            border: `1px solid ${nodeColor}`,
            backgroundColor: isActive ? '#000F2D' : isCompleted ? '#001A0E' : '#000000',
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
            <span className="text-[8px] font-mono text-[#3B82F6]" style={{ animation: 'blink 1s step-end infinite' }}>
              ●
            </span>
          )}
          {isPending && (
            <span className="text-[8px] font-mono text-[#1C1C1C]">PENDING</span>
          )}
        </div>

        {isCompleted && (
          <>
            <div className="flex items-center gap-1.5">
              <MonoValue color="#E8E8E8" size="xs">{cycle.hypothesesStart}</MonoValue>
              <span className="text-[8px] font-mono text-[#333333]">→</span>
              <MonoValue color="#00C27A" size="xs">{cycle.hypothesesEnd}</MonoValue>
              <span className="text-[8px] font-mono text-[#333333]">hyp</span>
            </div>

            {cycle.eliminations.length > 0 && (
              <span className="text-[8px] font-mono text-[#555555]">
                −{cycle.eliminations.length} eliminated
              </span>
            )}

            <MonoValue color="#333333" size="xs">
              {(cycle.durationMs / 1000).toFixed(1)}s
            </MonoValue>

            {/* Mini context snapshot bar */}
            {cycle.contextSnapshot && (
              <div className="mt-0.5 w-full h-px flex overflow-hidden" style={{ backgroundColor: '#111111' }}>
                <div
                  style={{
                    width: `${(cycle.contextSnapshot.compressedTokens / cycle.contextSnapshot.totalCapacity) * 100}%`,
                    backgroundColor: '#8B5CF6',
                    height: '100%',
                  }}
                />
                <div
                  style={{
                    width: `${(cycle.contextSnapshot.evidenceTokens / cycle.contextSnapshot.totalCapacity) * 100}%`,
                    backgroundColor: '#00C27A',
                    height: '100%',
                  }}
                />
                <div
                  style={{
                    width: `${(cycle.contextSnapshot.reasoningTokens / cycle.contextSnapshot.totalCapacity) * 100}%`,
                    backgroundColor: '#3B82F6',
                    height: '100%',
                  }}
                />
              </div>
            )}
          </>
        )}

        {isActive && (
          <div className="text-[8px] font-mono text-[#3B82F6]" style={{ animation: 'blink 1s step-end infinite' }}>
            REASONING...
          </div>
        )}
      </div>
    </div>
  )
}
