import { useStore } from '../../../store'
import { CycleTimeline } from './CycleTimeline/CycleTimeline'
import { HypothesisPanel } from './HypothesisPanel/HypothesisPanel'
import { RightPanel } from './RightPanel/RightPanel'
import { ContextBreathingChart } from './ContextBreathingChart'

export function InvestigationScreen() {
  const tier = useStore((s) => s.currentTier)

  return (
    <div
      className="flex flex-col h-full"
      style={{ backgroundColor: '#0F172A' }}
    >
      {/* T3 investigation banner */}
      {tier === 3 && (
        <div
          className="shrink-0 flex items-center justify-between px-4 py-1.5 border-b"
          style={{
            backgroundColor: '#0D0000',
            borderColor: '#EF444420',
            boxShadow: 'inset 0 -1px 0 #EF444410',
          }}
        >
          <div className="flex items-center gap-3">
            <div
              className="w-1.5 h-1.5 rounded-full"
              style={{
                backgroundColor: '#EF4444',
                boxShadow: '0 0 8px #EF4444, 0 0 3px #EF4444',
                animation: 'pulse-dot 0.8s ease-in-out infinite',
              }}
            />
            <span className="text-[9px] font-terminal font-bold tracking-widest text-[#EF4444]">
              TIER 3 — FULL INVESTIGATION
            </span>
            <span className="text-[8px] font-terminal text-[#334155]">
              4-5 deep reasoning cycles · Orchestrator + Investigator + Evidence Packager
            </span>
          </div>
          <span
            className="text-[7px] font-terminal tracking-wider px-1.5 py-0.5 rounded border"
            style={{ color: '#EF4444', borderColor: '#EF444440', backgroundColor: '#EF444410' }}
          >
            CORE PRODUCT
          </span>
        </div>
      )}

      {/* Three-column grid */}
      <div className="flex-1 grid overflow-hidden" style={{ gridTemplateColumns: '200px 1fr 280px' }}>
        {/* Left: Cycle timeline */}
        <div className="border-r border-[#1E293B] overflow-hidden">
          <CycleTimeline />
        </div>

        {/* Center: Hypothesis panel */}
        <div className="overflow-hidden border-r border-[#1E293B]">
          <HypothesisPanel />
        </div>

        {/* Right: Tabbed panel (Evidence | Tokens | Reasoning) */}
        <div className="overflow-hidden">
          <RightPanel />
        </div>
      </div>

      {/* Bottom: Context breathing chart */}
      <div className="shrink-0" style={{ backgroundColor: '#0A1120' }}>
        <ContextBreathingChart />
      </div>
    </div>
  )
}
