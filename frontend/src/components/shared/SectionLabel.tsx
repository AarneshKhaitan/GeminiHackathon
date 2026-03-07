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
      {accent && <div className="w-0.5 h-3" style={{ backgroundColor: accent }} />}
      <span className="text-[10px] font-terminal font-medium tracking-[0.2em] uppercase text-[#475569]">
        {children}
      </span>
    </div>
  )
}
