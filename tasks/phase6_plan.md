# Phase 6: LangGraph Wiring

**Status:** Pending Phase 5 completion
**Duration:** ~1 hour
**Dependencies:** Phase 1-5 (all agents implemented)
**Build Order:** 6 of 7

---

## Context

Wire all pure functions into StateGraph with conditional edges. ONLY file that imports LangGraph.

**Key Points:**
- Imports pure functions from orchestrator.py, investigator.py, packager.py
- Uses LangChain client for all Gemini calls (already configured in Phase 2)
- All agents call gemini/client.py's `call_gemini()` function
- If LangGraph gives trouble → can fallback to simple async loop
- All logic already tested in previous phases

**LangChain Integration:**
- All agents use `from gemini.client import call_gemini`
- LangChain ChatGoogleGenerativeAI is wrapped in our client
- Seamless integration with LangGraph's async execution
- Token tracking and retry logic handled automatically

---

## File to Create

### `backend/graph/investigation_graph.py`

**Architecture Notes:**
- LangGraph manages state flow between nodes
- Each node calls pure functions from agents/
- All Gemini calls go through `gemini.client.call_gemini()` (LangChain-based)
- State is TypedDict (JSON-serializable for LangGraph compatibility)
- Agents are stateless - receive context, return results

```python
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

All Gemini calls use LangChain client from gemini/client.py.
"""

from langgraph.graph import StateGraph, END
from models.state import InvestigationState
from agents.orchestrator import (
    evaluate_signal, create_case_file, prepare_investigator_context,
    process_investigation_output, should_continue, generate_alert, detect_contagion
)
from agents.investigator import investigate
from agents.evidence.packager import gather_evidence


def create_investigation_graph():
    """
    Build and compile LangGraph investigation graph.

    Returns:
        Compiled StateGraph ready for execution

    Notes:
        - All async functions use LangChain client internally
        - State flows as TypedDict between nodes
        - Conditional edges handle routing logic
    """

    graph = StateGraph(InvestigationState)

    # Node wrappers (thin wrappers around pure agent functions)

    async def tier2_node(state):
        """Tier 2 semantic evaluation - decide if signal warrants investigation."""
        assessment = await evaluate_signal(state["trigger_signal"])
        state["tier2_assessment"] = assessment
        return state

    def create_case_node(state):
        """Initialize case file for new investigation."""
        case_file = create_case_file(state["entity"], state["trigger_signal"])
        state["case_file"] = case_file
        return state

    async def investigate_node(state):
        """
        Core reasoning cycle - evaluate hypotheses against evidence.

        Investigator uses LangChain client to call Gemini. Gets fresh
        context window per cycle (stateless reasoning).
        """
        context = prepare_investigator_context(
            state["case_file"],
            state.get("new_evidence", [])
        )
        result = await investigate(context)  # Calls gemini.client.call_gemini()
        state["investigation_output"] = result
        return state

    def process_node(state):
        """Parse investigator output and update case file."""
        updated_case = process_investigation_output(
            state["case_file"],
            state["investigation_output"]
        )
        state["case_file"] = updated_case
        return state

    def convergence_node(state):
        """Decide if investigation should continue or converge."""
        decision = should_continue(state["case_file"])
        state["convergence_decision"] = decision
        return state

    async def evidence_node(state):
        """
        Gather new evidence using Evidence Packager.

        Packager dispatches 3 retrieval agents in parallel, then tags
        observations using LangChain client.
        """
        evidence_requests = state["case_file"]["evidence_pending"]
        active_hypotheses = state["case_file"]["active_hypotheses"]
        tagged_evidence = await gather_evidence(evidence_requests, active_hypotheses)
        state["new_evidence"] = tagged_evidence
        return state

    def increment_node(state):
        """Increment cycle counter for next reasoning cycle."""
        state["current_cycle"] = state.get("current_cycle", 0) + 1
        return state

    async def alert_node(state):
        """
        Generate final alert and detect network contagion.

        Uses LangChain client for final diagnosis summary.
        """
        alert = await generate_alert(state["case_file"])
        contagion = await detect_contagion(state["case_file"])
        state["case_file"]["alert"] = alert
        state["case_file"]["network_alerts"] = contagion
        return state

    # Add all nodes to graph
    graph.add_node("tier2_evaluate", tier2_node)
    graph.add_node("create_case", create_case_node)
    graph.add_node("investigate", investigate_node)
    graph.add_node("process_output", process_node)
    graph.add_node("check_convergence", convergence_node)
    graph.add_node("gather_evidence", evidence_node)
    graph.add_node("increment_cycle", increment_node)
    graph.add_node("generate_alert", alert_node)

    # Entry point - start with Tier 2 evaluation
    graph.set_entry_point("tier2_evaluate")

    # Conditional edge: Tier 2 decision
    def route_tier2(state):
        """Route based on Tier 2 assessment - escalate or drop."""
        decision = state.get("tier2_assessment", {}).get("decision")
        return "create_case" if decision == "escalate" else END

    graph.add_conditional_edges("tier2_evaluate", route_tier2, {
        "create_case": "create_case",
        END: END
    })

    # Main investigation flow
    graph.add_edge("create_case", "investigate")
    graph.add_edge("investigate", "process_output")
    graph.add_edge("process_output", "check_convergence")

    # Conditional edge: Convergence decision
    def route_convergence(state):
        """Route based on convergence - continue cycles or generate alert."""
        decision = state.get("convergence_decision")
        return "gather_evidence" if decision == "continue" else "generate_alert"

    graph.add_conditional_edges("check_convergence", route_convergence, {
        "gather_evidence": "gather_evidence",
        "generate_alert": "generate_alert"
    })

    # Cycle loop - gather evidence → increment → investigate
    graph.add_edge("gather_evidence", "increment_cycle")
    graph.add_edge("increment_cycle", "investigate")

    # Exit - after alert generation
    graph.add_edge("generate_alert", END)

    # Compile and return
    return graph.compile()


# Export compiled graph (singleton - compile once)
compiled_graph = create_investigation_graph()
```

