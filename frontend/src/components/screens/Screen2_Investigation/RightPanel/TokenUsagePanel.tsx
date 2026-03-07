import { useStore } from '../../../../store'
import { MonoValue } from '../../../shared/MonoValue'
import { SectionLabel } from '../../../shared/SectionLabel'

function fmt(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(2)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return String(n)
}

interface AgentBarProps {
  label: string
  abbrev: string
  color: string
  dimColor: string
  input: number
  reasoning: number
  output: number
  calls: number
  maxTotal: number
}

function AgentBar({ label, abbrev, color, dimColor, input, reasoning, output, calls, maxTotal }: AgentBarProps) {
  const total = input + reasoning + output
  const pct = maxTotal > 0 ? (total / maxTotal) * 100 : 0

  return (
    <div className="space-y-1.5 p-2.5 rounded border border-[#1E293B]" style={{ backgroundColor: '#0A1120' }}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div
            className="w-1.5 h-1.5 rounded-full"
            style={{ backgroundColor: color }}
          />
          <span className="text-[9px] font-terminal tracking-widest" style={{ color }}>
            {abbrev}
          </span>
          <span className="text-[9px] font-terminal text-[#475569] tracking-wider">
            {label}
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <MonoValue color="#475569" size="xs">{calls}</MonoValue>
          <span className="text-[8px] font-terminal text-[#334155]">CALLS</span>
        </div>
      </div>

      {/* Fill bar */}
      <div className="relative h-1.5 w-full rounded-full overflow-hidden bg-[#1E293B]">
        <div
          className="absolute top-0 left-0 h-full transition-all duration-700 ease-out"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>

      {/* Token breakdown */}
      <div className="grid grid-cols-3 gap-1">
        {input > 0 && (
          <div className="flex flex-col">
            <MonoValue color={dimColor} size="xs">{fmt(input)}</MonoValue>
            <span className="text-[7px] font-terminal text-[#334155]">INPUT</span>
          </div>
        )}
        {reasoning > 0 && (
          <div className="flex flex-col">
            <MonoValue color={color} size="xs">{fmt(reasoning)}</MonoValue>
            <span className="text-[7px] font-terminal text-[#334155]">REASONING</span>
          </div>
        )}
        {output > 0 && (
          <div className="flex flex-col">
            <MonoValue color={dimColor} size="xs">{fmt(output)}</MonoValue>
            <span className="text-[7px] font-terminal text-[#334155]">OUTPUT</span>
          </div>
        )}
        <div className="flex flex-col">
          <MonoValue color="#E2E8F0" size="xs">{fmt(total)}</MonoValue>
          <span className="text-[7px] font-terminal text-[#334155]">TOTAL</span>
        </div>
      </div>
    </div>
  )
}

