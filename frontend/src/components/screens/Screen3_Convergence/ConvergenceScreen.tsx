import { motion, AnimatePresence } from 'framer-motion'
import { useStore } from '../../../store'
import { MonoValue } from '../../shared/MonoValue'
import { TagPill } from '../../shared/TagPill'
import { SectionLabel } from '../../shared/SectionLabel'
import { ContextWindowBar } from '../../layout/StatusBar/ContextWindowBar'
import { SurvivingCard } from '../Screen2_Investigation/HypothesisPanel/SurvivingCard'

export function ConvergenceScreen() {
  const alertDiagnosis = useStore((s) => s.alertDiagnosis)
  const contagionTargets = useStore((s) => s.contagionTargets)
  const hypotheses = useStore((s) => s.hypotheses)
  const cycles = useStore((s) => s.cycles)
  const allCycleSnapshots = useStore((s) => s.allCycleSnapshots)

  const survivingHypotheses = hypotheses.filter(
    (h) => h.status === 'surviving' || h.status === 'contradiction'
  )
  const allEliminations = hypotheses
    .filter((h) => h.status === 'eliminated')
    .sort((a, b) => (a.eliminatedInCycle ?? 0) - (b.eliminatedInCycle ?? 0))

  const totalReasoningTokens = allCycleSnapshots.reduce(
    (acc, s) => acc + s.reasoningTokens,
    0
  )
  const totalEvidenceTokens = allCycleSnapshots.reduce(
    (acc, s) => acc + s.evidenceTokens,
    0
  )

  if (!alertDiagnosis) {
    return (
      <div className="h-full flex items-center justify-center">
        <span className="text-[#273548] font-terminal text-sm">AWAITING CONVERGENCE...</span>
      </div>
    )
  }

  return (
    <div
      className="h-full overflow-y-auto"
      style={{ backgroundColor: '#0F172A' }}
    >
      {/* Alert banner */}
      <motion.div
        initial={{ y: -80, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        className="sticky top-0 z-10 w-full px-6 py-3 flex items-center gap-4"
        style={{
          backgroundColor: '#450A0A',
          borderBottom: '1px solid #991B1B',
          boxShadow: '0 4px 24px #DC262630',
        }}
      >
        <span className="text-[#DC2626] text-xl">⚠</span>
        <div className="flex-1 min-w-0">
          <div className="text-[9px] font-terminal text-[#DC2626] tracking-[0.25em] mb-0.5">
            CRITICAL RISK ALERT — DIAGNOSIS CONVERGENCE REACHED
          </div>
          <p className="text-sm font-display font-bold text-[#FCA5A5] leading-snug truncate">
            {alertDiagnosis.headline}
          </p>
        </div>
        <div className="shrink-0">
          <TagPill type="critical" label="TIER 4 ALERT" />
        </div>
      </motion.div>

      {/* Body */}
      <div className="p-6 grid gap-6" style={{ gridTemplateColumns: '1fr 1fr', gridTemplateRows: 'auto' }}>

        {/* Full diagnosis */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.3 }}
          className="col-span-2 rounded border border-[#991B1B]/20 p-4"
          style={{ backgroundColor: '#0A0606' }}
        >
          <SectionLabel accent="#DC2626" className="mb-3">ITERATIVE DIAGNOSIS</SectionLabel>
          <p className="text-[11px] font-evidence text-[#94A3B8] leading-relaxed mb-4">
            {alertDiagnosis.iterativeDiagnosis}
          </p>

          {/* Single-pass vs iterative comparison */}
          <div className="grid grid-cols-2 gap-4">
            <div className="rounded border border-[#1E293B] p-3" style={{ backgroundColor: '#0D1526' }}>
              <div className="text-[9px] font-terminal text-[#334155] tracking-wider mb-2">
                SINGLE-PASS ANALYSIS
              </div>
              <p className="text-[10px] font-evidence text-[#334155] leading-relaxed italic">
                "{alertDiagnosis.singlePassSummary}"
              </p>
              <div className="mt-2 text-[8px] font-terminal text-[#273548]">
                Generic pattern-matching output
              </div>
            </div>
            <div className="rounded border border-[#059669]/20 p-3" style={{ backgroundColor: '#041009' }}>
              <div className="text-[9px] font-terminal text-[#059669] tracking-wider mb-2">
                ITERATIVE HYPOTHESIS ELIMINATION
              </div>
              <div className="flex gap-2 flex-wrap mb-2">
                {alertDiagnosis.survivingHypotheses.map((id) => {
                  const h = hypotheses.find((h) => h.id === id)
                  return h ? (
                    <span
                      key={id}
                      className="text-[9px] font-terminal px-1.5 py-0.5 rounded border border-[#059669]/20 bg-[#064E3B]/30 text-[#6EE7B7]"
                    >
                      {id}: {h.label}
                    </span>
                  ) : null
                })}
              </div>
              <div className="text-[8px] font-terminal text-[#059669]">
                Specific causal chain with evidence citations
              </div>
            </div>
          </div>

          {/* Earliest signal */}
          <div className="mt-3 flex items-center gap-3 p-2 rounded border border-[#D97706]/20" style={{ backgroundColor: '#0D0A00' }}>
            <span className="text-[#D97706] text-sm">⚡</span>
            <div>
              <span className="text-[9px] font-terminal text-[#D97706] tracking-wider">
                EARLIEST DECISIVE SIGNAL:
              </span>{' '}
              <span className="text-[9px] font-terminal text-[#92400E]">
                {alertDiagnosis.earliestSignalTimestamp}
              </span>{' '}
              <span className="text-[8px] font-terminal text-[#451A03]">
                (atom {alertDiagnosis.earliestSignalAtomId})
              </span>
            </div>
          </div>
        </motion.div>

        {/* Surviving hypotheses */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.3 }}
        >
          <SectionLabel accent="#059669" className="mb-3">SURVIVING HYPOTHESES</SectionLabel>
          <div className="space-y-3">
            <AnimatePresence>
              {survivingHypotheses.map((h) => (
                <SurvivingCard key={h.id} hypothesis={h} showChain />
              ))}
            </AnimatePresence>
          </div>
        </motion.div>

        {/* Right column: elimination timeline + contagion */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.3 }}
          className="flex flex-col gap-4"
        >
          {/* Elimination timeline */}
          <div>
            <SectionLabel accent="#DC2626" className="mb-3">ELIMINATION TIMELINE</SectionLabel>
            <div className="space-y-1">
              {cycles.map((cycle) => {
                const elimsThisCycle = allEliminations.filter(
                  (h) => h.eliminatedInCycle === cycle.cycleNumber
                )
                if (elimsThisCycle.length === 0) return null
                return (
                  <div key={cycle.cycleNumber} className="flex gap-2">
                    <div className="flex flex-col items-center">
                      <div className="w-4 h-4 rounded text-[8px] font-terminal flex items-center justify-center border border-[#1E293B] text-[#334155]">
                        {cycle.cycleNumber}
                      </div>
                      <div className="w-px flex-1 bg-[#1E293B] my-0.5" />
                    </div>
                    <div className="flex-1 pb-2">
                      {elimsThisCycle.map((h) => (
                        <div key={h.id} className="flex items-start gap-2 mb-1">
                          <span className="text-[8px] font-terminal text-[#DC2626] shrink-0">✗</span>
                          <div>
                            <span
                              className="text-[9px] font-terminal text-[#475569]"
                              style={{ textDecoration: 'line-through', textDecorationColor: '#DC262660' }}
                            >
                              {h.label}
                            </span>
                            {h.killAtomId && (
                              <span className="ml-1 text-[7px] font-terminal text-[#273548]">
                                → {h.killAtomId}
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Network contagion */}
          {contagionTargets.length > 0 && (
            <div>
              <SectionLabel accent="#D97706" className="mb-3">NETWORK CONTAGION DETECTED</SectionLabel>
              <div className="space-y-2">
                {contagionTargets.map((target) => (
                  <div
                    key={target.ticker}
                    className="rounded border-l-2 p-2.5"
                    style={{
                      borderLeftColor: target.riskScore > 0.8 ? '#DC2626' : '#D97706',
                      borderTopColor: '#1E293B',
                      borderRightColor: '#1E293B',
                      borderBottomColor: '#1E293B',
                      borderTopWidth: 1,
                      borderRightWidth: 1,
                      borderBottomWidth: 1,
                      backgroundColor: '#0D1526',
                    }}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[10px] font-terminal font-bold text-[#E2E8F0]">
                        {target.ticker}
                      </span>
                      <span className="text-[9px] font-terminal text-[#475569]">
                        {target.entityName}
                      </span>
                      <span className="ml-auto">
                        <TagPill
                          type="high"
                          label={`→ TIER ${target.promotedToTier}`}
                        />
                      </span>
                    </div>
                    <p className="text-[9px] font-evidence text-[#475569] leading-relaxed">
                      {target.sharedRiskFactor}
                    </p>
                    <div className="mt-1.5 flex items-center gap-2">
                      <div className="flex-1 h-1 bg-[#1E293B] rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full"
                          style={{
                            width: `${Math.round(target.riskScore * 100)}%`,
                            backgroundColor: target.riskScore > 0.8 ? '#DC2626' : '#D97706',
                          }}
                        />
                      </div>
                      <MonoValue
                        color={target.riskScore > 0.8 ? '#DC2626' : '#D97706'}
                        size="xs"
                      >
                        {Math.round(target.riskScore * 100)}%
                      </MonoValue>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </motion.div>

        {/* Context window full history */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.3 }}
          className="col-span-2 rounded border border-[#1E293B] p-4"
          style={{ backgroundColor: '#0A1120' }}
        >
          <div className="flex items-center justify-between mb-3">
            <SectionLabel accent="#7C3AED">CONTEXT WINDOW — FULL INVESTIGATION HISTORY</SectionLabel>
            <div className="flex items-center gap-4 text-[8px] font-terminal text-[#334155]">
              <span>
                TOTAL REASONING:{' '}
                <span className="text-[#2563EB]">
                  {(totalReasoningTokens / 1000).toFixed(0)}K tokens
                </span>
              </span>
              <span>
                TOTAL EVIDENCE:{' '}
                <span className="text-[#10B981]">
                  {(totalEvidenceTokens / 1000).toFixed(0)}K tokens
                </span>
              </span>
            </div>
          </div>

          <div className="space-y-2">
            {allCycleSnapshots.map((snapshot) => {
              const cycle = cycles.find((c) => c.cycleNumber === snapshot.cycleNumber)
              const total = snapshot.totalCapacity
              const used = snapshot.reasoningTokens + snapshot.evidenceTokens + snapshot.compressedTokens
              const usedPct = Math.round((used / total) * 100)
              const compressionRatio = cycle?.compressionRatio

              return (
                <div key={snapshot.cycleNumber} className="flex items-center gap-3">
                  <span className="text-[9px] font-terminal text-[#334155] w-12 shrink-0">
                    CYCLE {snapshot.cycleNumber}
                  </span>
                  <div className="flex-1">
                    <ContextWindowBar height={10} snapshot={snapshot} />
                  </div>
                  <div className="flex items-center gap-3 shrink-0 text-[8px] font-terminal">
                    <span className="text-[#334155]">
                      R:{' '}
                      <span className="text-[#2563EB]">
                        {(snapshot.reasoningTokens / 1000).toFixed(0)}K
                      </span>
                    </span>
                    <span className="text-[#334155]">
                      E:{' '}
                      <span className="text-[#10B981]">
                        {(snapshot.evidenceTokens / 1000).toFixed(0)}K
                      </span>
                    </span>
                    {snapshot.compressedTokens > 0 && (
                      <span className="text-[#334155]">
                        C:{' '}
                        <span className="text-[#7C3AED]">
                          {(snapshot.compressedTokens / 1000).toFixed(0)}K
                        </span>
                      </span>
                    )}
                    <span className="text-[#273548]">{usedPct}%</span>
                    {compressionRatio && (
                      <span className="text-[#7C3AED]">{compressionRatio.toFixed(1)}x</span>
                    )}
                  </div>
                </div>
              )
            })}
          </div>

          {/* Breathing narrative */}
          <div className="mt-3 pt-3 border-t border-[#1E293B] text-[8px] font-terminal text-[#273548] leading-relaxed">
            The context window fills with reasoning during each cycle, then compresses between cycles — preserving
            surviving hypotheses, elimination chains, and cross-modal contradictions while discarding raw reasoning.
            Reasoning tokens consumed 4x more context than evidence data. This is inference-time compute, not storage.
          </div>
        </motion.div>
      </div>
    </div>
  )
}
