"""
LangGraph investigation graph.

The ONLY module in this codebase that imports LangGraph.

Wires orchestrator pure functions + investigator + evidence packager
into a compiled StateGraph with the following node sequence:

  tier2_evaluate → [escalate] → create_case → investigate → process_output
                 → check_convergence → [continue] → gather_evidence → increment_cycle → investigate (loop)
                                    → [converge] → generate_alert → END

  tier2_evaluate → [dismiss] → END

Exports:
  compiled_graph  — module-level singleton, ready for ainvoke()
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from langgraph.graph import StateGraph, END

from models.state import InvestigationState
from agents.orchestrator import (
    evaluate_signal,
    create_case_file,
    prepare_investigator_context,
    process_investigation_output,
    should_continue,
    generate_alert,
    detect_contagion,
)
from agents.investigator_5phase import investigate
from agents.evidence.packager import gather_evidence


# ── Node Functions ─────────────────────────────────────────────────────────────

async def tier2_evaluate_node(state: InvestigationState) -> dict:
    """Tier 2: Semantic evaluation — decide escalate or dismiss."""
    trigger = state["trigger_signal"]
    assessment = await evaluate_signal(trigger)
    return {"tier2_assessment": assessment}


async def create_case_node(state: InvestigationState) -> dict:
    """Initialize the case file for a new investigation."""
    entity = state["entity"]
    trigger = state["trigger_signal"]
    case_file = create_case_file(entity, trigger)
    return {
        "case_file": case_file,
        "current_cycle": 0,
        "active_hypotheses": [],
        "eliminated_hypotheses": [],
        "new_evidence": [],
        "compressed_state": None,
        "cycle_history": [],
    }


async def investigate_node(state: InvestigationState) -> dict:
    """Run one cycle of the 5-phase investigator."""
    case_file = state["case_file"]
    new_evidence = state.get("new_evidence", [])
    context = prepare_investigator_context(case_file, new_evidence)
    output = await investigate(context)
    return {"investigation_output": output}


async def process_output_node(state: InvestigationState) -> dict:
    """Integrate investigation output into the case file."""
    case_file = state["case_file"]
    investigation_output = state["investigation_output"]
    updated_case = process_investigation_output(case_file, investigation_output)
    return {
        "case_file": updated_case,
        "active_hypotheses": updated_case.get("active_hypotheses", []),
        "eliminated_hypotheses": updated_case.get("eliminated_hypotheses", []),
        "compressed_state": updated_case.get("compressed_reasoning"),
        "cycle_history": updated_case.get("cycle_history", []),
    }


async def check_convergence_node(state: InvestigationState) -> dict:
    """Decide whether to continue investigation or converge."""
    case_file = state["case_file"]
    decision = should_continue(case_file)
    return {"convergence_decision": decision}


async def gather_evidence_node(state: InvestigationState) -> dict:
    """Collect new tagged evidence atoms for the next cycle."""
    case_file = state["case_file"]
    entity = state["entity"]
    evidence_requests = case_file.get("evidence_pending", [])
    active_hypotheses = case_file.get("active_hypotheses", [])

    if not evidence_requests:
        return {"new_evidence": []}

    new_evidence = await gather_evidence(evidence_requests, active_hypotheses, entity)
    return {"new_evidence": new_evidence}


async def increment_cycle_node(state: InvestigationState) -> dict:
    """Increment the investigation cycle counter."""
    current = state.get("current_cycle", 0)
    return {"current_cycle": current + 1}


async def generate_alert_node(state: InvestigationState) -> dict:
    """Generate the final alert and check for contagion after convergence."""
    case_file = state["case_file"]
    alert = await generate_alert(case_file)
    network_alerts = await detect_contagion(case_file)

    # Store results in the case file
    updated_case = {
        **case_file,
        "alert": alert,
        "network_alerts": network_alerts,
        "status": "converged",
    }
    return {
        "alert": alert,
        "network_alerts": network_alerts,
        "case_file": updated_case,
    }


# ── Conditional Routing ────────────────────────────────────────────────────────

def route_tier2(state: InvestigationState) -> str:
    """Route after Tier 2 evaluation: escalate → create_case, dismiss → END."""
    assessment = state.get("tier2_assessment") or {}
    decision = assessment.get("decision", "dismiss")
    return "escalate" if decision == "escalate" else "dismiss"


def route_convergence(state: InvestigationState) -> str:
    """Route after convergence check: continue → gather_evidence, converge → generate_alert."""
    return state.get("convergence_decision", "converge")


# ── Graph Builder ──────────────────────────────────────────────────────────────

def create_investigation_graph():
    """
    Build and compile the LangGraph investigation StateGraph.

    Returns:
        Compiled LangGraph graph ready for ainvoke()
    """
    graph = StateGraph(InvestigationState)

    # Register all nodes
    graph.add_node("tier2_evaluate", tier2_evaluate_node)
    graph.add_node("create_case", create_case_node)
    graph.add_node("investigate", investigate_node)
    graph.add_node("process_output", process_output_node)
    graph.add_node("check_convergence", check_convergence_node)
    graph.add_node("gather_evidence", gather_evidence_node)
    graph.add_node("increment_cycle", increment_cycle_node)
    graph.add_node("generate_alert", generate_alert_node)

    # Entry point
    graph.set_entry_point("tier2_evaluate")

    # Tier 2 conditional routing
    graph.add_conditional_edges(
        "tier2_evaluate",
        route_tier2,
        {
            "escalate": "create_case",
            "dismiss": END,
        },
    )

    # Linear flow: case creation → investigation → output processing → convergence check
    graph.add_edge("create_case", "investigate")
    graph.add_edge("investigate", "process_output")
    graph.add_edge("process_output", "check_convergence")

    # Convergence conditional routing
    graph.add_conditional_edges(
        "check_convergence",
        route_convergence,
        {
            "continue": "gather_evidence",
            "converge": "generate_alert",
        },
    )

    # Evidence gather → cycle increment → back to investigate (loop)
    graph.add_edge("gather_evidence", "increment_cycle")
    graph.add_edge("increment_cycle", "investigate")

    # Terminal
    graph.add_edge("generate_alert", END)

    return graph.compile()


# Module-level singleton — import this in main.py and test_phase6.py
compiled_graph = create_investigation_graph()
