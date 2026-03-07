import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import type {
  TierLevel,
  SystemStatus,
  Hypothesis,
  EvidenceAtom,
  EvidencePending,
  EvidenceRequest,
  Cycle,
  CycleSnapshot,
  CycleHistoryEntry,
  AlertDiagnosis,
  ContagionTarget,
  ContextWindow,
  ContextWindowTracking,
  AgentStatus,
  TokenUsage,
  KeyInsight,
  InvestigatorCycleWindow,
  PackagerCycleWindow,
  OrchestratorCycleWindow,
} from '../types/investigation'
import type { WSMessage } from '../types/api'

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

const defaultTokenUsage: TokenUsage = {
  totalInput: 0,
  totalOutput: 0,
  totalReasoning: 0,
  byAgent: {
    orchestrator: { totalInput: 0, totalOutput: 0, totalReasoning: 0, geminiCalls: 0 },
    investigator: { totalInput: 0, totalOutput: 0, totalReasoning: 0, geminiCalls: 0 },
    evidencePackager: { totalInput: 0, totalOutput: 0, totalReasoning: 0, geminiCalls: 0 },
  },
  byCycle: [],
}

const defaultContextWindowTracking: ContextWindowTracking = {
  orchestrator: {
    type: 'FIXED',
    totalContext: TOTAL_CAPACITY,
    perCycleSnapshot: [],
  },
  investigator: {
    type: 'FRESH_PER_CYCLE',
    totalContext: TOTAL_CAPACITY,
    perCycle: [],
  },
  evidencePackager: {
    type: 'FRESH_PER_RUN',
    totalContext: TOTAL_CAPACITY,
    perCycle: [],
  },
}

// ─── State Interfaces ────────────────────────────────────────────────────────

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
  contextWindowTracking: ContextWindowTracking

  hypotheses: Hypothesis[]
  cycles: Cycle[]
  cycleHistory: CycleHistoryEntry[]
  evidenceAtoms: EvidenceAtom[]
  evidencePending: EvidencePending[]
  activeEvidenceRequests: EvidenceRequest[]
  agentStatuses: Record<'structural' | 'market' | 'news', AgentStatus>

  tier2EvalText: string
  tier2EvalDone: boolean

  compressedReasoning: string
  keyInsights: KeyInsight[]

  tokenUsage: TokenUsage

  alertDiagnosis: AlertDiagnosis | null
  contagionTargets: ContagionTarget[]
  allCycleSnapshots: CycleSnapshot[]

  applyWebSocketMessage: (msg: WSMessage) => void
  resetInvestigation: () => void
  setEntity: (name: string, ticker: string) => void
}

interface UIState {
  activeScreen: 0 | 1 | 2
  rightPanelTab: 'evidence' | 'tokens' | 'reasoning'
  mockMode: boolean
  mockPlaybackSpeed: number
  isTransitioning: boolean
  alertFlashActive: boolean
  tierTransitionFrom: TierLevel | null
  tierTransitionTo: TierLevel | null

  setActiveScreen: (screen: 0 | 1 | 2) => void
  setRightPanelTab: (tab: 'evidence' | 'tokens' | 'reasoning') => void
  setMockMode: (enabled: boolean) => void
  setMockPlaybackSpeed: (speed: number) => void
  triggerAlertFlash: () => void
  setTierTransition: (from: TierLevel | null, to: TierLevel | null) => void
}

type Store = InvestigationState & UIState

// ─── Store ───────────────────────────────────────────────────────────────────

