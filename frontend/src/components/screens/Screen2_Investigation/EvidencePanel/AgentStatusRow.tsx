import { useStore } from '../../../../store'
import type { AgentStatus } from '../../../../types/investigation'

interface AgentRowProps {
  label: string
  key_: 'structural' | 'market' | 'news'
}

function statusIcon(s: AgentStatus) {
  if (s === 'complete') return { icon: '✓', color: '#059669' }
  if (s === 'fetching') return { icon: '⟳', color: '#D97706' }
  if (s === 'error') return { icon: '✗', color: '#DC2626' }
  return { icon: '○', color: '#334155' }
}

function AgentRow({ label, key_ }: AgentRowProps) {
  const status = useStore((s) => s.agentStatuses[key_])
  const { icon, color } = statusIcon(status)
  const isFetching = status === 'fetching'

  return (
    <div className="flex items-center gap-2 py-1">
      <span
        className="text-[11px] font-terminal"
        style={{
          color,
          animation: isFetching ? 'spin 1s linear infinite' : 'none',
          display: 'inline-block',
        }}
      >
        {icon}
      </span>
      <span className="text-[10px] font-terminal text-[#475569] tracking-wider">{label}</span>
      <span
        className="ml-auto text-[9px] font-terminal uppercase tracking-widest"
        style={{ color }}
      >
        {status}
      </span>
    </div>
  )
}

export function AgentStatusRow() {
  return (
    <div className="rounded border border-[#1E293B] bg-[#0D1526] p-2">
      <div className="text-[9px] font-terminal text-[#273548] tracking-widest mb-2">
        EVIDENCE AGENTS
      </div>
      <AgentRow label="STRUCTURAL READER" key_="structural" />
      <div className="h-px bg-[#1E293B]" />
      <AgentRow label="MARKET WATCHER" key_="market" />
      <div className="h-px bg-[#1E293B]" />
      <AgentRow label="NEWS LISTENER" key_="news" />
    </div>
  )
}
