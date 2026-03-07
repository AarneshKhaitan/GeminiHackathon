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
        style={{ borderBottom: '1px solid #2E2820', backgroundColor: '#161310' }}
      >
        <div className="flex items-center gap-2">
          <div style={{ width: '2px', height: '12px', backgroundColor: '#2E9E72' }} />
          <span
            className="text-[9px] tracking-[0.2em]"
            style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, color: '#8C7A5E' }}
          >HYPOTHESIS BOARD</span>
        </div>
        <span className="text-[9px] font-mono" style={{ color: '#4A3D2A' }}>
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
          <div className="flex items-center gap-2 px-3 py-1.5" style={{ borderBottom: '1px solid #2E2820' }}>
            <div className="flex-1 h-px" style={{ backgroundColor: '#2E2820' }} />
            <span className="text-[8px] font-mono tracking-wider" style={{ color: '#4A3D2A' }}>ELIMINATED</span>
            <div className="flex-1 h-px" style={{ backgroundColor: '#2E2820' }} />
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
            <span className="text-[9px] font-mono tracking-wider" style={{ color: '#4A3D2A' }}>
              AWAITING INVESTIGATION START
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
