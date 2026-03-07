import { useEffect, useRef, useState } from 'react'
import { useStore } from '../../../store'

const tierConfig = {
  2: { color: '#EAB308', bg: '#422006', label: 'T2', text: 'TIER 2' },
  3: { color: '#F97316', bg: '#431407', label: 'T3', text: 'TIER 3' },
  4: { color: '#EF4444', bg: '#450A0A', label: 'T4', text: 'TIER 4' },
}

export function TierIndicator() {
  const tier = useStore((s) => s.currentTier)
  const [isPulsing, setIsPulsing] = useState(false)
  const prevTierRef = useRef(tier)

  useEffect(() => {
    if (tier !== prevTierRef.current && tier !== null) {
      setIsPulsing(true)
      const t = setTimeout(() => setIsPulsing(false), 2000)
      prevTierRef.current = tier
      return () => clearTimeout(t)
    }
  }, [tier])

  if (!tier) {
    return (
      <div className="flex items-center gap-1.5 px-2 py-1 rounded border border-[#273548] bg-[#1E293B]">
        <span className="text-[10px] font-terminal text-[#334155] tracking-widest">T—</span>
      </div>
    )
  }

  const cfg = tierConfig[tier]

  return (
    <div
      className="flex items-center gap-1.5 px-2.5 py-1 rounded border"
      style={{
        borderColor: `${cfg.color}40`,
        backgroundColor: cfg.bg,
        animation: isPulsing ? 'pulse-tier 0.6s ease-in-out 3' : 'none',
        boxShadow: isPulsing ? `0 0 12px ${cfg.color}60` : `0 0 4px ${cfg.color}20`,
        transition: 'box-shadow 0.5s ease, background-color 0.5s ease',
      }}
    >
      <div
        className="w-1.5 h-1.5 rounded-full"
        style={{
          backgroundColor: cfg.color,
          boxShadow: `0 0 4px ${cfg.color}`,
          animation: 'pulse-dot 1.5s ease-in-out infinite',
        }}
      />
      <span
        className="text-[10px] font-terminal font-bold tracking-widest"
        style={{ color: cfg.color }}
      >
        {cfg.text}
      </span>
    </div>
  )
}
