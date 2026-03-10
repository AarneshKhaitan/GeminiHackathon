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
from agents.evidence.batch_tagger import tag_all_evidence_parallel
from agents.evidence.selector import select_evidence_for_requests


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

    # ChromaDB embedding management
    embeddings_indexed: bool  # Flag to prevent re-indexing
    embedding_launched: bool  # Flag to prevent duplicate launches

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

    # If Cycle 1 and we have hypotheses, embed all observations for semantic search
    # Do NOT tag them yet - we'll tag selected observations per-cycle
    if (cycle_num == 1 and
        result.get("surviving_hypotheses") and
        not state.get("embeddings_indexed") and
        not state.get("embedding_launched")):

        entity = state["case_file"]["entity"]

        print(f"  📊 Indexing observations in vector database (for semantic search)...")

        # Mark as launched to prevent duplicates
        state["embedding_launched"] = True

        # Load all observations (untagged)
        from utils.corpus_loader import load_all_corpus
        structural_obs = load_all_corpus(entity, "structural")
        empirical_obs = load_all_corpus(entity, "empirical")
        all_observations = structural_obs + empirical_obs

        # Index in ChromaDB (computes embeddings)
        try:
            from agents.evidence.selector import index_observations
            index_observations(all_observations, entity)
            state["embeddings_indexed"] = True
            print(f"  ✓ Vector index complete: {len(all_observations)} observations indexed")
        except Exception as e:
            print(f"  ⚠️  Vector indexing failed: {e}")

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

    # Track evidence gathered in this cycle (add to cycle history)
    new_evidence = state.get("new_evidence", [])
    if new_evidence and case_file.get("cycle_history"):
        # Find the current cycle in history and add evidence_gathered
        for cycle in case_file["cycle_history"]:
            if cycle["cycle_num"] == cycle_num:
                cycle["evidence_gathered"] = [obs["observation_id"] for obs in new_evidence]
                break

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
        min_cycles=3,  # Force minimum 3 cycles for demo
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

    # Track which observations have already been gathered (from evidence_collected)
    already_gathered = [ref["atom_id"] for ref in state["case_file"].get("evidence_collected", [])]

    print(f"  Requests: {len(evidence_requests)}")
    print(f"  Already gathered: {len(already_gathered)} observations")

    # Use ChromaDB to select semantically matching observations
    if state.get("embeddings_indexed") and evidence_requests:
        print(f"  🔍 Using semantic search to match {len(evidence_requests)} requests...")

        # Get entity name
        entity = state["case_file"]["entity"]

        # Load all observations (untagged)
        from utils.corpus_loader import load_all_corpus
        structural_obs = load_all_corpus(entity, "structural")
        empirical_obs = load_all_corpus(entity, "empirical")
        all_observations = structural_obs + empirical_obs

        # Use selector to find best matches via ChromaDB
        selected_observations = await select_evidence_for_requests(
            evidence_requests=evidence_requests,
            available_observations=all_observations,
            already_gathered=already_gathered,
        )

        print(f"  📋 Selected {len(selected_observations)} observations via semantic search")

        # Now tag the selected observations against current hypotheses
        if selected_observations and active_hypotheses:
            print(f"  🏷️  Tagging {len(selected_observations)} selected observations...")

            from agents.evidence.batch_tagger import tag_single_batch

            tagged_evidence = await tag_single_batch(
                observations=selected_observations,
                hypotheses=active_hypotheses,
                batch_num=1
            )

            print(f"  ✓ Tagged {len(tagged_evidence)} observations")
        else:
            tagged_evidence = selected_observations

    else:
        # Fallback: no embeddings yet or no requests
        print(f"  ⚠️  Embeddings not ready or no requests, returning empty")
        tagged_evidence = []

    state["new_evidence"] = tagged_evidence

    # Update evidence_collected in case_file (FIX: properly track evidence)
    from agents.orchestrator import update_evidence_collected
    if tagged_evidence:
        state["case_file"] = update_evidence_collected(
            state["case_file"],
            tagged_evidence,
            state["current_cycle"]
        )

    # Track which observations were gathered (for next cycle filtering)
    gathered_ids = [obs["observation_id"] for obs in tagged_evidence]

    print(f"  Retrieved: {len(tagged_evidence)} observations: {gathered_ids}")

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
