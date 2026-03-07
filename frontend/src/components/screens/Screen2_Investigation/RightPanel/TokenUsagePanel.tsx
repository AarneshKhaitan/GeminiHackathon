import { useStore } from '../../../../store'
import { MonoValue } from '../../../shared/MonoValue'
import { fmt } from '../../../../utils/format'

interface AgentBarProps {
  label: string
  abbrev: string
  color: string
  input: number
  reasoning: number
  output: number
  calls: number
  maxTotal: number
}

function AgentBar({ label, abbrev, color, input, reasoning, output, calls, maxTotal }: AgentBarProps) {
  const total = input + reasoning + output
  const pct = maxTotal > 0 ? (total / maxTotal) * 100 : 0

  return (
    <div
      className="p-2.5"
      style={{ borderBottom: '1px solid #2E2820' }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-1.5">
        <div className="flex items-center gap-2">
          <div className="inline-block w-1.5 h-1.5" style={{ backgroundColor: color }} />
          <span className="text-[9px] font-mono tracking-widest" style={{ color }}>{abbrev}</span>
          <span className="text-[9px] font-mono" style={{ color: '#8C7A5E' }}>{label}</span>
        </div>
        <div className="flex items-center gap-1">
          <MonoValue color="#8C7A5E" size="xs">{calls}</MonoValue>
          <span className="text-[7px] font-mono" style={{ color: '#4A3D2A' }}>CALLS</span>
        </div>
      </div>

      {/* Fill bar */}
      <div className="relative h-px w-full overflow-hidden" style={{ backgroundColor: '#2E2820' }}>
        <div
          className="absolute top-0 left-0 h-full transition-all duration-700 ease-out"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>

      {/* Token breakdown */}
      <div className="mt-1.5 flex gap-4">
        {input > 0 && (
          <div>
            <MonoValue color="#8C7A5E" size="xs">{fmt(input)}</MonoValue>
            <div className="text-[7px] font-mono" style={{ color: '#4A3D2A' }}>INPUT</div>
          </div>
        )}
        {reasoning > 0 && (
          <div>
            <MonoValue color={color} size="xs">{fmt(reasoning)}</MonoValue>
            <div className="text-[7px] font-mono" style={{ color: '#4A3D2A' }}>REASONING</div>
          </div>
        )}
        {output > 0 && (
          <div>
            <MonoValue color="#8C7A5E" size="xs">{fmt(output)}</MonoValue>
            <div className="text-[7px] font-mono" style={{ color: '#4A3D2A' }}>OUTPUT</div>
          </div>
        )}
        <div>
          <MonoValue color="#EDE4D4" size="xs">{fmt(total)}</MonoValue>
          <div className="text-[7px] font-mono" style={{ color: '#4A3D2A' }}>TOTAL</div>
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
    <div className="flex flex-col h-full overflow-y-auto" style={{ backgroundColor: '#161310' }}>
      {/* Header */}
      <div
        className="shrink-0 px-3 py-2 flex items-center gap-2"
        style={{ borderBottom: '1px solid #2E2820', backgroundColor: '#161310' }}
      >
        <div style={{ width: '2px', height: '12px', backgroundColor: '#C8912A' }} />
        <span
          className="text-[9px] tracking-[0.2em]"
          style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, color: '#8C7A5E' }}
        >TOKEN USAGE</span>
      </div>

      {/* Grand totals */}
      <div className="grid grid-cols-3" style={{ borderBottom: '1px solid #2E2820' }}>
        <div className="px-3 py-2 flex flex-col" style={{ borderRight: '1px solid #2E2820' }}>
          <MonoValue color="#C8912A" size="sm">{fmt(usage.totalInput)}</MonoValue>
          <span className="text-[7px] font-mono tracking-wider" style={{ color: '#4A3D2A' }}>INPUT</span>
        </div>
        <div className="px-3 py-2 flex flex-col" style={{ borderRight: '1px solid #2E2820' }}>
          <MonoValue color="#7C6DB8" size="sm">{fmt(usage.totalReasoning)}</MonoValue>
          <span className="text-[7px] font-mono tracking-wider" style={{ color: '#4A3D2A' }}>REASONING</span>
        </div>
        <div className="px-3 py-2 flex flex-col">
          <MonoValue color="#EDE4D4" size="sm">{fmt(usage.totalInput + usage.totalReasoning + usage.totalOutput)}</MonoValue>
          <span className="text-[7px] font-mono tracking-wider" style={{ color: '#4A3D2A' }}>TOTAL</span>
        </div>
      </div>

      {/* By-agent label */}
      <div className="px-3 py-1.5" style={{ borderBottom: '1px solid #2E2820' }}>
        <span className="text-[8px] font-mono tracking-widest" style={{ color: '#4A3D2A' }}>BY AGENT</span>
      </div>

      {/* Per-agent breakdown */}
      <AgentBar
        label="ORCHESTRATOR"
        abbrev="ORC"
        color="#C8912A"
        input={orchestrator.totalInput}
        reasoning={orchestrator.totalReasoning}
        output={orchestrator.totalOutput}
        calls={orchestrator.geminiCalls}
        maxTotal={maxAgentTotal}
      />
      <AgentBar
        label="INVESTIGATOR"
        abbrev="INV"
        color="#2E9E72"
        input={investigator.totalInput}
        reasoning={investigator.totalReasoning}
        output={investigator.totalOutput}
        calls={investigator.geminiCalls}
        maxTotal={maxAgentTotal}
      />
      <AgentBar
        label="PACKAGER"
        abbrev="PKG"
        color="#7C6DB8"
        input={evidencePackager.totalInput}
        reasoning={evidencePackager.totalReasoning}
        output={evidencePackager.totalOutput}
        calls={evidencePackager.geminiCalls}
        maxTotal={maxAgentTotal}
      />

      {/* Per-cycle breakdown */}
      {byCycle.length > 0 && (
        <>
          <div className="px-3 py-1.5" style={{ borderBottom: '1px solid #2E2820' }}>
            <span className="text-[8px] font-mono tracking-widest" style={{ color: '#4A3D2A' }}>BY CYCLE</span>
          </div>

          {byCycle.map((c) => {
            const cycleMax = Math.max(
              c.investigatorInput + c.investigatorReasoning,
              c.packagerInput + c.packagerTagging,
              1
            )
            return (
              <div key={c.cycle} className="px-3 py-2" style={{ borderBottom: '1px solid #2E2820' }}>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[8px] font-mono tracking-wider" style={{ color: '#8C7A5E' }}>
                    CYCLE {c.cycle}
                  </span>
                  {c.orchestratorGemini && (
                    <span className="text-[7px] font-mono" style={{ color: '#C8912A' }}>ORC ●</span>
                  )}
                </div>

                {/* Investigator row */}
                <div className="mb-1.5">
                  <div className="flex items-center justify-between mb-0.5">
                    <span className="text-[7px] font-mono" style={{ color: '#2E9E72' }}>INV</span>
                    <span className="text-[7px] font-mono" style={{ color: '#4A3D2A' }}>
                      {fmt(c.investigatorInput + c.investigatorReasoning)}
                    </span>
                  </div>
                  <div className="relative h-px w-full overflow-hidden" style={{ backgroundColor: '#2E2820' }}>
                    <div
                      className="absolute top-0 left-0 h-full"
                      style={{ width: `${(c.investigatorInput / cycleMax) * 100}%`, backgroundColor: '#2E9E7240' }}
                    />
                    <div
                      className="absolute top-0 h-full"
                      style={{
                        left: `${(c.investigatorInput / cycleMax) * 100}%`,
                        width: `${(c.investigatorReasoning / cycleMax) * 100}%`,
                        backgroundColor: '#2E9E72',
                      }}
                    />
                  </div>
                </div>

                {/* Packager row */}
                <div>
                  <div className="flex items-center justify-between mb-0.5">
                    <span className="text-[7px] font-mono" style={{ color: '#7C6DB8' }}>PKG</span>
                    <span className="text-[7px] font-mono" style={{ color: '#4A3D2A' }}>
                      {fmt(c.packagerInput + c.packagerTagging)}
                    </span>
                  </div>
                  <div className="relative h-px w-full overflow-hidden" style={{ backgroundColor: '#2E2820' }}>
                    <div
                      className="absolute top-0 left-0 h-full"
                      style={{ width: `${(c.packagerInput / cycleMax) * 100}%`, backgroundColor: '#7C6DB840' }}
                    />
                    <div
                      className="absolute top-0 h-full"
                      style={{
                        left: `${(c.packagerInput / cycleMax) * 100}%`,
                        width: `${(c.packagerTagging / cycleMax) * 100}%`,
                        backgroundColor: '#7C6DB8',
                      }}
                    />
                  </div>
                </div>
              </div>
            )
          })}
        </>
      )}

      {byCycle.length === 0 && (
        <div className="flex flex-col items-center justify-center h-24 gap-1">
          <span className="text-[9px] font-mono tracking-wider" style={{ color: '#4A3D2A' }}>NO CYCLE DATA</span>
        </div>
      )}
    </div>
  )
}
