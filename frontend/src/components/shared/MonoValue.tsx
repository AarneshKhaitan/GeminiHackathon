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
      className={clsx('font-mono tabular-nums', sizeClasses[size], className)}
      style={{ color: dimmed ? '#333333' : (color ?? '#E8E8E8') }}
    >
      {children}
    </span>
  )
}
