"""
LangGraph investigation graph - wires all agent functions together.

CRITICAL: This is the ONLY file that imports LangGraph.
All agents are pure functions that receive state and return results.

Flow:
  1. Tier 2 Evaluation → decide escalate or drop
  2. Create Case File → initialize investigation
  3. [CYCLE LOOP]:
     - Investigate → reason about hypotheses
     - Process Output → update case file
     - Check Convergence → continue or converge?
     - Gather Evidence → if continue
     - Increment Cycle → loop back to Investigate
  4. Generate Alert → produce final output

All Gemini calls use client from gemini/client.py.
"""

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

# Phase 5: Orchestrator functions
from agents.orchestrator import (
    evaluate_signal,
    assess_tier2_promotion,
    create_case_file,
    prepare_investigator_context,
    parse_investigator_output,
    update_case_file_with_investigator_output,
    decide_convergence,
    needs_evidence,
    generate_alert,
    finalize_case_file,
    detect_network_contagion,
    update_network_alerts,
)

# Phase 3: Investigator V2
from agents.investigator_v2 import investigate

# Phase 4: Evidence Pipeline
from agents.evidence.packager import gather_evidence


# =============================================================================
# STATE DEFINITION
# =============================================================================


class InvestigationState(TypedDict, total=False):
    """
    State flowing between LangGraph nodes.

    All fields are JSON-serializable dicts/lists.
    """
    # Inputs
    trigger_signal: dict
    entity: str

    # Cycle management
    current_cycle: int
    max_cycles: int

    # Core state
    case_file: dict

    # Intermediate results
    tier2_assessment: dict
    tier2_decision: dict
    investigation_output: dict
    new_evidence: list[dict]
    convergence_decision: dict


# =============================================================================
# NODE FUNCTIONS
# =============================================================================


async def tier2_evaluate_node(state: InvestigationState) -> InvestigationState:
    """Tier 2 semantic evaluation - decide if signal warrants investigation."""
    print(f"\n🔍 Tier 2 Evaluation: {state['entity']}")

    assessment = await evaluate_signal(state["trigger_signal"])
    state["tier2_assessment"] = assessment

    # Make promotion decision
    decision = assess_tier2_promotion(assessment)
    state["tier2_decision"] = decision

    print(f"  Decision: {decision['decision']} (confidence: {decision['confidence']})")

    return state


def create_case_node(state: InvestigationState) -> InvestigationState:
    """Initialize case file for new investigation."""
    print(f"\n📋 Creating case file for {state['entity']}")

    case_file = create_case_file(
        entity=state["entity"],
        trigger=state["trigger_signal"],
        tier=4,  # Start at Tier 4 (full investigation)
    )

    state["case_file"] = case_file
    state["current_cycle"] = 1  # Start at cycle 1

    print(f"  Case file created: Tier {case_file['tier']}, Status: {case_file['status']}")

    return state


async def investigate_node(state: InvestigationState) -> InvestigationState:
    """
    Core reasoning cycle - evaluate hypotheses against evidence.

    Investigator gets fresh context window per cycle (stateless reasoning).
    """
    cycle_num = state["current_cycle"]
    print(f"\n🔬 Investigation Cycle {cycle_num}")

    # Prepare context for investigator
    context = prepare_investigator_context(
        case_file=state["case_file"],
        cycle_num=cycle_num,
        new_evidence=state.get("new_evidence", []),
    )

    print(f"  Context: {len(context['evidence'])} evidence, {len(context['active_hypotheses'])} hypotheses")

    # Call investigator (5 phases)
    result = await investigate(context)

    state["investigation_output"] = result

    print(f"  Completed: {result['token_usage']['total']} tokens used")

    return state


def process_output_node(state: InvestigationState) -> InvestigationState:
    """Parse investigator output and update case file."""
    cycle_num = state["current_cycle"]

    print(f"\n📊 Processing Cycle {cycle_num} Output")

    # Parse investigator output
    parsed = parse_investigator_output(
        state["investigation_output"],
        cycle_num=cycle_num,
    )

    # Update case file
    case_file = update_case_file_with_investigator_output(
        state["case_file"],
        parsed,
        cycle_num=cycle_num,
    )

    state["case_file"] = case_file

    print(f"  Active: {len(case_file['active_hypotheses'])}, "
          f"Eliminated: {len(case_file['eliminated_hypotheses'])}")

    return state


def check_convergence_node(state: InvestigationState) -> InvestigationState:
    """Decide if investigation should continue or converge."""
    cycle_num = state["current_cycle"]

    print(f"\n🎯 Checking Convergence (Cycle {cycle_num})")

    decision = decide_convergence(
        state["case_file"],
        cycle_num=cycle_num,
    )

    state["convergence_decision"] = decision

    print(f"  Decision: {decision['decision']}")
    print(f"  Reason: {decision['reason']}")

    return state


