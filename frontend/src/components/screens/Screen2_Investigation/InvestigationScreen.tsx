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
      style={{ backgroundColor: '#000000' }}
    >
      {/* T3 investigation banner — tight, surgical */}
      {tier === 3 && (
        <div
          className="shrink-0 flex items-center justify-between px-4 py-1.5"
          style={{
            backgroundColor: '#050000',
            borderBottom: '1px solid #FF3333',
          }}
        >
          <div className="flex items-center gap-3">
            <span
              className="inline-block w-1.5 h-1.5"
              style={{ backgroundColor: '#FF3333', animation: 'pulse-dot 0.8s ease-in-out infinite' }}
            />
            <span className="text-[9px] font-mono font-medium tracking-widest text-[#FF3333]">
              T3 — FULL INVESTIGATION
            </span>
            <span className="text-[9px] font-mono text-[#333333]">
              4-5 deep reasoning cycles · Orchestrator + Investigator + Evidence Packager
            </span>
          </div>
          <span
            className="text-[8px] font-mono tracking-wider px-1.5 py-0.5"
            style={{ color: '#FF3333', border: '1px solid #FF333340', backgroundColor: '#FF333310' }}
          >
            CORE PRODUCT
          </span>
        </div>
      )}

      {/* Three-column grid */}
      <div className="flex-1 grid overflow-hidden" style={{ gridTemplateColumns: '196px 1fr 276px' }}>
        {/* Left: Cycle timeline */}
        <div className="overflow-hidden" style={{ borderRight: '1px solid #1C1C1C' }}>
          <CycleTimeline />
        </div>

        {/* Center: Hypothesis panel */}
        <div className="overflow-hidden" style={{ borderRight: '1px solid #1C1C1C' }}>
          <HypothesisPanel />
        </div>

        {/* Right: Tabbed panel */}
        <div className="overflow-hidden">
          <RightPanel />
        </div>
      </div>

      {/* Bottom: Context breathing chart */}
      <div className="shrink-0" style={{ borderTop: '1px solid #1C1C1C' }}>
        <ContextBreathingChart />
      </div>
    </div>
  )
}
