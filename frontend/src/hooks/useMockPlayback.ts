import { useEffect, useRef, useCallback } from 'react'
import { useStore } from '../store'
import svbCase from '../data/svb-case.json'
import type { WSMessage } from '../types/api'
import type {
  Hypothesis,
  EvidenceAtom,
  AlertDiagnosis,
  ContagionTarget,
  TokenUsageByCycle,
  CycleHistoryEntry,
  KeyInsight,
} from '../types/investigation'

type PlaybackEvent = {
  t_ms: number
  type: string
  [key: string]: unknown
}

// Maps raw fixture data into typed WSMessage objects
function buildMessage(event: PlaybackEvent, fixture: typeof svbCase): WSMessage | null {
  switch (event.type) {
    case 'SESSION_STARTED':
      return {
        type: 'SESSION_STARTED',
        entity: event.entity as string,
        tier: event.tier as 2 | 3,
      }

    case 'TIER2_EVALUATION':
      return {
        type: 'TIER2_EVALUATION',
        text: event.text as string,
        done: event.done as boolean,
      }

    case 'TIER_ESCALATED':
      return {
        type: 'TIER_ESCALATED',
        from: 2,
        to: 3,
      }

    case 'CYCLE_STARTED':
      return {
        type: 'CYCLE_STARTED',
        cycle_number: event.cycle_number as number,
      }

    case 'TOKENS_UPDATED':
      return {
        type: 'TOKENS_UPDATED',
        reasoning: event.reasoning as number,
        evidence: event.evidence as number,
        compressed: event.compressed as number,
      }

    case 'HYPOTHESIS_GENERATED': {
      const h = fixture.hypotheses.find((h) => h.id === event.hypothesis_id)
      if (!h) return null
      return {
        type: 'HYPOTHESIS_GENERATED',
        hypothesis: {
          id: h.id,
          label: h.label,
          description: h.description,
          status: 'surviving',
          initialConfidence: h.initial_confidence,
          currentConfidence: h.initial_confidence,
          generatedInCycle: h.generated_in_cycle,
          supportingAtoms: h.supporting_atoms,
          contradictingAtoms: h.contradicting_atoms,
        } as Hypothesis,
      }
    }

    case 'HYPOTHESIS_SCORED':
      return {
        type: 'HYPOTHESIS_SCORED',
        id: event.hypothesis_id as string,
        confidence: event.confidence as number,
      }

    case 'HYPOTHESIS_ELIMINATED':
      return {
        type: 'HYPOTHESIS_ELIMINATED',
        id: event.hypothesis_id as string,
        kill_atom: event.kill_atom as string,
        kill_reason: event.kill_reason as string,
        cycle: event.cycle as number,
      }

    case 'EVIDENCE_ATOM_ARRIVED': {
      const atom = fixture.evidence_atoms.find((a) => a.id === event.atom_id)
      if (!atom) return null
      return {
        type: 'EVIDENCE_ATOM_ARRIVED',
        atom: {
          id: atom.id,
          type: atom.type as 'empirical' | 'structural',
          observation: atom.observation,
          timestamp: atom.timestamp,
          source: atom.source,
          modality: atom.modality as 'text' | 'visual' | 'audio',
          confidence: atom.confidence,
          supports: atom.supports,
          contradicts: atom.contradicts,
          neutral: atom.neutral,
          novelty: atom.novelty as 'low' | 'medium' | 'high' | 'critical',
          quoteOrVisualAnchor: atom.quote_or_visual_anchor,
          cycle: atom.cycle,
        } as EvidenceAtom,
      }
    }

    case 'EVIDENCE_PENDING_ADDED':
      return {
        type: 'EVIDENCE_PENDING_ADDED',
        item: {
          type: event.item_type as 'structural' | 'market' | 'news' | 'filing',
          description: event.description as string,
          requestedInCycle: event.requested_in_cycle as number,
          requestedBecause: event.requested_because as string,
        },
      }

    case 'EVIDENCE_PENDING_FULFILLED':
      return {
        type: 'EVIDENCE_PENDING_FULFILLED',
        description: event.description as string,
      }

    case 'AGENT_STATUS_CHANGED':
      return {
        type: 'AGENT_STATUS_CHANGED',
        agent: event.agent as 'structural' | 'market' | 'news',
        status: event.status as 'idle' | 'fetching' | 'complete' | 'error',
      }

    case 'CYCLE_COMPLETE':
      return {
        type: 'CYCLE_COMPLETE',
        cycle_number: event.cycle_number as number,
        survivors: event.survivors as number,
        duration_ms: event.duration_ms as number,
        key_insight: (event.key_insight as string) ?? '',
        evidence_collected: (event.evidence_collected as string[]) ?? [],
      }

    case 'CYCLE_HISTORY_UPDATED':
      return {
        type: 'CYCLE_HISTORY_UPDATED',
        entry: {
          cycle: event.cycle as number,
          startCount: event.start_count as number,
          endCount: event.end_count as number,
          eliminated: event.eliminated as string[],
          evidenceCollected: event.evidence_collected as string[],
          crossModalDetected: (event.cross_modal_detected as string[]) ?? [],
          keyInsight: event.key_insight as string,
        } as CycleHistoryEntry,
      }

    case 'KEY_INSIGHT_ADDED':
      return {
        type: 'KEY_INSIGHT_ADDED',
        insight: {
          cycle: event.cycle as number,
          insight: event.insight as string,
        } as KeyInsight,
      }

    case 'TOKEN_USAGE_CYCLE':
      return {
        type: 'TOKEN_USAGE_CYCLE',
        data: {
          cycle: event.cycle as number,
          investigatorInput: event.investigator_input as number,
          investigatorReasoning: event.investigator_reasoning as number,
          packagerInput: event.packager_input as number,
          packagerTagging: event.packager_tagging as number,
          orchestratorGemini: event.orchestrator_gemini as boolean,
        } as TokenUsageByCycle,
      }

    case 'COMPRESSED_REASONING_UPDATED':
      return {
        type: 'COMPRESSED_REASONING_UPDATED',
        text: event.text as string,
      }

    case 'COMPRESSION_STARTED':
      return { type: 'COMPRESSION_STARTED' }

    case 'COMPRESSION_COMPLETE':
      return {
        type: 'COMPRESSION_COMPLETE',
        compressed_tokens: event.compressed_tokens as number,
        compression_ratio: event.compression_ratio as number,
      }

    case 'CONVERGENCE_REACHED': {
      const alert = fixture.alert
      return {
        type: 'CONVERGENCE_REACHED',
        diagnosis: {
          level: (alert.level ?? 'CRITICAL') as 'CRITICAL' | 'WARNING' | 'ALL-CLEAR',
          severity: alert.severity as 'critical' | 'high' | 'medium',
          headline: alert.headline,
          detail: alert.detail,
          diagnosis: alert.iterative_diagnosis,
          survivingHypotheses: alert.surviving_hypotheses,
          earliestSignalTimestamp: alert.earliest_signal_timestamp,
          earliestSignalAtomId: alert.earliest_signal_atom_id,
          singlePassSummary: alert.single_pass_summary,
          iterativeDiagnosis: alert.iterative_diagnosis,
          groundTruthMatch: alert.ground_truth_match,
        } as AlertDiagnosis,
      }
    }

    case 'CONTAGION_DETECTED': {
      const targets = fixture.contagion_targets.map((t) => ({
        entityName: t.entity_name,
        ticker: t.ticker,
        sharedRiskFactor: t.shared_risk_factor,
        riskScore: t.risk_score,
        promotedToTier: t.promoted_to_tier as 2 | 3,
      })) as ContagionTarget[]
      return { type: 'CONTAGION_DETECTED', targets }
    }

    default:
      return null
  }
}

