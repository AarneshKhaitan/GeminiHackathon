import { type ReactNode } from 'react'
import { clsx } from 'clsx'

interface SectionLabelProps {
  children: ReactNode
  className?: string
  accent?: string
}

export function SectionLabel({ children, className, accent }: SectionLabelProps) {
  return (
    <div className={clsx('flex items-center gap-2', className)}>
      {accent && (
        <div style={{ width: '2px', height: '12px', backgroundColor: accent }} />
      )}
      <span className="text-[9px] font-mono tracking-[0.2em] uppercase" style={{ color: '#8C7A5E' }}>
        {children}
      </span>
    </div>
  )
}
