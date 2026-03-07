import { useStore } from '../../../store'
import { PulseDot } from '../../shared/PulseDot'
import type { SystemStatus } from '../../../types/investigation'

const statusConfig: Record<SystemStatus, { label: string; color: 'green' | 'red' | 'amber' | 'blue' | 'gray'; textColor: string }> = {
  IDLE: { label: 'IDLE', color: 'gray', textColor: '#475569' },
  EVALUATING: { label: 'EVALUATING', color: 'amber', textColor: '#D97706' },
  INVESTIGATING: { label: 'INVESTIGATING', color: 'blue', textColor: '#3B82F6' },
  CONVERGING: { label: 'CONVERGING', color: 'amber', textColor: '#D97706' },
  ALERT: { label: 'ALERT', color: 'red', textColor: '#EF4444' },
  ALL_CLEAR: { label: 'ALL CLEAR', color: 'green', textColor: '#10B981' },
}

export function StatusLabel() {
  const status = useStore((s) => s.systemStatus)
  const cfg = statusConfig[status]

  return (
    <div className="flex items-center gap-1.5">
      <PulseDot color={cfg.color} />
      <span
        className="text-[10px] font-terminal font-semibold tracking-[0.15em]"
        style={{ color: cfg.textColor }}
      >
        {cfg.label}
      </span>
    </div>
  )
}
