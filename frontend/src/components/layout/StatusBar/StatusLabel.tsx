import { useStore } from '../../../store'
import type { SystemStatus } from '../../../types/investigation'

const statusConfig: Record<SystemStatus, { label: string; color: string }> = {
  IDLE:         { label: 'IDLE',         color: '#333333' },
  EVALUATING:   { label: 'EVALUATING',   color: '#F59E0B' },
  INVESTIGATING:{ label: 'INVESTIGATING', color: '#3B82F6' },
  CONVERGING:   { label: 'CONVERGING',   color: '#F59E0B' },
  ALERT:        { label: 'ALERT',        color: '#FF3333' },
  ALL_CLEAR:    { label: 'ALL CLEAR',    color: '#00C27A' },
}

export function StatusLabel() {
  const status = useStore((s) => s.systemStatus)
  const cfg = statusConfig[status]

  return (
    <div className="flex items-center gap-1.5">
      <span
        className="inline-block w-1.5 h-1.5"
        style={{
          backgroundColor: cfg.color,
          animation: 'pulse-dot 1.5s ease-in-out infinite',
        }}
      />
      <span
        className="text-[9px] font-mono font-medium tracking-[0.12em]"
        style={{ color: cfg.color }}
      >
        {cfg.label}
      </span>
    </div>
  )
}
