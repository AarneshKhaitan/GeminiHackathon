"""
Orchestrator - Pure logic functions for investigation lifecycle management.

The orchestrator is the ONLY stateful agent with a persistent context window.
All other agents (investigator, evidence packager, retrieval agents) get fresh
context windows per execution.

CRITICAL: This file contains PURE FUNCTIONS only - NO LangGraph imports.
LangGraph wiring happens in graph/investigation_graph.py.

Orchestrator responsibilities:
1. Create case files for new investigations
2. Decide when to fetch evidence
3. Parse investigator self-compressed output
4. Decide continue/converge based on hypothesis count
5. Generate alerts (CRITICAL/ALL-CLEAR/MONITOR)
6. Handle network contagion detection
"""

from datetime import datetime, timezone
from typing import Literal

from models.case_file import (
    CaseFile,
    Hypothesis,
    EliminatedHypothesis,
    CrossModalFlag,
    EvidenceRef,
    CycleRecord,
    Alert,
    NetworkAlert,
)
from config import (
    MAX_CYCLES,
    CONVERGENCE_THRESHOLD,
    STAGNATION_CYCLES,
    TIER2_CONFIDENCE_THRESHOLD,
)
from gemini.client import call_gemini
from gemini.prompts.tier2_evaluation import build_tier2_prompt
from utils.corpus_loader import load_all_corpus


