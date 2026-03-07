import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useStore } from '../../../store'

const tierConfig = {
  2: {
    color: '#EAB308',
    dimColor: '#A16207',
    bg: '#1A1200',
    borderColor: '#78350F50',
    label: 'T2',
    sublabel: 'EVAL',
    glow: false,
    pulse: 'pulse-dot 2s ease-in-out infinite',
  },
  3: {
    color: '#EF4444',
    dimColor: '#DC2626',
    bg: '#1A0000',
    borderColor: '#EF444440',
    label: 'T3',
    sublabel: 'INVESTIGATION',
    glow: true,
    pulse: 'pulse-dot 0.8s ease-in-out infinite',
  },
}

export function TierIndicator() {
  const tier = useStore((s) => s.currentTier)
  const [isEscalating, setIsEscalating] = useState(false)
  const prevTierRef = useRef(tier)

  useEffect(() => {
    if (tier !== null && prevTierRef.current !== null && tier !== prevTierRef.current) {
      setIsEscalating(true)
      const t = setTimeout(() => setIsEscalating(false), 3000)
      prevTierRef.current = tier
      return () => clearTimeout(t)
    }
    prevTierRef.current = tier
  }, [tier])

  if (!tier) {
    return (
      <div className="flex items-center gap-2 px-2.5 py-1.5 rounded border border-[#1E293B] bg-[#0A1120]">
        <div className="w-1.5 h-1.5 rounded-full bg-[#273548]" />
        <div className="flex flex-col leading-none">
          <span className="text-[9px] font-terminal font-bold text-[#334155] tracking-widest">T—</span>
          <span className="text-[7px] font-terminal text-[#273548] tracking-wider">DORMANT</span>
        </div>
      </div>
    )
  }

  const cfg = tierConfig[tier as 2 | 3]

  return (
    <div className="relative flex items-center gap-1.5">
      {/* Escalation flash label */}
      <AnimatePresence>
        {isEscalating && (
          <motion.div
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: -4 }}
            exit={{ opacity: 0 }}
            className="absolute -top-5 left-0 text-[8px] font-terminal tracking-wider whitespace-nowrap"
            style={{ color: cfg.color }}
          >
            ▲ ESCALATED
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div
        layout
        className="flex items-center gap-2 px-2.5 py-1.5 rounded border"
        animate={isEscalating ? { scale: [1, 1.08, 1, 1.05, 1] } : { scale: 1 }}
        transition={{ duration: 0.6, ease: 'easeInOut' }}
        style={{
          borderColor: isEscalating ? cfg.color : cfg.borderColor,
          backgroundColor: cfg.bg,
          boxShadow: cfg.glow
            ? isEscalating
              ? `0 0 24px ${cfg.color}70, inset 0 0 16px ${cfg.color}15`
              : `0 0 10px ${cfg.color}40, inset 0 0 6px ${cfg.color}10`
            : isEscalating
            ? `0 0 14px ${cfg.color}60`
            : 'none',
          transition: 'box-shadow 0.5s ease, border-color 0.3s ease',
        }}
      >
        {/* Status dot */}
        <div
          className="w-1.5 h-1.5 rounded-full shrink-0"
          style={{
            backgroundColor: cfg.color,
            boxShadow: cfg.glow ? `0 0 8px ${cfg.color}, 0 0 3px ${cfg.color}` : `0 0 4px ${cfg.color}`,
            animation: cfg.pulse,
          }}
        />

        {/* Labels */}
        <div className="flex flex-col leading-none">
          <div className="flex items-baseline gap-1.5">
            <span
              className="text-[10px] font-terminal font-bold tracking-widest"
              style={{ color: cfg.color }}
            >
              {cfg.label}
            </span>
            <span
              className="text-[8px] font-terminal tracking-wider"
              style={{ color: cfg.dimColor }}
            >
              {cfg.sublabel}
            </span>
          </div>
        </div>

        {/* T3 is the CORE product — mark it */}
        {tier === 3 && (
          <div
            className="ml-0.5 px-1 py-0.5 rounded text-[6px] font-terminal tracking-wider"
            style={{
              color: '#EF4444',
              backgroundColor: '#EF444415',
              border: '1px solid #EF444440',
              animation: 'blink 2s step-end infinite',
            }}
          >
            CORE
          </div>
        )}
      </motion.div>
    </div>
  )
}
