import { motion, AnimatePresence } from 'framer-motion'
import { useStore } from '../../../store'
import { MonoValue } from '../../shared/MonoValue'
import { TagPill } from '../../shared/TagPill'
import { ContextWindowBar } from '../../layout/StatusBar/ContextWindowBar'
import { SurvivingCard } from '../Screen2_Investigation/HypothesisPanel/SurvivingCard'

export function ConvergenceScreen() {
  const resetInvestigation = useStore((s) => s.resetInvestigation)
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
      <div className="h-full flex items-center justify-center" style={{ backgroundColor: '#0C0A07' }}>
        <span className="font-mono text-sm" style={{ color: '#4A3D2A' }}>AWAITING CONVERGENCE...</span>
      </div>
    )
  }

  return (
    <div
      className="h-full overflow-y-auto"
      style={{ backgroundColor: '#0C0A07' }}
    >
      {/* Alert banner — editorial weight */}
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.3, ease: 'easeOut' }}
        className="sticky top-0 z-10 w-full px-5 py-3 flex items-center gap-4"
        style={{
          background: 'linear-gradient(135deg, #2A0E09 0%, #1A0F09 60%, #161310 100%)',
          borderBottom: '1px solid #D14B35',
          boxShadow: '0 8px 40px rgba(209,75,53,0.25)',
        }}
      >
        <span className="text-sm" style={{ color: '#D14B35' }}>⚠</span>
        <div className="flex-1 min-w-0">
          <div
            className="tracking-[0.25em] mb-0.5"
            style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '9px', color: '#D14B35' }}
          >
            CRITICAL RISK ALERT — DIAGNOSIS CONVERGENCE REACHED
          </div>
          <p
            className="leading-snug truncate"
            style={{ fontFamily: 'Syne, sans-serif', fontWeight: 800, fontSize: '13px', color: '#EDE4D4' }}
          >
            {alertDiagnosis.headline}
          </p>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <TagPill type="critical" label="T3 ALERT" />
          <button
            onClick={resetInvestigation}
            className="text-[8px] font-mono tracking-wider px-2 py-0.5 transition-colors"
            style={{
              color: '#8C7A5E',
              border: '1px solid #3D3529',
              backgroundColor: 'transparent',
              cursor: 'pointer',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.color = '#EDE4D4'; e.currentTarget.style.borderColor = '#524835' }}
            onMouseLeave={(e) => { e.currentTarget.style.color = '#8C7A5E'; e.currentTarget.style.borderColor = '#3D3529' }}
          >
            NEW INVESTIGATION
          </button>
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
          style={{ border: '1px solid #2E2820', backgroundColor: '#161310' }}
        >
          <div
            className="px-4 py-2 flex items-center gap-2"
            style={{ borderBottom: '1px solid #2E2820' }}
          >
            <div style={{ width: '2px', height: '12px', backgroundColor: '#D14B35' }} />
            <span
              className="text-[9px] tracking-[0.2em]"
              style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, color: '#8C7A5E' }}
            >ITERATIVE DIAGNOSIS</span>
          </div>
          <div className="px-4 py-3">
            <p className="text-[10px] font-mono leading-relaxed mb-4" style={{ color: '#8C7A5E' }}>
              {alertDiagnosis.iterativeDiagnosis}
            </p>

            {/* Single-pass vs iterative comparison */}
            <div className="grid grid-cols-2 gap-3">
              <div style={{ border: '1px solid #2E2820', backgroundColor: '#0C0A07' }}>
                <div className="px-3 py-2" style={{ borderBottom: '1px solid #2E2820' }}>
                  <span className="text-[8px] font-mono tracking-wider" style={{ color: '#4A3D2A' }}>SINGLE-PASS ANALYSIS</span>
                </div>
                <div className="px-3 py-2">
                  <p className="text-[9px] font-mono leading-relaxed italic" style={{ color: '#4A3D2A' }}>
                    "{alertDiagnosis.singlePassSummary}"
                  </p>
                  <div className="mt-1.5 text-[7px] font-mono" style={{ color: '#4A3D2A' }}>
                    Generic pattern-matching output
                  </div>
                </div>
              </div>
              <div style={{ border: '1px solid #2E9E7220', backgroundColor: '#0C0A07' }}>
                <div className="px-3 py-2" style={{ borderBottom: '1px solid #2E9E7220' }}>
                  <span className="text-[8px] font-mono tracking-wider" style={{ color: '#2E9E72' }}>ITERATIVE HYPOTHESIS ELIMINATION</span>
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
                            border: '1px solid #2E9E7220',
                            backgroundColor: '#0A2D1E',
                            color: '#2E9E72',
                          }}
                        >
                          {id}: {h.label}
                        </span>
                      ) : null
                    })}
                  </div>
                  <div className="text-[7px] font-mono" style={{ color: '#2E9E72' }}>
                    Specific causal chain with evidence citations
                  </div>
                </div>
              </div>
            </div>

            {/* Earliest signal */}
            <div
              className="mt-3 flex items-center gap-3 px-3 py-2"
              style={{ border: '1px solid #C8912A20', backgroundColor: '#2D1E07' }}
            >
              <span className="font-mono text-sm" style={{ color: '#C8912A' }}>⚡</span>
              <div>
                <span className="text-[9px] font-mono tracking-wider" style={{ color: '#C8912A' }}>
                  EARLIEST DECISIVE SIGNAL:
                </span>{' '}
                <span className="text-[9px] font-mono" style={{ color: '#8C7A5E' }}>
                  {alertDiagnosis.earliestSignalTimestamp}
                </span>{' '}
                <span className="text-[8px] font-mono" style={{ color: '#4A3D2A' }}>
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
            <div style={{ width: '2px', height: '12px', backgroundColor: '#2E9E72' }} />
            <span
              className="text-[9px] tracking-[0.2em]"
              style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, color: '#8C7A5E' }}
            >SURVIVING HYPOTHESES</span>
          </div>
          <div style={{ border: '1px solid #2E2820' }}>
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
              <div style={{ width: '2px', height: '12px', backgroundColor: '#D14B35' }} />
              <span
                className="text-[9px] tracking-[0.2em]"
                style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, color: '#8C7A5E' }}
              >ELIMINATION TIMELINE</span>
            </div>
            <div style={{ border: '1px solid #2E2820' }}>
              {cycles.map((cycle) => {
                const elimsThisCycle = allEliminations.filter(
                  (h) => h.eliminatedInCycle === cycle.cycleNumber
                )
                if (elimsThisCycle.length === 0) return null
                return (
                  <div
                    key={cycle.cycleNumber}
                    className="flex gap-3 px-3 py-2"
                    style={{ borderBottom: '1px solid #2E2820' }}
                  >
                    <div
                      className="shrink-0 w-4 h-4 flex items-center justify-center text-[8px] font-mono mt-0.5"
                      style={{ border: '1px solid #2E2820', color: '#4A3D2A' }}
                    >
                      {cycle.cycleNumber}
                    </div>
                    <div className="flex-1">
                      {elimsThisCycle.map((h) => (
                        <div key={h.id} className="flex items-start gap-2 mb-1">
                          <span className="text-[8px] font-mono shrink-0" style={{ color: '#D14B35' }}>✗</span>
                          <div>
                            <span
                              className="text-[9px] font-mono"
                              style={{ color: '#4A3D2A', textDecoration: 'line-through', textDecorationColor: '#D14B3550' }}
                            >
                              {h.label}
                            </span>
                            {h.killAtomId && (
                              <span className="ml-1 text-[7px] font-mono" style={{ color: '#4A3D2A' }}>
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
                <div style={{ width: '2px', height: '12px', backgroundColor: '#D4651A' }} />
                <span
                  className="text-[9px] tracking-[0.2em]"
                  style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, color: '#8C7A5E' }}
                >NETWORK CONTAGION DETECTED</span>
              </div>
              <div style={{ border: '1px solid #2E2820' }}>
                {contagionTargets.map((target) => {
                  const isHighRisk = target.riskScore > 0.8
                  return (
                    <div
                      key={target.ticker}
                      className="px-3 py-2"
                      style={{
                        borderBottom: '1px solid #2E2820',
                        borderLeft: `2px solid ${isHighRisk ? '#D14B35' : '#D4651A'}`,
                      }}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-[10px] font-mono font-medium" style={{ color: '#EDE4D4' }}>
                          {target.ticker}
                        </span>
                        <span className="text-[9px] font-mono" style={{ color: '#8C7A5E' }}>
                          {target.entityName}
                        </span>
                        <span className="ml-auto">
                          <TagPill type="high" label={`→ TIER ${target.promotedToTier}`} />
                        </span>
                      </div>
                      <p className="text-[9px] font-mono leading-relaxed" style={{ color: '#8C7A5E' }}>
                        {target.sharedRiskFactor}
                      </p>
                      <div className="mt-1.5 flex items-center gap-2">
                        <div className="flex-1 h-px overflow-hidden" style={{ backgroundColor: '#2E2820' }}>
                          <div
                            className="h-full"
                            style={{
                              width: `${Math.round(target.riskScore * 100)}%`,
                              backgroundColor: isHighRisk ? '#D14B35' : '#D4651A',
                              transition: 'width 0.5s ease-out',
                            }}
                          />
                        </div>
                        <MonoValue
                          color={isHighRisk ? '#D14B35' : '#D4651A'}
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
          style={{ border: '1px solid #2E2820', backgroundColor: '#161310' }}
        >
          <div
            className="px-4 py-2 flex items-center justify-between"
            style={{ borderBottom: '1px solid #2E2820' }}
          >
            <div className="flex items-center gap-2">
              <div style={{ width: '2px', height: '12px', backgroundColor: '#7C6DB8' }} />
              <span
                className="text-[9px] tracking-[0.2em]"
                style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, color: '#8C7A5E' }}
              >
                CONTEXT WINDOW — FULL INVESTIGATION HISTORY
              </span>
            </div>
            <div className="flex items-center gap-4 text-[8px] font-mono" style={{ color: '#4A3D2A' }}>
              <span>
                TOTAL REASONING:{' '}
                <span style={{ color: '#C8912A' }}>
                  {(totalReasoningTokens / 1000).toFixed(0)}K tokens
                </span>
              </span>
              <span>
                TOTAL EVIDENCE:{' '}
                <span style={{ color: '#2E9E72' }}>
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
                  <span className="text-[8px] font-mono w-12 shrink-0" style={{ color: '#4A3D2A' }}>
                    CYCLE {snapshot.cycleNumber}
                  </span>
                  <div className="flex-1">
                    <ContextWindowBar height={8} snapshot={snapshot} />
                  </div>
                  <div className="flex items-center gap-3 shrink-0 text-[8px] font-mono">
                    <span style={{ color: '#4A3D2A' }}>
                      R: <span style={{ color: '#C8912A' }}>{(snapshot.reasoningTokens / 1000).toFixed(0)}K</span>
                    </span>
                    <span style={{ color: '#4A3D2A' }}>
                      E: <span style={{ color: '#2E9E72' }}>{(snapshot.evidenceTokens / 1000).toFixed(0)}K</span>
                    </span>
                    {snapshot.compressedTokens > 0 && (
                      <span style={{ color: '#4A3D2A' }}>
                        C: <span style={{ color: '#7C6DB8' }}>{(snapshot.compressedTokens / 1000).toFixed(0)}K</span>
                      </span>
                    )}
                    <span style={{ color: '#4A3D2A' }}>{usedPct}%</span>
                    {compressionRatio && (
                      <span style={{ color: '#7C6DB8' }}>{compressionRatio.toFixed(1)}x</span>
                    )}
                  </div>
                </div>
              )
            })}
          </div>

          {/* Breathing narrative */}
          <div
            className="px-4 py-2 text-[8px] font-mono leading-relaxed"
            style={{ borderTop: '1px solid #2E2820', color: '#4A3D2A' }}
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
