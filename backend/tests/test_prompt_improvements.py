"""
Test prompt improvements:
1. Phase 1: Hypothesis quality examples
2. Phase 2: Cross-modal elimination clarification
3. Phase 4: Evidence request specificity guidance
"""

import sys
import os

# Fix path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_path)

from gemini.prompts.investigation_phases_v2 import (
    build_phase1_score_and_crossmodal_prompt,
    build_phase2_elimination_prompt,
    build_phase4_request_prompt
)


def test_phase1_examples():
    """Test that Phase 1 prompt includes hypothesis quality examples."""

    print("\n" + "=" * 80)
    print("TEST 1: Phase 1 Hypothesis Quality Examples")
    print("=" * 80)

    # Generate Cycle 1 prompt (initial hypothesis generation)
    prompt = build_phase1_score_and_crossmodal_prompt(
        cycle_num=1,
        trigger="Credit Suisse CDS spreads spike to 450bps",
        entity="Credit Suisse",
        compressed_state=None,
        evidence=[],
        active_hypotheses=[]
    )

    # Check for example patterns
    checks = [
        ("❌ BAD", "Bad hypothesis examples"),
        ("✅ GOOD", "Good hypothesis examples"),
        ("CET1 ratio below 10.5%", "Specific mechanism example"),
        ("HTM bond portfolio", "Technical term example"),
        ("testable predictions", "Testing guidance"),
        ("falsifiable", "Falsifiability requirement")
    ]

    print("\nChecking for hypothesis quality guidance:")
    all_passed = True
    for pattern, description in checks:
        if pattern in prompt:
            print(f"  ✓ Found: {description}")
        else:
            print(f"  ✗ Missing: {description}")
            all_passed = False

    if all_passed:
        print("\n✅ Phase 1 prompt includes all hypothesis quality examples")
    else:
        print("\n❌ Phase 1 prompt missing some examples")

    return all_passed


def test_phase2_crossmodal_logic():
    """Test that Phase 2 prompt clarifies cross-modal elimination logic."""

    print("\n" + "=" * 80)
    print("TEST 2: Phase 2 Cross-Modal Elimination Logic")
    print("=" * 80)

    prompt = build_phase2_elimination_prompt(
        scored_hypotheses=[
            {"id": "H01", "name": "Test hypothesis", "score": 0.75}
        ],
        evidence=[],
        cross_modal_flags=[],
        cycle_num=2
    )

    # Check for clarification patterns
    checks = [
        ("LOGICALLY INCONSISTENT", "Logical inconsistency criterion"),
        ("✅ Eliminate if", "Positive elimination criterion"),
        ("❌ Do NOT eliminate if", "Negative elimination criterion (what not to do)"),
        ("fails to explain a contradiction is NOT necessarily wrong", "Key clarification"),
        ("P(hypothesis | evidence) < 5%", "Quantitative score interpretation"),
        ("score below 0.15", "Updated threshold"),
    ]

    print("\nChecking for cross-modal logic clarification:")
    all_passed = True
    for pattern, description in checks:
        if pattern in prompt:
            print(f"  ✓ Found: {description}")
        else:
            print(f"  ✗ Missing: {description}")
            all_passed = False

    if all_passed:
        print("\n✅ Phase 2 prompt includes cross-modal clarification")
    else:
        print("\n❌ Phase 2 prompt missing some clarifications")

    return all_passed


def test_phase4_specificity():
    """Test that Phase 4 prompt includes evidence request specificity guidance."""

    print("\n" + "=" * 80)
    print("TEST 3: Phase 4 Evidence Request Specificity")
    print("=" * 80)

    prompt = build_phase4_request_prompt(
        surviving_hypotheses=[
            {"id": "H01", "name": "Test", "score": 0.75}
        ],
        forward_simulations=[],
        evidence_collected=[],
        cycle_num=3
    )

    # Check for specificity guidance
    checks = [
        ("EVIDENCE REQUEST SPECIFICITY", "Section header"),
        ("semantic search", "Search method mentioned"),
        ("❌ BAD (too general)", "Bad example"),
        ("✅ GOOD:", "Good example with specific details"),
        ("CDS spread levels", "Specific metric example"),
        ("Q4 2022", "Time period example"),
        ("compared to UBS", "Comparison example"),
        ("Include in each request:", "Explicit guidance list"),
    ]

    print("\nChecking for specificity guidance:")
    all_passed = True
    for pattern, description in checks:
        if pattern in prompt:
            print(f"  ✓ Found: {description}")
        else:
            print(f"  ✗ Missing: {description}")
            all_passed = False

    if all_passed:
        print("\n✅ Phase 4 prompt includes specificity guidance")
    else:
        print("\n❌ Phase 4 prompt missing some guidance")

    return all_passed


def main():
    """Run all prompt tests."""

    print("\n" + "=" * 80)
    print("PROMPT IMPROVEMENT TESTS")
    print("=" * 80)

    results = {
        "Phase 1 Examples": test_phase1_examples(),
        "Phase 2 Cross-Modal": test_phase2_crossmodal_logic(),
        "Phase 4 Specificity": test_phase4_specificity()
    }

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    all_passed = all(results.values())
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {test_name}")

    if all_passed:
        print("\n🎉 All prompt improvements verified!")
    else:
        print("\n⚠️  Some prompt improvements need attention")

    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
