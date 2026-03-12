import { useStore } from '../../../../store'
import { EvidencePanel } from '../EvidencePanel/EvidencePanel'
import { TokenUsagePanel } from './TokenUsagePanel'
import { CompressedReasoningPanel } from './CompressedReasoningPanel'
import { CrossModalPanel } from './CrossModalPanel'
import { EvidencePendingPanel } from './EvidencePendingPanel'

type Tab = 'evidence' | 'tokens' | 'reasoning' | 'crossModal' | 'pending'

const TABS: { id: Tab; label: string; accent: string }[] = [
  { id: 'evidence', label: 'EVIDENCE', accent: '#2E9E72' },
  { id: 'crossModal', label: 'CROSS-MODAL', accent: '#D14B35' },
  { id: 'pending', label: 'PENDING', accent: '#C8912A' },
  { id: 'tokens', label: 'TOKENS', accent: '#7C6DB8' },
  { id: 'reasoning', label: 'REASONING', accent: '#8C7A5E' },
]

export function RightPanel() {
  const activeTab = useStore((s) => s.rightPanelTab)
  const setTab = useStore((s) => s.setRightPanelTab)
  const evidenceAtoms = useStore((s) => s.evidenceAtoms)
  const crossModalFlags = useStore((s) => s.crossModalFlags)
  const evidencePending = useStore((s) => s.evidencePending)
  const tokenUsage = useStore((s) => s.tokenUsage)
  const compressedReasoning = useStore((s) => s.compressedReasoning)

  return (
    <div className="flex flex-col h-full" style={{ backgroundColor: '#161310' }}>
      {/* Tab bar — underline style, full-width border at bottom */}
      <div
        className="flex shrink-0"
        style={{ borderBottom: '1px solid #2E2820', backgroundColor: '#161310' }}
      >
        {TABS.map((tab) => {
          const isActive = activeTab === tab.id
          const badge =
            tab.id === 'evidence'
              ? evidenceAtoms.length
              : tab.id === 'crossModal'
              ? crossModalFlags.length
              : tab.id === 'pending'
              ? evidencePending.length
              : tab.id === 'tokens'
              ? tokenUsage.byCycle.length
              : null

          return (
            <button
              key={tab.id}
              onClick={() => setTab(tab.id)}
              className="relative flex items-center gap-1.5 px-2.5 py-2 text-[8px] font-mono tracking-widest transition-colors duration-150"
              style={{
                color: isActive ? tab.accent : '#4A3D2A',
                borderBottom: isActive ? `2px solid ${tab.accent}` : '2px solid transparent',
                marginBottom: '-1px',
                backgroundColor: 'transparent',
              }}
            >
              {tab.label}
              {badge !== null && badge > 0 && (
                <span
                  className="text-[7px] font-mono tabular-nums px-1"
                  style={{
                    backgroundColor: isActive ? `${tab.accent}18` : '#1E1B15',
                    color: isActive ? tab.accent : '#4A3D2A',
                    border: `1px solid ${isActive ? `${tab.accent}30` : '#2E2820'}`,
                  }}
                >
                  {badge}
                </span>
              )}
              {tab.id === 'reasoning' && compressedReasoning && (
                <span
                  className="inline-block w-1.5 h-1.5"
                  style={{ backgroundColor: isActive ? tab.accent : '#4A3D2A' }}
                />
              )}
            </button>
          )
        })}
      </div>

      {/* Panel content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'evidence' && <EvidencePanel />}
        {activeTab === 'crossModal' && <CrossModalPanel />}
        {activeTab === 'pending' && <EvidencePendingPanel />}
        {activeTab === 'tokens' && <TokenUsagePanel />}
        {activeTab === 'reasoning' && <CompressedReasoningPanel />}
      </div>
    </div>
  )
}
