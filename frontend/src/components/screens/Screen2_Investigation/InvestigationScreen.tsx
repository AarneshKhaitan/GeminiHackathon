import { CycleTimeline } from './CycleTimeline/CycleTimeline'
import { HypothesisPanel } from './HypothesisPanel/HypothesisPanel'
import { EvidencePanel } from './EvidencePanel/EvidencePanel'
import { ContextBreathingChart } from './ContextBreathingChart'

export function InvestigationScreen() {
  return (
    <div
      className="flex flex-col h-full"
      style={{ backgroundColor: '#0F172A' }}
    >
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

        {/* Right: Evidence panel */}
        <div className="overflow-hidden">
          <EvidencePanel />
        </div>
      </div>

      {/* Bottom: Context breathing chart */}
      <div className="shrink-0" style={{ backgroundColor: '#0A1120' }}>
        <ContextBreathingChart />
      </div>
    </div>
  )
}
