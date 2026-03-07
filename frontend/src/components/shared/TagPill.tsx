import { clsx } from 'clsx'

interface TagPillProps {
  type: 'supports' | 'contradicts' | 'neutral' | 'structural' | 'empirical' | 'critical' | 'high' | 'medium' | 'low'
  label?: string
  className?: string
}

const styles = {
  supports: 'bg-[#064E3B] text-[#6EE7B7] border border-[#059669]/30',
  contradicts: 'bg-[#7F1D1D] text-[#FCA5A5] border border-[#DC2626]/30',
  neutral: 'bg-[#1E293B] text-[#94A3B8] border border-[#334155]',
  structural: 'bg-[#1E1B4B] text-[#A5B4FC] border border-[#4F46E5]/30',
  empirical: 'bg-[#0C2340] text-[#7DD3FC] border border-[#0369A1]/30',
  critical: 'bg-[#7F1D1D] text-[#FCA5A5] border border-[#DC2626]/50',
  high: 'bg-[#78350F] text-[#FCD34D] border border-[#D97706]/30',
  medium: 'bg-[#1E293B] text-[#94A3B8] border border-[#334155]',
  low: 'bg-[#1E293B] text-[#475569] border border-[#273548]',
}

const defaultLabels = {
  supports: 'SUPPORTS',
  contradicts: 'CONTRADICTS',
  neutral: 'NEUTRAL',
  structural: 'STRUCTURAL',
  empirical: 'EMPIRICAL',
  critical: 'CRITICAL',
  high: 'HIGH',
  medium: 'MEDIUM',
  low: 'LOW',
}

export function TagPill({ type, label, className }: TagPillProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-terminal font-medium tracking-wider uppercase',
        styles[type],
        className
      )}
    >
      {label ?? defaultLabels[type]}
    </span>
  )
}
