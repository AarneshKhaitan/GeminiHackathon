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
      {/* Tier phase banner */}
      {tier && (
        <div
          className="shrink-0 flex items-center justify-between px-4 py-1.5 border-b"
          style={{
            backgroundColor: tier === 4 ? '#12000A' : '#0A0800',
            borderColor: tier === 4 ? '#EF444420' : '#F9731615',
          }}
        >
          <div className="flex items-center gap-3">
            <div
              className="w-1.5 h-1.5 rounded-full"
              style={{
                backgroundColor: tier === 4 ? '#EF4444' : '#F97316',
                boxShadow: `0 0 6px ${tier === 4 ? '#EF4444' : '#F97316'}`,
                animation: 'pulse-dot 1s ease-in-out infinite',
              }}
            />
            <span
              className="text-[9px] font-terminal font-bold tracking-widest"
              style={{ color: tier === 4 ? '#EF4444' : '#F97316' }}
            >
              {tier === 4 ? 'TIER 4 — FULL INVESTIGATION' : 'TIER 3 — INITIAL INVESTIGATION'}
            </span>
            <span className="text-[8px] font-terminal text-[#334155]">
              {tier === 4
                ? '4-5 deep reasoning cycles · Orchestrator + Investigator + Evidence Packager'
                : '1-2 quick cycles · Determines whether to promote to Tier 4 full investigation'}
            </span>
          </div>
          {tier === 3 && (
            <span className="text-[8px] font-terminal text-[#473409] tracking-wider">
              PROMOTE → T4 IF WARRANTED
            </span>
          )}
          {tier === 4 && (
            <span
              className="text-[8px] font-terminal tracking-wider px-2 py-0.5 rounded border"
              style={{ color: '#EF4444', borderColor: '#EF444430', backgroundColor: '#EF444408' }}
            >
              CORE PRODUCT
            </span>
          )}
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
