import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import type {
  TierLevel,
  SystemStatus,
  Hypothesis,
  EvidenceAtom,
  EvidenceRequest,
  Cycle,
  CycleSnapshot,
  AlertDiagnosis,
  ContagionTarget,
  ContextWindow,
  AgentStatus,
} from '../types/investigation'
import type { WSMessage } from '../types/api'

// ─── Investigation State ───────────────────────────────────────────────────

interface InvestigationState {
  entityName: string | null
  ticker: string | null
  currentTier: TierLevel | null
  systemStatus: SystemStatus
  currentCycle: number
  maxCycles: number
  budgetUsedPercent: number
  isCompressing: boolean

  contextWindow: ContextWindow

  hypotheses: Hypothesis[]
  cycles: Cycle[]
  evidenceAtoms: EvidenceAtom[]
  activeEvidenceRequests: EvidenceRequest[]
  agentStatuses: Record<'structural' | 'market' | 'news', AgentStatus>

  tier2EvalText: string
  tier2EvalDone: boolean

  alertDiagnosis: AlertDiagnosis | null
  contagionTargets: ContagionTarget[]
  allCycleSnapshots: CycleSnapshot[]

  // Actions
  applyWebSocketMessage: (msg: WSMessage) => void
  resetInvestigation: () => void
  setEntity: (name: string, ticker: string) => void
}

// ─── UI State ─────────────────────────────────────────────────────────────

interface UIState {
  activeScreen: 0 | 1 | 2
  mockMode: boolean
  mockPlaybackSpeed: number
  isTransitioning: boolean
  alertFlashActive: boolean
  tierTransitionFrom: TierLevel | null
  tierTransitionTo: TierLevel | null

  setActiveScreen: (screen: 0 | 1 | 2) => void
  setMockMode: (enabled: boolean) => void
  setMockPlaybackSpeed: (speed: number) => void
  triggerAlertFlash: () => void
  setTierTransition: (from: TierLevel | null, to: TierLevel | null) => void
}

// ─── Combined Store ────────────────────────────────────────────────────────

type Store = InvestigationState & UIState

const TOTAL_CAPACITY = 1_000_000

const defaultContextWindow: ContextWindow = {
  reasoningTokens: 0,
  evidenceTokens: 0,
  compressedTokens: 0,
  totalCapacity: TOTAL_CAPACITY,
}

const defaultAgentStatuses = {
  structural: 'idle' as AgentStatus,
  market: 'idle' as AgentStatus,
  news: 'idle' as AgentStatus,
}

