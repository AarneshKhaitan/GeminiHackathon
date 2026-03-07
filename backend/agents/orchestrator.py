"""
Orchestrator — pure functions managing the investigation lifecycle.

No LangGraph imports. Each function is independently testable.
The LangGraph graph in graph/investigation_graph.py wires these together.

Functions:
  evaluate_signal       — Tier 2 semantic evaluation (async, Gemini call)
  create_case_file      — Initialize CaseFile for new investigation
  prepare_investigator_context — Build context dict for investigate()
  process_investigation_output — Integrate investigator output into case file
  should_continue       — Convergence logic (pure, no Gemini)
  generate_alert        — Final alert generation (async, Gemini call)
  detect_contagion      — Stub contagion detection (async)
"""

import copy
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from gemini.client import call_gemini
from gemini.prompts.tier2_evaluation import build_tier2_prompt
from models.case_file import CaseFile
import config


# ── Alert Generation Prompt ────────────────────────────────────────────────────

def _build_alert_prompt(case_file: dict) -> str:
    entity = case_file.get("entity", "unknown")
    active_hyps = case_file.get("active_hypotheses", [])
    eliminated = case_file.get("eliminated_hypotheses", [])
    key_insights = case_file.get("key_insights", [])
    compressed = case_file.get("compressed_reasoning", "")
    cycles = len(case_file.get("cycle_history", []))

    hyp_text = "\n".join([
        f"  [{h.get('id', '?')}] {h.get('name', '?')} (score: {h.get('score', 0):.2f}): {h.get('description', '')}"
        for h in active_hyps
    ]) or "  None — all hypotheses eliminated."

    eliminated_text = "\n".join([
        f"  [{e.get('id', '?')}] {e.get('name', '?')} — killed by {e.get('killed_by_atom', '?')}: {e.get('reason', '')}"
        for e in eliminated
    ]) or "  None"

    insights_text = "\n".join(f"  - {i}" for i in key_insights) or "  None recorded."

    return f"""
You are generating the final alert for a financial risk investigation.

# INVESTIGATION SUMMARY
Entity: {entity}
Cycles completed: {cycles}
Compressed reasoning: {compressed or 'Not available'}

# SURVIVING HYPOTHESES (after {cycles} cycles of elimination)
{hyp_text}

# ELIMINATED HYPOTHESES
{eliminated_text}

# KEY INSIGHTS
{insights_text}

# TASK
Generate the final risk alert. The alert level must be:
- "CRITICAL": one or more high-confidence hypotheses (score > 0.6) survive — real systemic risk confirmed
- "MONITOR": surviving hypotheses have moderate confidence (0.4-0.6) — watch closely
- "ALL-CLEAR": no surviving hypotheses or all have low confidence (<0.4)

# OUTPUT FORMAT (JSON):
{{
  "level": "CRITICAL",
  "diagnosis": "2-3 sentence diagnosis of the situation and its implications",
  "surviving_hypotheses": ["H01", "H02"],
  "key_evidence": ["S01", "E03"],
  "recommended_actions": ["Action 1", "Action 2", "Action 3"]
}}

Where:
- "level" must be exactly "CRITICAL", "MONITOR", or "ALL-CLEAR"
- "surviving_hypotheses" lists hypothesis IDs from the surviving list above only
- "key_evidence" lists observation IDs from evidence chains of surviving hypotheses
- "recommended_actions" gives 2-4 concrete next steps for risk managers

Provide only the JSON, no additional text.
"""


# ── Pure Functions ─────────────────────────────────────────────────────────────

async def evaluate_signal(trigger: dict) -> dict:
    """
    Tier 2 semantic evaluation — decides escalate or dismiss.

    Args:
        trigger: Signal dict with entity, event, magnitude, date, description

    Returns:
        {"assessment": str, "decision": "escalate"|"dismiss",
         "confidence": float, "key_risk_factors": list, "recommended_tier": int}
    """
    prompt = build_tier2_prompt(trigger)
    result = await call_gemini(prompt)
    response = result.get("response", {})

    return {
        "assessment": response.get("assessment", "Signal evaluation inconclusive."),
        "decision": response.get("decision", "dismiss"),
        "confidence": float(response.get("confidence", 0.5)),
        "key_risk_factors": response.get("key_risk_factors", []),
        "recommended_tier": response.get("recommended_tier", 3),
    }


