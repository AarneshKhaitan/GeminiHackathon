import { clsx } from 'clsx'

interface TagPillProps {
  type: 'supports' | 'contradicts' | 'neutral' | 'structural' | 'empirical' | 'critical' | 'high' | 'medium' | 'low'
  label?: string
  className?: string
}

const styles: Record<TagPillProps['type'], { color: string; bg: string; border: string }> = {
  supports:    { color: '#2E9E72', bg: '#0A2D1E', border: '#2E9E7230' },
  contradicts: { color: '#D14B35', bg: '#2A0E09', border: '#D14B3530' },
  neutral:     { color: '#8C7A5E', bg: '#1E1B15', border: '#2E2820' },
  structural:  { color: '#7C6DB8', bg: '#16103A', border: '#7C6DB830' },
  empirical:   { color: '#C8912A', bg: '#2D1E07', border: '#C8912A30' },
  critical:    { color: '#D14B35', bg: '#2A0E09', border: '#D14B3550' },
  high:        { color: '#D4651A', bg: '#2D1407', border: '#D4651A30' },
  medium:      { color: '#8C7A5E', bg: '#1E1B15', border: '#2E2820' },
  low:         { color: '#4A3D2A', bg: '#161310', border: '#2E2820' },
}

const defaultLabels: Record<TagPillProps['type'], string> = {
  supports:    'SUPPORTS',
  contradicts: 'CONTRADICTS',
  neutral:     'NEUTRAL',
  structural:  'STRUCTURAL',
  empirical:   'EMPIRICAL',
  critical:    'CRITICAL',
  high:        'HIGH',
  medium:      'MEDIUM',
  low:         'LOW',
}

export function TagPill({ type, label, className }: TagPillProps) {
  const s = styles[type]
  return (
    <span
      className={clsx('inline-flex items-center text-[8px] font-mono tracking-wider uppercase', className)}
      style={{
        color: s.color,
        backgroundColor: s.bg,
        border: `1px solid ${s.border}`,
        padding: '1px 6px',
      }}
    >
      {label ?? defaultLabels[type]}
    </span>
  )
}
