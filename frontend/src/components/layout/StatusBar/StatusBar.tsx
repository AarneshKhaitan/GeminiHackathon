import { EntityBadge } from './EntityBadge'
import { TierIndicator } from './TierIndicator'
import { CycleCounter } from './CycleCounter'
import { StatusLabel } from './StatusLabel'
import { BudgetMeter } from './BudgetMeter'
import { ContextWindowBar } from './ContextWindowBar'

interface StatusBarProps {
  t3Active?: boolean
}

export function StatusBar({ t3Active }: StatusBarProps) {
  return (
    <header
      className="sticky top-0 z-50 w-full"
      style={{
        backgroundColor: '#000000',
        borderBottom: `1px solid ${t3Active ? '#FF3333' : '#1C1C1C'}`,
        transition: 'border-color 0.4s ease',
      }}
    >
      <div className="flex items-center gap-4 px-4 py-2.5">
        {/* Branding */}
        <div className="flex items-center gap-3 shrink-0">
          <div className="flex items-center gap-2">
            <div
              className="w-5 h-5 flex items-center justify-center"
              style={{ border: '1px solid #1C1C1C' }}
            >
              <span className="text-[8px] font-mono font-bold text-[#3B82F6]">IH</span>
            </div>
            <div className="flex flex-col leading-none">
              <span className="text-[8px] font-mono font-medium text-[#333333] tracking-[0.3em]">IHEE</span>
            </div>
          </div>
          <div className="w-px h-4 bg-[#1C1C1C]" />
          <EntityBadge />
        </div>

        {/* Divider */}
        <div className="w-px h-4 bg-[#1C1C1C] shrink-0" />

        {/* Status indicators */}
        <div className="flex items-center gap-5 shrink-0">
          <TierIndicator />
          <CycleCounter />
          <StatusLabel />
        </div>

        {/* Divider */}
        <div className="w-px h-4 bg-[#1C1C1C] shrink-0" />

        {/* Budget */}
        <div className="shrink-0">
          <BudgetMeter />
        </div>

        {/* Spacer */}
        <div className="flex-1 min-w-0" />

        {/* Context window bar */}
        <div className="flex items-center gap-3 w-72 shrink-0">
          <span className="text-[9px] font-mono text-[#333333] tracking-wider whitespace-nowrap">
            CTX
          </span>
          <div className="flex-1">
            <ContextWindowBar height={6} />
          </div>
        </div>

        {/* Timestamp */}
        <div className="shrink-0 text-[9px] font-mono text-[#333333] tabular-nums">
          {new Date().toLocaleTimeString('en-US', { hour12: false })}
        </div>
      </div>
    </header>
  )
}
