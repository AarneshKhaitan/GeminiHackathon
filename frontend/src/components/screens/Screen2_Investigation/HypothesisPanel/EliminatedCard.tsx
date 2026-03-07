import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { MonoValue } from '../../../shared/MonoValue'
import type { Hypothesis } from '../../../../types/investigation'

interface EliminatedCardProps {
  hypothesis: Hypothesis
}

export function EliminatedCard({ hypothesis }: EliminatedCardProps) {
  const [isExpanded, setIsExpanded] = useState(true)  // Start expanded to show kill reason
  const [flashBg, setFlashBg] = useState(true)

  useEffect(() => {
    const t = setTimeout(() => setFlashBg(false), 600)
    return () => clearTimeout(t)
  }, [])

  const finalConf = Math.round(hypothesis.currentConfidence * 100)

  return (
    <motion.div
      layout
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.2 }}
      style={{
        borderBottom: '1px solid #2E2820',
        borderLeft: '2px solid #D14B35',
        backgroundColor: flashBg ? '#2A0E09' : '#161310',
        transition: 'background-color 0.4s ease',
        cursor: 'pointer',
      }}
      onClick={() => setIsExpanded((p) => !p)}
    >
      <div className="px-3 py-2">
        <div className="flex items-center gap-2">
          <span className="text-[9px] font-mono" style={{ color: '#4A3D2A' }}>{hypothesis.id}</span>
          <span className="text-[9px] font-mono" style={{ color: '#D14B35' }}>✗</span>
          {/* Strikethrough label */}
          <span
            className="text-[10px] font-mono leading-tight"
            style={{ color: '#4A3D2A', textDecoration: 'line-through', textDecorationColor: '#D14B3550' }}
          >
            {hypothesis.label}
          </span>
          <span className="ml-auto text-[9px] font-mono" style={{ color: '#4A3D2A' }}>
            ELIM C{hypothesis.eliminatedInCycle}
          </span>
          <span className="text-[8px] font-mono" style={{ color: '#4A3D2A' }}>{isExpanded ? '▲' : '▼'}</span>
        </div>

        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.18 }}
              className="overflow-hidden"
            >
              <div className="pt-2 space-y-1.5">
                {/* Kill reason */}
                {hypothesis.killReason && (
                  <div
                    className="p-2"
                    style={{ border: '1px solid #D14B3515', backgroundColor: '#2A0E09' }}
                  >
                    <div className="text-[8px] font-mono tracking-wider mb-0.5" style={{ color: '#D14B35' }}>
                      ELIMINATION REASON
                    </div>
                    <p className="text-[9px] font-mono leading-relaxed" style={{ color: '#8C7A5E' }}>
                      {hypothesis.killReason}
                    </p>
                  </div>
                )}
                {/* Kill atom */}
                {hypothesis.killAtomId && (
                  <div className="flex items-center gap-2">
                    <span className="text-[8px] font-mono" style={{ color: '#4A3D2A' }}>KILLED BY:</span>
                    <span
                      className="text-[8px] font-mono px-1.5 py-0.5"
                      style={{
                        border: '1px solid #D14B3520',
                        backgroundColor: '#2A0E09',
                        color: '#D14B35',
                      }}
                    >
                      {hypothesis.killAtomId}
                    </span>
                  </div>
                )}
                {/* Final confidence */}
                <div className="flex items-center gap-2">
                  <span className="text-[8px] font-mono" style={{ color: '#4A3D2A' }}>FINAL CONF:</span>
                  <MonoValue color="#333333" size="xs">{finalConf}%</MonoValue>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}
