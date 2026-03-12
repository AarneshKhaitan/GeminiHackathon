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
  const isUnscored = hypothesis.currentConfidence < 0  // -1 means not yet scored

  const accentColor = isContradiction ? '#D4651A' : '#2E9E72'

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
      style={{
        borderBottom: '1px solid #2E2820',
        borderLeft: `2px solid ${accentColor}`,
        backgroundColor: '#161310',
        animation: isContradiction ? 'glow-contradiction 2s ease-in-out infinite' : 'none',
        position: 'relative',
      }}
    >
      {/* Confidence bar — thin line at bottom, only if scored */}
      {!isUnscored && (
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
      )}

      <div className="px-3 py-2.5">
        {/* Header row */}
        <div className="flex items-start justify-between gap-2 mb-1.5">
          <div className="flex items-center gap-2 min-w-0">
            <span className="shrink-0 text-[9px] font-mono" style={{ color: '#4A3D2A' }}>
              {hypothesis.id}
            </span>
            <span className="shrink-0 text-[9px] font-mono" style={{ color: accentColor }}>
              {isContradiction ? '≠' : isUnscored ? '·' : '✓'}
            </span>
            <span className="text-[10px] font-mono font-medium leading-tight" style={{ color: '#EDE4D4' }}>
              {hypothesis.label}
            </span>
          </div>
          <div className="shrink-0 flex flex-col items-end gap-0.5">
            {isUnscored ? (
              <span className="text-[8px] font-mono" style={{ color: '#4A3D2A' }}>
                NOT SCORED
              </span>
            ) : (
              <>
                <MonoValue color={accentColor} size="sm">{conf}%</MonoValue>
                <span className="text-[7px] font-mono" style={{ color: '#4A3D2A' }}>CONF</span>
              </>
            )}
          </div>
        </div>

        {/* Description */}
        {hypothesis.description && (
          <p className="text-[9px] font-mono leading-relaxed mb-1.5" style={{ color: '#8C7A5E' }}>
            {hypothesis.description}
          </p>
        )}

        {/* Cross-modal conflict */}
        {isContradiction && hypothesis.crossModalConflict && (
          <div
            className="mt-1.5 p-2"
            style={{ border: '1px solid #D4651A20', backgroundColor: '#2D1407' }}
          >
            <div className="text-[8px] font-mono tracking-wider mb-1" style={{ color: '#D4651A' }}>
              CROSS-MODAL CONTRADICTION
            </div>
            <div className="text-[9px] font-mono leading-relaxed" style={{ color: '#8C7A5E' }}>
              <span style={{ color: '#D4651A' }}>STRUCTURAL:</span>{' '}
              {hypothesis.crossModalConflict.structuralObservation}
            </div>
            <div className="text-[9px] font-mono leading-relaxed mt-0.5" style={{ color: '#8C7A5E' }}>
              <span style={{ color: '#D4651A' }}>EMPIRICAL:</span>{' '}
              {hypothesis.crossModalConflict.empiricalObservation}
            </div>
          </div>
        )}

        {/* Key evidence */}
        {hypothesis.keyEvidence && hypothesis.keyEvidence.length > 0 && (
          <div className="mt-1.5 space-y-0.5">
            {hypothesis.keyEvidence.map((e, i) => (
              <div key={i} className="flex items-start gap-1.5">
                <span className="text-[8px] mt-0.5 shrink-0" style={{ color: '#2E9E72' }}>↑</span>
                <span className="text-[9px] font-mono" style={{ color: '#8C7A5E' }}>{e}</span>
              </div>
            ))}
          </div>
        )}

        {/* Key contradictions */}
        {hypothesis.keyContradiction && hypothesis.keyContradiction.length > 0 && (
          <div className="mt-1 space-y-0.5">
            {hypothesis.keyContradiction.map((c, i) => (
              <div key={i} className="flex items-start gap-1.5">
                <span className="text-[8px] mt-0.5 shrink-0" style={{ color: '#D4651A' }}>≠</span>
                <span className="text-[9px] font-mono" style={{ color: '#8C7A5E' }}>{c}</span>
              </div>
            ))}
          </div>
        )}

        {/* Evidence chain (atom IDs) */}
        {showChain && hypothesis.supportingAtoms.length > 0 && (
          <div className="mt-1.5 flex items-center gap-1 flex-wrap">
            <span className="text-[8px] font-mono" style={{ color: '#4A3D2A' }}>ATOMS:</span>
            {hypothesis.supportingAtoms.map((id) => (
              <span
                key={id}
                className="text-[8px] font-mono px-1 py-0.5"
                style={{
                  border: '1px solid #2E9E7230',
                  backgroundColor: '#0A2D1E',
                  color: '#2E9E72',
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
