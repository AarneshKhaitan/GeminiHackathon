import { useStore } from '../../../../store'

export function CompressedReasoningPanel() {
  const compressed = useStore((s) => s.compressedReasoning)
  const keyInsights = useStore((s) => s.keyInsights)
  const isCompressing = useStore((s) => s.isCompressing)

  return (
    <div className="flex flex-col h-full" style={{ backgroundColor: '#161310' }}>
      {/* Header */}
      <div
        className="shrink-0 px-3 py-2 flex items-center gap-2"
        style={{ borderBottom: '1px solid #2E2820', backgroundColor: '#161310' }}
      >
        <div style={{ width: '2px', height: '12px', backgroundColor: '#7C6DB8' }} />
        <span
          className="text-[9px] tracking-[0.2em]"
          style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, color: '#8C7A5E' }}
        >COMPRESSED REASONING</span>
      </div>

      {/* Key insights */}
      {keyInsights.length > 0 && (
        <div style={{ borderBottom: '1px solid #2E2820' }}>
          <div className="px-3 py-1.5">
            <span className="text-[8px] font-mono tracking-widest" style={{ color: '#4A3D2A' }}>KEY INSIGHTS</span>
          </div>
          {keyInsights.map((ki, i) => (
            <div
              key={i}
              className="flex items-start gap-2 px-3 py-2"
              style={{ borderBottom: '1px solid #2E2820' }}
            >
              <span className="text-[7px] font-mono shrink-0 mt-0.5" style={{ color: '#7C6DB8' }}>C{ki.cycle}</span>
              <p className="text-[9px] font-mono leading-relaxed" style={{ color: '#8C7A5E' }}>{ki.insight}</p>
            </div>
          ))}
        </div>
      )}

      {/* Compression in progress */}
      {isCompressing && (
        <div
          className="px-3 py-2 flex items-center gap-2"
          style={{ borderBottom: '1px solid #7C6DB830', backgroundColor: '#16103A' }}
        >
          <span className="text-[9px] font-mono" style={{ color: '#7C6DB8', animation: 'blink 0.8s step-end infinite' }}>
            ▓▒░
          </span>
          <span className="text-[9px] font-mono" style={{ color: '#7C6DB8' }}>COMPRESSING REASONING...</span>
        </div>
      )}

      {/* Compressed state text */}
      <div className="flex-1 overflow-hidden flex flex-col">
        <div className="px-3 py-1.5" style={{ borderBottom: '1px solid #2E2820' }}>
          <span className="text-[8px] font-mono tracking-widest" style={{ color: '#4A3D2A' }}>CUMULATIVE COMPRESSED STATE</span>
        </div>

        <div
          className="flex-1 overflow-y-auto px-3 py-2 font-mono text-[9px] leading-relaxed"
          style={{
            backgroundColor: '#161310',
            color: '#8C7A5E',
            scrollbarWidth: 'thin',
            scrollbarColor: '#2E2820 transparent',
          }}
        >
          {compressed ? (
            <pre className="whitespace-pre-wrap break-words">{compressed}</pre>
          ) : (
            <div className="flex flex-col items-center justify-center h-full gap-2 opacity-30">
              <span className="text-xl font-mono" style={{ color: '#4A3D2A' }}>▒▒▒</span>
              <span className="text-[8px] font-mono tracking-wider" style={{ color: '#4A3D2A' }}>NO COMPRESSED STATE</span>
              <span className="text-[7px] font-mono text-center" style={{ color: '#4A3D2A' }}>
                Reasoning is compressed<br />between cycles
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