def create_case_file(entity: str, trigger: dict) -> dict:
    """
    Initialize a new CaseFile for a Tier 3/4 investigation.

    Args:
        entity: Full entity name (e.g. "Credit Suisse")
        trigger: Original trigger signal

    Returns:
        Serialized CaseFile dict (pydantic model_dump)
    """
    case = CaseFile(
        entity=entity,
        tier=3,
        status="investigating",
        trigger=trigger,
    )
    return case.model_dump(mode="json")


def prepare_investigator_context(case_file: dict, new_evidence: list[dict]) -> dict:
    """
    Build the context dict for the investigator's investigate() call.

    Args:
        case_file: Current serialized CaseFile
        new_evidence: Newly tagged evidence atoms from the packager

    Returns:
        Context dict matching investigate()'s expected input signature:
        {trigger, entity, cycle_num, compressed_state, evidence, active_hypotheses}
    """
    cycle_num = len(case_file.get("cycle_history", [])) + 1
    return {
        "trigger": case_file["trigger"],
        "entity": case_file["entity"],
        "cycle_num": cycle_num,
        "compressed_state": case_file.get("compressed_reasoning"),
        "evidence": new_evidence,
        "active_hypotheses": case_file.get("active_hypotheses", []),
    }


def process_investigation_output(case_file: dict, investigation_output: dict) -> dict:
    """
    Integrate investigator output into the case file.

    Replaces active_hypotheses with survivors, appends eliminated hypotheses,
    updates compressed reasoning, records cycle history, and queues new evidence
    requests.

    Args:
        case_file: Current serialized CaseFile (deep-copied internally)
        investigation_output: Return value from investigate()

    Returns:
        Updated case_file dict
    """
    cf = copy.deepcopy(case_file)

    surviving = investigation_output.get("surviving_hypotheses", [])
    new_eliminated = investigation_output.get("eliminated_hypotheses", [])
    cross_modal = investigation_output.get("cross_modal_flags", [])
    evidence_requests = investigation_output.get("evidence_requests", [])
    compressed = investigation_output.get("compressed_state")
    new_insights = investigation_output.get("key_insights", [])
    token_usage = investigation_output.get("token_usage", {})

    # Current cycle number (before appending this cycle's record)
    cycle_num = len(cf.get("cycle_history", [])) + 1

    # Replace active hypotheses with survivors
    cf["active_hypotheses"] = surviving

    # Append newly eliminated hypotheses (dedup by id)
    existing_eliminated = cf.get("eliminated_hypotheses", [])
    existing_elim_ids = {e.get("id") for e in existing_eliminated}
    for elim in new_eliminated:
        if elim.get("id") not in existing_elim_ids:
            if "killed_in_cycle" not in elim:
                elim = {**elim, "killed_in_cycle": cycle_num}
            existing_eliminated.append(elim)
    cf["eliminated_hypotheses"] = existing_eliminated

    # Update cross-modal flags
    existing_flags = cf.get("cross_modal_flags", [])
    for flag in cross_modal:
        if "detected_in_cycle" not in flag:
            flag = {**flag, "detected_in_cycle": cycle_num}
        existing_flags.append(flag)
    cf["cross_modal_flags"] = existing_flags

    # Replace compressed reasoning
    if compressed:
        cf["compressed_reasoning"] = compressed

    # Extend key insights (dedup by content)
    existing_insights = cf.get("key_insights", [])
    existing_set = set(existing_insights)
    for insight in new_insights:
        if insight not in existing_set:
            existing_insights.append(insight)
            existing_set.add(insight)
    cf["key_insights"] = existing_insights

    # Append cycle record
    cycle_record = {
        "cycle_num": cycle_num,
        "hypotheses_count": len(surviving),
        "eliminations_count": len(new_eliminated),
        "evidence_collected_count": len(cf.get("evidence_pending", [])),
        "token_usage": token_usage,
        "duration_seconds": None,
    }
    history = cf.get("cycle_history", [])
    history.append(cycle_record)
    cf["cycle_history"] = history

    # Queue new evidence requests for next cycle
    cf["evidence_pending"] = evidence_requests

    # Update metadata
    cf["status"] = "investigating"
    cf["updated_at"] = datetime.now(timezone.utc).isoformat()

    return cf


