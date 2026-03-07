#!/usr/bin/env python3
"""Test score-based elimination (score < 0.2)"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agents.investigator_5phase import investigate


async def test_score_elimination():
    """Test that hypotheses with score < 0.2 are eliminated."""
    print("=" * 60)
    print("Testing Score-Based Elimination (score < 0.2)")
    print("=" * 60)

    # Create mock evidence
    evidence = [
        {
            "observation_id": "S01",
            "content": "Strong evidence supporting duration mismatch",
            "source": "Test",
            "type": "structural",
            "supports": ["H01"],
            "contradicts": ["H03"],
            "neutral": []
        }
    ]

    # Create hypotheses with varying scores
    hypotheses = [
        {
            "id": "H01",
            "name": "Duration mismatch",
            "description": "Strong hypothesis",
            "score": 0.85,  # Should survive
            "evidence_chain": [],
            "status": "active"
        },
        {
            "id": "H02",
            "name": "Weak hypothesis",
            "description": "Should be eliminated by score",
            "score": 0.15,  # Should be eliminated (< 0.2)
            "evidence_chain": [],
            "status": "active"
        },
        {
            "id": "H03",
            "name": "Borderline hypothesis",
            "description": "Right at threshold",
            "score": 0.20,  # Should survive (>= 0.2)
            "evidence_chain": [],
            "status": "active"
        }
    ]

    context = {
        "trigger": "Test trigger",
        "entity": "Test Bank",
        "cycle_num": 2,
        "compressed_state": "Test state",
        "evidence": evidence,
        "active_hypotheses": hypotheses
    }

    result = await investigate(context)

    # Check eliminations
    eliminated = result["eliminated_hypotheses"]
    surviving = result["surviving_hypotheses"]

    print(f"\n✓ Eliminated: {len(eliminated)}")
    for elim in eliminated:
        print(f"  - {elim['id']}: {elim['name']}")
        print(f"    Killed by: {elim['killed_by_atom']}")
        print(f"    Reason: {elim['reason']}")

    print(f"\n✓ Surviving: {len(surviving)}")
    for surv in surviving:
        print(f"  - {surv['id']}: {surv['name']} (score: {surv['score']})")

    # Validate
    eliminated_ids = [e["id"] for e in eliminated]
    surviving_ids = [s["id"] for s in surviving]

    # H02 (score 0.15) should be eliminated
    if "H02" in eliminated_ids:
        print("\n✅ H02 correctly eliminated (score 0.15 < 0.2)")
        h02_elim = [e for e in eliminated if e["id"] == "H02"][0]
        assert h02_elim["killed_by_atom"] == "low_confidence", "Should cite low_confidence"
        print(f"  ✓ Cited as: {h02_elim['killed_by_atom']}")
    else:
        print("\n❌ ERROR: H02 should be eliminated but wasn't!")
        return False

    # H01 (score 0.85) should survive
    if "H01" in surviving_ids:
        print("✅ H01 correctly survived (score 0.85 > 0.2)")
    else:
        print("❌ ERROR: H01 should survive but was eliminated!")
        return False

    # H03 (score 0.20) should survive (threshold is <0.2, not <=0.2)
    if "H03" in surviving_ids:
        print("✅ H03 correctly survived (score 0.20 = threshold)")
    else:
        print("❌ ERROR: H03 should survive but was eliminated!")
        return False

    print("\n" + "=" * 60)
    print("✅ SCORE-BASED ELIMINATION WORKING CORRECTLY")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = asyncio.run(test_score_elimination())
    sys.exit(0 if success else 1)
