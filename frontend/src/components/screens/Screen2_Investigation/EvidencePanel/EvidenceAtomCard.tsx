import { motion } from 'framer-motion'
import { TagPill } from '../../../shared/TagPill'
import { MonoValue } from '../../../shared/MonoValue'
import type { EvidenceAtom } from '../../../../types/investigation'

interface EvidenceAtomCardProps {
  atom: EvidenceAtom
}

const noveltyColors: Record<string, string> = {
  critical: '#D14B35',
  high: '#D4651A',
  medium: '#C8912A',
  low: '#3D3529',
}

export function EvidenceAtomCard({ atom }: EvidenceAtomCardProps) {
  const accentColor = noveltyColors[atom.novelty] ?? '#333333'

  return (
    <motion.div
      layout
      initial={{ x: 24, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.22, ease: 'easeOut' }}
      style={{
        borderBottom: '1px solid #2E2820',
        borderLeft: `2px solid ${accentColor}`,
        backgroundColor: '#161310',
      }}
    >
      <div className="px-3 py-2">
        {/* Header */}
        <div className="flex items-center gap-2 mb-1.5">
          <MonoValue color="#555555" size="xs">{atom.id}</MonoValue>
          <TagPill type={atom.type === 'empirical' ? 'empirical' : 'structural'} />
          <TagPill type={atom.novelty} />
          <span className="ml-auto text-[8px] font-mono" style={{ color: '#4A3D2A' }}>C{atom.cycle}</span>
        </div>

        {/* Observation text */}
        <p className="text-[9px] font-mono leading-relaxed" style={{ color: '#8C7A5E' }}>
          {atom.observation}
        </p>

        {/* Hypothesis tags */}
        {(atom.supports.length > 0 || atom.contradicts.length > 0) && (
          <div className="mt-1.5 flex flex-wrap gap-1">
            {atom.supports.map((id) => (
              <span
                key={`s-${id}`}
                className="text-[8px] font-mono px-1 py-0.5"
                style={{
                  border: '1px solid #2E9E7220',
                  backgroundColor: '#0A2D1E',
                  color: '#2E9E72',
                }}
              >
                ↑ {id}
              </span>
            ))}
            {atom.contradicts.map((id) => (
              <span
                key={`c-${id}`}
                className="text-[8px] font-mono px-1 py-0.5"
                style={{
                  border: '1px solid #D14B3520',
                  backgroundColor: '#2A0E09',
                  color: '#D14B35',
                }}
              >
                ↓ {id}
              </span>
            ))}
          </div>
        )}

        {/* Confidence bar — 1px line */}
        <div className="mt-1.5 flex items-center gap-2">
          <div className="flex-1 h-px overflow-hidden" style={{ backgroundColor: '#2E2820' }}>
            <div
              className="h-full"
              style={{
                width: `${Math.round(atom.confidence * 100)}%`,
                backgroundColor: accentColor,
                transition: 'width 0.4s ease-out',
              }}
            />
          </div>
          <MonoValue color="#333333" size="xs">
            {Math.round(atom.confidence * 100)}%
          </MonoValue>
        </div>
      </div>
    </motion.div>
  )
}