async def gather_evidence_node(state: InvestigationState) -> InvestigationState:
    """
    Gather new evidence using Evidence Packager.

    Packager dispatches 3 retrieval agents in parallel, then tags
    observations via Gemini.
    """
    print(f"\n📦 Gathering Evidence")

    evidence_requests = state["case_file"]["evidence_pending"]
    active_hypotheses = state["case_file"]["active_hypotheses"]
    entity = state["case_file"]["entity"]

    print(f"  Requests: {len(evidence_requests)}")

    # Gather and tag evidence
    tagged_evidence = await gather_evidence(
        evidence_requests=evidence_requests,
        active_hypotheses=active_hypotheses,
        entity=entity,
    )

    state["new_evidence"] = tagged_evidence

    print(f"  Retrieved: {len(tagged_evidence)} observations")

    return state


def increment_cycle_node(state: InvestigationState) -> InvestigationState:
    """Increment cycle counter for next reasoning cycle."""
    state["current_cycle"] = state.get("current_cycle", 0) + 1
    print(f"\n➡️  Advancing to Cycle {state['current_cycle']}")
    return state


async def generate_alert_node(state: InvestigationState) -> InvestigationState:
    """
    Generate final alert and detect network contagion.
    """
    print(f"\n🚨 Generating Alert")

    # Generate alert
    alert = generate_alert(state["case_file"])

    # Detect contagion
    network_alerts = detect_network_contagion(state["case_file"])

    # Update case file
    case_file = finalize_case_file(state["case_file"], alert)
    case_file = update_network_alerts(case_file, network_alerts)

    state["case_file"] = case_file

    print(f"  Alert Level: {alert['level']}")
    print(f"  Network Alerts: {len(network_alerts)}")

    return state


# =============================================================================
# ROUTING FUNCTIONS
# =============================================================================


def route_tier2(state: InvestigationState) -> Literal["create_case", "__end__"]:
    """Route based on Tier 2 assessment - escalate or drop."""
    decision = state.get("tier2_decision", {}).get("decision", "demote")

    if decision == "promote":
        return "create_case"
    else:
        print("\n⏹️  Investigation demoted - END")
        return "__end__"


def route_convergence(state: InvestigationState) -> Literal["gather_evidence", "generate_alert"]:
    """Route based on convergence - continue cycles or generate alert."""
    decision = state.get("convergence_decision", {}).get("decision", "converge")

    if decision == "continue":
        # Check if we need evidence
        cycle_num = state["current_cycle"] + 1
        if needs_evidence(state["case_file"], cycle_num):
            return "gather_evidence"
        else:
            # No evidence needed, go straight to next investigate cycle
            # But LangGraph doesn't allow direct loops, so gather_evidence with empty result
            return "gather_evidence"
    else:
        return "generate_alert"


# =============================================================================
# GRAPH CONSTRUCTION
# =============================================================================


def create_investigation_graph():
    """
    Build and compile LangGraph investigation graph.

    Returns:
        Compiled StateGraph ready for execution
    """

    graph = StateGraph(InvestigationState)

    # Add all nodes
    graph.add_node("tier2_evaluate", tier2_evaluate_node)
    graph.add_node("create_case", create_case_node)
    graph.add_node("investigate", investigate_node)
    graph.add_node("process_output", process_output_node)
    graph.add_node("check_convergence", check_convergence_node)
    graph.add_node("gather_evidence", gather_evidence_node)
    graph.add_node("increment_cycle", increment_cycle_node)
    graph.add_node("generate_alert", generate_alert_node)

    # Entry point - start with Tier 2 evaluation
    graph.set_entry_point("tier2_evaluate")

    # Conditional edge: Tier 2 decision
    graph.add_conditional_edges(
        "tier2_evaluate",
        route_tier2,
        {
            "create_case": "create_case",
            "__end__": END,
        }
    )

    # Main investigation flow
    graph.add_edge("create_case", "investigate")
    graph.add_edge("investigate", "process_output")
    graph.add_edge("process_output", "check_convergence")

    # Conditional edge: Convergence decision
    graph.add_conditional_edges(
        "check_convergence",
        route_convergence,
        {
            "gather_evidence": "gather_evidence",
            "generate_alert": "generate_alert",
        }
    )

    # Cycle loop - gather evidence → increment → investigate
    graph.add_edge("gather_evidence", "increment_cycle")
    graph.add_edge("increment_cycle", "investigate")

    # Exit - after alert generation
    graph.add_edge("generate_alert", END)

    # Compile and return
    print("✅ LangGraph compiled successfully")
    return graph.compile()


# Export compiled graph (singleton - compile once)
compiled_graph = create_investigation_graph()
