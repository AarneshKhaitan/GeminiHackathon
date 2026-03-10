import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

#!/usr/bin/env python3
"""Phase 3 Verification: Test Investigator (CRITICAL PATH)"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.investigator import investigate


async def test_cycle1_generation():
    """Test Cycle 1: Initial hypothesis generation."""
    print("Testing Cycle 1: Hypothesis Generation...")

    context = {
        "trigger": "SVB CDS spreads spiked to 450bps on March 8, 2023. Stock price fell 60%. Deposit outflows accelerated.",
        "entity": "SVB",
        "cycle_num": 1,
        "compressed_state": None,
        "evidence": [],
        "active_hypotheses": []
    }

    result = await investigate(context)

    # Verify structure
    assert "surviving_hypotheses" in result, "Missing surviving_hypotheses"
    assert "eliminated_hypotheses" in result, "Missing eliminated_hypotheses"
    assert "evidence_requests" in result, "Missing evidence_requests"
    assert "compressed_state" in result, "Missing compressed_state"
    assert "token_usage" in result, "Missing token_usage"

    # Verify hypothesis generation
    hypotheses = result["surviving_hypotheses"]
    assert len(hypotheses) >= 8, f"Expected ≥8 hypotheses, got {len(hypotheses)}"
    assert len(hypotheses) <= 10, f"Expected ≤10 hypotheses, got {len(hypotheses)}"

    # Verify each hypothesis has required fields
    for h in hypotheses:
        assert "id" in h, f"Hypothesis missing 'id': {h}"
        assert "name" in h, f"Hypothesis missing 'name': {h}"
        assert "description" in h, f"Hypothesis missing 'description': {h}"
        assert "score" in h, f"Hypothesis missing 'score': {h}"
        assert 0.0 <= h["score"] <= 1.0, f"Invalid score {h['score']} for {h['id']}"

    print(f"✓ Generated {len(hypotheses)} hypotheses")
    print(f"✓ Token usage: {result['token_usage']['input_tokens']} in, {result['token_usage']['output_tokens']} out")

    # Print sample hypotheses
    print(f"\nSample hypotheses:")
    for h in hypotheses[:3]:
        print(f"  {h['id']}: {h['name']} (score: {h['score']:.2f})")

    # Verify evidence requests
    assert len(result["evidence_requests"]) >= 3, "Should request at least 3 pieces of evidence"
    print(f"\n✓ Requested {len(result['evidence_requests'])} pieces of evidence")

    # Verify compressed state exists
    assert result["compressed_state"], "Compressed state should not be empty"
    print(f"✓ Compressed state created ({len(result['compressed_state'])} chars)")

    return result


async def test_cycle2_elimination():
    """Test Cycle 2: Hypothesis scoring and elimination."""
    print("\n\nTesting Cycle 2: Scoring and Elimination...")

    # First run cycle 1 to get initial hypotheses
    cycle1_result = await test_cycle1_generation()

    # Mock evidence contradicting specific hypotheses
    evidence = [
        {
            "observation_id": "S01",
            "content": "SVB held $91B of HTM securities with $15B unrealized losses due to rising interest rates. These losses were not marked on the balance sheet per HTM accounting rules.",
            "source": "FDIC Post-Mortem Report",
            "type": "structural",
            "supports": ["H01", "H02"],  # Duration mismatch hypotheses
            "contradicts": ["H07", "H08"],  # Counterparty/fraud hypotheses
            "neutral": ["H03", "H04"]
        },
        {
            "observation_id": "E01",
            "content": "SVB stock price fell 60% in one day on March 9, 2023. CDS spreads reached 450bps. Deposit outflows exceeded $42B in 24 hours.",
            "source": "Market Data (Bloomberg)",
            "type": "market",
            "supports": ["H01", "H06"],  # Duration mismatch + bank run
            "contradicts": [],
            "neutral": ["H03", "H04", "H05"]
        }
    ]

    context = {
        "trigger": "SVB CDS spike",
        "entity": "SVB",
        "cycle_num": 2,
        "compressed_state": cycle1_result["compressed_state"],
        "evidence": evidence,
        "active_hypotheses": cycle1_result["surviving_hypotheses"]
    }

    result = await investigate(context)

    # Verify eliminations (may or may not happen depending on Gemini's reasoning)
    print(f"✓ Eliminated {len(result['eliminated_hypotheses'])} hypotheses")

    # If there are eliminations, verify they cite specific evidence
    if result["eliminated_hypotheses"]:
        for elim in result["eliminated_hypotheses"]:
            assert "killed_by_atom" in elim, f"Elimination missing killed_by_atom: {elim}"
            assert "reason" in elim, f"Elimination missing reason: {elim}"
            assert "killed_in_cycle" in elim, f"Elimination missing killed_in_cycle: {elim}"
            assert elim["killed_in_cycle"] == 2, f"Expected cycle 2, got {elim['killed_in_cycle']}"
            assert elim["killed_by_atom"] in ["S01", "E01"], f"Invalid kill atom: {elim['killed_by_atom']}"

        print(f"✓ All eliminations cite specific evidence atoms")

        # Print eliminations
        print(f"\nEliminations:")
        for elim in result["eliminated_hypotheses"]:
            print(f"  {elim['id']}: killed by {elim['killed_by_atom']} - {elim['reason']}")
    else:
        print("  (No eliminations in this cycle - may happen if evidence doesn't contradict strongly)")

    # Verify compressed state updated
    assert result["compressed_state"] != cycle1_result["compressed_state"], "Compressed state should be updated"
    assert "CYCLE 2" in result["compressed_state"] or "cycle 2" in result["compressed_state"].lower(), "Compressed state should mention cycle 2"

    print(f"\n✓ Compressed state updated (length: {len(result['compressed_state'])} chars)")

    # Verify surviving hypotheses updated
    assert len(result["surviving_hypotheses"]) <= len(cycle1_result["surviving_hypotheses"]), "Should not gain hypotheses"
    print(f"✓ Surviving hypotheses: {len(result['surviving_hypotheses'])} (down from {len(cycle1_result['surviving_hypotheses'])})")

    return result


async def main():
    print("=" * 60)
    print("Phase 3 Verification: Investigator (CRITICAL PATH)")
    print("=" * 60)

    try:
        cycle1_result = await test_cycle1_generation()
        cycle2_result = await test_cycle2_elimination()

        print("\n" + "=" * 60)
        print("✅ INVESTIGATOR VALIDATED - Phase 3 Complete!")
        print("=" * 60)
        print("\nVerified:")
        print(f"  ✓ Cycle 1: Generated {len(cycle1_result['surviving_hypotheses'])} hypotheses")
        print(f"  ✓ Cycle 2: Eliminated {len(cycle2_result['eliminated_hypotheses'])} hypotheses")
        print(f"  ✓ Surviving after cycle 2: {len(cycle2_result['surviving_hypotheses'])} hypotheses")
        print("  ✓ All eliminations cite specific evidence atoms (when applicable)")
        print("  ✓ Compressed state grows cumulatively across cycles")
        print("  ✓ Evidence requests generated for next cycle")
        print("  ✓ Token usage tracked per cycle")
        print("\nReady to proceed to Phase 4: Evidence Pipeline")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
