import { clsx } from 'clsx'

interface PulseDotProps {
  color?: 'green' | 'red' | 'amber' | 'blue' | 'gray'
  size?: 'sm' | 'md'
  className?: string
}

const colorMap = {
  green: '#00C27A',
  red:   '#FF3333',
  amber: '#F59E0B',
  blue:  '#3B82F6',
  gray:  '#333333',
}

const sizeMap = {
  sm: '6px',
  md: '8px',
}

export function PulseDot({ color = 'green', size = 'sm', className }: PulseDotProps) {
  return (
    <span
      className={clsx('inline-block', className)}
      style={{
        width: sizeMap[size],
        height: sizeMap[size],
        backgroundColor: colorMap[color],
        animation: 'pulse-dot 1.5s ease-in-out infinite',
      }}
    />
  )
}
