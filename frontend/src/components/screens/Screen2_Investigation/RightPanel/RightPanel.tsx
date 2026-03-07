import { useStore } from '../../../../store'
import { EvidencePanel } from '../EvidencePanel/EvidencePanel'
import { TokenUsagePanel } from './TokenUsagePanel'
import { CompressedReasoningPanel } from './CompressedReasoningPanel'

type Tab = 'evidence' | 'tokens' | 'reasoning'

const TABS: { id: Tab; label: string; accent: string }[] = [
  { id: 'evidence', label: 'EVIDENCE', accent: '#10B981' },
  { id: 'tokens', label: 'TOKENS', accent: '#2563EB' },
  { id: 'reasoning', label: 'REASONING', accent: '#7C3AED' },
]

export function RightPanel() {
  const activeTab = useStore((s) => s.rightPanelTab)
  const setTab = useStore((s) => s.setRightPanelTab)
  const evidenceAtoms = useStore((s) => s.evidenceAtoms)
  const tokenUsage = useStore((s) => s.tokenUsage)
  const compressedReasoning = useStore((s) => s.compressedReasoning)

  return (
    <div className="flex flex-col h-full" style={{ backgroundColor: '#0F172A' }}>
      {/* Tab bar */}
      <div
        className="flex shrink-0 border-b border-[#1E293B]"
        style={{ backgroundColor: '#0A1120' }}
      >
        {TABS.map((tab) => {
          const isActive = activeTab === tab.id
          // Badge counts
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
              className="relative flex items-center gap-1.5 px-3 py-2 text-[9px] font-terminal tracking-widest transition-colors duration-150"
              style={{
                color: isActive ? tab.accent : '#334155',
                borderBottom: isActive ? `1px solid ${tab.accent}` : '1px solid transparent',
                marginBottom: '-1px',
              }}
            >
              {tab.label}
              {badge !== null && badge > 0 && (
                <span
                  className="text-[7px] px-1 py-0.5 rounded font-terminal tabular-nums"
                  style={{
                    backgroundColor: isActive ? `${tab.accent}20` : '#1E293B',
                    color: isActive ? tab.accent : '#475569',
                  }}
                >
                  {badge}
                </span>
              )}
              {tab.id === 'reasoning' && compressedReasoning && (
                <span
                  className="w-1.5 h-1.5 rounded-full"
                  style={{ backgroundColor: isActive ? '#7C3AED' : '#334155' }}
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
