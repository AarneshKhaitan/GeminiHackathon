import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { MonoValue } from '../../../shared/MonoValue'
import type { Hypothesis } from '../../../../types/investigation'

interface EliminatedCardProps {
  hypothesis: Hypothesis
}

export function EliminatedCard({ hypothesis }: EliminatedCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)
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
        borderBottom: '1px solid #1C1C1C',
        borderLeft: '2px solid #FF3333',
        backgroundColor: flashBg ? '#0D0000' : '#000000',
        transition: 'background-color 0.4s ease',
        cursor: 'pointer',
      }}
      onClick={() => setIsExpanded((p) => !p)}
    >
      <div className="px-3 py-2">
        <div className="flex items-center gap-2">
          <span className="text-[9px] font-mono text-[#333333]">{hypothesis.id}</span>
          <span className="text-[9px] font-mono text-[#FF3333]">✗</span>
          {/* Strikethrough label */}
          <span
            className="text-[10px] font-mono text-[#333333] leading-tight"
            style={{ textDecoration: 'line-through', textDecorationColor: '#FF333350' }}
          >
            {hypothesis.label}
          </span>
          <span className="ml-auto text-[9px] font-mono text-[#333333]">
            ELIM C{hypothesis.eliminatedInCycle}
          </span>
          <span className="text-[8px] font-mono text-[#333333]">{isExpanded ? '▲' : '▼'}</span>
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
                    style={{ border: '1px solid #FF333315', backgroundColor: '#050000' }}
                  >
                    <div className="text-[8px] font-mono text-[#FF3333] tracking-wider mb-0.5">
                      ELIMINATION REASON
                    </div>
                    <p className="text-[9px] font-mono text-[#555555] leading-relaxed">
                      {hypothesis.killReason}
                    </p>
                  </div>
                )}
                {/* Kill atom */}
                {hypothesis.killAtomId && (
                  <div className="flex items-center gap-2">
                    <span className="text-[8px] font-mono text-[#333333]">KILLED BY:</span>
                    <span
                      className="text-[8px] font-mono px-1.5 py-0.5"
                      style={{
                        border: '1px solid #FF333320',
                        backgroundColor: '#0A0000',
                        color: '#FF3333',
                      }}
                    >
                      {hypothesis.killAtomId}
                    </span>
                  </div>
                )}
                {/* Final confidence */}
                <div className="flex items-center gap-2">
                  <span className="text-[8px] font-mono text-[#333333]">FINAL CONF:</span>
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
