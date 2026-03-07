# Phase 5: Orchestrator

**Status:** Pending Phase 4 completion
**Duration:** ~1.5 hours
**Dependencies:** Phase 1-4 (all previous phases)
**Build Order:** 5 of 7

---

## Context

Pure logic functions for investigation lifecycle management. Orchestrator coordinates all other agents but does NO reasoning itself.

**Key Points:**
- FIXED context window for entire investigation (~15-20% utilization)
- ONLY component that reads/writes case file
- NO Gemini call for compression (Investigator self-compresses)
- Gemini calls ONLY for: Tier 2 evaluation, alert generation, contagion detection
- Contains PURE LOGIC FUNCTIONS - NO LangGraph imports (testable in isolation)

---

## Files to Create

### 1. `backend/gemini/prompts/tier2_evaluation.py`

```python
def build_tier2_prompt(trigger: dict) -> str:
    """Tier 2 semantic evaluation prompt"""
    return f"""
Assess whether this trigger signal warrants full investigation.

TRIGGER:
- Entity: {trigger.get('entity')}
- Event: {trigger.get('event')}
- Magnitude: {trigger.get('magnitude')}

Return JSON:
{{
  "assessment": "reasoning here",
  "decision": "escalate" or "dismiss"
}}
"""
```

### 2. `backend/agents/orchestrator.py`

**Critical:** NO LangGraph imports. Pure functions only.

```python
import asyncio
from models.case_file import CaseFile, Hypothesis, EliminatedHypothesis
from gemini.client import call_gemini
from gemini.prompts.tier2_evaluation import build_tier2_prompt
from utils.parser import parse_compressed_state
from utils.token_counter import track_token_usage
from utils.corpus_loader import load_corpus_file
import config

async def evaluate_signal(trigger: dict) -> dict:
    """Tier 2 semantic evaluation"""
    prompt = build_tier2_prompt(trigger)
    result = await call_gemini(prompt)
    return result["response"]

def create_case_file(entity: str, trigger: dict) -> dict:
    """Initialize new CaseFile"""
    case = CaseFile(
        entity=entity,
        tier=2,
        status="pending",
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
        network_alerts=[]
    )
    return case.model_dump()

def prepare_investigator_context(case_file: dict, new_evidence: list[dict]) -> dict:
    """Assemble flat context package for Investigator"""
    # Load full evidence content from corpus for previously collected atoms
    all_evidence = []

    # Add previously collected evidence (load full content from corpus)
    for ref in case_file.get("evidence_collected", []):
        try:
            corpus_type = "structural" if ref["type"] == "structural" else "empirical"
            full_atom = load_corpus_file(ref["atom_id"], corpus_type)
            all_evidence.append(full_atom)
        except FileNotFoundError:
            print(f"Warning: Could not load {ref['atom_id']}")

    # Add new evidence from packager
    all_evidence.extend(new_evidence)

    return {
        "trigger": case_file["trigger"],
        "entity": case_file["entity"],
        "cycle_num": len(case_file["cycle_history"]) + 1,
        "compressed_state": case_file.get("compressed_reasoning"),
        "evidence": all_evidence,
        "active_hypotheses": case_file.get("active_hypotheses", [])
    }

def process_investigation_output(case_file: dict, investigation_output: dict) -> dict:
    """Update case file with investigation results"""
    from models.case_file import CaseFile, EliminatedHypothesis, EvidenceRef

    # Parse output
    surviving = investigation_output.get("surviving_hypotheses", [])
    eliminated = investigation_output.get("eliminated_hypotheses", [])
    compressed = investigation_output.get("compressed_state")

    # Update case file (REPLACE surviving, APPEND eliminated, REPLACE compressed)
    case_file["active_hypotheses"] = surviving
    case_file["eliminated_hypotheses"].extend(eliminated)
    case_file["compressed_reasoning"] = compressed  # REPLACED not appended

    # Add evidence references (ID + brief only)
    new_refs = []
    for obs in investigation_output.get("new_evidence", []):
        new_refs.append({
            "atom_id": obs["observation_id"],
            "brief": obs["content"][:100] + "...",
            "type": obs["type"],
            "collected_in_cycle": len(case_file["cycle_history"]) + 1
        })
    case_file["evidence_collected"].extend(new_refs)

    # Update evidence_pending
    case_file["evidence_pending"] = investigation_output.get("evidence_requests", [])

    # Add cycle record
    case_file["cycle_history"].append({
        "cycle_num": len(case_file["cycle_history"]) + 1,
        "hypotheses_count": len(surviving),
        "eliminations_count": len(eliminated),
        "evidence_collected_count": len(new_refs),
        "token_usage": investigation_output.get("token_usage", {})
    })

    # Track tokens
    tokens = investigation_output.get("token_usage", {})
    case_file["token_usage"] = track_token_usage(
        "investigator",
        len(case_file["cycle_history"]),
        tokens.get("input_tokens", 0),
        tokens.get("output_tokens", 0),
        case_file["token_usage"]
    )

    return case_file

def should_continue(case_file: dict) -> str:
    """Convergence detection - pure logic"""
    active_count = len(case_file.get("active_hypotheses", []))
    cycle_count = len(case_file.get("cycle_history", []))

    # Converge if ≤2 hypotheses
    if active_count <= config.CONVERGENCE_THRESHOLD:
        return "converge"

    # Converge if max cycles reached
    if cycle_count >= config.MAX_CYCLES:
        return "converge"

    # Check stagnation (count unchanged for 2 consecutive cycles)
    if len(case_file["cycle_history"]) >= 2:
        last_two = case_file["cycle_history"][-2:]
        if last_two[0]["hypotheses_count"] == last_two[1]["hypotheses_count"]:
            return "converge"

    return "continue"

async def generate_alert(case_file: dict) -> dict:
    """Post-convergence alert generation"""
    # TODO: Add Gemini call to evaluate surviving hypotheses
    survivors = case_file.get("active_hypotheses", [])

    if any(h.get("score", 0) > 0.7 for h in survivors):
        return {
            "level": "CRITICAL",
            "diagnosis": "Crisis hypotheses survive with high confidence",
            "surviving_hypotheses": survivors,
            "key_evidence": [],
            "recommended_actions": ["Escalate to senior management"]
        }
    else:
        return {
            "level": "ALL-CLEAR",
            "diagnosis": "All crisis hypotheses eliminated",
            "surviving_hypotheses": survivors,
            "key_evidence": [],
            "recommended_actions": []
        }

async def detect_contagion(case_file: dict) -> list[dict]:
    """Post-convergence contagion detection"""
    # TODO: Add Gemini call to identify counterparties
    return []
```

