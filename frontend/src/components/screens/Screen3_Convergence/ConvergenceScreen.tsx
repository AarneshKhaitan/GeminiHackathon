import { motion, AnimatePresence } from 'framer-motion'
import { useStore } from '../../../store'
import { MonoValue } from '../../shared/MonoValue'
import { TagPill } from '../../shared/TagPill'
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

  const totalReasoningTokens = allCycleSnapshots.reduce((acc, s) => acc + s.reasoningTokens, 0)
  const totalEvidenceTokens = allCycleSnapshots.reduce((acc, s) => acc + s.evidenceTokens, 0)

  if (!alertDiagnosis) {
    return (
      <div className="h-full flex items-center justify-center" style={{ backgroundColor: '#000000' }}>
        <span className="text-[#333333] font-mono text-sm">AWAITING CONVERGENCE...</span>
      </div>
    )
  }

  return (
    <div
      className="h-full overflow-y-auto"
      style={{ backgroundColor: '#000000' }}
    >
      {/* Alert banner — tight, surgical */}
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.3, ease: 'easeOut' }}
        className="sticky top-0 z-10 w-full px-5 py-2.5 flex items-center gap-4"
        style={{
          backgroundColor: '#060000',
          borderBottom: '1px solid #FF3333',
        }}
      >
        <span className="text-[#FF3333] text-sm font-mono">⚠</span>
        <div className="flex-1 min-w-0">
          <div className="text-[8px] font-mono text-[#FF3333] tracking-[0.25em] mb-0.5">
            CRITICAL RISK ALERT — DIAGNOSIS CONVERGENCE REACHED
          </div>
          <p className="text-[11px] font-mono font-medium text-[#E8E8E8] leading-snug truncate">
            {alertDiagnosis.headline}
          </p>
        </div>
        <div className="shrink-0">
          <TagPill type="critical" label="T3 ALERT" />
        </div>
      </motion.div>

      {/* Body */}
      <div className="p-5 grid gap-5" style={{ gridTemplateColumns: '1fr 1fr' }}>

        {/* Full diagnosis — col span 2 */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.25 }}
          className="col-span-2"
          style={{ border: '1px solid #1C1C1C' }}
        >
          <div
            className="px-4 py-2 flex items-center gap-2"
            style={{ borderBottom: '1px solid #1C1C1C' }}
          >
            <div style={{ width: '2px', height: '12px', backgroundColor: '#FF3333' }} />
            <span className="text-[9px] font-mono tracking-[0.2em] text-[#555555]">ITERATIVE DIAGNOSIS</span>
          </div>
          <div className="px-4 py-3">
            <p className="text-[10px] font-mono text-[#555555] leading-relaxed mb-4">
              {alertDiagnosis.iterativeDiagnosis}
            </p>

            {/* Single-pass vs iterative comparison */}
            <div className="grid grid-cols-2 gap-3">
              <div style={{ border: '1px solid #1C1C1C', backgroundColor: '#000000' }}>
                <div className="px-3 py-2" style={{ borderBottom: '1px solid #1C1C1C' }}>
                  <span className="text-[8px] font-mono text-[#333333] tracking-wider">SINGLE-PASS ANALYSIS</span>
                </div>
                <div className="px-3 py-2">
                  <p className="text-[9px] font-mono text-[#333333] leading-relaxed italic">
                    "{alertDiagnosis.singlePassSummary}"
                  </p>
                  <div className="mt-1.5 text-[7px] font-mono text-[#333333]">
                    Generic pattern-matching output
                  </div>
                </div>
              </div>
              <div style={{ border: '1px solid #00C27A20', backgroundColor: '#000000' }}>
                <div className="px-3 py-2" style={{ borderBottom: '1px solid #00C27A20' }}>
                  <span className="text-[8px] font-mono text-[#00C27A] tracking-wider">ITERATIVE HYPOTHESIS ELIMINATION</span>
                </div>
                <div className="px-3 py-2">
                  <div className="flex flex-wrap gap-1 mb-2">
                    {alertDiagnosis.survivingHypotheses.map((id) => {
                      const h = hypotheses.find((h) => h.id === id)
                      return h ? (
                        <span
                          key={id}
                          className="text-[8px] font-mono px-1 py-0.5"
                          style={{
                            border: '1px solid #00C27A20',
                            backgroundColor: '#001A0E',
                            color: '#00C27A',
                          }}
                        >
                          {id}: {h.label}
                        </span>
                      ) : null
                    })}
                  </div>
                  <div className="text-[7px] font-mono text-[#00C27A]">
                    Specific causal chain with evidence citations
                  </div>
                </div>
              </div>
            </div>

            {/* Earliest signal */}
            <div
              className="mt-3 flex items-center gap-3 px-3 py-2"
              style={{ border: '1px solid #F59E0B20', backgroundColor: '#040200' }}
            >
              <span className="text-[#F59E0B] font-mono text-sm">⚡</span>
              <div>
                <span className="text-[9px] font-mono text-[#F59E0B] tracking-wider">
                  EARLIEST DECISIVE SIGNAL:
                </span>{' '}
                <span className="text-[9px] font-mono text-[#555555]">
                  {alertDiagnosis.earliestSignalTimestamp}
                </span>{' '}
                <span className="text-[8px] font-mono text-[#333333]">
                  (atom {alertDiagnosis.earliestSignalAtomId})
                </span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Surviving hypotheses */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.25 }}
        >
          <div className="flex items-center gap-2 mb-3">
            <div style={{ width: '2px', height: '12px', backgroundColor: '#00C27A' }} />
            <span className="text-[9px] font-mono tracking-[0.2em] text-[#555555]">SURVIVING HYPOTHESES</span>
          </div>
          <div style={{ border: '1px solid #1C1C1C' }}>
            <AnimatePresence>
              {survivingHypotheses.map((h) => (
                <SurvivingCard key={h.id} hypothesis={h} showChain />
              ))}
            </AnimatePresence>
          </div>
        </motion.div>

        {/* Right: elimination timeline + contagion */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.25 }}
          className="flex flex-col gap-4"
        >
          {/* Elimination timeline */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div style={{ width: '2px', height: '12px', backgroundColor: '#FF3333' }} />
              <span className="text-[9px] font-mono tracking-[0.2em] text-[#555555]">ELIMINATION TIMELINE</span>
            </div>
            <div style={{ border: '1px solid #1C1C1C' }}>
              {cycles.map((cycle) => {
                const elimsThisCycle = allEliminations.filter(
                  (h) => h.eliminatedInCycle === cycle.cycleNumber
                )
                if (elimsThisCycle.length === 0) return null
                return (
                  <div
                    key={cycle.cycleNumber}
                    className="flex gap-3 px-3 py-2"
                    style={{ borderBottom: '1px solid #1C1C1C' }}
                  >
                    <div
                      className="shrink-0 w-4 h-4 flex items-center justify-center text-[8px] font-mono mt-0.5"
                      style={{ border: '1px solid #1C1C1C', color: '#333333' }}
                    >
                      {cycle.cycleNumber}
                    </div>
                    <div className="flex-1">
                      {elimsThisCycle.map((h) => (
                        <div key={h.id} className="flex items-start gap-2 mb-1">
                          <span className="text-[8px] font-mono text-[#FF3333] shrink-0">✗</span>
                          <div>
                            <span
                              className="text-[9px] font-mono text-[#333333]"
                              style={{ textDecoration: 'line-through', textDecorationColor: '#FF333350' }}
                            >
                              {h.label}
                            </span>
                            {h.killAtomId && (
                              <span className="ml-1 text-[7px] font-mono text-[#333333]">
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
              <div className="flex items-center gap-2 mb-3">
                <div style={{ width: '2px', height: '12px', backgroundColor: '#F59E0B' }} />
                <span className="text-[9px] font-mono tracking-[0.2em] text-[#555555]">NETWORK CONTAGION DETECTED</span>
              </div>
              <div style={{ border: '1px solid #1C1C1C' }}>
                {contagionTargets.map((target) => {
                  const isHighRisk = target.riskScore > 0.8
                  return (
                    <div
                      key={target.ticker}
                      className="px-3 py-2"
                      style={{
                        borderBottom: '1px solid #1C1C1C',
                        borderLeft: `2px solid ${isHighRisk ? '#FF3333' : '#F59E0B'}`,
                      }}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-[10px] font-mono font-medium text-[#E8E8E8]">
                          {target.ticker}
                        </span>
                        <span className="text-[9px] font-mono text-[#555555]">
                          {target.entityName}
                        </span>
                        <span className="ml-auto">
                          <TagPill type="high" label={`→ TIER ${target.promotedToTier}`} />
                        </span>
                      </div>
                      <p className="text-[9px] font-mono text-[#555555] leading-relaxed">
                        {target.sharedRiskFactor}
                      </p>
                      <div className="mt-1.5 flex items-center gap-2">
                        <div className="flex-1 h-px overflow-hidden" style={{ backgroundColor: '#1C1C1C' }}>
                          <div
                            className="h-full"
                            style={{
                              width: `${Math.round(target.riskScore * 100)}%`,
                              backgroundColor: isHighRisk ? '#FF3333' : '#F59E0B',
                              transition: 'width 0.5s ease-out',
                            }}
                          />
                        </div>
                        <MonoValue
                          color={isHighRisk ? '#FF3333' : '#F59E0B'}
                          size="xs"
                        >
                          {Math.round(target.riskScore * 100)}%
                        </MonoValue>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </motion.div>

        {/* Context window full history — col span 2 */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.25 }}
          className="col-span-2"
          style={{ border: '1px solid #1C1C1C' }}
        >
          <div
            className="px-4 py-2 flex items-center justify-between"
            style={{ borderBottom: '1px solid #1C1C1C' }}
          >
            <div className="flex items-center gap-2">
              <div style={{ width: '2px', height: '12px', backgroundColor: '#8B5CF6' }} />
              <span className="text-[9px] font-mono tracking-[0.2em] text-[#555555]">
                CONTEXT WINDOW — FULL INVESTIGATION HISTORY
              </span>
            </div>
            <div className="flex items-center gap-4 text-[8px] font-mono text-[#333333]">
              <span>
                TOTAL REASONING:{' '}
                <span className="text-[#3B82F6]">
                  {(totalReasoningTokens / 1000).toFixed(0)}K tokens
                </span>
              </span>
              <span>
                TOTAL EVIDENCE:{' '}
                <span className="text-[#00C27A]">
                  {(totalEvidenceTokens / 1000).toFixed(0)}K tokens
                </span>
              </span>
            </div>
          </div>

          <div className="px-4 py-3 space-y-2">
            {allCycleSnapshots.map((snapshot) => {
              const cycle = cycles.find((c) => c.cycleNumber === snapshot.cycleNumber)
              const total = snapshot.totalCapacity
              const used = snapshot.reasoningTokens + snapshot.evidenceTokens + snapshot.compressedTokens
              const usedPct = Math.round((used / total) * 100)
              const compressionRatio = cycle?.compressionRatio

              return (
                <div key={snapshot.cycleNumber} className="flex items-center gap-3">
                  <span className="text-[8px] font-mono text-[#333333] w-12 shrink-0">
                    CYCLE {snapshot.cycleNumber}
                  </span>
                  <div className="flex-1">
                    <ContextWindowBar height={8} snapshot={snapshot} />
                  </div>
                  <div className="flex items-center gap-3 shrink-0 text-[8px] font-mono">
                    <span className="text-[#333333]">
                      R: <span className="text-[#3B82F6]">{(snapshot.reasoningTokens / 1000).toFixed(0)}K</span>
                    </span>
                    <span className="text-[#333333]">
                      E: <span className="text-[#00C27A]">{(snapshot.evidenceTokens / 1000).toFixed(0)}K</span>
                    </span>
                    {snapshot.compressedTokens > 0 && (
                      <span className="text-[#333333]">
                        C: <span className="text-[#8B5CF6]">{(snapshot.compressedTokens / 1000).toFixed(0)}K</span>
                      </span>
                    )}
                    <span className="text-[#333333]">{usedPct}%</span>
                    {compressionRatio && (
                      <span className="text-[#8B5CF6]">{compressionRatio.toFixed(1)}x</span>
                    )}
                  </div>
                </div>
              )
            })}
          </div>

          {/* Breathing narrative */}
          <div
            className="px-4 py-2 text-[8px] font-mono text-[#333333] leading-relaxed"
            style={{ borderTop: '1px solid #1C1C1C' }}
          >
            The context window fills with reasoning during each cycle, then compresses between cycles — preserving
            surviving hypotheses, elimination chains, and cross-modal contradictions while discarding raw reasoning.
            Reasoning tokens consumed 4x more context than evidence data. This is inference-time compute, not storage.
          </div>
        </motion.div>
      </div>
    </div>
  )
}
