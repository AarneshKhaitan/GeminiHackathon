import { EntityBadge } from './EntityBadge'
import { TierIndicator } from './TierIndicator'
import { CycleCounter } from './CycleCounter'
import { StatusLabel } from './StatusLabel'
import { BudgetMeter } from './BudgetMeter'
import { ContextWindowBar } from './ContextWindowBar'

export function StatusBar() {
  return (
    <header
      className="sticky top-0 z-50 w-full border-b border-[#1E293B]"
      style={{ backgroundColor: '#0A1120' }}
    >
      {/* Main row */}
      <div className="flex items-center gap-4 px-4 py-2.5">
        {/* Left: Branding */}
        <div className="flex items-center gap-3 min-w-0 shrink-0">
          <div className="flex items-center gap-1.5">
            {/* IHEE logo mark */}
            <div className="w-6 h-6 flex items-center justify-center rounded border border-[#2563EB]/40 bg-[#1E293B]">
              <span className="text-[8px] font-terminal font-bold text-[#2563EB]">IH</span>
            </div>
            <div className="flex flex-col leading-none">
              <span className="text-[8px] font-terminal text-[#334155] tracking-[0.25em]">IHEE</span>
              <span className="text-[7px] font-terminal text-[#273548] tracking-[0.15em]">HYPOTHESIS ENGINE</span>
            </div>
          </div>
          <div className="w-px h-5 bg-[#1E293B]" />
          <EntityBadge />
        </div>

        {/* Divider */}
        <div className="w-px h-5 bg-[#1E293B] shrink-0" />

        {/* Center: Status indicators */}
        <div className="flex items-center gap-4 shrink-0">
          <TierIndicator />
          <CycleCounter />
          <StatusLabel />
        </div>

        {/* Divider */}
        <div className="w-px h-5 bg-[#1E293B] shrink-0" />

        {/* Budget */}
        <div className="shrink-0">
          <BudgetMeter />
        </div>

        {/* Spacer */}
        <div className="flex-1 min-w-0" />

        {/* Right: Context window bar (the signature) */}
        <div className="flex items-center gap-2 w-72 shrink-0">
          <span className="text-[9px] font-terminal text-[#273548] tracking-wider whitespace-nowrap">
            CTX WINDOW
          </span>
          <div className="flex-1">
            <ContextWindowBar height={8} />
          </div>
        </div>

        {/* Timestamp */}
        <div className="shrink-0 text-[9px] font-terminal text-[#273548]">
          {new Date().toLocaleTimeString('en-US', { hour12: false })}
        </div>
      </div>

      {/* Bottom micro-bar: scanning animation */}
      <div className="h-px w-full bg-[#1E293B] relative overflow-hidden">
        <div
          className="absolute top-0 left-0 h-full w-24 opacity-60"
          style={{
            background: 'linear-gradient(90deg, transparent, #2563EB, transparent)',
            animation: 'scan-line 3s linear infinite',
          }}
        />
      </div>
    </header>
  )
}
