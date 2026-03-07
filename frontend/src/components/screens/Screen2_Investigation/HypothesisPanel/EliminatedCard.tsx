import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { MonoValue } from '../../../shared/MonoValue'
import type { Hypothesis } from '../../../../types/investigation'

interface EliminatedCardProps {
  hypothesis: Hypothesis
}

export function EliminatedCard({ hypothesis }: EliminatedCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [flashPhase, setFlashPhase] = useState<'flash' | 'drain' | 'settled'>('settled')

  // Trigger animation when card first renders as eliminated
  useEffect(() => {
    setFlashPhase('flash')
    const t1 = setTimeout(() => setFlashPhase('drain'), 200)
    const t2 = setTimeout(() => setFlashPhase('settled'), 1000)
    return () => { clearTimeout(t1); clearTimeout(t2) }
  }, [])

  const isFinalConf = Math.round(hypothesis.currentConfidence * 100)

  return (
    <motion.div
      layout
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.2 }}
    >
      <div
        className="relative rounded border-l-4 overflow-hidden cursor-pointer"
        style={{
          borderLeftColor: '#DC2626',
          borderTopColor: '#1E293B',
          borderRightColor: '#1E293B',
          borderBottomColor: '#1E293B',
          borderTopWidth: 1,
          borderRightWidth: 1,
          borderBottomWidth: 1,
          backgroundColor: flashPhase === 'flash' ? '#3B0000' : '#100808',
          transition: 'background-color 0.3s ease',
        }}
        onClick={() => setIsExpanded((p) => !p)}
      >
        {/* Drained confidence bar (empty) */}
        <div className="absolute bottom-0 left-0 h-0.5 w-0 bg-[#DC2626] opacity-30" />

        <div className="p-2.5">
          <div className="flex items-center gap-2">
            <span className="text-[9px] font-terminal text-[#334155]">{hypothesis.id}</span>
            <span className="text-[9px] text-[#DC2626]">✗</span>
            {/* Strikethrough label */}
            <span
              className="text-[11px] font-display text-[#475569] leading-tight"
              style={{ textDecoration: 'line-through', textDecorationColor: '#DC262680' }}
            >
              {hypothesis.label}
            </span>
            <span className="ml-auto text-[9px] font-terminal text-[#334155]">
              ELIM. C{hypothesis.eliminatedInCycle}
            </span>
            {/* Expand toggle */}
            <span className="text-[9px] text-[#273548]">{isExpanded ? '▲' : '▼'}</span>
          </div>

          <AnimatePresence>
            {isExpanded && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <div className="pt-2 space-y-1.5">
                  {/* Kill reason */}
                  {hypothesis.killReason && (
                    <div className="p-2 rounded border border-[#DC2626]/15 bg-[#7F1D1D]/10">
                      <div className="text-[8px] font-terminal text-[#DC2626] tracking-wider mb-0.5">
                        ELIMINATION REASON
                      </div>
                      <p className="text-[10px] font-evidence text-[#7F1D1D] leading-relaxed">
                        {hypothesis.killReason}
                      </p>
                    </div>
                  )}
                  {/* Kill atom */}
                  {hypothesis.killAtomId && (
                    <div className="flex items-center gap-2">
                      <span className="text-[8px] font-terminal text-[#334155]">KILLED BY:</span>
                      <span className="text-[8px] font-terminal px-1.5 py-0.5 rounded border border-[#DC2626]/20 bg-[#7F1D1D]/20 text-[#FCA5A5]">
                        {hypothesis.killAtomId}
                      </span>
                    </div>
                  )}
                  {/* Final confidence */}
                  <div className="flex items-center gap-2">
                    <span className="text-[8px] font-terminal text-[#334155]">FINAL CONF:</span>
                    <MonoValue color="#334155" size="xs">{isFinalConf}%</MonoValue>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  )
}
