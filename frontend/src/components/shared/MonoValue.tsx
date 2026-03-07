import { type ReactNode } from 'react'
import { clsx } from 'clsx'

interface MonoValueProps {
  children: ReactNode
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  color?: string
  className?: string
  dimmed?: boolean
}

const sizeClasses = {
  xs: 'text-[10px]',
  sm: 'text-xs',
  md: 'text-sm',
  lg: 'text-base',
  xl: 'text-lg',
}

export function MonoValue({ children, size = 'sm', color, className, dimmed }: MonoValueProps) {
  return (
    <span
      className={clsx(
        'font-terminal tabular-nums tracking-tight',
        sizeClasses[size],
        dimmed ? 'text-[#475569]' : (color ?? 'text-[#E2E8F0]'),
        className
      )}
    >
      {children}
    </span>
  )
}
