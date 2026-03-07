import { type ReactNode } from 'react'
import { StatusBar } from './StatusBar/StatusBar'
import { useStore } from '../../store'
import type { TierLevel } from '../../types/investigation'

interface AppShellProps {
  children: ReactNode
  tierActive?: TierLevel | null
}

export function AppShell({ children, tierActive }: AppShellProps) {
  const alertFlashActive = useStore((s) => s.alertFlashActive)

  return (
    <div
      className="flex flex-col h-screen overflow-hidden relative"
      style={{ backgroundColor: '#000000' }}
    >
      {/* Alert flash overlay — functional only */}
      {alertFlashActive && (
        <div
          className="absolute inset-0 pointer-events-none z-40"
          style={{ animation: 'flash-alert 0.8s ease-out forwards' }}
        />
      )}

      <StatusBar t3Active={tierActive === 3} />

      <main className="flex-1 overflow-hidden relative z-0">
        {children}
      </main>
    </div>
  )
}