def utcnow() -> datetime:
    """Get timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


# =============================================================================
# CASE FILE CREATION
# =============================================================================


def create_case_file(
    entity: str,
    trigger: dict,
    tier: Literal[2, 3, 4] = 2,
) -> dict:
    """
    Create a new case file for an investigation.

    Args:
        entity: Entity under investigation (e.g., 'SVB')
        trigger: Trigger signal that initiated investigation
        tier: Investigation tier (2=evaluation, 3=initial, 4=full)

    Returns:
        Case file as dict (CaseFile model serialized)
    """
    case_file = CaseFile(
        entity=entity,
        tier=tier,
        status="evaluating" if tier == 2 else "investigating",
        trigger=trigger,
        active_hypotheses=[],
        eliminated_hypotheses=[],
        cross_modal_flags=[],
        key_insights=[],
        evidence_collected=[],
        evidence_pending=[],
        compressed_reasoning=None,
        cycle_history=[],
        context_windows={},
        token_usage={},
        alert=None,
        network_alerts=[],
    )

    return case_file.model_dump()


def escalate_tier(case_file: dict, new_tier: Literal[3, 4]) -> dict:
    """
    Escalate investigation to higher tier.

    Args:
        case_file: Current case file (dict)
        new_tier: New tier to escalate to (3 or 4)

    Returns:
        Updated case file as dict
    """
    case_file = CaseFile(**case_file)
    case_file.tier = new_tier
    case_file.status = "investigating"
    case_file.updated_at = utcnow()

    return case_file.model_dump()


# =============================================================================
# TIER 2 EVALUATION
# =============================================================================


async def evaluate_signal(trigger: dict) -> dict:
    """
    Tier 2 semantic evaluation using Gemini.

    Decides whether a trigger signal warrants full investigation.

    Args:
        trigger: Trigger signal dict

    Returns:
        {
            "thinking": str,
            "promotes": bool,
            "confidence": float,
            "reasoning": str,
            "token_usage": dict
        }
    """
    prompt = build_tier2_prompt(trigger)
    result = await call_gemini(prompt)

    # Extract response and token usage
    response = result["response"]
    token_usage = result["token_usage"]

    # Add token usage to response
    return {
        **response,
        "token_usage": token_usage,
    }


def assess_tier2_promotion(tier2_result: dict) -> dict:
    """
    Decide whether to promote to Tier 3 based on Tier 2 evaluation.

    Args:
        tier2_result: Result from Tier 2 semantic evaluation
            {
                "promotes": bool,
                "confidence": float,
                "reasoning": str
            }

    Returns:
        {
            "decision": "promote" | "demote",
            "reason": str,
            "confidence": float
        }
    """
    promotes = tier2_result.get("promotes", False)
    confidence = tier2_result.get("confidence", 0.0)
    reasoning = tier2_result.get("reasoning", "")

    # Promote if model says promote OR confidence exceeds threshold
    should_promote = promotes or (confidence >= TIER2_CONFIDENCE_THRESHOLD)

    return {
        "decision": "promote" if should_promote else "demote",
        "reason": reasoning,
        "confidence": confidence,
    }


# =============================================================================
# EVIDENCE MANAGEMENT
# =============================================================================


def needs_evidence(case_file: dict, cycle_num: int) -> bool:
    """
    Decide if new evidence is needed for this cycle.

    Args:
        case_file: Current case file (dict)
        cycle_num: Current cycle number

    Returns:
        True if evidence collection needed, False otherwise

    Logic:
        - Cycle 1: NO evidence needed (generate initial hypotheses first)
        - Cycle 2+: YES if evidence_pending has requests
    """
    # Cycle 1: No evidence needed - just generate hypotheses
    if cycle_num == 1:
        return False

    # Cycle 2+: Check if there are pending evidence requests
    evidence_pending = case_file.get("evidence_pending", [])
    return len(evidence_pending) > 0


def prioritize_evidence_requests(evidence_requests: list[dict]) -> list[dict]:
    """
    Prioritize and filter evidence requests.

    Orchestrator QC check - prevents investigator from requesting too much
    evidence or duplicate evidence.

    Args:
        evidence_requests: List of evidence request dicts from investigator

    Returns:
        Prioritized and filtered list of evidence requests
    """
    # For now, simple passthrough
    # TODO: Add deduplication, prioritization by type, limit to top 5
    return evidence_requests[:5]  # Limit to 5 requests per cycle


def update_evidence_collected(
    case_file: dict, new_evidence: list[dict], cycle_num: int
) -> dict:
    """
    Update case file with newly collected evidence.

    Args:
        case_file: Current case file (dict)
        new_evidence: List of observation dicts (tagged by packager)
        cycle_num: Current cycle number

    Returns:
        Updated case file as dict
    """
    case_file = CaseFile(**case_file)

    # Add evidence references (not full content)
    for obs in new_evidence:
        evidence_ref = EvidenceRef(
            atom_id=obs["observation_id"],
            brief=obs["content"][:200],  # First 200 chars as summary
            type=obs["type"],
            collected_in_cycle=cycle_num,
        )
        case_file.evidence_collected.append(evidence_ref)

    # Clear pending requests (they've been fulfilled)
    case_file.evidence_pending = []

    case_file.updated_at = utcnow()

    return case_file.model_dump()


# =============================================================================
# INVESTIGATOR OUTPUT PARSING
# =============================================================================


def parse_investigator_output(investigation_output: dict, cycle_num: int) -> dict:
    """
    Parse investigator output and extract key components.

    Args:
        investigation_output: Raw output from investigator agent
        cycle_num: Current cycle number

    Returns:
        Parsed output with structured components:
        {
            "surviving_hypotheses": list[dict],
            "eliminated_hypotheses": list[dict],
            "cross_modal_flags": list[dict],
            "evidence_requests": list[dict],
            "compressed_state": str,
            "key_insights": list[str],
            "token_usage": dict
        }
    """
    # For Cycle 1, map "surviving_hypotheses" to active hypotheses
    if cycle_num == 1:
        surviving = investigation_output.get("surviving_hypotheses", [])
        eliminated = []
        cross_modal = []
    else:
        # Cycle 2+: Use standard keys
        surviving = investigation_output.get("surviving_hypotheses", [])
        eliminated = investigation_output.get("eliminated_hypotheses", [])
        cross_modal = investigation_output.get("cross_modal_flags", [])

    return {
        "surviving_hypotheses": surviving,
        "eliminated_hypotheses": eliminated,
        "cross_modal_flags": cross_modal,
        "evidence_requests": investigation_output.get("evidence_requests", []),
        "compressed_state": investigation_output.get("compressed_state", ""),
        "key_insights": investigation_output.get("key_insights", []),
        "token_usage": investigation_output.get("token_usage", {}),
    }


def update_case_file_with_investigator_output(
    case_file: dict, parsed_output: dict, cycle_num: int
) -> dict:
    """
    Update case file with investigator output.

    Args:
        case_file: Current case file (dict)
        parsed_output: Parsed investigator output from parse_investigator_output()
        cycle_num: Current cycle number

    Returns:
        Updated case file as dict
    """
    case_file = CaseFile(**case_file)

    # Update active hypotheses
    case_file.active_hypotheses = [
        Hypothesis(**h) for h in parsed_output["surviving_hypotheses"]
    ]

    # Append eliminated hypotheses
    for elim in parsed_output["eliminated_hypotheses"]:
        case_file.eliminated_hypotheses.append(EliminatedHypothesis(**elim))

    # Append cross-modal flags
    for flag in parsed_output["cross_modal_flags"]:
        case_file.cross_modal_flags.append(CrossModalFlag(**flag))

    # Update compressed reasoning (replaces previous state)
    case_file.compressed_reasoning = parsed_output["compressed_state"]

    # Append key insights
    case_file.key_insights.extend(parsed_output["key_insights"])

    # Store evidence requests for next cycle
    case_file.evidence_pending = parsed_output["evidence_requests"]

    # Update token usage
    agent_key = f"investigator_cycle_{cycle_num}"
    case_file.token_usage[agent_key] = parsed_output["token_usage"]

    # Add cycle record
    cycle_record = CycleRecord(
        cycle_num=cycle_num,
        hypotheses_count=len(case_file.active_hypotheses),
        eliminations_count=len(parsed_output["eliminated_hypotheses"]),
        evidence_collected_count=len(parsed_output.get("evidence_collected", [])),
        token_usage=parsed_output["token_usage"],
    )
    case_file.cycle_history.append(cycle_record)

    case_file.updated_at = utcnow()

    return case_file.model_dump()


# =============================================================================
# CONVERGENCE DECISIONS
# =============================================================================


def decide_convergence(case_file: dict, cycle_num: int) -> dict:
    """
    Decide whether to continue investigation or converge.

    Args:
        case_file: Current case file (dict)
        cycle_num: Current cycle number

    Returns:
        {
            "decision": "continue" | "converge",
            "reason": str,
            "hypotheses_count": int,
            "cycles_completed": int
        }

    Convergence triggers:
        1. Hypothesis count ≤ CONVERGENCE_THRESHOLD (2)
        2. Max cycles reached
        3. Stagnation: hypothesis count unchanged for STAGNATION_CYCLES
        4. All hypotheses eliminated (edge case)
    """
    case_file_obj = CaseFile(**case_file)
    hypotheses_count = len(case_file_obj.active_hypotheses)

    # Trigger 1: Hypothesis count at or below threshold
    if hypotheses_count <= CONVERGENCE_THRESHOLD:
        return {
            "decision": "converge",
            "reason": f"Converged: {hypotheses_count} hypotheses remaining (threshold: {CONVERGENCE_THRESHOLD})",
            "hypotheses_count": hypotheses_count,
            "cycles_completed": cycle_num,
        }

    # Trigger 2: Max cycles reached
    if cycle_num >= MAX_CYCLES:
        return {
            "decision": "converge",
            "reason": f"Max cycles ({MAX_CYCLES}) reached",
            "hypotheses_count": hypotheses_count,
            "cycles_completed": cycle_num,
        }

    # Trigger 3: Stagnation check (hypothesis count unchanged)
    if len(case_file_obj.cycle_history) >= STAGNATION_CYCLES:
        recent_counts = [
            record.hypotheses_count
            for record in case_file_obj.cycle_history[-STAGNATION_CYCLES:]
        ]
        if len(set(recent_counts)) == 1:  # All counts identical
            return {
                "decision": "converge",
                "reason": f"Stagnation: hypothesis count unchanged for {STAGNATION_CYCLES} cycles",
                "hypotheses_count": hypotheses_count,
                "cycles_completed": cycle_num,
            }

    # Trigger 4: All hypotheses eliminated (edge case)
    if hypotheses_count == 0:
        return {
            "decision": "converge",
            "reason": "All hypotheses eliminated",
            "hypotheses_count": 0,
            "cycles_completed": cycle_num,
        }

    # Default: Continue investigation
    return {
        "decision": "continue",
        "reason": f"Investigation ongoing: {hypotheses_count} hypotheses remaining",
        "hypotheses_count": hypotheses_count,
        "cycles_completed": cycle_num,
    }


# =============================================================================
# ALERT GENERATION
# =============================================================================


def generate_alert(case_file: dict) -> dict:
    """
    Generate final alert after investigation convergence.

    Args:
        case_file: Complete case file (dict)

    Returns:
        Alert dict with level, diagnosis, and recommended actions

    Alert levels:
        - CRITICAL: ≥1 surviving hypothesis with systemic risk indicators
        - MONITOR: 1-2 surviving hypotheses, no systemic risk
        - ALL-CLEAR: 0 surviving hypotheses or all benign
    """
    case_file_obj = CaseFile(**case_file)
    hypotheses_count = len(case_file_obj.active_hypotheses)

    # Edge case: No surviving hypotheses
    if hypotheses_count == 0:
        alert = Alert(
            level="ALL-CLEAR",
            diagnosis="All hypotheses eliminated. Signal likely false positive or resolved.",
            surviving_hypotheses=[],
            key_evidence=[],
            recommended_actions=["Continue routine monitoring"],
        )
        return alert.model_dump()

    # Extract surviving hypothesis info
    surviving_ids = [h.id for h in case_file_obj.active_hypotheses]
    surviving_names = [h.name for h in case_file_obj.active_hypotheses]
    top_scores = [h.score for h in case_file_obj.active_hypotheses]

    # Get key evidence (top 5 most-referenced observations)
    evidence_refs = {}
    for h in case_file_obj.active_hypotheses:
        for atom_id in h.evidence_chain:
            evidence_refs[atom_id] = evidence_refs.get(atom_id, 0) + 1

    key_evidence = sorted(evidence_refs.items(), key=lambda x: x[1], reverse=True)[:5]
    key_evidence_ids = [atom_id for atom_id, _ in key_evidence]

    # Determine alert level based on systemic risk indicators
    systemic_keywords = [
        "contagion",
        "systemic",
        "liquidity crisis",
        "deposit flight",
        "bank run",
        "capital shortfall",
        "insolvency",
    ]

    has_systemic_risk = any(
        any(keyword in h.description.lower() for keyword in systemic_keywords)
        for h in case_file_obj.active_hypotheses
    )

    # Determine level
    if has_systemic_risk or max(top_scores, default=0) >= 0.8:
        level = "CRITICAL"
        diagnosis = f"HIGH RISK: {hypotheses_count} hypothesis(es) indicate systemic concern - {', '.join(surviving_names)}"
        recommended_actions = [
            "Immediate escalation to risk committee",
            "Activate enhanced monitoring protocols",
            "Assess counterparty exposure",
            "Prepare contingency plans",
        ]
    elif hypotheses_count <= 2:
        level = "MONITOR"
        diagnosis = f"MODERATE RISK: {hypotheses_count} hypothesis(es) remaining - {', '.join(surviving_names)}"
        recommended_actions = [
            "Continue monitoring key metrics",
            "Assess if additional evidence needed",
            "Brief risk management team",
        ]
    else:
        level = "MONITOR"
        diagnosis = f"INCONCLUSIVE: {hypotheses_count} hypotheses remain - {', '.join(surviving_names)}"
        recommended_actions = [
            "Investigation did not converge decisively",
            "Consider additional evidence collection",
            "Manual review recommended",
        ]

    alert = Alert(
        level=level,
        diagnosis=diagnosis,
        surviving_hypotheses=surviving_ids,
        key_evidence=key_evidence_ids,
        recommended_actions=recommended_actions,
    )

    return alert.model_dump()


def finalize_case_file(case_file: dict, alert: dict) -> dict:
    """
    Finalize case file with alert and mark as converged.

    Args:
        case_file: Current case file (dict)
        alert: Generated alert (dict)

    Returns:
        Finalized case file as dict
    """
    case_file = CaseFile(**case_file)
    case_file.alert = Alert(**alert)
    case_file.status = "converged"
    case_file.updated_at = utcnow()

    return case_file.model_dump()


# =============================================================================
# NETWORK CONTAGION DETECTION
# =============================================================================


def detect_network_contagion(case_file: dict) -> list[dict]:
    """
    Detect potential contagion to counterparties.

    Scans evidence and hypotheses for mentions of other entities that may
    warrant investigation.

    Args:
        case_file: Current case file (dict)

    Returns:
        List of NetworkAlert dicts for counterparties

    Contagion triggers:
        - Hypothesis mentions specific counterparty exposure
        - Cross-modal flags indicate systemic risk
        - Evidence mentions correlated exposures
    """
    case_file_obj = CaseFile(**case_file)
    network_alerts = []

    # Counterparty keywords to scan for
    counterparty_patterns = [
        "counterparty",
        "exposure to",
        "contagion",
        "correlated",
        "interconnected",
        "shared exposure",
    ]

    # Scan active hypotheses for counterparty mentions
    for h in case_file_obj.active_hypotheses:
        desc_lower = h.description.lower()
        if any(pattern in desc_lower for pattern in counterparty_patterns):
            # Extract entity name (simplified - would use NER in production)
            # For demo, just flag generic contagion risk
            network_alert = NetworkAlert(
                entity="COUNTERPARTY_NETWORK",
                reason=f"Hypothesis {h.id} suggests potential contagion: {h.name}",
                inherited_context=case_file_obj.compressed_reasoning or "",
                priority="HIGH" if h.score >= 0.7 else "MEDIUM",
            )
            network_alerts.append(network_alert.model_dump())

    # Scan cross-modal flags for systemic indicators
    systemic_flags = [
        flag
        for flag in case_file_obj.cross_modal_flags
        if "systemic" in flag.contradiction_description.lower()
        or "contagion" in flag.contradiction_description.lower()
    ]

    if systemic_flags and not network_alerts:
        # Generic systemic risk alert
        network_alert = NetworkAlert(
            entity="SYSTEMIC_NETWORK",
            reason=f"Cross-modal analysis detected {len(systemic_flags)} systemic risk flags",
            inherited_context=case_file_obj.compressed_reasoning or "",
            priority="HIGH",
        )
        network_alerts.append(network_alert.model_dump())

    return network_alerts


def update_network_alerts(case_file: dict, network_alerts: list[dict]) -> dict:
    """
    Update case file with network contagion alerts.

    Args:
        case_file: Current case file (dict)
        network_alerts: List of NetworkAlert dicts

    Returns:
        Updated case file as dict
    """
    case_file = CaseFile(**case_file)
    case_file.network_alerts = [NetworkAlert(**alert) for alert in network_alerts]
    case_file.updated_at = utcnow()

    return case_file.model_dump()


# =============================================================================
# QUALITY CONTROL
# =============================================================================


def validate_compression_quality(
    compressed_state: str, previous_state: str | None, cycle_num: int
) -> dict:
    """
    QC check on investigator self-compression.

    Ensures compressed state is not losing critical information.

    Args:
        compressed_state: New compressed state from investigator
        previous_state: Previous compressed state (if exists)
        cycle_num: Current cycle number

    Returns:
        {
            "valid": bool,
            "issues": list[str],
            "should_retry": bool
        }

    Validation checks:
        - Not empty
        - Not significantly shorter than previous (>50% reduction is suspicious)
        - Contains cycle number reference
        - Contains hypothesis count reference
    """
    issues = []

    # Check 1: Not empty
    if not compressed_state or len(compressed_state.strip()) < 50:
        issues.append("Compressed state is too short or empty")

    # Check 2: Contains cycle reference
    if f"cycle {cycle_num}" not in compressed_state.lower() and f"cycle_{cycle_num}" not in compressed_state.lower():
        issues.append(f"Missing cycle {cycle_num} reference in compressed state")

    # Check 3: Not too much compression
    if previous_state and len(compressed_state) < len(previous_state) * 0.5:
        issues.append(
            f"Suspicious compression: {len(compressed_state)} chars vs {len(previous_state)} chars previous"
        )

    # Check 4: Contains key structural terms (check for either singular or plural)
    has_hypothesis = "hypothesis" in compressed_state.lower() or "hypotheses" in compressed_state.lower()
    has_evidence = "evidence" in compressed_state.lower()

    if not has_hypothesis:
        issues.append("Missing hypothesis/hypotheses reference")
    if not has_evidence:
        issues.append("Missing evidence reference")

    valid = len(issues) == 0
    should_retry = len(issues) > 0 and cycle_num <= MAX_CYCLES  # Only retry if not at max cycles

    return {
        "valid": valid,
        "issues": issues,
        "should_retry": should_retry,
    }


# =============================================================================
# ORCHESTRATOR STATE MANAGEMENT
# =============================================================================


def prepare_investigator_context(case_file: dict, cycle_num: int, new_evidence: list[dict]) -> dict:
    """
    Prepare context for investigator agent.

    For now, since Phase 4 provides evidence already, we don't need to
    load from corpus. Phase 4's evidence packager handles that.

    Args:
        case_file: Current case file (dict)
        cycle_num: Current cycle number
        new_evidence: Newly collected evidence (empty for Cycle 1)

    Returns:
        Context dict for investigator:
        {
            "trigger": str,
            "entity": str,
            "cycle_num": int,
            "compressed_state": str | None,
            "evidence": list[dict],
            "active_hypotheses": list[dict]
        }
    """
    case_file_obj = CaseFile(**case_file)

    # Format trigger as string
    trigger_str = f"{case_file_obj.trigger.get('event', 'Unknown event')} - {case_file_obj.trigger}"

    # For Phase 5, new_evidence already contains everything we need
    # (Phase 4 evidence packager loads from corpus and tags it)
    all_evidence = new_evidence

    return {
        "trigger": trigger_str,
        "entity": case_file_obj.entity,
        "cycle_num": cycle_num,
        "compressed_state": case_file_obj.compressed_reasoning,
        "evidence": all_evidence,
        "active_hypotheses": [h.model_dump() for h in case_file_obj.active_hypotheses],
    }
