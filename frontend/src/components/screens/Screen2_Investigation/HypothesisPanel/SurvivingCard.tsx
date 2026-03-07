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

  const accentColor = isContradiction ? '#F59E0B' : '#00C27A'

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
      style={{
        borderBottom: '1px solid #1C1C1C',
        borderLeft: `2px solid ${accentColor}`,
        backgroundColor: '#000000',
        animation: isContradiction ? 'glow-contradiction 2s ease-in-out infinite' : 'none',
        position: 'relative',
      }}
    >
      {/* Confidence bar — thin line at bottom */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          height: '1px',
          width: `${conf}%`,
          backgroundColor: accentColor,
          opacity: 0.5,
          transition: 'width 0.5s ease-out',
        }}
      />

      <div className="px-3 py-2.5">
        {/* Header row */}
        <div className="flex items-start justify-between gap-2 mb-1.5">
          <div className="flex items-center gap-2 min-w-0">
            <span className="shrink-0 text-[9px] font-mono text-[#333333]">
              {hypothesis.id}
            </span>
            <span className="shrink-0 text-[9px] font-mono" style={{ color: accentColor }}>
              {isContradiction ? '≠' : '✓'}
            </span>
            <span className="text-[10px] font-mono font-medium text-[#E8E8E8] leading-tight">
              {hypothesis.label}
            </span>
          </div>
          <div className="shrink-0 flex flex-col items-end gap-0.5">
            <MonoValue color={accentColor} size="sm">{conf}%</MonoValue>
            <span className="text-[7px] font-mono text-[#333333]">CONF</span>
          </div>
        </div>

        {/* Description */}
        <p className="text-[9px] font-mono text-[#555555] leading-relaxed mb-1.5">
          {hypothesis.description}
        </p>

        {/* Cross-modal conflict */}
        {isContradiction && hypothesis.crossModalConflict && (
          <div
            className="mt-1.5 p-2"
            style={{ border: '1px solid #F59E0B20', backgroundColor: '#140900' }}
          >
            <div className="text-[8px] font-mono text-[#F59E0B] tracking-wider mb-1">
              CROSS-MODAL CONTRADICTION
            </div>
            <div className="text-[9px] font-mono text-[#555555] leading-relaxed">
              <span className="text-[#F59E0B]">STRUCTURAL:</span>{' '}
              {hypothesis.crossModalConflict.structuralObservation}
            </div>
            <div className="text-[9px] font-mono text-[#555555] leading-relaxed mt-0.5">
              <span className="text-[#F59E0B]">EMPIRICAL:</span>{' '}
              {hypothesis.crossModalConflict.empiricalObservation}
            </div>
          </div>
        )}

        {/* Key evidence */}
        {hypothesis.keyEvidence && hypothesis.keyEvidence.length > 0 && (
          <div className="mt-1.5 space-y-0.5">
            {hypothesis.keyEvidence.map((e, i) => (
              <div key={i} className="flex items-start gap-1.5">
                <span className="text-[#00C27A] text-[8px] mt-0.5 shrink-0">↑</span>
                <span className="text-[9px] font-mono text-[#555555]">{e}</span>
              </div>
            ))}
          </div>
        )}

        {/* Key contradictions */}
        {hypothesis.keyContradiction && hypothesis.keyContradiction.length > 0 && (
          <div className="mt-1 space-y-0.5">
            {hypothesis.keyContradiction.map((c, i) => (
              <div key={i} className="flex items-start gap-1.5">
                <span className="text-[#F59E0B] text-[8px] mt-0.5 shrink-0">≠</span>
                <span className="text-[9px] font-mono text-[#555555]">{c}</span>
              </div>
            ))}
          </div>
        )}

        {/* Evidence chain (atom IDs) */}
        {showChain && hypothesis.supportingAtoms.length > 0 && (
          <div className="mt-1.5 flex items-center gap-1 flex-wrap">
            <span className="text-[8px] font-mono text-[#333333]">ATOMS:</span>
            {hypothesis.supportingAtoms.map((id) => (
              <span
                key={id}
                className="text-[8px] font-mono px-1 py-0.5"
                style={{
                  border: '1px solid #00C27A20',
                  backgroundColor: '#001A0E',
                  color: '#00C27A',
                }}
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
