export type TierLevel = 2 | 3

export type SystemStatus =
  | 'IDLE'
  | 'EVALUATING'
  | 'INVESTIGATING'
  | 'CONVERGING'
  | 'ALERT'
  | 'ALL_CLEAR'

export type HypothesisStatus = 'surviving' | 'eliminated' | 'contradiction'

export type AgentStatus = 'idle' | 'fetching' | 'complete' | 'error'

export type EvidenceModality = 'text' | 'visual' | 'audio'

export type EvidenceType = 'structural' | 'market' | 'news' | 'filing'

export type Novelty = 'low' | 'medium' | 'high' | 'critical'

// ─── Hypothesis ─────────────────────────────────────────────────────────────

export interface CrossModalConflict {
  structuralAtom: string
  empiricalAtom: string
  structuralObservation: string
  empiricalObservation: string
  conflictSummary: string
  detectedInCycle: number
}

export interface Hypothesis {
  id: string
  label: string
  description: string
  status: HypothesisStatus
  initialConfidence: number
  currentConfidence: number
  generatedInCycle: number
  eliminatedInCycle?: number
  killAtomId?: string
  killReason?: string
  supportingAtoms: string[]
  contradictingAtoms: string[]
  crossModalConflict?: CrossModalConflict
  keyEvidence?: string[]
  keyContradiction?: string[]
}

// ─── Evidence ────────────────────────────────────────────────────────────────

export interface EvidenceAtom {
  id: string
  type: 'empirical' | 'structural'
  evidenceType?: EvidenceType
  observation: string
  brief?: string
  timestamp: string | null
  source: string
  modality: EvidenceModality
  confidence: number
  supports: string[]
  contradicts: string[]
  neutral: string[]
  usedToEliminate?: string[]
  novelty: Novelty
  quoteOrVisualAnchor?: string
  cycle: number
}

export interface EvidencePending {
  type: EvidenceType
  description: string
  requestedInCycle: number
  requestedBecause: string
}

export interface EvidenceRequest {
  id: string
  description: string
  targetHypotheses: string[]
  agentType: 'structural' | 'market' | 'news'
  status: 'pending' | 'fulfilled'
}

// ─── Context Window Tracking ─────────────────────────────────────────────────

export interface OrchestratorCycleWindow {
  cycle: number
  systemInstructions: number
  caseFileState: number
  decisionLog: number
  totalUsed: number
  utilizationPercent: number
  geminiCalls: number
  callTypes: string[]
}

export interface InvestigatorCycleWindow {
  cycle: number
  loaded: {
    compressedState: number
    structuralEvidence: number
    empiricalEvidence: number
    newTaggedEvidence: number
    activeHypotheses: number
    instructions: number
    totalLoaded: number
  }
  generated: {
    reasoningTokens: number
  }
  availableAfterReasoning: number
  utilizationPercent: number
  windowStatus: 'DISCARDED' | 'ACTIVE'
}

export interface PackagerCycleWindow {
  cycle: number
  loaded: {
    evidenceRequests: number
    rawEvidenceRetrieved: number
    activeHypotheses: number
    taggingInstructions: number
    totalLoaded: number
  }
  generated: {
    taggingReasoning: number
  }
  utilizationPercent: number
  windowStatus: 'DISCARDED' | 'ACTIVE'
}

export interface ContextWindowTracking {
  orchestrator: {
    type: 'FIXED'
    totalContext: number
    perCycleSnapshot: OrchestratorCycleWindow[]
  }
  investigator: {
    type: 'FRESH_PER_CYCLE'
    totalContext: number
    perCycle: InvestigatorCycleWindow[]
  }
  evidencePackager: {
    type: 'FRESH_PER_RUN'
    totalContext: number
    perCycle: PackagerCycleWindow[]
  }
}

// ─── Token Usage ─────────────────────────────────────────────────────────────

export interface AgentTokenUsage {
  totalInput: number
  totalOutput: number
  totalReasoning: number
  geminiCalls: number
}

export interface TokenUsageByCycle {
  cycle: number
  investigatorInput: number
  investigatorReasoning: number
  packagerInput: number
  packagerTagging: number
  orchestratorGemini: boolean
}

export interface TokenUsage {
  totalInput: number
  totalOutput: number
  totalReasoning: number
  byAgent: {
    orchestrator: AgentTokenUsage
    investigator: AgentTokenUsage
    evidencePackager: AgentTokenUsage
  }
  byCycle: TokenUsageByCycle[]
}

// ─── Cycle ───────────────────────────────────────────────────────────────────

export interface CycleHistoryEntry {
  cycle: number
  startCount: number
  endCount: number
  eliminated: string[]
  evidenceCollected: string[]
  crossModalDetected: string[]
  keyInsight: string
}

export interface CycleSnapshot {
  cycleNumber: number
  reasoningTokens: number
  evidenceTokens: number
  compressedTokens: number
  totalCapacity: number
}

export interface Cycle {
  cycleNumber: number
  status: 'completed' | 'active' | 'pending'
  hypothesesStart: number
  hypothesesEnd: number
  eliminations: string[]
  contradictionsFound: number
  durationMs: number
  contextSnapshot: CycleSnapshot
  compressionRatio?: number
  keyInsight?: string
  evidenceCollected?: string[]
}

// ─── Forward Simulation ──────────────────────────────────────────────────────

export interface ForwardSimulation {
  scenario: string
  prediction: string
  confidence: number
  pendingEvidence: string
  structuralBasis: string[]
}

// ─── Alert & Convergence ─────────────────────────────────────────────────────

export interface AlertDiagnosis {
  level: 'CRITICAL' | 'WARNING' | 'ALL-CLEAR'
  severity: 'critical' | 'high' | 'medium'
  headline: string
  detail: string
  diagnosis: string
  survivingHypotheses: string[]
  earliestSignalTimestamp: string
  earliestSignalAtomId: string
  singlePassSummary: string
  iterativeDiagnosis: string
  groundTruthMatch?: string
}

export interface ContagionTarget {
  entityName: string
  ticker: string
  sharedRiskFactor: string
  riskScore: number
  promotedToTier: 2 | 3
  inheritedContext?: string
}

// ─── Context Window (live) ───────────────────────────────────────────────────

export interface ContextWindow {
  reasoningTokens: number
  evidenceTokens: number
  compressedTokens: number
  totalCapacity: number
}

// ─── Key Insight ─────────────────────────────────────────────────────────────

export interface KeyInsight {
  cycle: number
  insight: string
}
