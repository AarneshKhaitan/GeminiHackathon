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
      <span className="text-[9px] font-mono text-[#333333] tracking-wider">T—</span>
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
            style={{ color: isT3 ? '#FF3333' : '#F59E0B' }}
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
          border: `1px solid ${isT3 ? '#FF3333' : '#2D2D2D'}`,
          backgroundColor: isT3 ? '#0A0000' : '#0A0A0A',
          transition: 'border-color 0.3s ease, background-color 0.3s ease',
        }}
      >
        <span
          className="inline-block w-1.5 h-1.5"
          style={{
            backgroundColor: isT3 ? '#FF3333' : '#F59E0B',
            animation: `pulse-dot ${isT3 ? '0.9s' : '2s'} ease-in-out infinite`,
          }}
        />
        <span
          className="text-[9px] font-mono font-medium tracking-wider"
          style={{ color: isT3 ? '#FF3333' : '#F59E0B' }}
        >
          T{tier} {isT3 ? 'INVESTIGATION' : 'EVAL'}
        </span>
        {isT3 && (
          <span
            className="text-[7px] font-mono tracking-wider"
            style={{
              color: '#FF3333',
              borderLeft: '1px solid #FF333330',
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