export const useStore = create<Store>()(
  immer((set, _get) => ({
    // ── Investigation defaults ──
    entityName: null,
    ticker: null,
    currentTier: null,
    systemStatus: 'IDLE',
    currentCycle: 0,
    maxCycles: 5,
    budgetUsedPercent: 0,
    isCompressing: false,

    contextWindow: { ...defaultContextWindow },

    hypotheses: [],
    cycles: [],
    evidenceAtoms: [],
    activeEvidenceRequests: [],
    agentStatuses: { ...defaultAgentStatuses },

    tier2EvalText: '',
    tier2EvalDone: false,

    alertDiagnosis: null,
    contagionTargets: [],
    allCycleSnapshots: [],

    // ── UI defaults ──
    activeScreen: 0,
    mockMode: true,
    mockPlaybackSpeed: 1,
    isTransitioning: false,
    alertFlashActive: false,
    tierTransitionFrom: null,
    tierTransitionTo: null,

    // ── UI actions ──
    setActiveScreen: (screen) =>
      set((s) => {
        s.activeScreen = screen
      }),

    setMockMode: (enabled) =>
      set((s) => {
        s.mockMode = enabled
      }),

    setMockPlaybackSpeed: (speed) =>
      set((s) => {
        s.mockPlaybackSpeed = speed
      }),

    triggerAlertFlash: () => {
      set((s) => {
        s.alertFlashActive = true
      })
      setTimeout(() => {
        set((s) => {
          s.alertFlashActive = false
        })
      }, 1000)
    },

    setTierTransition: (from, to) =>
      set((s) => {
        s.tierTransitionFrom = from
        s.tierTransitionTo = to
      }),

    // ── Investigation actions ──
    setEntity: (name, ticker) =>
      set((s) => {
        s.entityName = name
        s.ticker = ticker
      }),

    resetInvestigation: () =>
      set((s) => {
        s.entityName = null
        s.ticker = null
        s.currentTier = null
        s.systemStatus = 'IDLE'
        s.currentCycle = 0
        s.budgetUsedPercent = 0
        s.isCompressing = false
        s.contextWindow = { ...defaultContextWindow }
        s.hypotheses = []
        s.cycles = []
        s.evidenceAtoms = []
        s.activeEvidenceRequests = []
        s.agentStatuses = { ...defaultAgentStatuses }
        s.tier2EvalText = ''
        s.tier2EvalDone = false
        s.alertDiagnosis = null
        s.contagionTargets = []
        s.allCycleSnapshots = []
        s.activeScreen = 0
      }),

    applyWebSocketMessage: (msg: WSMessage) =>
      set((s) => {
        switch (msg.type) {
          case 'SESSION_STARTED':
            s.entityName = msg.entity
            s.currentTier = msg.tier
            s.systemStatus = 'EVALUATING'
            s.tier2EvalText = ''
            s.tier2EvalDone = false
            break

          case 'TIER2_EVALUATION':
            s.tier2EvalText += msg.text
            if (msg.done) {
              s.tier2EvalDone = true
            }
            break

          case 'TIER_ESCALATED':
            s.currentTier = msg.to
            s.systemStatus = 'INVESTIGATING'
            if (msg.to >= 3) {
              s.activeScreen = 1
            }
            break

          case 'CYCLE_STARTED':
            s.currentCycle = msg.cycle_number
            s.systemStatus = 'INVESTIGATING'
            s.agentStatuses = { structural: 'fetching', market: 'fetching', news: 'fetching' }
            // Add pending cycle
            if (!s.cycles.find((c) => c.cycleNumber === msg.cycle_number)) {
              s.cycles.push({
                cycleNumber: msg.cycle_number,
                status: 'active',
                hypothesesStart: s.hypotheses.length,
                hypothesesEnd: s.hypotheses.length,
                eliminations: [],
                contradictionsFound: 0,
                durationMs: 0,
                contextSnapshot: {
                  cycleNumber: msg.cycle_number,
                  ...s.contextWindow,
                },
              })
            }
            break

          case 'TOKENS_UPDATED':
            s.contextWindow.reasoningTokens = msg.reasoning
            s.contextWindow.evidenceTokens = msg.evidence
            s.contextWindow.compressedTokens = msg.compressed
            // Rough budget estimate based on token usage
            s.budgetUsedPercent = Math.min(
              100,
              Math.round(((msg.reasoning + msg.evidence + msg.compressed) / TOTAL_CAPACITY) * 100 * 3)
            )
            break

          case 'HYPOTHESIS_GENERATED':
            if (!s.hypotheses.find((h) => h.id === msg.hypothesis.id)) {
              s.hypotheses.push(msg.hypothesis)
            }
            break

          case 'HYPOTHESIS_SCORED':
            {
              const h = s.hypotheses.find((h) => h.id === msg.id)
              if (h) h.currentConfidence = msg.confidence
            }
            break

          case 'HYPOTHESIS_ELIMINATED':
            {
              const h = s.hypotheses.find((h) => h.id === msg.id)
              if (h) {
                h.status = 'eliminated'
                h.eliminatedInCycle = msg.cycle
                h.killAtomId = msg.kill_atom
                h.killReason = msg.kill_reason
              }
              const cycle = s.cycles.find((c) => c.cycleNumber === msg.cycle)
              if (cycle) {
                cycle.eliminations.push(msg.id)
                cycle.hypothesesEnd = s.hypotheses.filter((h) => h.status === 'surviving').length
              }
            }
            break

          case 'EVIDENCE_ATOM_ARRIVED':
            if (!s.evidenceAtoms.find((a) => a.id === msg.atom.id)) {
              s.evidenceAtoms.unshift(msg.atom) // newest first
            }
            break

          case 'AGENT_STATUS_CHANGED':
            s.agentStatuses[msg.agent] = msg.status
            break

          case 'CYCLE_COMPLETE':
            {
              const cycle = s.cycles.find((c) => c.cycleNumber === msg.cycle_number)
              if (cycle) {
                cycle.status = 'completed'
                cycle.hypothesesEnd = msg.survivors
                cycle.durationMs = msg.duration_ms
              }
              s.allCycleSnapshots.push({
                cycleNumber: msg.cycle_number,
                ...s.contextWindow,
              })
            }
            break

          case 'COMPRESSION_STARTED':
            s.isCompressing = true
            break

          case 'COMPRESSION_COMPLETE':
            s.isCompressing = false
            s.contextWindow.compressedTokens = msg.compressed_tokens
            s.contextWindow.reasoningTokens = 0
            break

          case 'CONVERGENCE_REACHED':
            s.alertDiagnosis = msg.diagnosis
            s.systemStatus = 'ALERT'
            s.activeScreen = 2
            break

          case 'CONTAGION_DETECTED':
            s.contagionTargets = msg.targets
            break

          case 'INVESTIGATION_COMPLETE':
            s.systemStatus = s.alertDiagnosis ? 'ALERT' : 'ALL_CLEAR'
            break
        }
      }),
  }))
)
