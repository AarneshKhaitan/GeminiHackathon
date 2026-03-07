import { useStore } from '../../../../store'
import { EvidencePanel } from '../EvidencePanel/EvidencePanel'
import { TokenUsagePanel } from './TokenUsagePanel'
import { CompressedReasoningPanel } from './CompressedReasoningPanel'

type Tab = 'evidence' | 'tokens' | 'reasoning'

const TABS: { id: Tab; label: string; accent: string }[] = [
  { id: 'evidence', label: 'EVIDENCE', accent: '#00C27A' },
  { id: 'tokens', label: 'TOKENS', accent: '#3B82F6' },
  { id: 'reasoning', label: 'REASONING', accent: '#8B5CF6' },
]

export function RightPanel() {
  const activeTab = useStore((s) => s.rightPanelTab)
  const setTab = useStore((s) => s.setRightPanelTab)
  const evidenceAtoms = useStore((s) => s.evidenceAtoms)
  const tokenUsage = useStore((s) => s.tokenUsage)
  const compressedReasoning = useStore((s) => s.compressedReasoning)

  return (
    <div className="flex flex-col h-full" style={{ backgroundColor: '#000000' }}>
      {/* Tab bar — underline style, full-width border at bottom */}
      <div
        className="flex shrink-0"
        style={{ borderBottom: '1px solid #1C1C1C', backgroundColor: '#000000' }}
      >
        {TABS.map((tab) => {
          const isActive = activeTab === tab.id
          const badge =
            tab.id === 'evidence'
              ? evidenceAtoms.length
              : tab.id === 'tokens'
              ? tokenUsage.byCycle.length
              : null

          return (
            <button
              key={tab.id}
              onClick={() => setTab(tab.id)}
              className="relative flex items-center gap-1.5 px-3 py-2 text-[9px] font-mono tracking-widest transition-colors duration-150"
              style={{
                color: isActive ? tab.accent : '#333333',
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
                    backgroundColor: isActive ? `${tab.accent}18` : '#0A0A0A',
                    color: isActive ? tab.accent : '#333333',
                    border: `1px solid ${isActive ? `${tab.accent}30` : '#1C1C1C'}`,
                  }}
                >
                  {badge}
                </span>
              )}
              {tab.id === 'reasoning' && compressedReasoning && (
                <span
                  className="inline-block w-1.5 h-1.5"
                  style={{ backgroundColor: isActive ? '#8B5CF6' : '#333333' }}
                />
              )}
            </button>
          )
        })}
      </div>

      {/* Panel content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'evidence' && <EvidencePanel />}
        {activeTab === 'tokens' && <TokenUsagePanel />}
        {activeTab === 'reasoning' && <CompressedReasoningPanel />}
      </div>
    </div>
  )
}
