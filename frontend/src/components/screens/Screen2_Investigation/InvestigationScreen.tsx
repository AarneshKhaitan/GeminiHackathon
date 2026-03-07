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
      style={{ backgroundColor: '#0C0A07' }}
    >
      {/* T3 investigation banner — tight, surgical */}
      {tier === 3 && (
        <div
          className="shrink-0 flex items-center justify-between px-4 py-1.5"
          style={{
            background: 'linear-gradient(135deg, #2A0E09 0%, #161310 100%)',
            borderBottom: '1px solid #D14B35',
            boxShadow: '0 4px 24px rgba(209,75,53,0.15)',
          }}
        >
          <div className="flex items-center gap-3">
            <span
              className="inline-block w-1.5 h-1.5"
              style={{ backgroundColor: '#D14B35', animation: 'pulse-dot 0.8s ease-in-out infinite' }}
            />
            <span
              className="text-[9px] tracking-widest font-medium"
              style={{ fontFamily: 'Syne, sans-serif', color: '#D14B35' }}
            >
              DEEP INVESTIGATION
            </span>
            <span className="text-[9px] font-mono" style={{ color: '#8C7A5E' }}>
              Generating hypotheses · Scoring against evidence · Eliminating what's structurally impossible
            </span>
          </div>
          <span
            className="text-[8px] font-mono tracking-wider px-1.5 py-0.5"
            style={{ color: '#D14B35', border: '1px solid #D14B3540', backgroundColor: '#D14B3510' }}
          >
            CORE PRODUCT
          </span>
        </div>
      )}

      {/* Three-column grid */}
      <div className="flex-1 grid overflow-hidden" style={{ gridTemplateColumns: '196px 1fr 276px' }}>
        {/* Left: Cycle timeline */}
        <div className="overflow-hidden" style={{ borderRight: '1px solid #2E2820' }}>
          <CycleTimeline />
        </div>

        {/* Center: Hypothesis panel */}
        <div className="overflow-hidden" style={{ borderRight: '1px solid #2E2820' }}>
          <HypothesisPanel />
        </div>

        {/* Right: Tabbed panel */}
        <div className="overflow-hidden">
          <RightPanel />
        </div>
      </div>

      {/* Bottom: Context breathing chart */}
      <div className="shrink-0" style={{ borderTop: '1px solid #2E2820' }}>
        <ContextBreathingChart />
      </div>
    </div>
  )
}
