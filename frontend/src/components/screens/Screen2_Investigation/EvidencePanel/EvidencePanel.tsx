import { AnimatePresence } from 'framer-motion'
import { useStore } from '../../../../store'
import { EvidenceAtomCard } from './EvidenceAtomCard'
import { AgentStatusRow } from './AgentStatusRow'

export function EvidencePanel() {
  const atoms = useStore((s) => s.evidenceAtoms)

  return (
    <div className="flex flex-col h-full" style={{ backgroundColor: '#000000' }}>
      {/* Header */}
      <div
        className="shrink-0 px-3 py-2 flex items-center gap-2"
        style={{ borderBottom: '1px solid #1C1C1C' }}
      >
        <div style={{ width: '2px', height: '12px', backgroundColor: '#00C27A' }} />
        <span className="text-[9px] font-mono tracking-[0.2em] text-[#555555]">EVIDENCE STREAM</span>
      </div>

      {/* Agent status */}
      <div style={{ borderBottom: '1px solid #1C1C1C' }}>
        <AgentStatusRow />
      </div>

      {/* Evidence atoms feed */}
      <div className="flex-1 overflow-y-auto">
        <AnimatePresence mode="popLayout" initial={false}>
          {atoms.map((atom) => (
            <EvidenceAtomCard key={atom.id} atom={atom} />
          ))}
        </AnimatePresence>

        {atoms.length === 0 && (
          <div className="flex flex-col items-center justify-center h-24 gap-1">
            <span className="text-[9px] font-mono text-[#333333] tracking-wider">NO EVIDENCE GATHERED</span>
          </div>
        )}
      </div>
    </div>
  )
}
