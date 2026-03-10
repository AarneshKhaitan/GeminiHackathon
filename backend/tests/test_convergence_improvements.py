"""
Test orchestrator convergence improvements:
1. Elimination rate tracking
2. Early convergence on low elimination rate
"""

import sys
import os

# Fix path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_path)

from agents.orchestrator import decide_convergence
from models.case_file import CaseFile, Hypothesis, EliminatedHypothesis, CycleRecord


def create_test_case_file(
    active_count: int,
    eliminated_count: int,
    cycles: int,
    varying_counts: bool = True
) -> dict:
    """Create a test case file with specified hypothesis counts."""

    # Create active hypotheses
    active_hypotheses = [
        Hypothesis(
            id=f"H{i:02d}",
            name=f"Hypothesis {i}",
            description=f"Test hypothesis {i}",
            score=0.5,
            evidence_chain=[],
            status="active",
            reasoning="Test"
        )
        for i in range(1, active_count + 1)
    ]

    # Create eliminated hypotheses
    eliminated_hypotheses = [
        EliminatedHypothesis(
            id=f"H{i:02d}",
            name=f"Eliminated {i}",
            killed_by_atom="S01",
            killed_in_cycle=i,
            reason="Test elimination"
        )
        for i in range(1, eliminated_count + 1)
    ]

    # Create cycle history with varying or stagnant counts
    cycle_history = []
    if varying_counts:
        # Varying counts - ensure at least one elimination per cycle to avoid stagnation
        # For low elimination rate test: spread eliminations across cycles
        total_initial = active_count + eliminated_count

        # Distribute eliminations to avoid stagnation (last STAGNATION_CYCLES must differ)
        # STAGNATION_CYCLES = 2 in config, so we need cycles to have different counts
        for i in range(1, cycles + 1):
            if i == 1:
                # First cycle: start with all hypotheses
                hypotheses_at_cycle = total_initial
            elif i <= eliminated_count:
                # Eliminate one per cycle
                hypotheses_at_cycle = total_initial - i + 1
            else:
                # No more eliminations
                hypotheses_at_cycle = active_count

            cycle_history.append(
                CycleRecord(
                    cycle_num=i,
                    hypotheses_count=hypotheses_at_cycle,
                    eliminations_count=1 if i <= eliminated_count else 0,
                    evidence_collected_count=3,
                    token_usage={}
                )
            )
    else:
        # Stagnant counts (all same)
        for i in range(1, cycles + 1):
            cycle_history.append(
                CycleRecord(
                    cycle_num=i,
                    hypotheses_count=active_count,
                    eliminations_count=0,
                    evidence_collected_count=3,
                    token_usage={}
                )
            )

    case_file = CaseFile(
        entity="Test Entity",
        tier=4,
        status="investigating",
        trigger={"event": "test"},
        active_hypotheses=active_hypotheses,
        eliminated_hypotheses=eliminated_hypotheses,
        cross_modal_flags=[],
        key_insights=[],
        evidence_collected=[],
        evidence_pending=[],
        compressed_reasoning=None,
        cycle_history=cycle_history,
        context_windows={},
        token_usage={},
        alert=None,
        network_alerts=[]
    )

    return case_file.model_dump()


def test_low_elimination_rate_convergence():
    """Test that low elimination rate triggers convergence."""

    print("\n" + "=" * 80)
    print("TEST: Low Elimination Rate Convergence")
    print("=" * 80)

    # Scenario: After 4 cycles, only 1 out of 8 hypotheses eliminated
    # Elimination rate = 1 / 4 = 25%, which is below 30% threshold
    # Use varying_counts to avoid stagnation trigger
    case_file = create_test_case_file(
        active_count=7,      # 7 still active
        eliminated_count=1,  # Only 1 eliminated
        cycles=4,            # Over 4 cycles = 25% elimination rate
        varying_counts=True  # Avoid stagnation trigger
    )

    result = decide_convergence(case_file, cycle_num=4, min_cycles=3)

    print(f"\nScenario: 4 cycles, 1 eliminated (25% elimination rate)")
    print(f"  Decision: {result['decision']}")
    print(f"  Reason: {result['reason']}")
    print(f"  Hypotheses remaining: {result['hypotheses_count']}")

    # Should converge due to low elimination rate
    if result['decision'] == 'converge' and 'elimination rate' in result['reason'].lower():
        print("\n✅ PASS: Low elimination rate triggers convergence")
        return True
    else:
        print("\n❌ FAIL: Should converge on low elimination rate")
        return False


