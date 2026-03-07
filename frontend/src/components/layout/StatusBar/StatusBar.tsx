import { useState, useEffect } from 'react'
import { EntityBadge } from './EntityBadge'
import { TierIndicator } from './TierIndicator'
import { CycleCounter } from './CycleCounter'
import { StatusLabel } from './StatusLabel'
import { BudgetMeter } from './BudgetMeter'
import { ContextWindowBar } from './ContextWindowBar'
import { useStore } from '../../../store'

interface StatusBarProps {
  t3Active?: boolean
}

export function StatusBar({ t3Active }: StatusBarProps) {
  const mockMode = useStore((s) => s.mockMode)
  const mockPlaybackSpeed = useStore((s) => s.mockPlaybackSpeed)
  const setMockPlaybackSpeed = useStore((s) => s.setMockPlaybackSpeed)

  const [time, setTime] = useState(() =>
    new Date().toLocaleTimeString('en-US', { hour12: false })
  )
  useEffect(() => {
    const id = setInterval(
      () => setTime(new Date().toLocaleTimeString('en-US', { hour12: false })),
      1000
    )
    return () => clearInterval(id)
  }, [])

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

        {/* Playback speed control — visible only in mock mode */}
        {mockMode && (
          <div className="flex items-center gap-1 shrink-0">
            <button
              onClick={() => setMockPlaybackSpeed(Math.max(0.25, mockPlaybackSpeed / 1.5))}
              className="text-[9px] font-mono text-[#333333] hover:text-[#555555] transition-colors px-0.5"
              style={{ cursor: 'pointer' }}
            >
              ◀
            </button>
            <span className="text-[9px] font-mono text-[#555555] tabular-nums w-8 text-center">
              {mockPlaybackSpeed.toFixed(1)}×
            </span>
            <button
              onClick={() => setMockPlaybackSpeed(Math.min(10, mockPlaybackSpeed * 1.5))}
              className="text-[9px] font-mono text-[#333333] hover:text-[#555555] transition-colors px-0.5"
              style={{ cursor: 'pointer' }}
            >
              ▶
            </button>
          </div>
        )}

        {/* Live timestamp */}
        <div className="shrink-0 text-[9px] font-mono text-[#333333] tabular-nums">
          {time}
        </div>
      </div>
    </header>
  )
}
