import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useStore } from '../../../store'

type TierLevel = 2 | 3 | 4

const tierConfig: Record<TierLevel, {
  color: string
  dimColor: string
  bg: string
  borderColor: string
  label: string
  sublabel: string
  cycles: string | null
  glow: boolean
}> = {
  2: {
    color: '#EAB308',
    dimColor: '#A16207',
    bg: '#1A1200',
    borderColor: '#78350F60',
    label: 'T2',
    sublabel: 'EVAL',
    cycles: null,
    glow: false,
  },
  3: {
    color: '#F97316',
    dimColor: '#9A3412',
    bg: '#1A0900',
    borderColor: '#9A341260',
    label: 'T3',
    sublabel: 'INITIAL',
    cycles: '1-2',
    glow: false,
  },
  4: {
    color: '#EF4444',
    dimColor: '#7F1D1D',
    bg: '#1A0000',
    borderColor: '#EF444440',
    label: 'T4',
    sublabel: 'FULL',
    cycles: '4-5',
    glow: true,
  },
}

export function TierIndicator() {
  const tier = useStore((s) => s.currentTier)
  const [isPulsing, setIsPulsing] = useState(false)
  const [wasPromoted, setWasPromoted] = useState(false)
  const [wasDemoted, setWasDemoted] = useState(false)
  const prevTierRef = useRef(tier)

  useEffect(() => {
    if (tier !== prevTierRef.current && tier !== null && prevTierRef.current !== null) {
      const promoted = tier > prevTierRef.current
      const demoted = tier < prevTierRef.current
      setIsPulsing(true)
      setWasPromoted(promoted)
      setWasDemoted(demoted)
      const t = setTimeout(() => {
        setIsPulsing(false)
        setWasPromoted(false)
        setWasDemoted(false)
      }, 2500)
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

  const cfg = tierConfig[tier]

  return (
    <div className="relative flex items-center gap-1.5">
      {/* Demotion flash */}
      <AnimatePresence>
        {wasDemoted && (
          <motion.div
            initial={{ opacity: 0, x: 0 }}
            animate={{ opacity: 1, x: -4 }}
            exit={{ opacity: 0 }}
            className="absolute -top-5 left-0 text-[8px] font-terminal text-[#EAB308] tracking-wider whitespace-nowrap"
          >
            ▼ DEMOTED
          </motion.div>
        )}
        {wasPromoted && (
          <motion.div
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: -4 }}
            exit={{ opacity: 0 }}
            className="absolute -top-5 left-0 text-[8px] font-terminal tracking-wider whitespace-nowrap"
            style={{ color: cfg.color }}
          >
            ▲ PROMOTED
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div
        layout
        className="flex items-center gap-2 px-2.5 py-1.5 rounded border"
        style={{
          borderColor: isPulsing ? `${cfg.color}80` : cfg.borderColor,
          backgroundColor: cfg.bg,
          boxShadow: cfg.glow
            ? isPulsing
              ? `0 0 20px ${cfg.color}60, inset 0 0 12px ${cfg.color}10`
              : `0 0 8px ${cfg.color}30, inset 0 0 4px ${cfg.color}08`
            : isPulsing
            ? `0 0 12px ${cfg.color}50`
            : 'none',
          animation: isPulsing ? 'pulse-tier 0.5s ease-in-out 3' : 'none',
          transition: 'box-shadow 0.5s ease, border-color 0.3s ease',
        }}
      >
        {/* Dot */}
        <div
          className="w-1.5 h-1.5 rounded-full shrink-0"
          style={{
            backgroundColor: cfg.color,
            boxShadow: `0 0 6px ${cfg.color}`,
            animation: cfg.glow
              ? 'pulse-dot 1s ease-in-out infinite'
              : 'pulse-dot 1.8s ease-in-out infinite',
          }}
        />

        {/* Labels */}
        <div className="flex flex-col leading-none">
          <div className="flex items-baseline gap-1">
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
          {cfg.cycles && (
            <span
              className="text-[7px] font-terminal tracking-wider"
              style={{ color: `${cfg.color}60` }}
            >
              {cfg.cycles} CYCLES
            </span>
          )}
        </div>

        {/* Core product marker for T4 */}
        {tier === 4 && (
          <div
            className="ml-0.5 px-1 py-0.5 rounded text-[6px] font-terminal tracking-wider"
            style={{
              color: '#EF4444',
              backgroundColor: '#EF444415',
              border: '1px solid #EF444430',
            }}
          >
            CORE
          </div>
        )}
      </motion.div>
    </div>
  )
}
