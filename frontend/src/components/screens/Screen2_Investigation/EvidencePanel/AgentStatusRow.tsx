import { useStore } from '../../../../store'
import type { AgentStatus } from '../../../../types/investigation'

interface AgentRowProps {
  label: string
  key_: 'structural' | 'market' | 'news'
}

function statusStyle(s: AgentStatus): { icon: string; color: string } {
  if (s === 'complete') return { icon: '✓', color: '#00C27A' }
  if (s === 'fetching') return { icon: '⟳', color: '#F59E0B' }
  if (s === 'error') return { icon: '✗', color: '#FF3333' }
  return { icon: '○', color: '#333333' }
}

function AgentRow({ label, key_ }: AgentRowProps) {
  const status = useStore((s) => s.agentStatuses[key_])
  const { icon, color } = statusStyle(status)
  const isFetching = status === 'fetching'

  return (
    <div className="flex items-center gap-2 px-3 py-1.5" style={{ borderBottom: '1px solid #1C1C1C' }}>
      <span
        className="text-[9px] font-mono"
        style={{
          color,
          animation: isFetching ? 'spin 1s linear infinite' : 'none',
          display: 'inline-block',
        }}
      >
        {icon}
      </span>
      <span className="text-[9px] font-mono text-[#555555]">{label}</span>
      <span
        className="ml-auto text-[8px] font-mono uppercase tracking-widest"
        style={{ color }}
      >
        {status}
      </span>
    </div>
  )
}

export function AgentStatusRow() {
  return (
    <div>
      <div className="px-3 py-1.5" style={{ borderBottom: '1px solid #1C1C1C' }}>
        <span className="text-[8px] font-mono text-[#333333] tracking-widest">EVIDENCE AGENTS</span>
      </div>
      <AgentRow label="STRUCTURAL READER" key_="structural" />
      <AgentRow label="MARKET WATCHER" key_="market" />
      <AgentRow label="NEWS LISTENER" key_="news" />
    </div>
  )
}
