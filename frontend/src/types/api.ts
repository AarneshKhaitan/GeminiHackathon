import type {
  Hypothesis,
  EvidenceAtom,
  AlertDiagnosis,
  ContagionTarget,
  AgentStatus,
  TierLevel,
} from './investigation'

export type WSMessage =
  | { type: 'SESSION_STARTED'; entity: string; tier: TierLevel }
  | { type: 'TIER_ESCALATED'; from: TierLevel; to: TierLevel }
  | { type: 'CYCLE_STARTED'; cycle_number: number }
  | { type: 'TOKENS_UPDATED'; reasoning: number; evidence: number; compressed: number }
  | { type: 'HYPOTHESIS_GENERATED'; hypothesis: Hypothesis }
  | { type: 'HYPOTHESIS_ELIMINATED'; id: string; kill_atom: string; kill_reason: string; cycle: number }
  | { type: 'HYPOTHESIS_SCORED'; id: string; confidence: number }
  | { type: 'EVIDENCE_ATOM_ARRIVED'; atom: EvidenceAtom }
  | { type: 'AGENT_STATUS_CHANGED'; agent: 'structural' | 'market' | 'news'; status: AgentStatus }
  | { type: 'CYCLE_COMPLETE'; cycle_number: number; survivors: number; duration_ms: number }
  | { type: 'COMPRESSION_STARTED' }
  | { type: 'COMPRESSION_COMPLETE'; compressed_tokens: number; compression_ratio: number }
  | { type: 'TIER2_EVALUATION'; text: string; done: boolean }
  | { type: 'CONVERGENCE_REACHED'; diagnosis: AlertDiagnosis }
  | { type: 'CONTAGION_DETECTED'; targets: ContagionTarget[] }
  | { type: 'INVESTIGATION_COMPLETE' }

export interface TriggerEvent {
  id: string
  entity: string
  ticker: string
  event: string
  date: string
  magnitudeSigma: number
  description: string
}
