import { useStore } from '../../../store'
import type { SystemStatus } from '../../../types/investigation'

const statusConfig: Record<SystemStatus, { label: string; color: string }> = {
  IDLE:         { label: 'IDLE',         color: '#4A3D2A' },
  EVALUATING:   { label: 'EVALUATING',   color: '#D4651A' },
  INVESTIGATING:{ label: 'INVESTIGATING', color: '#C8912A' },
  CONVERGING:   { label: 'CONVERGING',   color: '#D4651A' },
  ALERT:        { label: 'ALERT',        color: '#D14B35' },
  ALL_CLEAR:    { label: 'ALL CLEAR',    color: '#2E9E72' },
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
