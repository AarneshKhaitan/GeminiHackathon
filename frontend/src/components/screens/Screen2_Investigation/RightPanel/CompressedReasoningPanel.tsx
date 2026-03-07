import { useStore } from '../../../../store'

export function CompressedReasoningPanel() {
  const compressed = useStore((s) => s.compressedReasoning)
  const keyInsights = useStore((s) => s.keyInsights)
  const isCompressing = useStore((s) => s.isCompressing)

  return (
    <div className="flex flex-col h-full" style={{ backgroundColor: '#000000' }}>
      {/* Header */}
      <div
        className="shrink-0 px-3 py-2 flex items-center gap-2"
        style={{ borderBottom: '1px solid #1C1C1C' }}
      >
        <div style={{ width: '2px', height: '12px', backgroundColor: '#8B5CF6' }} />
        <span className="text-[9px] font-mono tracking-[0.2em] text-[#555555]">COMPRESSED REASONING</span>
      </div>

      {/* Key insights */}
      {keyInsights.length > 0 && (
        <div style={{ borderBottom: '1px solid #1C1C1C' }}>
          <div className="px-3 py-1.5">
            <span className="text-[8px] font-mono text-[#333333] tracking-widest">KEY INSIGHTS</span>
          </div>
          {keyInsights.map((ki, i) => (
            <div
              key={i}
              className="flex items-start gap-2 px-3 py-2"
              style={{ borderBottom: '1px solid #1C1C1C' }}
            >
              <span className="text-[7px] font-mono text-[#8B5CF6] shrink-0 mt-0.5">C{ki.cycle}</span>
              <p className="text-[9px] font-mono text-[#555555] leading-relaxed">{ki.insight}</p>
            </div>
          ))}
        </div>
      )}

      {/* Compression in progress */}
      {isCompressing && (
        <div
          className="px-3 py-2 flex items-center gap-2"
          style={{ borderBottom: '1px solid #8B5CF630', backgroundColor: '#050010' }}
        >
          <span className="text-[9px] font-mono text-[#8B5CF6]" style={{ animation: 'blink 0.8s step-end infinite' }}>
            ▓▒░
          </span>
          <span className="text-[9px] font-mono text-[#8B5CF6]">COMPRESSING REASONING...</span>
        </div>
      )}

      {/* Compressed state text */}
      <div className="flex-1 overflow-hidden flex flex-col">
        <div className="px-3 py-1.5" style={{ borderBottom: '1px solid #1C1C1C' }}>
          <span className="text-[8px] font-mono text-[#333333] tracking-widest">CUMULATIVE COMPRESSED STATE</span>
        </div>

        <div
          className="flex-1 overflow-y-auto px-3 py-2 font-mono text-[9px] leading-relaxed"
          style={{
            backgroundColor: '#000000',
            color: '#555555',
            scrollbarWidth: 'thin',
            scrollbarColor: '#1C1C1C transparent',
          }}
        >
          {compressed ? (
            <pre className="whitespace-pre-wrap break-words">{compressed}</pre>
          ) : (
            <div className="flex flex-col items-center justify-center h-full gap-2 opacity-30">
              <span className="text-xl font-mono text-[#333333]">▒▒▒</span>
              <span className="text-[8px] font-mono text-[#333333] tracking-wider">NO COMPRESSED STATE</span>
              <span className="text-[7px] font-mono text-[#333333] text-center">
                Reasoning is compressed<br />between cycles
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