export function useMockPlayback() {
  const { applyWebSocketMessage, mockPlaybackSpeed, triggerAlertFlash, mockMode } = useStore()
  const timeoutsRef = useRef<ReturnType<typeof setTimeout>[]>([])
  const isPlayingRef = useRef(false)

  const clearAll = useCallback(() => {
    timeoutsRef.current.forEach(clearTimeout)
    timeoutsRef.current = []
    isPlayingRef.current = false
  }, [])

  const start = useCallback(() => {
    if (isPlayingRef.current) return
    if (!mockMode) return

    clearAll()
    isPlayingRef.current = true

    const events = svbCase.playback_events as PlaybackEvent[]

    events.forEach((event) => {
      const delay = event.t_ms / mockPlaybackSpeed
      const id = setTimeout(() => {
        const msg = buildMessage(event, svbCase)
        if (msg) {
          applyWebSocketMessage(msg)
          if (msg.type === 'CONVERGENCE_REACHED') {
            triggerAlertFlash()
          }
        }
      }, delay)
      timeoutsRef.current.push(id)
    })
  }, [mockMode, mockPlaybackSpeed, applyWebSocketMessage, triggerAlertFlash, clearAll])

  const stop = useCallback(() => {
    clearAll()
  }, [clearAll])

  // Keyboard speed control: [ to slow, ] to speed up
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === '[') {
        const current = useStore.getState().mockPlaybackSpeed
        useStore.getState().setMockPlaybackSpeed(Math.max(0.25, current / 1.5))
      }
      if (e.key === ']') {
        const current = useStore.getState().mockPlaybackSpeed
        useStore.getState().setMockPlaybackSpeed(Math.min(10, current * 1.5))
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  useEffect(() => {
    return () => clearAll()
  }, [clearAll])

  return { start, stop }
}
