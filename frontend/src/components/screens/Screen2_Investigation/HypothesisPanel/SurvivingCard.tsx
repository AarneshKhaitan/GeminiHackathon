import { motion } from 'framer-motion'
import { MonoValue } from '../../../shared/MonoValue'
import type { Hypothesis } from '../../../../types/investigation'

interface SurvivingCardProps {
  hypothesis: Hypothesis
  showChain?: boolean
}

export function SurvivingCard({ hypothesis, showChain = false }: SurvivingCardProps) {
  const conf = Math.round(hypothesis.currentConfidence * 100)
  const isContradiction = hypothesis.status === 'contradiction'

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="relative rounded border-l-4 overflow-hidden"
      style={{
        borderLeftColor: isContradiction ? '#D97706' : '#059669',
        borderTopColor: '#1E293B',
        borderRightColor: '#1E293B',
        borderBottomColor: '#1E293B',
        borderTopWidth: 1,
        borderRightWidth: 1,
        borderBottomWidth: 1,
        backgroundColor: isContradiction ? '#1C1810' : '#0A1A12',
        animation: isContradiction ? 'glow-contradiction 2s ease-in-out infinite' : 'none',
      }}
    >
      {/* Confidence bar background */}
      <div
        className="absolute bottom-0 left-0 h-0.5 transition-all duration-500 ease-out"
        style={{
          width: `${conf}%`,
          backgroundColor: isContradiction ? '#D97706' : '#059669',
          opacity: 0.6,
        }}
      />

      <div className="p-3">
        {/* Header row */}
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="flex items-center gap-2 min-w-0">
            <span className="shrink-0 text-[9px] font-terminal font-bold text-[#475569]">
              {hypothesis.id}
            </span>
            {isContradiction ? (
              <span className="shrink-0 text-[10px] text-[#D97706]">⚠</span>
            ) : (
              <span className="shrink-0 text-[10px] text-[#059669]">✓</span>
            )}
            <span className="text-xs font-display font-medium text-[#E2E8F0] leading-tight">
              {hypothesis.label}
            </span>
          </div>
          {/* Confidence score */}
          <div className="shrink-0 flex flex-col items-end">
            <MonoValue
              color={isContradiction ? '#D97706' : '#10B981'}
              size="md"
            >
              {conf}%
            </MonoValue>
            <span className="text-[8px] font-terminal text-[#334155]">CONF</span>
          </div>
        </div>

        {/* Description */}
        <p className="text-[10px] font-evidence text-[#475569] leading-relaxed mb-2">
          {hypothesis.description}
        </p>

        {/* Cross-modal conflict */}
        {isContradiction && hypothesis.crossModalConflict && (
          <div className="mt-2 p-2 rounded border border-[#D97706]/20 bg-[#78350F]/10">
            <div className="text-[9px] font-terminal text-[#D97706] tracking-wider mb-1">
              ⚡ CROSS-MODAL CONTRADICTION
            </div>
            <div className="text-[9px] font-terminal text-[#92400E] leading-relaxed">
              <span className="text-[#D97706]">STRUCTURAL:</span>{' '}
              {hypothesis.crossModalConflict.structuralObservation}
            </div>
            <div className="text-[9px] font-terminal text-[#92400E] leading-relaxed mt-1">
              <span className="text-[#FBBF24]">EMPIRICAL:</span>{' '}
              {hypothesis.crossModalConflict.empiricalObservation}
            </div>
          </div>
        )}

        {/* Key evidence (from case file format) */}
        {hypothesis.keyEvidence && hypothesis.keyEvidence.length > 0 && (
          <div className="mt-2 space-y-0.5">
            {hypothesis.keyEvidence.map((e, i) => (
              <div key={i} className="flex items-start gap-1.5">
                <span className="text-[#059669] text-[8px] mt-0.5">↑</span>
                <span className="text-[9px] font-evidence text-[#475569]">{e}</span>
              </div>
            ))}
          </div>
        )}

        {/* Key contradictions */}
        {hypothesis.keyContradiction && hypothesis.keyContradiction.length > 0 && (
          <div className="mt-1 space-y-0.5">
            {hypothesis.keyContradiction.map((c, i) => (
              <div key={i} className="flex items-start gap-1.5">
                <span className="text-[#D97706] text-[8px] mt-0.5">≠</span>
                <span className="text-[9px] font-evidence text-[#78350F]">{c}</span>
              </div>
            ))}
          </div>
        )}

        {/* Evidence chain (atom IDs) */}
        {showChain && hypothesis.supportingAtoms.length > 0 && (
          <div className="mt-2 flex items-center gap-1 flex-wrap">
            <span className="text-[8px] font-terminal text-[#334155]">ATOMS:</span>
            {hypothesis.supportingAtoms.map((id) => (
              <span
                key={id}
                className="text-[8px] font-terminal px-1 py-0.5 rounded border border-[#059669]/20 bg-[#064E3B]/30 text-[#6EE7B7]"
              >
                {id}
              </span>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  )
}
