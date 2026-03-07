import { AnimatePresence } from 'framer-motion'
import { useStore } from '../../../../store'
import { SurvivingCard } from './SurvivingCard'
import { EliminatedCard } from './EliminatedCard'
import { SectionLabel } from '../../../shared/SectionLabel'

export function HypothesisPanel() {
  const hypotheses = useStore((s) => s.hypotheses)

  const surviving = hypotheses.filter((h) => h.status === 'surviving' || h.status === 'contradiction')
  const eliminated = hypotheses.filter((h) => h.status === 'eliminated')

  return (
    <div className="flex flex-col h-full p-3 gap-3">
      <div className="flex items-center justify-between">
        <SectionLabel accent="#059669">HYPOTHESIS STATUS</SectionLabel>
        <span className="text-[9px] font-terminal text-[#334155]">
          {surviving.length} surviving · {eliminated.length} eliminated
        </span>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2 pr-1">
        {/* Surviving hypotheses */}
        <AnimatePresence mode="popLayout">
          {surviving.map((h) => (
            <SurvivingCard key={h.id} hypothesis={h} />
          ))}
        </AnimatePresence>

        {/* Divider between surviving and eliminated */}
        {eliminated.length > 0 && (
          <div className="flex items-center gap-2 py-1">
            <div className="flex-1 h-px bg-[#1E293B]" />
            <span className="text-[8px] font-terminal text-[#273548] tracking-wider">
              ELIMINATED
            </span>
            <div className="flex-1 h-px bg-[#1E293B]" />
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
            <div className="text-[#273548] text-2xl">⬡</div>
            <span className="text-[10px] font-terminal text-[#273548] tracking-wider">
              AWAITING INVESTIGATION START
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