export const useStore = create<Store>()(
  immer((set, _get) => ({
    // Investigation defaults
    entityName: null,
    ticker: null,
    currentTier: null,
    systemStatus: 'IDLE',
    currentCycle: 0,
    maxCycles: 5,
    budgetUsedPercent: 0,
    isCompressing: false,

    contextWindow: { ...defaultContextWindow },
    contextWindowTracking: {
      orchestrator: { ...defaultContextWindowTracking.orchestrator, perCycleSnapshot: [] },
      investigator: { ...defaultContextWindowTracking.investigator, perCycle: [] },
      evidencePackager: { ...defaultContextWindowTracking.evidencePackager, perCycle: [] },
    },

    hypotheses: [],
    cycles: [],
    cycleHistory: [],
    evidenceAtoms: [],
    evidencePending: [],
    activeEvidenceRequests: [],
    agentStatuses: { ...defaultAgentStatuses },

    tier2EvalText: '',
    tier2EvalDone: false,

    compressedReasoning: '',
    keyInsights: [],

    tokenUsage: structuredClone(defaultTokenUsage),

    alertDiagnosis: null,
    contagionTargets: [],
    allCycleSnapshots: [],

    // UI defaults
    activeScreen: 0,
    rightPanelTab: 'evidence',
    mockMode: true,
    mockPlaybackSpeed: 1,
    isTransitioning: false,
    alertFlashActive: false,
    tierTransitionFrom: null,
    tierTransitionTo: null,

    // UI actions
    setActiveScreen: (screen) => set((s) => { s.activeScreen = screen }),
    setRightPanelTab: (tab) => set((s) => { s.rightPanelTab = tab }),
    setMockMode: (enabled) => set((s) => { s.mockMode = enabled }),
    setMockPlaybackSpeed: (speed) => set((s) => { s.mockPlaybackSpeed = speed }),
    triggerAlertFlash: () => {
      set((s) => { s.alertFlashActive = true })
      setTimeout(() => set((s) => { s.alertFlashActive = false }), 1000)
    },
    setTierTransition: (from, to) => set((s) => {
      s.tierTransitionFrom = from
      s.tierTransitionTo = to
    }),

    // Investigation actions
    setEntity: (name, ticker) => set((s) => {
      s.entityName = name
      s.ticker = ticker
    }),

    resetInvestigation: () => set((s) => {
      s.entityName = null
      s.ticker = null
      s.currentTier = null
      s.systemStatus = 'IDLE'
      s.currentCycle = 0
      s.budgetUsedPercent = 0
      s.isCompressing = false
      s.contextWindow = { ...defaultContextWindow }
      s.contextWindowTracking = {
        orchestrator: { ...defaultContextWindowTracking.orchestrator, perCycleSnapshot: [] },
        investigator: { ...defaultContextWindowTracking.investigator, perCycle: [] },
        evidencePackager: { ...defaultContextWindowTracking.evidencePackager, perCycle: [] },
      }
      s.hypotheses = []
      s.cycles = []
      s.cycleHistory = []
      s.evidenceAtoms = []
      s.evidencePending = []
      s.activeEvidenceRequests = []
      s.agentStatuses = { ...defaultAgentStatuses }
      s.tier2EvalText = ''
      s.tier2EvalDone = false
      s.compressedReasoning = ''
      s.keyInsights = []
      s.tokenUsage = structuredClone(defaultTokenUsage)
      s.alertDiagnosis = null
      s.contagionTargets = []
      s.allCycleSnapshots = []
      s.activeScreen = 0
      s.rightPanelTab = 'evidence'
    }),

    applyWebSocketMessage: (msg: WSMessage) => set((s) => {
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
          if (msg.done) s.tier2EvalDone = true
          break

        case 'TIER_ESCALATED':
          // T2 → T3: signal confirmed, begin full investigation
          s.currentTier = msg.to
          s.systemStatus = 'INVESTIGATING'
          s.activeScreen = 1
          break

        case 'CYCLE_STARTED':
          s.currentCycle = msg.cycle_number
          s.systemStatus = 'INVESTIGATING'
          s.agentStatuses = { structural: 'fetching', market: 'fetching', news: 'fetching' }
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
              evidenceCollected: [],
            })
          }
          break

        case 'TOKENS_UPDATED':
          s.contextWindow.reasoningTokens = msg.reasoning
          s.contextWindow.evidenceTokens = msg.evidence
          s.contextWindow.compressedTokens = msg.compressed
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

        case 'HYPOTHESIS_SCORED': {
          const h = s.hypotheses.find((h) => h.id === msg.id)
          if (h) h.currentConfidence = msg.confidence
          break
        }

        case 'HYPOTHESIS_ELIMINATED': {
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
          break
        }

        case 'EVIDENCE_ATOM_ARRIVED':
          if (!s.evidenceAtoms.find((a) => a.id === msg.atom.id)) {
            s.evidenceAtoms.unshift(msg.atom)
            // Add to current cycle's evidence collected
            const cycle = s.cycles.find((c) => c.cycleNumber === msg.atom.cycle)
            if (cycle && cycle.evidenceCollected) {
              cycle.evidenceCollected.push(msg.atom.id)
            }
          }
          break

        case 'EVIDENCE_PENDING_ADDED':
          s.evidencePending.push(msg.item)
          break

        case 'EVIDENCE_PENDING_FULFILLED':
          s.evidencePending = s.evidencePending.filter((p) => p.description !== msg.description)
          break

        case 'AGENT_STATUS_CHANGED':
          s.agentStatuses[msg.agent] = msg.status
          break

        case 'CYCLE_COMPLETE': {
          const cycle = s.cycles.find((c) => c.cycleNumber === msg.cycle_number)
          if (cycle) {
            cycle.status = 'completed'
            cycle.hypothesesEnd = msg.survivors
            cycle.durationMs = msg.duration_ms
            cycle.keyInsight = msg.key_insight
            if (msg.evidence_collected) cycle.evidenceCollected = msg.evidence_collected
            // Snapshot at end of cycle (not start — CYCLE_STARTED was too early)
            cycle.contextSnapshot = { cycleNumber: msg.cycle_number, ...s.contextWindow }
          }
          s.allCycleSnapshots.push({
            cycleNumber: msg.cycle_number,
            ...s.contextWindow,
          })
          break
        }

        case 'CYCLE_HISTORY_UPDATED':
          {
            const existing = s.cycleHistory.findIndex((c) => c.cycle === msg.entry.cycle)
            if (existing >= 0) s.cycleHistory[existing] = msg.entry
            else s.cycleHistory.push(msg.entry)
          }
          break

        case 'COMPRESSION_STARTED':
          s.isCompressing = true
          break

        case 'COMPRESSION_COMPLETE':
          s.isCompressing = false
          s.contextWindow.compressedTokens = msg.compressed_tokens
          s.contextWindow.reasoningTokens = 0
          {
            const cycle = s.cycles.find((c) => c.cycleNumber === s.currentCycle)
            if (cycle) cycle.compressionRatio = msg.compression_ratio
          }
          break

        case 'COMPRESSED_REASONING_UPDATED':
          s.compressedReasoning = msg.text
          break

        case 'KEY_INSIGHT_ADDED':
          s.keyInsights.push(msg.insight)
          break

        case 'TOKEN_USAGE_CYCLE': {
          const existing = s.tokenUsage.byCycle.findIndex((c) => c.cycle === msg.data.cycle)
          if (existing >= 0) s.tokenUsage.byCycle[existing] = msg.data
          else s.tokenUsage.byCycle.push(msg.data)

          // Accumulate totals
          s.tokenUsage.byAgent.investigator.totalInput += msg.data.investigatorInput
          s.tokenUsage.byAgent.investigator.totalReasoning += msg.data.investigatorReasoning
          s.tokenUsage.byAgent.investigator.geminiCalls += 1
          s.tokenUsage.byAgent.evidencePackager.totalInput += msg.data.packagerInput
          s.tokenUsage.byAgent.evidencePackager.totalOutput += msg.data.packagerTagging
          s.tokenUsage.byAgent.evidencePackager.geminiCalls += 1
          if (msg.data.orchestratorGemini) {
            s.tokenUsage.byAgent.orchestrator.geminiCalls += 1
          }
          s.tokenUsage.totalInput += msg.data.investigatorInput + msg.data.packagerInput
          s.tokenUsage.totalReasoning += msg.data.investigatorReasoning
          break
        }

        case 'INVESTIGATOR_WINDOW_UPDATE':
          {
            const existing = s.contextWindowTracking.investigator.perCycle.findIndex(
              (c: InvestigatorCycleWindow) => c.cycle === msg.data.cycle
            )
            if (existing >= 0) s.contextWindowTracking.investigator.perCycle[existing] = msg.data
            else s.contextWindowTracking.investigator.perCycle.push(msg.data)
          }
          break

        case 'PACKAGER_WINDOW_UPDATE':
          {
            const existing = s.contextWindowTracking.evidencePackager.perCycle.findIndex(
              (c: PackagerCycleWindow) => c.cycle === msg.data.cycle
            )
            if (existing >= 0) s.contextWindowTracking.evidencePackager.perCycle[existing] = msg.data
            else s.contextWindowTracking.evidencePackager.perCycle.push(msg.data)
          }
          break

        case 'ORCHESTRATOR_WINDOW_UPDATE':
          {
            const existing = s.contextWindowTracking.orchestrator.perCycleSnapshot.findIndex(
              (c: OrchestratorCycleWindow) => c.cycle === msg.data.cycle
            )
            if (existing >= 0) s.contextWindowTracking.orchestrator.perCycleSnapshot[existing] = msg.data
            else s.contextWindowTracking.orchestrator.perCycleSnapshot.push(msg.data)
          }
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
