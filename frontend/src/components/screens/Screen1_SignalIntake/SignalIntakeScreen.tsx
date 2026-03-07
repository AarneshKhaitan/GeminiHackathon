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

    // Set entity immediately
    applyWebSocketMessage({ type: 'SESSION_STARTED', entity: trigger.entity, tier: 2 })
    useStore.getState().setEntity(trigger.entity, trigger.ticker)

    // Start mock playback (which drives all subsequent events)
    startMock()
    setEvalPhase('done')
  }

  const sigmaColor =
    !selectedTrigger ? '#475569'
    : selectedTrigger.magnitudeSigma >= 4 ? '#DC2626'
    : selectedTrigger.magnitudeSigma >= 3 ? '#D97706'
    : '#059669'

  return (
    <div
      className="h-full flex flex-col items-center justify-center p-8 gap-8"
      style={{ backgroundColor: '#0F172A' }}
    >
      {/* Title block */}
      <div className="text-center max-w-xl">
        <div className="text-[10px] font-terminal text-[#273548] tracking-[0.3em] mb-2">
          ITERATIVE HYPOTHESIS ELIMINATION ENGINE
        </div>
        <h1 className="text-2xl font-display font-bold text-[#E2E8F0] mb-1">
          Signal Intake
        </h1>
        <p className="text-sm font-evidence text-[#475569] leading-relaxed">
          Select a trigger event to begin Tier 2 semantic evaluation.
          The Orchestrator will assess severity and escalate to full investigation if warranted.
        </p>
      </div>

      {/* Architecture note */}
      <div className="flex items-center gap-2 text-[9px] font-terminal text-[#273548]">
        <span className="px-1.5 py-0.5 rounded border border-[#1E293B] bg-[#0D1526] text-[#334155]">ORCHESTRATOR</span>
        <span>→</span>
        <span className="px-1.5 py-0.5 rounded border border-[#1E293B] bg-[#0D1526] text-[#334155]">INVESTIGATOR</span>
        <span>→</span>
        <span className="px-1.5 py-0.5 rounded border border-[#1E293B] bg-[#0D1526] text-[#334155]">EVIDENCE COLLECTOR</span>
      </div>

      {/* Trigger buttons */}
      <div className="flex flex-col gap-3 w-full max-w-2xl">
        <div className="text-[9px] font-terminal text-[#273548] tracking-widest mb-1">
          SELECT TRIGGER EVENT
        </div>
        {TRIGGERS.map((trigger) => (
          <motion.button
            key={trigger.id}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            disabled={evalPhase !== 'idle'}
            onClick={() => handleTrigger(trigger)}
            className="relative text-left rounded border overflow-hidden group"
            style={{
              borderColor: selectedTrigger?.id === trigger.id ? '#2563EB' : '#1E293B',
              backgroundColor: selectedTrigger?.id === trigger.id ? '#0C1A3A' : '#0D1526',
              opacity: evalPhase !== 'idle' && selectedTrigger?.id !== trigger.id ? 0.4 : 1,
            }}
          >
            {/* Left accent bar */}
            <div
              className="absolute left-0 top-0 bottom-0 w-0.5 transition-all duration-300"
              style={{
                backgroundColor:
                  trigger.magnitudeSigma >= 4 ? '#DC2626'
                  : trigger.magnitudeSigma >= 3.5 ? '#D97706'
                  : '#2563EB',
              }}
            />
            <div className="pl-4 pr-4 py-3">
              <div className="flex items-start gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-terminal font-bold text-[#E2E8F0]">
                      {trigger.ticker}
                    </span>
                    <span className="text-[10px] font-terminal text-[#475569]">·</span>
                    <span className="text-xs font-display text-[#94A3B8]">{trigger.entity}</span>
                    <span className="text-[9px] font-terminal text-[#334155]">{trigger.date}</span>
                  </div>
                  <p className="text-xs font-evidence text-[#64748B] leading-relaxed">
                    {trigger.event}
                  </p>
                </div>
                <div className="shrink-0 text-right">
                  <div
                    className="text-xl font-terminal font-bold"
                    style={{ color: sigmaColor }}
                  >
                    {trigger.magnitudeSigma}σ
                  </div>
                  <div className="text-[8px] font-terminal text-[#334155]">MAGNITUDE</div>
                </div>
              </div>
            </div>
          </motion.button>
        ))}
      </div>

      {/* Tier 2 evaluation panel */}
      <AnimatePresence>
        {selectedTrigger && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
            className="w-full max-w-2xl rounded border border-[#1E293B] overflow-hidden"
            style={{ backgroundColor: '#0A1120' }}
          >
            {/* Panel header */}
            <div className="px-4 py-2 border-b border-[#1E293B] flex items-center gap-2">
              <div
                className="w-1.5 h-1.5 rounded-full bg-[#D97706]"
                style={{ animation: 'pulse-dot 0.8s ease-in-out infinite' }}
              />
              <span className="text-[9px] font-terminal text-[#D97706] tracking-widest">
                TIER 2 SEMANTIC EVALUATION — ORCHESTRATOR
              </span>
            </div>

            {/* Signal card */}
            <div className="px-4 py-3 border-b border-[#1E293B] grid grid-cols-3 gap-4">
              <div>
                <div className="text-[8px] font-terminal text-[#273548] tracking-wider">ENTITY</div>
                <div className="text-sm font-terminal font-bold text-[#E2E8F0]">{selectedTrigger.ticker}</div>
              </div>
              <div>
                <div className="text-[8px] font-terminal text-[#273548] tracking-wider">DATE</div>
                <div className="text-sm font-terminal text-[#94A3B8]">{selectedTrigger.date}</div>
              </div>
              <div>
                <div className="text-[8px] font-terminal text-[#273548] tracking-wider">MAGNITUDE</div>
                <div className="text-sm font-terminal font-bold" style={{ color: sigmaColor }}>
                  {selectedTrigger.magnitudeSigma}σ
                </div>
              </div>
            </div>

            {/* Streaming evaluation text */}
            <div className="px-4 py-3 min-h-[80px]">
              <div className="text-[9px] font-terminal text-[#334155] tracking-wider mb-2">
                ASSESSMENT
              </div>
              <p className="text-xs font-evidence text-[#64748B] leading-relaxed">
                {tier2EvalText}
                {!tier2EvalDone && tier2EvalText.length > 0 && (
                  <span
                    className="inline-block w-[6px] h-3 bg-[#10B981] ml-0.5 align-text-bottom"
                    style={{ animation: 'blink 0.7s step-end infinite' }}
                  />
                )}
              </p>
            </div>

            {/* Decision */}
            <AnimatePresence>
              {tier2EvalDone && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  transition={{ duration: 0.3, delay: 0.2 }}
                  className="overflow-hidden"
                >
                  <div
                    className="px-4 py-3 border-t"
                    style={{ borderColor: '#DC262630', backgroundColor: '#100808' }}
                  >
                    <div className="flex items-center gap-3">
                      <span
                        className="text-[10px] font-terminal font-bold tracking-widest text-[#DC2626]"
                        style={{ animation: 'pulse-tier 0.8s ease-in-out 3' }}
                      >
                        ▲ ESCALATE TO TIER 3
                      </span>
                      <span className="text-[9px] font-terminal text-[#475569]">
                        Full hypothesis elimination cycle initiated
                      </span>
                    </div>
                    <div className="mt-2 flex gap-2">
                      <TagPill type="critical" label="TIER 2 → TIER 3" />
                      <span className="text-[8px] font-terminal text-[#334155]">
                        Transitioning to investigation dashboard...
                      </span>
                    </div>
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
