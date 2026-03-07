import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useStore } from '../../../store'
import { TRIGGERS } from '../../../data/triggers'
import { useMockPlayback } from '../../../hooks/useMockPlayback'
import { TagPill } from '../../shared/TagPill'
import type { TriggerEvent } from '../../../types/api'

export function SignalIntakeScreen() {
  const [selectedTrigger, setSelectedTrigger] = useState<TriggerEvent | null>(null)
  const [evalPhase, setEvalPhase] = useState<'idle' | 'evaluating' | 'done'>('idle')
  const tier2EvalText = useStore((s) => s.tier2EvalText)
  const tier2EvalDone = useStore((s) => s.tier2EvalDone)
  const { start: startMock } = useMockPlayback()
  const resetInvestigation = useStore((s) => s.resetInvestigation)
  const applyWebSocketMessage = useStore((s) => s.applyWebSocketMessage)

  function handleTrigger(trigger: TriggerEvent) {
    resetInvestigation()
    setSelectedTrigger(trigger)
    setEvalPhase('evaluating')
    applyWebSocketMessage({ type: 'SESSION_STARTED', entity: trigger.entity, tier: 2 })
    useStore.getState().setEntity(trigger.entity, trigger.ticker)
    startMock()
    setEvalPhase('done')
  }

  const sigmaColor = (s: number) => s >= 4 ? '#FF3333' : s >= 3 ? '#F59E0B' : '#00C27A'

  return (
    <div
      className="h-full flex flex-col items-center justify-center p-10 gap-8"
      style={{ backgroundColor: '#000000' }}
    >
      {/* Header */}
      <div className="text-center max-w-xl">
        <div className="text-[9px] font-mono text-[#333333] tracking-[0.35em] mb-3">
          ITERATIVE HYPOTHESIS ELIMINATION ENGINE
        </div>
        <h1 className="text-xl font-mono font-medium text-[#E8E8E8] mb-2 tracking-tight">
          Signal Intake
        </h1>
        <p className="text-[11px] font-mono text-[#555555] leading-relaxed">
          Events are evaluated for severity before initiating investigation.
          Most signals are dismissed at T2. Only credible crises escalate to T3.
        </p>
      </div>

      {/* Pipeline — clean text diagram */}
      <div className="flex items-center gap-0 text-[9px] font-mono">
        <div
          className="flex flex-col items-center gap-1 px-4 py-2"
          style={{ border: '1px solid #2D2D2D', backgroundColor: '#0A0A0A' }}
        >
          <span className="text-[#F59E0B] font-medium tracking-wider">T2</span>
          <span className="text-[#555555]">SEMANTIC EVAL</span>
          <span className="text-[#333333]">1 CALL</span>
        </div>

        <div className="flex flex-col items-center gap-1 px-3">
          <span className="text-[#00C27A]">→ ESCALATE</span>
          <span className="text-[#333333]">→ DISMISS</span>
        </div>

        <div
          className="flex flex-col items-center gap-1 px-4 py-2"
          style={{ border: '1px solid #FF3333', backgroundColor: '#050000' }}
        >
          <div className="flex items-center gap-2">
            <span
              className="inline-block w-1.5 h-1.5"
              style={{ backgroundColor: '#FF3333', animation: 'pulse-dot 0.9s ease-in-out infinite' }}
            />
            <span className="text-[#FF3333] font-medium tracking-wider">T3</span>
            <span className="text-[8px] text-[#FF3333] border border-[#FF333340] px-1" style={{ backgroundColor: '#FF333410' }}>CORE</span>
          </div>
          <span className="text-[#555555]">FULL INVESTIGATION</span>
          <span className="text-[#333333]">4-5 DEEP CYCLES</span>
        </div>

        <div className="flex flex-col items-center gap-1 px-3">
          <span className="text-[#FF3333]">→ ALERT</span>
          <span className="text-[#00C27A]">→ ALL-CLEAR</span>
        </div>

        <div className="flex flex-col gap-1">
          {[
            { label: 'ORCHESTRATOR', color: '#3B82F6', note: 'STATEFUL' },
            { label: 'INVESTIGATOR', color: '#00C27A', note: 'FRESH/CYCLE' },
            { label: 'PKG + 3 AGENTS', color: '#8B5CF6', note: 'FRESH/RUN' },
          ].map(({ label, color, note }) => (
            <div
              key={label}
              className="flex items-center gap-2 px-2.5 py-1"
              style={{ border: '1px solid #1C1C1C', backgroundColor: '#0A0A0A' }}
            >
              <span className="font-mono" style={{ color }}>{label}</span>
              <span className="text-[#333333]">{note}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Trigger selection */}
      <div className="w-full max-w-2xl">
        <div className="text-[9px] font-mono text-[#333333] tracking-[0.25em] mb-2 pb-2" style={{ borderBottom: '1px solid #1C1C1C' }}>
          SELECT TRIGGER EVENT
        </div>

        {TRIGGERS.map((trigger) => {
          const isSelected = selectedTrigger?.id === trigger.id
          const isDisabled = evalPhase !== 'idle' && !isSelected

          return (
            <motion.button
              key={trigger.id}
              whileTap={{ scale: 0.995 }}
              disabled={evalPhase !== 'idle'}
              onClick={() => handleTrigger(trigger)}
              className="relative w-full text-left"
              style={{
                borderBottom: '1px solid #1C1C1C',
                borderLeft: isSelected ? `2px solid #3B82F6` : '2px solid transparent',
                backgroundColor: isSelected ? '#050A14' : 'transparent',
                opacity: isDisabled ? 0.35 : 1,
                padding: '10px 12px',
                cursor: evalPhase !== 'idle' ? 'default' : 'pointer',
              }}
            >
              <div className="flex items-start gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-mono font-medium text-[#E8E8E8]">
                      {trigger.ticker}
                    </span>
                    <span className="text-[#333333]">·</span>
                    <span className="text-[10px] font-mono text-[#555555]">{trigger.entity}</span>
                    <span className="text-[9px] font-mono text-[#333333]">{trigger.date}</span>
                  </div>
                  <p className="text-[10px] font-mono text-[#555555] leading-relaxed">
                    {trigger.event}
                  </p>
                </div>
                <div className="shrink-0 text-right">
                  <div
                    className="text-lg font-mono font-medium tabular-nums"
                    style={{ color: sigmaColor(trigger.magnitudeSigma) }}
                  >
                    {trigger.magnitudeSigma}σ
                  </div>
                </div>
              </div>
            </motion.button>
          )
        })}
      </div>

      {/* T2 evaluation panel */}
      <AnimatePresence>
        {selectedTrigger && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25, ease: 'easeOut' }}
            className="w-full max-w-2xl"
            style={{ border: '1px solid #1C1C1C', backgroundColor: '#000000' }}
          >
            {/* Panel header */}
            <div
              className="px-4 py-2 flex items-center justify-between"
              style={{ borderBottom: '1px solid #1C1C1C' }}
            >
              <div className="flex items-center gap-2">
                <span
                  className="inline-block w-1.5 h-1.5"
                  style={{ backgroundColor: '#F59E0B', animation: 'pulse-dot 0.8s ease-in-out infinite' }}
                />
                <span className="text-[9px] font-mono text-[#F59E0B] tracking-wider">
                  T2 — SEMANTIC EVALUATION
                </span>
              </div>
              <span className="text-[9px] font-mono text-[#333333]">
                1 GEMINI CALL · ~5K TOKENS
              </span>
            </div>

            {/* Signal details */}
            <div className="px-4 py-3 grid grid-cols-3 gap-4" style={{ borderBottom: '1px solid #1C1C1C' }}>
              {[
                { label: 'ENTITY', value: selectedTrigger.ticker },
                { label: 'DATE', value: selectedTrigger.date },
                { label: 'MAGNITUDE', value: `${selectedTrigger.magnitudeSigma}σ`, color: sigmaColor(selectedTrigger.magnitudeSigma) },
              ].map(({ label, value, color }) => (
                <div key={label}>
                  <div className="text-[8px] font-mono text-[#333333] tracking-wider mb-1">{label}</div>
                  <div className="text-[11px] font-mono font-medium" style={{ color: color ?? '#E8E8E8' }}>{value}</div>
                </div>
              ))}
            </div>

            {/* Streaming text */}
            <div className="px-4 py-3 min-h-[72px]">
              <div className="text-[8px] font-mono text-[#333333] tracking-wider mb-2">ASSESSMENT</div>
              <p className="text-[10px] font-mono text-[#555555] leading-relaxed">
                {tier2EvalText}
                {!tier2EvalDone && tier2EvalText.length > 0 && (
                  <span
                    className="inline-block w-[5px] h-[11px] ml-0.5 align-text-bottom"
                    style={{ backgroundColor: '#F59E0B', animation: 'blink 0.7s step-end infinite' }}
                  />
                )}
              </p>
            </div>

            {/* Escalation decision */}
            <AnimatePresence>
              {tier2EvalDone && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  transition={{ duration: 0.25, delay: 0.15 }}
                  className="overflow-hidden"
                >
                  <div
                    className="px-4 py-3 flex items-center justify-between"
                    style={{ borderTop: '1px solid #FF333330', backgroundColor: '#040000' }}
                  >
                    <div className="flex flex-col gap-1">
                      <span
                        className="text-[10px] font-mono font-medium tracking-wider text-[#FF3333]"
                        style={{ animation: 'pulse-tier 0.8s ease-in-out 3' }}
                      >
                        ↑ ESCALATE → T3 FULL INVESTIGATION
                      </span>
                      <span className="text-[9px] font-mono text-[#555555]">
                        4-5 deep reasoning cycles · Iterative hypothesis elimination
                      </span>
                    </div>
                    <TagPill type="critical" label="T2 → T3" />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
