import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useStore } from '../../../store'
import { TRIGGERS } from '../../../data/triggers'
import { useMockPlayback } from '../../../hooks/useMockPlayback'
import { useWebSocket } from '../../../hooks/useWebSocket'
import { useSSEInvestigation } from '../../../hooks/useSSEInvestigation'
import { TagPill } from '../../shared/TagPill'
import type { TriggerEvent } from '../../../types/api'

export function SignalIntakeScreen() {
  const [selectedTrigger, setSelectedTrigger] = useState<TriggerEvent | null>(null)
  const [evalPhase, setEvalPhase] = useState<'idle' | 'evaluating' | 'done'>('idle')
  const tier2EvalText = useStore((s) => s.tier2EvalText)
  const tier2EvalDone = useStore((s) => s.tier2EvalDone)
  const resetInvestigation = useStore((s) => s.resetInvestigation)
  const applyWebSocketMessage = useStore((s) => s.applyWebSocketMessage)
  const { startCachedInvestigation } = useSSEInvestigation()

  function handleTrigger(trigger: TriggerEvent) {
    resetInvestigation()
    setSelectedTrigger(trigger)
    setEvalPhase('evaluating')
    useStore.getState().setEntity(trigger.entity, trigger.ticker)
    // Always use cached investigation
    applyWebSocketMessage({ type: 'SESSION_STARTED', entity: trigger.entity, tier: 2 })
    startCachedInvestigation(trigger.entity)
    setEvalPhase('done')
  }

  const sigmaColor = (s: number) => s >= 4 ? '#D14B35' : s >= 3 ? '#D4651A' : '#2E9E72'

  return (
    <div
      className="h-full flex flex-col items-center justify-center p-10 gap-8"
      style={{ backgroundColor: '#0C0A07' }}
    >
      {/* Header */}
      <div className="text-center max-w-xl">
        <div
          className="mb-3 tracking-[0.35em]"
          style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '10px', color: '#4A3D2A' }}
        >
          ITERATIVE HYPOTHESIS ELIMINATION ENGINE
        </div>
        <h1
          className="mb-2 tracking-tight"
          style={{ fontFamily: 'Syne, sans-serif', fontWeight: 800, fontSize: '1.25rem', color: '#EDE4D4' }}
        >
          Signal Intake
        </h1>
        <p className="text-[11px] font-mono leading-relaxed" style={{ color: '#8C7A5E' }}>
          A market signal arrives that can't be explained away.
          The system evaluates severity, then decides: dismiss or investigate.
        </p>
      </div>

      {/* Pipeline — clean text diagram */}
      <div className="flex items-center gap-0 text-[9px] font-mono">
        <div
          className="flex flex-col items-center gap-1 px-4 py-2"
          style={{ border: '1px solid #2E2820', backgroundColor: '#161310' }}
        >
          <span className="font-medium tracking-wider" style={{ color: '#D4651A' }}>T2</span>
          <span style={{ color: '#8C7A5E' }}>EVALUATE</span>
          <span style={{ color: '#4A3D2A' }}>1 CALL</span>
        </div>

        <div className="flex flex-col items-center gap-1 px-3">
          <span style={{ color: '#2E9E72' }}>→ ESCALATE</span>
          <span style={{ color: '#4A3D2A' }}>→ DISMISS</span>
        </div>

        <div
          className="flex flex-col items-center gap-1 px-4 py-2"
          style={{ border: '1px solid #D14B35', backgroundColor: '#2A0E09' }}
        >
          <div className="flex items-center gap-2">
            <span
              className="inline-block w-1.5 h-1.5"
              style={{ backgroundColor: '#D14B35', animation: 'pulse-dot 0.9s ease-in-out infinite' }}
            />
            <span className="font-medium tracking-wider" style={{ color: '#D14B35' }}>T3</span>
            <span
              className="text-[8px] border px-1"
              style={{ color: '#D14B35', borderColor: '#D14B3540', backgroundColor: '#D14B3510' }}
            >CORE</span>
          </div>
          <span style={{ color: '#8C7A5E' }}>DEEP INVESTIGATION</span>
          <span style={{ color: '#4A3D2A' }}>3-5 CYCLES</span>
        </div>

        <div className="flex flex-col items-center gap-1 px-3">
          <span style={{ color: '#D14B35' }}>→ ALERT</span>
          <span style={{ color: '#2E9E72' }}>→ ALL-CLEAR</span>
        </div>

        <div className="flex flex-col gap-1">
          {[
            { label: 'ORCHESTRATOR', color: '#C8912A', note: 'STATEFUL' },
            { label: 'INVESTIGATOR', color: '#2E9E72', note: 'FRESH/CYCLE' },
            { label: 'PKG + 3 AGENTS', color: '#7C6DB8', note: 'FRESH/RUN' },
          ].map(({ label, color, note }) => (
            <div
              key={label}
              className="flex items-center gap-2 px-2.5 py-1"
              style={{ border: '1px solid #2E2820', backgroundColor: '#161310' }}
            >
              <span className="font-mono" style={{ color }}>{label}</span>
              <span style={{ color: '#4A3D2A' }}>{note}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Trigger selection */}
      <div className="w-full max-w-2xl">
        <div
          className="flex items-center justify-between mb-2 pb-2"
          style={{ borderBottom: '1px solid #2E2820' }}
        >
          <span className="text-[9px] font-mono tracking-[0.25em]" style={{ color: '#4A3D2A' }}>
            SELECT TRIGGER EVENT
          </span>
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
                borderBottom: '1px solid #2E2820',
                borderLeft: isSelected ? `2px solid #C8912A` : '2px solid transparent',
                backgroundColor: isSelected ? '#2D1E07' : 'transparent',
                opacity: isDisabled ? 0.35 : 1,
                padding: '10px 12px',
                cursor: evalPhase !== 'idle' ? 'default' : 'pointer',
              }}
            >
              <div className="flex items-start gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-mono font-medium" style={{ color: '#EDE4D4' }}>
                      {trigger.ticker}
                    </span>
                    <span style={{ color: '#3D3529' }}>·</span>
                    <span className="text-[10px] font-mono" style={{ color: '#8C7A5E' }}>{trigger.entity}</span>
                    <span className="text-[9px] font-mono" style={{ color: '#4A3D2A' }}>{trigger.date}</span>
                  </div>
                  <p className="text-[10px] font-mono leading-relaxed" style={{ color: '#8C7A5E' }}>
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
            style={{ border: '1px solid #2E2820', backgroundColor: '#161310' }}
          >
            {/* Panel header */}
            <div
              className="px-4 py-2 flex items-center justify-between"
              style={{ borderBottom: '1px solid #2E2820' }}
            >
              <div className="flex items-center gap-2">
                <span
                  className="inline-block w-1.5 h-1.5"
                  style={{ backgroundColor: '#D4651A', animation: 'pulse-dot 0.8s ease-in-out infinite' }}
                />
                <span className="text-[9px] font-mono tracking-wider" style={{ color: '#D4651A' }}>
                  SIGNAL EVALUATION
                </span>
              </div>
              <span className="text-[9px] font-mono" style={{ color: '#4A3D2A' }}>
                1 GEMINI CALL · ~5K TOKENS
              </span>
            </div>

            {/* Signal details */}
            <div className="px-4 py-3 grid grid-cols-3 gap-4" style={{ borderBottom: '1px solid #2E2820' }}>
              {[
                { label: 'ENTITY', value: selectedTrigger.ticker },
                { label: 'DATE', value: selectedTrigger.date },
                { label: 'MAGNITUDE', value: `${selectedTrigger.magnitudeSigma}σ`, color: sigmaColor(selectedTrigger.magnitudeSigma) },
              ].map(({ label, value, color }) => (
                <div key={label}>
                  <div className="text-[8px] font-mono tracking-wider mb-1" style={{ color: '#4A3D2A' }}>{label}</div>
                  <div className="text-[11px] font-mono font-medium" style={{ color: color ?? '#EDE4D4' }}>{value}</div>
                </div>
              ))}
            </div>

            {/* Streaming text */}
            <div className="px-4 py-3 min-h-[72px]">
              <div className="text-[8px] font-mono tracking-wider mb-2" style={{ color: '#4A3D2A' }}>ASSESSMENT</div>
              <p className="text-[10px] font-mono leading-relaxed" style={{ color: '#8C7A5E' }}>
                {tier2EvalText}
                {!tier2EvalDone && tier2EvalText.length > 0 && (
                  <span
                    className="inline-block w-[5px] h-[11px] ml-0.5 align-text-bottom"
                    style={{ backgroundColor: '#D4651A', animation: 'blink 0.7s step-end infinite' }}
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
                    style={{ borderTop: '1px solid #D14B3530', backgroundColor: '#2A0E09' }}
                  >
                    <div className="flex flex-col gap-1">
                      <span
                        className="text-[10px] tracking-wider font-medium"
                        style={{
                          fontFamily: 'Syne, sans-serif',
                          color: '#D14B35',
                          animation: 'pulse-tier 0.8s ease-in-out 3',
                        }}
                      >
                        ↑ ESCALATE — Signal warrants deep investigation
                      </span>
                      <span className="text-[9px] font-mono" style={{ color: '#8C7A5E' }}>
                        Generating competing hypotheses · Testing against structural evidence · Eliminating what's impossible
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
