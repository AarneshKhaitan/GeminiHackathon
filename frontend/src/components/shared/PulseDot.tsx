import { clsx } from 'clsx'

interface PulseDotProps {
  color?: 'green' | 'red' | 'amber' | 'blue' | 'gray'
  size?: 'sm' | 'md'
  className?: string
}

const colorClasses = {
  green: 'bg-[#059669]',
  red: 'bg-[#DC2626]',
  amber: 'bg-[#D97706]',
  blue: 'bg-[#2563EB]',
  gray: 'bg-[#475569]',
}

const sizeClasses = {
  sm: 'w-1.5 h-1.5',
  md: 'w-2 h-2',
}

export function PulseDot({ color = 'green', size = 'sm', className }: PulseDotProps) {
  return (
    <span
      className={clsx(
        'inline-block rounded-full',
        colorClasses[color],
        sizeClasses[size],
        'animate-[pulse-dot_1.5s_ease-in-out_infinite]',
        className
      )}
    />
  )
}