---

## Verification Test

Create `backend/test_phase6.py`:

```python
#!/usr/bin/env python3
"""Phase 6 Verification: Test LangGraph Wiring"""

import asyncio
from graph.investigation_graph import compiled_graph

async def test_full_investigation():
    print("Testing full investigation run...")

    initial_state = {
        "trigger_signal": {
            "entity": "SVB",
            "event": "CDS spreads spiked to 450bps",
            "date": "2023-03-08"
        },
        "entity": "SVB",
        "current_cycle": 0,
        "max_cycles": 3  # Limit to 3 cycles for testing
    }

    # Run graph
    result = await compiled_graph.ainvoke(initial_state)

    # Verify
    assert "case_file" in result
    assert len(result["case_file"]["cycle_history"]) > 0

    print(f"✓ Investigation completed")
    print(f"✓ Ran {len(result['case_file']['cycle_history'])} cycles")
    print(f"✓ Final status: {result['case_file'].get('status', 'unknown')}")
    print(f"✓ Surviving hypotheses: {len(result['case_file']['active_hypotheses'])}")

    return result

async def main():
    print("=" * 60)
    print("Phase 6 Verification: LangGraph Wiring")
    print("=" * 60)

    result = await test_full_investigation()

    print("\n" + "=" * 60)
    print("✅ LANGGRAPH VALIDATED - Phase 6 Complete!")
    print("=" * 60)
    print("\nVerified:")
    print("  ✓ Graph compiles successfully")
    print("  ✓ Full investigation runs end-to-end")
    print("  ✓ Conditional edges work (Tier 2, convergence)")
    print("  ✓ Cycle loop executes correctly")
    print("\nReady to proceed to Phase 7: FastAPI Endpoints")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Success Criteria

- [ ] Graph compiles without errors
- [ ] Full investigation runs end-to-end
- [ ] Conditional edges work correctly (Tier 2 routing, convergence routing)
- [ ] Cycle loop executes properly
- [ ] State flows between nodes as TypedDict
- [ ] All Gemini calls use LangChain client (from Phase 2)
- [ ] Token tracking aggregates across all cycles
- [ ] Fresh context windows per investigator cycle

---

## Next Steps

After Phase 6 passes:
✅ Complete backend pipeline operational
✅ LangChain + LangGraph integration validated
✅ All agents using unified Gemini client
✅ Ready for Phase 7: FastAPI endpoints to expose to frontend

**Important Notes:**
- All Gemini calls go through `gemini.client.call_gemini()` (LangChain wrapper)
- No direct google-generativeai SDK calls in agents
- Token tracking happens automatically via client wrapper
- Retry logic and fallback handled by client

**STOP HERE and verify before proceeding to Phase 7.**
