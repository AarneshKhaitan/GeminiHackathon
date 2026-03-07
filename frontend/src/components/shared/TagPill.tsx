import { clsx } from 'clsx'

interface TagPillProps {
  type: 'supports' | 'contradicts' | 'neutral' | 'structural' | 'empirical' | 'critical' | 'high' | 'medium' | 'low'
  label?: string
  className?: string
}

const styles: Record<TagPillProps['type'], { color: string; bg: string; border: string }> = {
  supports:    { color: '#00C27A', bg: '#001A0E', border: '#00C27A30' },
  contradicts: { color: '#FF3333', bg: '#1A0000', border: '#FF333330' },
  neutral:     { color: '#555555', bg: '#0A0A0A', border: '#1C1C1C' },
  structural:  { color: '#8B5CF6', bg: '#0D0020', border: '#8B5CF630' },
  empirical:   { color: '#3B82F6', bg: '#000F2D', border: '#3B82F630' },
  critical:    { color: '#FF3333', bg: '#1A0000', border: '#FF333350' },
  high:        { color: '#F59E0B', bg: '#140900', border: '#F59E0B30' },
  medium:      { color: '#555555', bg: '#0A0A0A', border: '#1C1C1C' },
  low:         { color: '#333333', bg: '#000000', border: '#1C1C1C' },
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
