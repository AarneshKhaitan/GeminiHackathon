import { AnimatePresence } from 'framer-motion'
import { useStore } from '../../../../store'
import { SurvivingCard } from './SurvivingCard'
import { EliminatedCard } from './EliminatedCard'

export function HypothesisPanel() {
  const hypotheses = useStore((s) => s.hypotheses)

  const surviving = hypotheses.filter((h) => h.status === 'surviving' || h.status === 'contradiction')
  const eliminated = hypotheses.filter((h) => h.status === 'eliminated')

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div
        className="shrink-0 px-3 py-2 flex items-center justify-between"
        style={{ borderBottom: '1px solid #1C1C1C' }}
      >
        <div className="flex items-center gap-2">
          <div style={{ width: '2px', height: '12px', backgroundColor: '#00C27A' }} />
          <span className="text-[9px] font-mono tracking-[0.2em] text-[#555555]">HYPOTHESIS STATUS</span>
        </div>
        <span className="text-[9px] font-mono text-[#333333]">
          {surviving.length} surviving · {eliminated.length} eliminated
        </span>
      </div>

      <div className="flex-1 overflow-y-auto">
        {/* Surviving hypotheses */}
        <AnimatePresence mode="popLayout">
          {surviving.map((h) => (
            <SurvivingCard key={h.id} hypothesis={h} />
          ))}
        </AnimatePresence>

        {/* Divider between surviving and eliminated */}
        {eliminated.length > 0 && (
          <div className="flex items-center gap-2 px-3 py-1.5" style={{ borderBottom: '1px solid #1C1C1C' }}>
            <div className="flex-1 h-px" style={{ backgroundColor: '#1C1C1C' }} />
            <span className="text-[8px] font-mono text-[#333333] tracking-wider">ELIMINATED</span>
            <div className="flex-1 h-px" style={{ backgroundColor: '#1C1C1C' }} />
          </div>
        )}

        {/* Eliminated hypotheses */}
        <AnimatePresence mode="popLayout">
          {eliminated.map((h) => (
            <EliminatedCard key={h.id} hypothesis={h} />
          ))}
        </AnimatePresence>

        {/* Empty state */}
        {hypotheses.length === 0 && (
          <div className="flex flex-col items-center justify-center h-32 gap-2">
            <span className="text-[9px] font-mono text-[#333333] tracking-wider">
              AWAITING INVESTIGATION START
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
