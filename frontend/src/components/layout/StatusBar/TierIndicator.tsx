import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useStore } from '../../../store'

export function TierIndicator() {
  const tier = useStore((s) => s.currentTier)
  const [isEscalating, setIsEscalating] = useState(false)
  const prevTierRef = useRef(tier)

  useEffect(() => {
    if (tier !== null && prevTierRef.current !== null && tier !== prevTierRef.current) {
      setIsEscalating(true)
      const t = setTimeout(() => setIsEscalating(false), 2500)
      prevTierRef.current = tier
      return () => clearTimeout(t)
    }
    prevTierRef.current = tier
  }, [tier])

  if (!tier) {
    return (
      <span className="text-[9px] font-mono tracking-wider" style={{ color: '#4A3D2A' }}>T—</span>
    )
  }

  const isT3 = tier === 3

  return (
    <div className="relative">
      <AnimatePresence>
        {isEscalating && (
          <motion.span
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: -4 }}
            exit={{ opacity: 0 }}
            className="absolute -top-5 left-0 text-[8px] font-mono whitespace-nowrap"
            style={{ color: isT3 ? '#D14B35' : '#D4651A' }}
          >
            ↑ ESCALATED
          </motion.span>
        )}
      </AnimatePresence>

      <motion.div
        animate={isEscalating ? { scale: [1, 1.06, 1] } : { scale: 1 }}
        transition={{ duration: 0.4 }}
        className="flex items-center gap-2 px-2 py-0.5"
        style={{
          border: `1px solid ${isT3 ? '#D14B35' : '#2E2820'}`,
          backgroundColor: isT3 ? '#2A0E09' : '#1E1B15',
          transition: 'border-color 0.3s ease, background-color 0.3s ease',
        }}
      >
        <span
          className="inline-block w-1.5 h-1.5"
          style={{
            backgroundColor: isT3 ? '#D14B35' : '#D4651A',
            animation: `pulse-dot ${isT3 ? '0.9s' : '2s'} ease-in-out infinite`,
          }}
        />
        <span
          className="text-[9px] font-mono font-medium tracking-wider"
          style={{ color: isT3 ? '#D14B35' : '#D4651A' }}
        >
          T{tier} {isT3 ? 'INVESTIGATION' : 'EVAL'}
        </span>
        {isT3 && (
          <span
            className="text-[7px] font-mono tracking-wider"
            style={{
              color: '#D14B35',
              borderLeft: '1px solid #D14B3530',
              paddingLeft: '6px',
              marginLeft: '2px',
            }}
          >
            CORE
          </span>
        )}
      </motion.div>
    </div>
  )
}
