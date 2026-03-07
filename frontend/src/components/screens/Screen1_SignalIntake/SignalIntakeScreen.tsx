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

  const sigmaColor =
    !selectedTrigger ? '#475569'
    : selectedTrigger.magnitudeSigma >= 4 ? '#DC2626'
    : selectedTrigger.magnitudeSigma >= 3 ? '#D97706'
    : '#059669'

  return (
    <div
      className="h-full flex flex-col items-center justify-center p-8 gap-6"
      style={{ backgroundColor: '#0F172A' }}
    >
      {/* Title block */}
      <div className="text-center max-w-2xl">
        <div className="text-[10px] font-terminal text-[#273548] tracking-[0.3em] mb-2">
          ITERATIVE HYPOTHESIS ELIMINATION ENGINE
        </div>
        <h1 className="text-2xl font-display font-bold text-[#E2E8F0] mb-1">
          Signal Intake
        </h1>
        <p className="text-sm font-evidence text-[#475569] leading-relaxed">
          Trigger events are evaluated for severity before initiating investigation.
          Most signals are dismissed at Tier 2. Only credible crises escalate.
        </p>
      </div>

      {/* Tier pipeline diagram */}
      <div className="flex items-center gap-1 text-[8px] font-terminal">
        {/* Tier 2 */}
        <div className="flex flex-col items-center gap-1 px-3 py-2 rounded border border-[#78350F]/40 bg-[#1A0900]">
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-[#EAB308]" style={{ boxShadow: '0 0 4px #EAB308' }} />
            <span className="text-[#EAB308] font-bold tracking-widest">T2</span>
          </div>
          <span className="text-[#A16207] tracking-wider">SEMANTIC EVAL</span>
          <span className="text-[#473409] tracking-wider">1 GEMINI CALL</span>
        </div>

        {/* Arrow: escalate or dismiss */}
        <div className="flex flex-col items-center gap-1 px-1">
          <span className="text-[#059669] tracking-wide">→ ESCALATE</span>
          <div className="h-px w-12 bg-[#1E293B]" />
          <span className="text-[#334155] tracking-wide">→ DISMISS</span>
        </div>

        {/* Tier 3 */}
        <div className="flex flex-col items-center gap-1 px-3 py-2 rounded border border-[#9A3412]/40 bg-[#1A0900]">
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-[#F97316]" style={{ boxShadow: '0 0 4px #F97316' }} />
            <span className="text-[#F97316] font-bold tracking-widest">T3</span>
          </div>
          <span className="text-[#9A3412] tracking-wider">INITIAL PASS</span>
          <span className="text-[#473409] tracking-wider">1-2 CYCLES</span>
        </div>

        {/* Arrow: promote or demote */}
        <div className="flex flex-col items-center gap-1 px-1">
          <span className="text-[#EF4444] tracking-wide">→ PROMOTE</span>
          <div className="h-px w-12 bg-[#1E293B]" />
          <span className="text-[#334155] tracking-wide">→ DEMOTE</span>
        </div>

        {/* Tier 4 */}
        <div
          className="flex flex-col items-center gap-1 px-3 py-2 rounded border"
          style={{
            borderColor: '#EF444440',
            backgroundColor: '#1A0000',
            boxShadow: '0 0 8px #EF444420',
          }}
        >
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-[#EF4444]" style={{ boxShadow: '0 0 6px #EF4444', animation: 'pulse-dot 1s ease-in-out infinite' }} />
            <span className="text-[#EF4444] font-bold tracking-widest">T4</span>
          </div>
          <span className="text-[#991B1B] tracking-wider">FULL INVESTIGATION</span>
          <span className="text-[#473409] tracking-wider">4-5 DEEP CYCLES</span>
        </div>

        {/* Arrow: outcome */}
        <div className="flex flex-col items-center gap-1 px-1">
          <span className="text-[#EF4444] tracking-wide">→ ALERT</span>
          <div className="h-px w-12 bg-[#1E293B]" />
          <span className="text-[#059669] tracking-wide">→ ALL-CLEAR</span>
        </div>

        {/* Agents */}
        <div className="flex flex-col gap-1">
          <div className="px-2.5 py-1 rounded border border-[#1E293B] bg-[#0D1526]">
            <span className="text-[#3B82F6] tracking-wider">ORCHESTRATOR</span>
            <span className="text-[#334155] ml-1">STATEFUL</span>
          </div>
          <div className="px-2.5 py-1 rounded border border-[#1E293B] bg-[#0D1526]">
            <span className="text-[#10B981] tracking-wider">INVESTIGATOR</span>
            <span className="text-[#334155] ml-1">FRESH/CYCLE</span>
          </div>
          <div className="px-2.5 py-1 rounded border border-[#1E293B] bg-[#0D1526]">
            <span className="text-[#8B5CF6] tracking-wider">PKG + 3 AGENTS</span>
            <span className="text-[#334155] ml-1">FRESH/RUN</span>
          </div>
        </div>
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
            <div
              className="absolute left-0 top-0 bottom-0 w-0.5"
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
                  <div className="text-xl font-terminal font-bold" style={{ color: sigmaColor }}>
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
            <div className="px-4 py-2 border-b border-[#1E293B] flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div
                  className="w-1.5 h-1.5 rounded-full bg-[#EAB308]"
                  style={{ animation: 'pulse-dot 0.8s ease-in-out infinite' }}
                />
                <span className="text-[9px] font-terminal text-[#EAB308] tracking-widest">
                  TIER 2 — SEMANTIC EVALUATION — ORCHESTRATOR
                </span>
              </div>
              <span className="text-[8px] font-terminal text-[#334155] tracking-wider">
                1 GEMINI CALL · ~5K TOKENS
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
                    className="inline-block w-[6px] h-3 bg-[#EAB308] ml-0.5 align-text-bottom"
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
                    style={{ borderColor: '#F9731630', backgroundColor: '#100500' }}
                  >
                    <div className="flex items-start gap-3">
                      <div className="flex flex-col gap-1">
                        <span
                          className="text-[10px] font-terminal font-bold tracking-widest text-[#F97316]"
                          style={{ animation: 'pulse-tier 0.8s ease-in-out 3' }}
                        >
                          ▲ ESCALATE → TIER 3: INITIAL INVESTIGATION
                        </span>
                        <span className="text-[9px] font-terminal text-[#475569]">
                          1-2 quick cycles · Promotes to Tier 4 full investigation if warranted
                        </span>
                      </div>
                    </div>
                    <div className="mt-2 flex gap-2 items-center">
                      <TagPill type="critical" label="T2 → T3" />
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
