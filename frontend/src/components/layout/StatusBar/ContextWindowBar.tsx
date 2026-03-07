import { useStore } from '../../../store'

interface ContextWindowBarProps {
  height?: number
  showLabels?: boolean
  showPercent?: boolean
  snapshot?: {
    reasoningTokens: number
    evidenceTokens: number
    compressedTokens: number
    totalCapacity: number
  }
}

function fmt(n: number): string {
  if (n >= 1000) return `${(n / 1000).toFixed(0)}K`
  return `${n}`
}

export function ContextWindowBar({
  height = 8,
  showLabels = false,
  showPercent = false,
  snapshot,
}: ContextWindowBarProps) {
  const liveCtx = useStore((s) => s.contextWindow)
  const isCompressing = useStore((s) => s.isCompressing)

  const ctx = snapshot ?? liveCtx
  const { reasoningTokens, evidenceTokens, compressedTokens, totalCapacity } = ctx

  const totalUsed = reasoningTokens + evidenceTokens + compressedTokens
  const available = Math.max(0, totalCapacity - totalUsed)

  const rPct = (reasoningTokens / totalCapacity) * 100
  const ePct = (evidenceTokens / totalCapacity) * 100
  const cPct = (compressedTokens / totalCapacity) * 100

  const usedPct = Math.round((totalUsed / totalCapacity) * 100)

  return (
    <div className="flex flex-col gap-1 w-full">
      {showLabels && (
        <div className="flex items-center gap-3 text-[9px] font-terminal text-[#475569]">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-sm inline-block" style={{ backgroundColor: '#2563EB' }} />
            REASONING {fmt(reasoningTokens)}
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-sm inline-block" style={{ backgroundColor: '#10B981' }} />
            EVIDENCE {fmt(evidenceTokens)}
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-sm inline-block" style={{ backgroundColor: '#7C3AED' }} />
            COMPRESSED {fmt(compressedTokens)}
          </span>
          {showPercent && (
            <span className="ml-auto text-[#334155]">{usedPct}% used</span>
          )}
        </div>
      )}

      {/* The bar itself */}
      <div
        className="relative w-full overflow-hidden rounded-full"
        style={{
          height: `${height}px`,
          backgroundColor: '#1E293B',
        }}
      >
        {/* Compressed (left-most, persistent across cycles) */}
        <div
          className="absolute top-0 left-0 h-full context-segment transition-all duration-700 ease-out"
          style={{
            width: `${cPct}%`,
            backgroundColor: isCompressing ? '#9F7AEA' : '#7C3AED',
          }}
        />
        {/* Evidence (stacked after compressed) */}
        <div
          className="absolute top-0 h-full context-segment transition-all duration-500 ease-out"
          style={{
            left: `${cPct}%`,
            width: `${ePct}%`,
            backgroundColor: '#10B981',
          }}
        />
        {/* Reasoning (grows during active cycle) */}
        <div
          className="absolute top-0 h-full context-segment"
          style={{
            left: `${cPct + ePct}%`,
            width: `${rPct}%`,
            backgroundColor: '#2563EB',
            transition: 'width 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
          }}
        />
        {/* Available (implicit — background shows through) */}
        {/* Subtle grid lines every 10% */}
        {[10, 20, 30, 40, 50, 60, 70, 80, 90].map((tick) => (
          <div
            key={tick}
            className="absolute top-0 h-full w-px opacity-20"
            style={{ left: `${tick}%`, backgroundColor: '#475569' }}
          />
        ))}
      </div>

      {/* Available space label */}
      {showLabels && (
        <div className="flex justify-between text-[9px] font-terminal text-[#273548]">
          <span>0</span>
          <span className="text-[#334155]">{fmt(available)} available</span>
          <span>1M</span>
        </div>
      )}
    </div>
  )
}
