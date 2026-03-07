import type {
  Hypothesis,
  EvidenceAtom,
  EvidencePending,
  AlertDiagnosis,
  ContagionTarget,
  AgentStatus,
  TierLevel,
  TokenUsageByCycle,
  KeyInsight,
  CycleHistoryEntry,
  InvestigatorCycleWindow,
  PackagerCycleWindow,
  OrchestratorCycleWindow,
} from './investigation'

export type WSMessage =
  | { type: 'SESSION_STARTED'; entity: string; tier: TierLevel }
  | { type: 'TIER_ESCALATED'; from: 2; to: 3 }
  | { type: 'CYCLE_STARTED'; cycle_number: number }
  | { type: 'TOKENS_UPDATED'; reasoning: number; evidence: number; compressed: number }
  | { type: 'HYPOTHESIS_GENERATED'; hypothesis: Hypothesis }
  | { type: 'HYPOTHESIS_ELIMINATED'; id: string; kill_atom: string; kill_reason: string; cycle: number }
  | { type: 'HYPOTHESIS_SCORED'; id: string; confidence: number }
  | { type: 'EVIDENCE_ATOM_ARRIVED'; atom: EvidenceAtom }
  | { type: 'EVIDENCE_PENDING_ADDED'; item: EvidencePending }
  | { type: 'EVIDENCE_PENDING_FULFILLED'; description: string }
  | { type: 'AGENT_STATUS_CHANGED'; agent: 'structural' | 'market' | 'news'; status: AgentStatus }
  | { type: 'CYCLE_COMPLETE'; cycle_number: number; survivors: number; duration_ms: number; key_insight: string; evidence_collected: string[] }
  | { type: 'CYCLE_HISTORY_UPDATED'; entry: CycleHistoryEntry }
  | { type: 'COMPRESSION_STARTED' }
  | { type: 'COMPRESSION_COMPLETE'; compressed_tokens: number; compression_ratio: number }
  | { type: 'COMPRESSED_REASONING_UPDATED'; text: string }
  | { type: 'KEY_INSIGHT_ADDED'; insight: KeyInsight }
  | { type: 'TIER2_EVALUATION'; text: string; done: boolean }
  | { type: 'CONVERGENCE_REACHED'; diagnosis: AlertDiagnosis }
  | { type: 'CONTAGION_DETECTED'; targets: ContagionTarget[] }
  | { type: 'INVESTIGATION_COMPLETE' }
  // Token tracking
  | { type: 'TOKEN_USAGE_CYCLE'; data: TokenUsageByCycle }
  | { type: 'INVESTIGATOR_WINDOW_UPDATE'; data: InvestigatorCycleWindow }
  | { type: 'PACKAGER_WINDOW_UPDATE'; data: PackagerCycleWindow }
  | { type: 'ORCHESTRATOR_WINDOW_UPDATE'; data: OrchestratorCycleWindow }

export interface TriggerEvent {
  id: string
  entity: string
  ticker: string
  event: string
  date: string
  magnitudeSigma: number
  description: string
}