export function TokenUsagePanel() {
  const usage = useStore((s) => s.tokenUsage)
  const { orchestrator, investigator, evidencePackager } = usage.byAgent
  const byCycle = usage.byCycle

  const maxAgentTotal = Math.max(
    orchestrator.totalInput + orchestrator.totalOutput + orchestrator.totalReasoning,
    investigator.totalInput + investigator.totalOutput + investigator.totalReasoning,
    evidencePackager.totalInput + evidencePackager.totalOutput + evidencePackager.totalReasoning,
    1
  )

  return (
    <div className="flex flex-col h-full p-3 gap-3 overflow-y-auto">
      <SectionLabel accent="#2563EB">TOKEN USAGE</SectionLabel>

      {/* Grand totals */}
      <div className="grid grid-cols-3 gap-1 p-2 rounded border border-[#1E293B] bg-[#0A1120]">
        <div className="flex flex-col items-center">
          <MonoValue color="#60A5FA" size="sm">{fmt(usage.totalInput)}</MonoValue>
          <span className="text-[7px] font-terminal text-[#334155] tracking-wider">INPUT</span>
        </div>
        <div className="flex flex-col items-center">
          <MonoValue color="#A78BFA" size="sm">{fmt(usage.totalReasoning)}</MonoValue>
          <span className="text-[7px] font-terminal text-[#334155] tracking-wider">REASONING</span>
        </div>
        <div className="flex flex-col items-center">
          <MonoValue color="#E2E8F0" size="sm">{fmt(usage.totalInput + usage.totalReasoning + usage.totalOutput)}</MonoValue>
          <span className="text-[7px] font-terminal text-[#334155] tracking-wider">TOTAL</span>
        </div>
      </div>

      {/* Per-agent breakdown */}
      <div className="space-y-2">
        <span className="text-[8px] font-terminal text-[#334155] tracking-widest">BY AGENT</span>

        <AgentBar
          label="ORCHESTRATOR"
          abbrev="ORC"
          color="#3B82F6"
          dimColor="#60A5FA"
          input={orchestrator.totalInput}
          reasoning={orchestrator.totalReasoning}
          output={orchestrator.totalOutput}
          calls={orchestrator.geminiCalls}
          maxTotal={maxAgentTotal}
        />
        <AgentBar
          label="INVESTIGATOR"
          abbrev="INV"
          color="#10B981"
          dimColor="#6EE7B7"
          input={investigator.totalInput}
          reasoning={investigator.totalReasoning}
          output={investigator.totalOutput}
          calls={investigator.geminiCalls}
          maxTotal={maxAgentTotal}
        />
        <AgentBar
          label="PACKAGER"
          abbrev="PKG"
          color="#8B5CF6"
          dimColor="#C4B5FD"
          input={evidencePackager.totalInput}
          reasoning={evidencePackager.totalReasoning}
          output={evidencePackager.totalOutput}
          calls={evidencePackager.geminiCalls}
          maxTotal={maxAgentTotal}
        />
      </div>

      {/* Per-cycle breakdown */}
      {byCycle.length > 0 && (
        <div className="space-y-1.5">
          <span className="text-[8px] font-terminal text-[#334155] tracking-widest">BY CYCLE</span>

          {byCycle.map((c) => {
            const cycleMax = Math.max(
              c.investigatorInput + c.investigatorReasoning,
              c.packagerInput + c.packagerTagging,
              1
            )
            return (
              <div key={c.cycle} className="p-2 rounded border border-[#1E293B]" style={{ backgroundColor: '#0A1120' }}>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[8px] font-terminal text-[#475569] tracking-wider">
                    CYCLE {c.cycle}
                  </span>
                  {c.orchestratorGemini && (
                    <span className="text-[7px] font-terminal text-[#3B82F6]">ORC ●</span>
                  )}
                </div>

                {/* Investigator row */}
                <div className="mb-1">
                  <div className="flex items-center justify-between mb-0.5">
                    <span className="text-[7px] font-terminal text-[#10B981]">INV</span>
                    <span className="text-[7px] font-terminal text-[#334155]">
                      {fmt(c.investigatorInput + c.investigatorReasoning)}
                    </span>
                  </div>
                  <div className="relative h-1 w-full rounded-full overflow-hidden bg-[#1E293B]">
                    <div
                      className="absolute top-0 left-0 h-full bg-[#10B981]/40"
                      style={{ width: `${(c.investigatorInput / cycleMax) * 100}%` }}
                    />
                    <div
                      className="absolute top-0 h-full bg-[#10B981]"
                      style={{
                        left: `${(c.investigatorInput / cycleMax) * 100}%`,
                        width: `${(c.investigatorReasoning / cycleMax) * 100}%`,
                      }}
                    />
                  </div>
                </div>

                {/* Packager row */}
                <div>
                  <div className="flex items-center justify-between mb-0.5">
                    <span className="text-[7px] font-terminal text-[#8B5CF6]">PKG</span>
                    <span className="text-[7px] font-terminal text-[#334155]">
                      {fmt(c.packagerInput + c.packagerTagging)}
                    </span>
                  </div>
                  <div className="relative h-1 w-full rounded-full overflow-hidden bg-[#1E293B]">
                    <div
                      className="absolute top-0 left-0 h-full bg-[#8B5CF6]/40"
                      style={{ width: `${(c.packagerInput / cycleMax) * 100}%` }}
                    />
                    <div
                      className="absolute top-0 h-full bg-[#8B5CF6]"
                      style={{
                        left: `${(c.packagerInput / cycleMax) * 100}%`,
                        width: `${(c.packagerTagging / cycleMax) * 100}%`,
                      }}
                    />
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {byCycle.length === 0 && (
        <div className="flex flex-col items-center justify-center h-24 gap-1">
          <span className="text-[#1E293B] text-xl">▒</span>
          <span className="text-[9px] font-terminal text-[#1E293B] tracking-wider">
            NO CYCLE DATA
          </span>
        </div>
      )}
    </div>
  )
}