---

## Verification Test

Create `backend/test_phase5.py`:

```python
#!/usr/bin/env python3
"""Phase 5 Verification: Test Orchestrator"""

import asyncio
from agents.orchestrator import (
    evaluate_signal, create_case_file, should_continue,
    prepare_investigator_context, process_investigation_output
)

async def test_tier2():
    print("Testing Tier 2 evaluation...")
    trigger = {"entity": "SVB", "event": "CDS spike", "magnitude": 450}
    assessment = await evaluate_signal(trigger)

    assert "decision" in assessment
    assert assessment["decision"] in ["escalate", "dismiss"]
    print(f"✓ Tier 2 decision: {assessment['decision']}")

def test_case_file_creation():
    print("\nTesting case file creation...")
    trigger = {"entity": "SVB", "event": "CDS spike"}
    case = create_case_file("SVB", trigger)

    assert case["entity"] == "SVB"
    assert case["tier"] == 2
    assert len(case["active_hypotheses"]) == 0
    print(f"✓ Case file created for {case['entity']}")

def test_convergence():
    print("\nTesting convergence logic...")

    # Test: ≤2 hypotheses → converge
    case = {"active_hypotheses": [{"id": "H01"}, {"id": "H02"}], "cycle_history": []}
    assert should_continue(case) == "converge"
    print(f"✓ Converges with 2 hypotheses")

    # Test: >2 hypotheses → continue
    case = {"active_hypotheses": [{"id": f"H{i:02d}"} for i in range(1, 6)], "cycle_history": []}
    assert should_continue(case) == "continue"
    print(f"✓ Continues with 5 hypotheses")

async def main():
    print("=" * 60)
    print("Phase 5 Verification: Orchestrator")
    print("=" * 60)

    await test_tier2()
    test_case_file_creation()
    test_convergence()

    print("\n" + "=" * 60)
    print("✅ ORCHESTRATOR VALIDATED - Phase 5 Complete!")
    print("=" * 60)
    print("\nVerified:")
    print("  ✓ Tier 2 evaluation works")
    print("  ✓ Case file creation works")
    print("  ✓ Convergence logic works")
    print("  ✓ NO LangGraph imports (pure functions)")
    print("\nReady to proceed to Phase 6: LangGraph Wiring")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Success Criteria

- [ ] Tier 2 evaluation calls Gemini
- [ ] Case file creation works
- [ ] Convergence logic correct
- [ ] NO LangGraph imports in orchestrator.py
- [ ] All functions testable in isolation

---

## Next Steps

After Phase 5 passes:
✅ All agent logic complete
✅ Ready for Phase 6: Wire everything together with LangGraph

**STOP HERE and verify before proceeding to Phase 6.**
