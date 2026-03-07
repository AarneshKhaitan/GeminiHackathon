import { AnimatePresence } from 'framer-motion'
import { useStore } from '../../../../store'
import { EvidenceAtomCard } from './EvidenceAtomCard'
import { AgentStatusRow } from './AgentStatusRow'
import { SectionLabel } from '../../../shared/SectionLabel'

export function EvidencePanel() {
  const atoms = useStore((s) => s.evidenceAtoms)

  return (
    <div className="flex flex-col h-full p-3 gap-3">
      <SectionLabel accent="#10B981">EVIDENCE STREAM</SectionLabel>

      {/* Agent status */}
      <AgentStatusRow />

      {/* Evidence atoms feed */}
      <div className="flex-1 overflow-y-auto space-y-2 pr-1">
        <AnimatePresence mode="popLayout" initial={false}>
          {atoms.map((atom) => (
            <EvidenceAtomCard key={atom.id} atom={atom} />
          ))}
        </AnimatePresence>

        {atoms.length === 0 && (
          <div className="flex flex-col items-center justify-center h-24 gap-1">
            <span className="text-[#1E293B] text-xl">▒</span>
            <span className="text-[9px] font-terminal text-[#1E293B] tracking-wider">
              NO EVIDENCE GATHERED
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
