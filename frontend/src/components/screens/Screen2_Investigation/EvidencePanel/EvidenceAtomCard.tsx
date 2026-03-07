import { motion } from 'framer-motion'
import { TagPill } from '../../../shared/TagPill'
import { MonoValue } from '../../../shared/MonoValue'
import type { EvidenceAtom } from '../../../../types/investigation'

interface EvidenceAtomCardProps {
  atom: EvidenceAtom
}

const noveltyColors = {
  critical: '#DC2626',
  high: '#D97706',
  medium: '#3B82F6',
  low: '#475569',
}

export function EvidenceAtomCard({ atom }: EvidenceAtomCardProps) {
  return (
    <motion.div
      layout
      initial={{ x: 40, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
      className="rounded border overflow-hidden"
      style={{
        borderLeftWidth: 3,
        borderLeftColor: noveltyColors[atom.novelty],
        borderTopColor: '#1E293B',
        borderRightColor: '#1E293B',
        borderBottomColor: '#1E293B',
        borderTopWidth: 1,
        borderRightWidth: 1,
        borderBottomWidth: 1,
        backgroundColor: '#0D1526',
      }}
    >
      <div className="p-2.5">
        {/* Header */}
        <div className="flex items-center gap-2 mb-1.5">
          <MonoValue color="#94A3B8" size="xs">{atom.id}</MonoValue>
          <TagPill type={atom.type === 'empirical' ? 'empirical' : 'structural'} />
          <TagPill type={atom.novelty} />
          <span className="ml-auto text-[8px] font-terminal text-[#273548]">
            C{atom.cycle}
          </span>
        </div>

        {/* Observation text */}
        <p className="text-[10px] font-evidence text-[#64748B] leading-relaxed">
          {atom.observation}
        </p>

        {/* Hypothesis tags */}
        {(atom.supports.length > 0 || atom.contradicts.length > 0) && (
          <div className="mt-2 flex flex-wrap gap-1">
            {atom.supports.map((id) => (
              <span
                key={`s-${id}`}
                className="text-[8px] font-terminal px-1 py-0.5 rounded border border-[#059669]/20 bg-[#064E3B]/30 text-[#6EE7B7]"
              >
                ↑ {id}
              </span>
            ))}
            {atom.contradicts.map((id) => (
              <span
                key={`c-${id}`}
                className="text-[8px] font-terminal px-1 py-0.5 rounded border border-[#DC2626]/20 bg-[#7F1D1D]/30 text-[#FCA5A5]"
              >
                ↓ {id}
              </span>
            ))}
          </div>
        )}

        {/* Confidence */}
        <div className="mt-1.5 flex items-center gap-2">
          <div className="flex-1 h-0.5 bg-[#1E293B] rounded-full overflow-hidden">
            <div
              className="h-full rounded-full"
              style={{
                width: `${Math.round(atom.confidence * 100)}%`,
                backgroundColor: noveltyColors[atom.novelty],
              }}
            />
          </div>
          <MonoValue color="#334155" size="xs">
            {Math.round(atom.confidence * 100)}%
          </MonoValue>
        </div>
      </div>
    </motion.div>
  )
}