def should_continue(case_file: dict) -> str:
    """
    Determine whether investigation should continue or converge.

    Convergence conditions (any one triggers convergence):
      1. Active hypotheses ≤ CONVERGENCE_THRESHOLD (2)
      2. Cycle count ≥ MAX_CYCLES (5)
      3. Stagnation: last STAGNATION_CYCLES (2) cycles have identical hypothesis counts

    Args:
        case_file: Current serialized CaseFile

    Returns:
        "continue" or "converge"
    """
    active = case_file.get("active_hypotheses", [])
    history = case_file.get("cycle_history", [])

    # 1. Hypothesis count at or below convergence threshold
    if len(active) <= config.CONVERGENCE_THRESHOLD:
        return "converge"

    # 2. Max cycles reached
    if len(history) >= config.MAX_CYCLES:
        return "converge"

    # 3. Stagnation — last N cycles have the same hypothesis count
    if len(history) >= config.STAGNATION_CYCLES:
        recent_counts = [
            h.get("hypotheses_count", -1)
            for h in history[-config.STAGNATION_CYCLES:]
        ]
        if len(set(recent_counts)) == 1:
            return "converge"

    return "continue"


async def generate_alert(case_file: dict) -> dict:
    """
    Generate the final AlertDiagnosis after convergence.

    Makes a single Gemini call to produce a structured diagnosis and
    recommended actions based on surviving hypotheses and investigation findings.

    Args:
        case_file: Converged CaseFile dict

    Returns:
        Alert dict matching Alert model schema
    """
    active = case_file.get("active_hypotheses", [])

    # Fast path: no survivors → all-clear without Gemini call
    if not active:
        return {
            "level": "ALL-CLEAR",
            "diagnosis": (
                "All hypotheses were eliminated through evidence contradiction. "
                "No systemic risk confirmed."
            ),
            "surviving_hypotheses": [],
            "key_evidence": [],
            "recommended_actions": ["Continue standard monitoring protocols."],
        }

    prompt = _build_alert_prompt(case_file)
    result = await call_gemini(prompt)
    response = result.get("response", {})

    # Fallback if Gemini returns unexpected format
    if not isinstance(response, dict) or "level" not in response:
        max_score = max((h.get("score", 0) for h in active), default=0)
        level = "CRITICAL" if max_score > 0.6 else "MONITOR"
        return {
            "level": level,
            "diagnosis": (
                f"Investigation converged with {len(active)} surviving hypothesis/hypotheses. "
                "Manual review recommended."
            ),
            "surviving_hypotheses": [h.get("id", "?") for h in active],
            "key_evidence": [],
            "recommended_actions": [
                "Escalate to senior risk officer.",
                "Review surviving hypotheses manually.",
            ],
        }

    return {
        "level": response.get("level", "MONITOR"),
        "diagnosis": response.get("diagnosis", ""),
        "surviving_hypotheses": response.get("surviving_hypotheses", []),
        "key_evidence": response.get("key_evidence", []),
        "recommended_actions": response.get("recommended_actions", []),
    }


async def detect_contagion(case_file: dict) -> list[dict]:
    """
    Identify counterparty contagion risks from the investigation.

    Stub implementation — returns empty list.
    Full implementation would identify connected entities and assess risk transfer.

    Args:
        case_file: Converged CaseFile dict

    Returns:
        List of NetworkAlert dicts (empty in stub)
    """
    return []