def test_normal_elimination_rate_continues():
    """Test that normal elimination rate allows continuation."""

    print("\n" + "=" * 80)
    print("TEST: Normal Elimination Rate Continues")
    print("=" * 80)

    # Scenario: After 3 cycles, 2 out of 8 hypotheses eliminated
    # Elimination rate = 2 / 3 = 66.7%, which is above 30% threshold
    case_file = create_test_case_file(
        active_count=6,      # 6 still active
        eliminated_count=2,  # 2 eliminated
        cycles=3,
        varying_counts=True  # Avoid stagnation trigger
    )

    result = decide_convergence(case_file, cycle_num=3, min_cycles=3)

    print(f"\nScenario: 3 cycles, 2 eliminated (66.7% elimination rate)")
    print(f"  Decision: {result['decision']}")
    print(f"  Reason: {result['reason']}")
    print(f"  Hypotheses remaining: {result['hypotheses_count']}")

    # Should continue (elimination rate is healthy)
    if result['decision'] == 'continue':
        print("\n✅ PASS: Normal elimination rate allows continuation")
        return True
    else:
        print("\n❌ FAIL: Should continue with healthy elimination rate")
        return False


def test_min_cycles_override():
    """Test that elimination rate check doesn't trigger before min_cycles."""

    print("\n" + "=" * 80)
    print("TEST: Min Cycles Override")
    print("=" * 80)

    # Scenario: After 2 cycles, 0 eliminations (0% rate)
    # But min_cycles=3, so should continue regardless
    case_file = create_test_case_file(
        active_count=8,
        eliminated_count=0,
        cycles=2,
        varying_counts=False  # Can be stagnant, still should continue due to min_cycles
    )

    result = decide_convergence(case_file, cycle_num=2, min_cycles=3)

    print(f"\nScenario: 2 cycles, 0/8 eliminated (0% rate), min_cycles=3")
    print(f"  Decision: {result['decision']}")
    print(f"  Reason: {result['reason']}")

    # Should continue because min_cycles not reached
    if result['decision'] == 'continue' and 'minimum' in result['reason'].lower():
        print("\n✅ PASS: Min cycles requirement enforced")
        return True
    else:
        print("\n❌ FAIL: Should continue until min_cycles")
        return False


def test_convergence_threshold_still_works():
    """Test that convergence threshold (≤2 hypotheses) still triggers."""

    print("\n" + "=" * 80)
    print("TEST: Convergence Threshold Still Works")
    print("=" * 80)

    # Scenario: 2 hypotheses remaining (at threshold)
    case_file = create_test_case_file(
        active_count=2,
        eliminated_count=6,
        cycles=3
    )

    result = decide_convergence(case_file, cycle_num=3, min_cycles=3)

    print(f"\nScenario: 3 cycles, 2 hypotheses remaining")
    print(f"  Decision: {result['decision']}")
    print(f"  Reason: {result['reason']}")

    # Should converge due to hypothesis count threshold
    if result['decision'] == 'converge' and result['hypotheses_count'] == 2:
        print("\n✅ PASS: Convergence threshold still works")
        return True
    else:
        print("\n❌ FAIL: Should converge on hypothesis threshold")
        return False


def main():
    """Run all convergence tests."""

    print("\n" + "=" * 80)
    print("ORCHESTRATOR CONVERGENCE TESTS")
    print("=" * 80)

    results = {
        "Low Elimination Rate": test_low_elimination_rate_convergence(),
        "Normal Elimination Rate": test_normal_elimination_rate_continues(),
        "Min Cycles Override": test_min_cycles_override(),
        "Convergence Threshold": test_convergence_threshold_still_works()
    }

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    all_passed = all(results.values())
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {test_name}")

    if all_passed:
        print("\n🎉 All convergence improvements verified!")
    else:
        print("\n⚠️  Some convergence tests need attention")

    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
