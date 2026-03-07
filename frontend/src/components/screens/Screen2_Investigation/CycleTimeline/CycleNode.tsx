import { MonoValue } from '../../../shared/MonoValue'
import type { Cycle } from '../../../../types/investigation'

interface CycleNodeProps {
  cycle: Cycle
  isActive: boolean
}

export function CycleNode({ cycle, isActive }: CycleNodeProps) {
  const isCompleted = cycle.status === 'completed'
  const isPending = cycle.status === 'pending'

  return (
    <div className="flex items-start gap-3">
      {/* Node indicator */}
      <div className="flex flex-col items-center shrink-0 mt-1">
        <div
          className="w-6 h-6 rounded border flex items-center justify-center text-[9px] font-terminal font-bold"
          style={{
            borderColor: isActive
              ? '#3B82F6'
              : isCompleted
              ? '#059669'
              : '#273548',
            backgroundColor: isActive
              ? '#1E3A5F'
              : isCompleted
              ? '#064E3B'
              : '#1E293B',
            color: isActive ? '#60A5FA' : isCompleted ? '#6EE7B7' : '#334155',
            boxShadow: isActive ? '0 0 8px #2563EB40' : 'none',
            animation: isActive ? 'glow-contradiction 2s ease-in-out infinite' : 'none',
          }}
        >
          {cycle.cycleNumber}
        </div>
      </div>

      {/* Content */}
      <div className="flex flex-col gap-0.5 pb-4 flex-1">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-terminal font-medium text-[#94A3B8] tracking-wider">
            CYCLE {cycle.cycleNumber}
          </span>
          {isActive && (
            <span className="text-[9px] font-terminal text-[#3B82F6] animate-[pulse-dot_1.5s_ease-in-out_infinite]">
              ●
            </span>
          )}
          {isPending && (
            <span className="text-[9px] font-terminal text-[#273548]">PENDING</span>
          )}
        </div>

        {isCompleted && (
          <>
            {/* Hypothesis reduction */}
            <div className="flex items-center gap-1.5">
              <MonoValue color="#E2E8F0" size="xs">
                {cycle.hypothesesStart}
              </MonoValue>
              <span className="text-[9px] text-[#334155]">→</span>
              <MonoValue color="#059669" size="xs">
                {cycle.hypothesesEnd}
              </MonoValue>
              <span className="text-[9px] font-terminal text-[#334155]">hypotheses</span>
            </div>

            {/* Eliminated */}
            {cycle.eliminations.length > 0 && (
              <div className="flex items-center gap-1">
                <span className="text-[9px] font-terminal text-[#475569]">
                  −{cycle.eliminations.length} eliminated
                </span>
              </div>
            )}

            {/* Duration */}
            <div>
              <MonoValue color="#273548" size="xs">
                {(cycle.durationMs / 1000).toFixed(1)}s
              </MonoValue>
            </div>

            {/* Context snapshot bar */}
            {cycle.contextSnapshot && (
              <div className="mt-1 w-full">
                <div className="relative h-1 w-full rounded-full overflow-hidden bg-[#1E293B]">
                  <div
                    className="absolute top-0 left-0 h-full"
                    style={{
                      width: `${(cycle.contextSnapshot.compressedTokens / cycle.contextSnapshot.totalCapacity) * 100}%`,
                      backgroundColor: '#7C3AED',
                    }}
                  />
                  <div
                    className="absolute top-0 h-full"
                    style={{
                      left: `${(cycle.contextSnapshot.compressedTokens / cycle.contextSnapshot.totalCapacity) * 100}%`,
                      width: `${(cycle.contextSnapshot.evidenceTokens / cycle.contextSnapshot.totalCapacity) * 100}%`,
                      backgroundColor: '#10B981',
                    }}
                  />
                  <div
                    className="absolute top-0 h-full"
                    style={{
                      left: `${((cycle.contextSnapshot.compressedTokens + cycle.contextSnapshot.evidenceTokens) / cycle.contextSnapshot.totalCapacity) * 100}%`,
                      width: `${(cycle.contextSnapshot.reasoningTokens / cycle.contextSnapshot.totalCapacity) * 100}%`,
                      backgroundColor: '#2563EB',
                    }}
                  />
                </div>
              </div>
            )}
          </>
        )}

        {isActive && (
          <div className="text-[9px] font-terminal text-[#3B82F6] animate-[blink_1s_step-end_infinite]">
            REASONING...
          </div>
        )}
      </div>
    </div>
  )
}
