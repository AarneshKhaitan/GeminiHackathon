#!/usr/bin/env python3
"""Phase 5 Verification: Orchestrator Pure Functions

Tests:
  1. create_case_file — initialization (pure)
  2. prepare_investigator_context — context builder (pure)
  3. process_investigation_output — state integration (pure)
  4. should_continue — convergence logic (pure, all 3 conditions)
  5. evaluate_signal — Tier 2 semantic eval (Gemini call)
  6. generate_alert — final alert generation (Gemini call)
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agents.orchestrator import (
    evaluate_signal,
    create_case_file,
    prepare_investigator_context,
    process_investigation_output,
    should_continue,
    generate_alert,
    detect_contagion,
)


# ── Test Data ──────────────────────────────────────────────────────────────────

MOCK_TRIGGER = {
    "entity": "Credit Suisse",
    "event": "CDS spread spike + Saudi National Bank capital refusal",
    "magnitude": "400bps CDS spread, 30% equity drop, $10B deposit outflows",
    "date": "2023-03-15",
    "description": "Saudi National Bank chairman publicly refused to inject capital. Depositor confidence collapsing.",
}

MOCK_HYPOTHESES = [
    {
        "id": "H01",
        "name": "AT1 bond wipeout risk",
        "description": "PONV clause triggers full AT1 write-down during resolution",
        "score": 0.80,
        "evidence_chain": ["S01", "S02"],
        "status": "active",
    },
    {
        "id": "H02",
        "name": "Confidence-driven bank run",
        "description": "Depositor panic driven by reputational contagion from SVB failure",
        "score": 0.72,
        "evidence_chain": ["E01"],
        "status": "active",
    },
    {
        "id": "H03",
        "name": "Regulatory forced acquisition",
        "description": "FINMA uses emergency powers to force UBS merger",
        "score": 0.68,
        "evidence_chain": [],
        "status": "active",
    },
]

MOCK_INVESTIGATION_OUTPUT = {
    "surviving_hypotheses": [MOCK_HYPOTHESES[0], MOCK_HYPOTHESES[1]],
    "eliminated_hypotheses": [
        {
            "id": "H03",
            "name": "Regulatory forced acquisition",
            "killed_by_atom": "S05",
            "killed_in_cycle": 1,
            "reason": "FINMA powers existed but merger was market-driven, not forced.",
        }
    ],
    "cross_modal_flags": [],
    "evidence_requests": [
        {
            "type": "market",
            "description": "CDS spreads week of March 15",
            "reason": "Track market reaction to capital refusal",
        }
    ],
    "compressed_state": "Cycle 1: AT1 write-down (H01) and bank run (H02) survive. FINMA acquisition (H03) eliminated by S05.",
    "key_insights": [
        "AT1 PONV clause confirmed in prospectus",
        "SNB refused capital injection on March 15",
    ],
    "token_usage": {"input_tokens": 12000, "output_tokens": 3000, "total_tokens": 15000},
}


# ── Tests ──────────────────────────────────────────────────────────────────────

def test_create_case_file():
    print("Testing create_case_file() — pure initialization...")
    print("-" * 50)

    case_file = create_case_file("Credit Suisse", MOCK_TRIGGER)

    assert case_file["entity"] == "Credit Suisse", "Wrong entity"
    assert case_file["tier"] == 3, "Wrong tier"
    assert case_file["status"] == "investigating", "Wrong status"
    assert case_file["trigger"] == MOCK_TRIGGER, "Wrong trigger"
    assert case_file["active_hypotheses"] == [], "Should start with no hypotheses"
    assert case_file["eliminated_hypotheses"] == [], "Should start with no eliminations"
    assert case_file["cycle_history"] == [], "Should start with no cycle history"
    assert case_file["compressed_reasoning"] is None, "Should start with no compressed reasoning"

    print(f"  entity = {case_file['entity']}")
    print(f"  tier = {case_file['tier']}")
    print(f"  status = {case_file['status']}")
    print("✓ create_case_file test passed\n")

    return case_file


def test_prepare_investigator_context(case_file: dict):
    print("Testing prepare_investigator_context() — pure context builder...")
    print("-" * 50)

    mock_evidence = [
        {
            "observation_id": "S01",
            "content": "AT1 prospectus clause content...",
            "type": "structural",
            "supports": ["H01"],
            "contradicts": [],
            "neutral": ["H02", "H03"],
        }
    ]

    context = prepare_investigator_context(case_file, mock_evidence)

    assert context["entity"] == "Credit Suisse", "Wrong entity"
    assert context["cycle_num"] == 1, f"Expected cycle 1, got {context['cycle_num']}"
    assert context["evidence"] == mock_evidence, "Evidence mismatch"
    assert context["trigger"] == MOCK_TRIGGER, "Trigger mismatch"
    assert context["compressed_state"] is None, "Should be None on first cycle"
    assert context["active_hypotheses"] == [], "Should be empty on first cycle"

    print(f"  entity = {context['entity']}")
    print(f"  cycle_num = {context['cycle_num']}")
    print(f"  evidence count = {len(context['evidence'])}")
    print(f"  compressed_state = {context['compressed_state']}")
    print("✓ prepare_investigator_context test passed\n")


def test_process_investigation_output(case_file: dict):
    print("Testing process_investigation_output() — pure state integration...")
    print("-" * 50)

    updated = process_investigation_output(case_file, MOCK_INVESTIGATION_OUTPUT)

    assert len(updated["active_hypotheses"]) == 2, f"Expected 2 survivors, got {len(updated['active_hypotheses'])}"
    assert len(updated["eliminated_hypotheses"]) == 1, f"Expected 1 eliminated, got {len(updated['eliminated_hypotheses'])}"
    assert updated["eliminated_hypotheses"][0]["id"] == "H03", "Wrong eliminated hypothesis"
    assert updated["compressed_reasoning"] == MOCK_INVESTIGATION_OUTPUT["compressed_state"]
    assert len(updated["cycle_history"]) == 1, "Expected 1 cycle record"
    assert updated["cycle_history"][0]["cycle_num"] == 1
    assert updated["cycle_history"][0]["hypotheses_count"] == 2
    assert updated["cycle_history"][0]["eliminations_count"] == 1
    assert len(updated["evidence_pending"]) == 1, "Expected 1 evidence request queued"
    assert len(updated["key_insights"]) == 2, "Expected 2 key insights"

    # Verify original case_file was NOT mutated (deep copy)
    assert case_file["active_hypotheses"] == [], "Original case_file was mutated!"

    print(f"  active_hypotheses: {len(updated['active_hypotheses'])} (H01, H02 survive)")
    print(f"  eliminated: {len(updated['eliminated_hypotheses'])} (H03 killed by S05)")
    print(f"  cycle_history: {len(updated['cycle_history'])} record")
    print(f"  evidence_pending: {len(updated['evidence_pending'])} request")
    print(f"  key_insights: {len(updated['key_insights'])}")
    print("✓ process_investigation_output test passed\n")

    return updated


def test_should_continue():
    print("Testing should_continue() — all 3 convergence conditions...")
    print("-" * 50)

    # Case 1: Many hypotheses, few cycles → continue
    case1 = {
        "active_hypotheses": [{"id": f"H0{i}"} for i in range(1, 6)],
        "cycle_history": [{"cycle_num": 1, "hypotheses_count": 5}],
    }
    result1 = should_continue(case1)
    assert result1 == "continue", f"Expected continue, got {result1}"
    print(f"  5 hypotheses, 1 cycle → {result1}")

    # Case 2: ≤2 hypotheses → converge (condition 1)
    case2 = {
        "active_hypotheses": [{"id": "H01"}, {"id": "H02"}],
        "cycle_history": [{"cycle_num": 1, "hypotheses_count": 2}],
    }
    result2 = should_continue(case2)
    assert result2 == "converge", f"Expected converge, got {result2}"
    print(f"  2 hypotheses → {result2}  (≤ CONVERGENCE_THRESHOLD)")

    # Case 3: Max cycles reached → converge (condition 2)
    case3 = {
        "active_hypotheses": [{"id": f"H0{i}"} for i in range(1, 5)],
        "cycle_history": [{"cycle_num": i, "hypotheses_count": 4} for i in range(1, 6)],
    }
    result3 = should_continue(case3)
    assert result3 == "converge", f"Expected converge, got {result3}"
    print(f"  5 cycles, 4 hypotheses → {result3}  (≥ MAX_CYCLES)")

    # Case 4: Stagnation — same count for 2 consecutive cycles → converge (condition 3)
    case4 = {
        "active_hypotheses": [{"id": f"H0{i}"} for i in range(1, 5)],
        "cycle_history": [
            {"cycle_num": 1, "hypotheses_count": 5},
            {"cycle_num": 2, "hypotheses_count": 4},
            {"cycle_num": 3, "hypotheses_count": 4},
        ],
    }
    result4 = should_continue(case4)
    assert result4 == "converge", f"Expected converge, got {result4}"
    print(f"  stagnation (4,4) in last 2 cycles → {result4}")

    # Case 5: 1 hypothesis → converge (below threshold)
    case5 = {
        "active_hypotheses": [{"id": "H01"}],
        "cycle_history": [{"cycle_num": 1, "hypotheses_count": 1}],
    }
    result5 = should_continue(case5)
    assert result5 == "converge", f"Expected converge, got {result5}"
    print(f"  1 hypothesis → {result5}  (≤ CONVERGENCE_THRESHOLD)")

    print("✓ should_continue tests passed\n")


async def test_evaluate_signal():
    print("Testing evaluate_signal() — Gemini Tier 2 evaluation...")
    print("-" * 50)

    result = await evaluate_signal(MOCK_TRIGGER)

    assert "decision" in result, "Missing decision field"
    assert result["decision"] in ("escalate", "dismiss"), f"Invalid decision: {result['decision']}"
    assert "assessment" in result, "Missing assessment field"
    assert "confidence" in result, "Missing confidence field"

    print(f"  decision   = {result['decision']}")
    print(f"  confidence = {result['confidence']:.2f}")
    print(f"  tier       = {result.get('recommended_tier', 'N/A')}")
    print(f"  assessment = {result['assessment'][:120]}...")
    print("✓ evaluate_signal test passed\n")

    return result


async def test_generate_alert():
    print("Testing generate_alert() — Gemini alert generation...")
    print("-" * 50)

    # Build a realistic converged case file
    case_file = create_case_file("Credit Suisse", MOCK_TRIGGER)
    case_file["active_hypotheses"] = MOCK_HYPOTHESES[:2]
    case_file["eliminated_hypotheses"] = [
        {
            "id": "H03",
            "name": "Regulatory forced acquisition",
            "killed_by_atom": "S05",
            "killed_in_cycle": 2,
            "reason": "FINMA powers existed but merger was market-driven.",
        }
    ]
    case_file["key_insights"] = [
        "AT1 PONV clause confirmed in prospectus",
        "Bank run confirmed by $10B deposit outflows in 48h",
    ]
    case_file["compressed_reasoning"] = (
        "Investigation confirms dual risk: AT1 wipeout (H01) and confidence crisis (H02). "
        "FINMA acquisition (H03) eliminated — merger was voluntary, not forced."
    )
    case_file["cycle_history"] = [
        {"cycle_num": 1, "hypotheses_count": 3},
        {"cycle_num": 2, "hypotheses_count": 2},
    ]

    alert = await generate_alert(case_file)

    assert "level" in alert, "Missing level"
    assert alert["level"] in ("CRITICAL", "MONITOR", "ALL-CLEAR"), f"Invalid level: {alert['level']}"
    assert "diagnosis" in alert, "Missing diagnosis"
    assert "surviving_hypotheses" in alert, "Missing surviving_hypotheses"
    assert "recommended_actions" in alert, "Missing recommended_actions"

    print(f"  level    = {alert['level']}")
    print(f"  diagnosis = {alert['diagnosis'][:120]}...")
    print(f"  surviving = {alert['surviving_hypotheses']}")
    print(f"  actions   = {alert['recommended_actions'][:2]}")
    print("✓ generate_alert test passed\n")

    return alert


async def test_detect_contagion():
    print("Testing detect_contagion() — stub...")
    print("-" * 50)

    case_file = create_case_file("Credit Suisse", MOCK_TRIGGER)
    result = await detect_contagion(case_file)

    assert isinstance(result, list), "Should return a list"
    assert result == [], "Stub should return empty list"

    print(f"  returns: {result} (empty stub)")
    print("✓ detect_contagion test passed\n")


# ── Main ───────────────────────────────────────────────────────────────────────

async def main():
    print("=" * 60)
    print("Phase 5 Verification: Orchestrator")
    print("=" * 60)
    print()

    # --- Pure function tests (no Gemini) ---
    case_file = test_create_case_file()
    test_prepare_investigator_context(case_file)
    updated_cf = test_process_investigation_output(case_file)
    test_should_continue()

    # --- Gemini tests ---
    tier2_result = await test_evaluate_signal()
    alert = await test_generate_alert()
    await test_detect_contagion()

    print("=" * 60)
    print("✅ ORCHESTRATOR VALIDATED — Phase 5 Complete!")
    print("=" * 60)
    print("\nVerified:")
    print("  ✓ create_case_file initializes CaseFile correctly")
    print("  ✓ prepare_investigator_context builds correct context dict")
    print("  ✓ process_investigation_output updates all case file fields (deep copy safe)")
    print("  ✓ should_continue implements all 3 convergence conditions")
    print(f"  ✓ evaluate_signal → decision={tier2_result['decision']}, confidence={tier2_result['confidence']:.2f}")
    print(f"  ✓ generate_alert → level={alert['level']}")
    print("  ✓ detect_contagion returns [] (stub)")
    print("\nReady to proceed to Phase 6: LangGraph Graph")


if __name__ == "__main__":
    asyncio.run(main())
