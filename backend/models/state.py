"""
LangGraph state definition.

TypedDict defining the state that flows between LangGraph nodes.
All fields must be JSON-serializable for LangGraph compatibility.
"""

from typing import TypedDict, Literal


class InvestigationState(TypedDict, total=False):
    """
    State flowing between LangGraph nodes.

    All fields are JSON-serializable dicts/lists, not Pydantic models.
    Pydantic models are converted to/from dicts at boundaries.
    """

    # Trigger information
    trigger_signal: dict
    """Trigger event that initiated investigation"""

    entity: str
    """Entity under investigation (e.g., 'SVB')"""

    # Cycle management
    current_cycle: int
    """Current investigation cycle number (1-indexed)"""

    max_cycles: int
    """Maximum cycles allowed before forced convergence"""

    # Core state
    case_file: dict
    """Complete case file (CaseFile model serialized to dict)"""

    active_hypotheses: list[dict]
    """Currently surviving hypotheses"""

    eliminated_hypotheses: list[dict]
    """Killed hypotheses with elimination reasons"""

    # Evidence management
    evidence_requests: list[dict]
    """Evidence requests from investigator for next cycle"""

    new_evidence: list[dict]
    """Newly collected and tagged evidence from packager"""

    raw_evidence: list[dict]
    """Raw untagged evidence from retrieval agents"""

    # Reasoning state
    compressed_state: str | None
    """Self-compressed state from investigator"""

    cross_modal_flags: list[dict]
    """Cross-modal contradictions detected"""

    cycle_history: list[dict]
    """Historical record of all cycles"""

    # Investigation control
    agent_status: dict[str, str]
    """Status of each agent (for monitoring)"""

    token_usage: dict[str, dict]
    """Token usage per agent per cycle"""

    context_windows: dict[str, dict]
    """Context window utilization tracking"""

    # Decision points
    tier2_assessment: dict | None
    """Result from Tier 2 evaluation"""

    convergence_decision: Literal["continue", "converge"] | None
    """Decision to continue investigation or converge"""

    investigation_output: dict | None
    """Raw output from investigator agent"""

    # Results
    alert: dict | None
    """Final alert after convergence"""

    network_alerts: list[dict]
    """Contagion alerts for counterparties"""
