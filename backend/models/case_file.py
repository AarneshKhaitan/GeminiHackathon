"""
Case file data model.

The investigation's persistent memory between cycles. Stores hypotheses,
evidence references, compressed reasoning state, and cycle history.
"""

from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime, timezone


def utcnow():
    """Helper to get timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class Hypothesis(BaseModel):
    """Active hypothesis being evaluated."""

    id: str = Field(..., description="Unique hypothesis identifier (e.g., 'H01')")
    name: str = Field(..., description="Short name for the hypothesis")
    description: str = Field(..., description="Detailed description of the hypothesis")
    score: float = Field(..., description="Confidence score 0.0-1.0")
    evidence_chain: list[str] = Field(
        default_factory=list,
        description="List of observation IDs supporting this hypothesis"
    )
    status: Literal["active", "eliminated", "confirmed"] = Field(
        default="active",
        description="Status of the hypothesis"
    )


class EliminatedHypothesis(BaseModel):
    """Record of a killed hypothesis."""

    id: str = Field(..., description="Hypothesis ID that was eliminated")
    name: str = Field(..., description="Name of eliminated hypothesis")
    killed_by_atom: str = Field(
        ...,
        description="Observation ID that contradicted and killed this hypothesis"
    )
    killed_in_cycle: int = Field(..., description="Cycle number when eliminated")
    reason: str = Field(
        ...,
        description="One-line explanation of why it was eliminated"
    )


class CrossModalFlag(BaseModel):
    """Cross-modal contradiction between structural and empirical evidence."""

    structural_atom_id: str = Field(
        ...,
        description="ID of structural observation"
    )
    empirical_atom_id: str = Field(
        ...,
        description="ID of empirical observation"
    )
    detected_in_cycle: int = Field(
        ...,
        description="Cycle when contradiction was detected"
    )
    contradiction_description: str = Field(
        ...,
        description="Description of the contradiction"
    )


class EvidenceRef(BaseModel):
    """Reference to collected evidence (stored in case file)."""

    atom_id: str = Field(..., description="Observation ID")
    brief: str = Field(
        ...,
        description="Short summary of the evidence (not full content)"
    )
    type: Literal["structural", "market", "news", "filing"] = Field(
        ...,
        description="Type of evidence"
    )
    collected_in_cycle: int = Field(
        ...,
        description="Cycle when this evidence was collected"
    )


class CycleRecord(BaseModel):
    """Record of a single investigation cycle."""

    cycle_num: int
    hypotheses_count: int
    eliminations_count: int
    evidence_collected_count: int
    token_usage: dict[str, int]
    duration_seconds: float | None = None


class Alert(BaseModel):
    """Final alert after investigation convergence."""

    level: Literal["CRITICAL", "ALL-CLEAR", "MONITOR"] = Field(
        ...,
        description="Alert severity level"
    )
    diagnosis: str = Field(..., description="Summary diagnosis")
    surviving_hypotheses: list[str] = Field(
        ...,
        description="Final surviving hypothesis IDs"
    )
    key_evidence: list[str] = Field(
        ...,
        description="Critical evidence atom IDs supporting the diagnosis"
    )
    recommended_actions: list[str] = Field(
        default_factory=list,
        description="Recommended next steps"
    )


class NetworkAlert(BaseModel):
    """Contagion alert for a counterparty entity."""

    entity: str = Field(..., description="Counterparty entity name")
    reason: str = Field(..., description="Reason for promotion to investigation")
    inherited_context: str = Field(
        ...,
        description="Context inherited from original investigation"
    )
    priority: Literal["HIGH", "MEDIUM", "LOW"] = Field(
        default="MEDIUM",
        description="Investigation priority"
    )


class CaseFile(BaseModel):
    """
    Complete investigation case file.

    The persistent memory spanning all cycles. Orchestrator is the ONLY
    component that reads/writes this structure.
    """

    entity: str = Field(..., description="Entity under investigation (e.g., 'SVB')")

    tier: Literal[2, 3, 4] = Field(
        ...,
        description="Investigation tier (2=semantic evaluation, 3=initial investigation, 4=full investigation)"
    )

    status: Literal["evaluating", "investigating", "converged", "all-clear"] = Field(
        default="evaluating",
        description="Current investigation status"
    )

    trigger: dict = Field(
        ...,
        description="Trigger signal that initiated investigation"
    )

    active_hypotheses: list[Hypothesis] = Field(
        default_factory=list,
        description="Currently surviving hypotheses being evaluated"
    )

    eliminated_hypotheses: list[EliminatedHypothesis] = Field(
        default_factory=list,
        description="Killed hypotheses with kill atom citations"
    )

    cross_modal_flags: list[CrossModalFlag] = Field(
        default_factory=list,
        description="Detected contradictions between structural and empirical evidence"
    )

    key_insights: list[str] = Field(
        default_factory=list,
        description="Important findings accumulated during investigation"
    )

    evidence_collected: list[EvidenceRef] = Field(
        default_factory=list,
        description="References to collected evidence (ID + brief, not full content)"
    )

    evidence_pending: list[dict] = Field(
        default_factory=list,
        description="Evidence requests for next cycle"
    )

    compressed_reasoning: str | None = Field(
        default=None,
        description="Self-compressed state from investigator (replaced each cycle)"
    )

    cycle_history: list[CycleRecord] = Field(
        default_factory=list,
        description="Record of each investigation cycle"
    )

    context_windows: dict[str, dict] = Field(
        default_factory=dict,
        description="Context window utilization tracking per agent per cycle"
    )

    token_usage: dict[str, dict] = Field(
        default_factory=dict,
        description="Token usage per agent per cycle (e.g., {'investigator': {'cycle_1': 45000}})"
    )

    alert: Alert | None = Field(
        default=None,
        description="Final alert after convergence"
    )

    network_alerts: list[NetworkAlert] = Field(
        default_factory=list,
        description="Contagion alerts for counterparties"
    )

    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "entity": "SVB",
                "tier": 4,
                "status": "investigating",
                "trigger": {
                    "event": "CDS spike",
                    "magnitude": 450,
                    "date": "2023-03-08"
                },
                "active_hypotheses": [],
                "eliminated_hypotheses": [],
                "cross_modal_flags": [],
                "key_insights": [],
                "evidence_collected": [],
                "evidence_pending": [],
                "compressed_reasoning": None,
                "cycle_history": [],
                "context_windows": {},
                "token_usage": {},
                "alert": None,
                "network_alerts": []
            }
        }
