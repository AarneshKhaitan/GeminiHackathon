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
  height = 6,
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
        <div className="flex items-center gap-3 text-[9px] font-mono" style={{ color: '#8C7A5E' }}>
          <span className="flex items-center gap-1">
            <span className="w-2 h-px inline-block" style={{ backgroundColor: '#C8912A' }} />
            R {fmt(reasoningTokens)}
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-px inline-block" style={{ backgroundColor: '#2E9E72' }} />
            E {fmt(evidenceTokens)}
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-px inline-block" style={{ backgroundColor: '#7C6DB8' }} />
            C {fmt(compressedTokens)}
          </span>
          {showPercent && (
            <span className="ml-auto" style={{ color: '#4A3D2A' }}>{usedPct}%</span>
          )}
        </div>
      )}

      {/* Bar */}
      <div
        className="relative w-full overflow-hidden"
        style={{ height: `${height}px`, backgroundColor: '#1E1B15' }}
      >
        {/* Compressed */}
        <div
          className="absolute top-0 left-0 h-full context-segment"
          style={{
            width: `${cPct}%`,
            backgroundColor: isCompressing ? '#A090D0' : '#7C6DB8',
            transition: 'width 0.7s ease-out',
          }}
        />
        {/* Evidence */}
        <div
          className="absolute top-0 h-full context-segment"
          style={{
            left: `${cPct}%`,
            width: `${ePct}%`,
            backgroundColor: '#2E9E72',
            transition: 'width 0.5s ease-out, left 0.7s ease-out',
          }}
        />
        {/* Reasoning — grows live */}
        <div
          className="absolute top-0 h-full"
          style={{
            left: `${cPct + ePct}%`,
            width: `${rPct}%`,
            backgroundColor: '#C8912A',
            transition: 'width 0.4s cubic-bezier(0.4, 0, 0.2, 1), left 0.5s ease-out',
          }}
        />
      </div>

      {showLabels && (
        <div className="flex justify-between text-[9px] font-mono" style={{ color: '#4A3D2A' }}>
          <span>0</span>
          <span>{fmt(available)} avail</span>
          <span>1M</span>
        </div>
      )}
    </div>
  )
}
