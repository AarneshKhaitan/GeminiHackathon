export type TierLevel = 2 | 3 | 4

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

export type Novelty = 'low' | 'medium' | 'high' | 'critical'

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
  // Case file format fields
  keyEvidence?: string[]       // Human-readable evidence snippets e.g. ["CDS 800bps", "CHF 110B outflow"]
  keyContradiction?: string[]  // Human-readable contradictions e.g. ["SNB says meets requirements"]
}

export interface CaseFileKeyInsight {
  text: string
  cycle: number
}

export interface ForwardSimulation {
  condition: string
  outcome: string
  confidence: number
}

export interface CaseFile {
  entity: string
  status: string
  lastUpdated: string
  cycleCount: number
  structuralKnowledgeLoaded: string[]
  openEvidenceRequests: string[]
  keyInsights: CaseFileKeyInsight[]
  crossModalContradictions: string[]
  forwardSimulations: ForwardSimulation[]
}

export interface CrossModalConflict {
  structuralObservation: string
  empiricalObservation: string
  conflictSummary: string
}

export interface EvidenceAtom {
  id: string
  type: 'empirical' | 'structural'
  observation: string
  timestamp: string | null
  source: string
  modality: EvidenceModality
  confidence: number
  supports: string[]
  contradicts: string[]
  neutral: string[]
  novelty: Novelty
  quoteOrVisualAnchor?: string
  cycle: number
}

export interface EvidenceRequest {
  id: string
  description: string
  targetHypotheses: string[]
  agentType: 'structural' | 'market' | 'news'
  status: 'pending' | 'fulfilled'
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
}

export interface AlertDiagnosis {
  severity: 'critical' | 'high' | 'medium'
  headline: string
  detail: string
  survivingHypotheses: string[]
  earliestSignalTimestamp: string
  earliestSignalAtomId: string
  singlePassSummary: string
  iterativeDiagnosis: string
}

export interface ContagionTarget {
  entityName: string
  ticker: string
  sharedRiskFactor: string
  riskScore: number
  promotedToTier: 2 | 3
}

export interface ContextWindow {
  reasoningTokens: number
  evidenceTokens: number
  compressedTokens: number
  totalCapacity: number
}
