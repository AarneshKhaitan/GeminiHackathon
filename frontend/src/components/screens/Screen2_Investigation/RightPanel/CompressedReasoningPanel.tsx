import { useStore } from '../../../../store'
import { SectionLabel } from '../../../shared/SectionLabel'

export function CompressedReasoningPanel() {
  const compressed = useStore((s) => s.compressedReasoning)
  const keyInsights = useStore((s) => s.keyInsights)
  const isCompressing = useStore((s) => s.isCompressing)

  return (
    <div className="flex flex-col h-full p-3 gap-3">
      <SectionLabel accent="#7C3AED">COMPRESSED REASONING</SectionLabel>

      {/* Key insights extracted */}
      {keyInsights.length > 0 && (
        <div className="space-y-1.5">
          <span className="text-[8px] font-terminal text-[#334155] tracking-widest">KEY INSIGHTS</span>
          <div className="space-y-1">
            {keyInsights.map((ki, i) => (
              <div
                key={i}
                className="flex items-start gap-2 p-2 rounded border border-[#7C3AED]/20"
                style={{ backgroundColor: '#1A1028' }}
              >
                <div className="shrink-0 flex flex-col items-center pt-0.5">
                  <span className="text-[7px] font-terminal text-[#7C3AED]">C{ki.cycle}</span>
                </div>
                <p className="text-[9px] font-evidence text-[#A78BFA] leading-relaxed">
                  {ki.insight}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Compression status indicator */}
      {isCompressing && (
        <div className="flex items-center gap-2 p-2 rounded border border-[#7C3AED]/40 bg-[#1A1028]">
          <span className="text-[9px] font-terminal text-[#7C3AED] animate-[blink_0.8s_step-end_infinite]">
            ▓▒░
          </span>
          <span className="text-[9px] font-terminal text-[#7C3AED]">
            COMPRESSING REASONING...
          </span>
        </div>
      )}

      {/* Compressed reasoning text */}
      <div className="flex-1 overflow-hidden flex flex-col">
        <span className="text-[8px] font-terminal text-[#334155] tracking-widest mb-1.5">
          CUMULATIVE COMPRESSED STATE
        </span>

        <div
          className="flex-1 overflow-y-auto p-2 rounded border border-[#1E293B] font-evidence text-[9px] leading-relaxed"
          style={{
            backgroundColor: '#080E1A',
            color: '#475569',
            scrollbarWidth: 'thin',
            scrollbarColor: '#1E293B transparent',
          }}
        >
          {compressed ? (
            <pre className="whitespace-pre-wrap break-words">
              {compressed}
            </pre>
          ) : (
            <div className="flex flex-col items-center justify-center h-full gap-2 opacity-30">
              <span className="text-xl">▒▒▒</span>
              <span className="text-[8px] font-terminal text-[#334155] tracking-wider">
                NO COMPRESSED STATE
              </span>
              <span className="text-[7px] font-terminal text-[#273548] text-center">
                Reasoning is compressed<br />between cycles
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
