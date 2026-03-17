import { motion, AnimatePresence } from 'framer-motion'
import { useStore } from '../../../../store'
import { MonoValue } from '../../../shared/MonoValue'

export function CrossModalPanel() {
  const flags = useStore((s) => s.crossModalFlags)

  return (
    <div className="flex flex-col h-full" style={{ backgroundColor: '#161310' }}>
      {/* Header */}
      <div
        className="shrink-0 px-3 py-2 flex items-center gap-2"
        style={{ borderBottom: '1px solid #2E2820', backgroundColor: '#161310' }}
      >
        <div style={{ width: '2px', height: '12px', backgroundColor: '#D14B35' }} />
        <span
          className="text-[9px] tracking-[0.2em]"
          style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, color: '#8C7A5E' }}
        >
          CROSS-MODAL CONTRADICTIONS
        </span>
        <span className="ml-auto text-[8px] font-mono" style={{ color: '#4A3D2A' }}>
          {flags.length} DETECTED
        </span>
      </div>

      {/* Explanation */}
      <div className="shrink-0 px-3 py-2" style={{ borderBottom: '1px solid #2E2820', backgroundColor: '#0C0A07' }}>
        <p className="text-[8px] font-mono leading-relaxed" style={{ color: '#4A3D2A' }}>
          Structural rules promise stability, but empirical data shows collapse. These contradictions reveal when
          regulatory frameworks fail under real-world stress.
        </p>
      </div>

      {/* Flags list */}
      <div className="flex-1 overflow-y-auto">
        <AnimatePresence mode="popLayout" initial={false}>
          {flags.map((flag, _idx) => (
            <motion.div
              key={`${flag.cycle}-${flag.structuralAtomId}-${flag.empiricalAtomId}`}
              layout
              initial={{ x: 24, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 0.3, ease: 'easeOut' }}
              style={{
                borderBottom: '1px solid #2E2820',
                borderLeft: '2px solid #D14B35',
                backgroundColor: '#161310',
              }}
            >
              <div className="px-3 py-3">
                {/* Header: cycle + atom IDs */}
                <div className="flex items-center gap-2 mb-2">
                  <MonoValue color="#D14B35" size="xs">
                    C{flag.cycle}
                  </MonoValue>
                  <div className="flex items-center gap-1">
                    <span
                      className="text-[8px] font-mono px-1.5 py-0.5"
                      style={{
                        backgroundColor: '#1A2D24',
                        border: '1px solid #2E9E7230',
                        color: '#2E9E72',
                      }}
                    >
                      {flag.structuralAtomId}
                    </span>
                    <span className="text-[8px]" style={{ color: '#4A3D2A' }}>
                      ⚡
                    </span>
                    <span
                      className="text-[8px] font-mono px-1.5 py-0.5"
                      style={{
                        backgroundColor: '#2A1A09',
                        border: '1px solid #C8912A30',
                        color: '#C8912A',
                      }}
                    >
                      {flag.empiricalAtomId}
                    </span>
                  </div>
                </div>

                {/* Description */}
                <p className="text-[9px] font-mono leading-relaxed" style={{ color: '#8C7A5E' }}>
                  {flag.description}
                </p>

                {/* Contradiction indicator */}
                <div className="mt-2 flex items-center gap-2">
                  <div className="flex-1 h-px" style={{ backgroundColor: '#2E2820' }} />
                  <span
                    className="text-[7px] font-mono tracking-wider px-1.5 py-0.5"
                    style={{
                      backgroundColor: '#2A0E09',
                      border: '1px solid #D14B3530',
                      color: '#D14B35',
                    }}
                  >
                    STRUCTURAL ≠ EMPIRICAL
                  </span>
                  <div className="flex-1 h-px" style={{ backgroundColor: '#2E2820' }} />
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {flags.length === 0 && (
          <div className="flex flex-col items-center justify-center h-32 gap-2 px-4">
            <span className="text-[9px] font-mono tracking-wider" style={{ color: '#4A3D2A' }}>
              NO CROSS-MODAL CONTRADICTIONS
            </span>
            <p className="text-[8px] font-mono text-center leading-relaxed" style={{ color: '#333333' }}>
              Detected in later cycles when structural rules fail to predict empirical outcomes
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
