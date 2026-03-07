import { type ReactNode } from 'react'
import { StatusBar } from './StatusBar/StatusBar'
import { useStore } from '../../store'

interface AppShellProps {
  children: ReactNode
}

export function AppShell({ children }: AppShellProps) {
  const alertFlashActive = useStore((s) => s.alertFlashActive)

  return (
    <div
      className="flex flex-col h-screen overflow-hidden relative"
      style={{ backgroundColor: '#0F172A' }}
    >
      {/* Alert flash overlay */}
      {alertFlashActive && (
        <div
          className="absolute inset-0 pointer-events-none z-40"
          style={{ animation: 'flash-alert 0.8s ease-out forwards' }}
        />
      )}

      {/* Scanline overlay — subtle CRT effect */}
      <div
        className="absolute inset-0 pointer-events-none z-10"
        style={{
          backgroundImage:
            'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.025) 2px, rgba(0,0,0,0.025) 4px)',
        }}
      />

      <StatusBar />

      <main className="flex-1 overflow-hidden relative z-0">
        {children}
      </main>
    </div>
  )
}
