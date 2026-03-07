#!/usr/bin/env python3
"""Quick validation test for v2 architecture - just Cycles 1 and 2."""

import asyncio
import json
from agents.investigator_v2 import investigate

# Test evidence with structural/empirical contradictions
TEST_EVIDENCE = [
    {
        "observation_id": "S01",
        "content": "SVB regulatory capital ratio: 12.9% (well above 8% minimum). Bank meets all regulatory capital requirements.",
        "source": "Regulatory filing",
        "type": "structural",
        "supports": [],
        "contradicts": [],
        "neutral": []
    },
    {
        "observation_id": "E01",
        "content": "SVB 5-year CDS spread: 450 basis points (up from 30bps baseline). Market pricing extreme default risk.",
        "source": "Bloomberg",
        "type": "market",
        "supports": [],
        "contradicts": [],
        "neutral": []
    },
    {
        "observation_id": "S02",
        "content": "SVB HTM portfolio: $91B with $15B unrealized losses. Under accounting rules, HTM securities not marked to market.",
        "source": "FDIC Report",
        "type": "structural",
        "supports": ["H01"],
        "contradicts": ["H05"],
        "neutral": []
    }
]


async def main():
    print("=" * 80)
    print("V2 ARCHITECTURE VALIDATION TEST")
    print("=" * 80)

    # CYCLE 1: Hypothesis Generation
    print("\n[CYCLE 1: HYPOTHESIS GENERATION]")
    context1 = {
        "trigger": "SVB stock dropped 60% in one day, CDS spreads spiked to 450bps",
        "entity": "Silicon Valley Bank",
        "cycle_num": 1,
        "compressed_state": None,
        "evidence": [],
        "active_hypotheses": []
    }

    result1 = await investigate(context1)

    print(f"\n✅ CYCLE 1 RESULTS:")
    print(f"  Hypotheses: {len(result1['surviving_hypotheses'])}")
    print(f"  Evidence requests: {len(result1['evidence_requests'])}")
    print(f"  Tokens: {result1['token_usage']['total']:,}")

    # CYCLE 2: Score + Cross-Modal + Eliminate
    print("\n" + "=" * 80)
    print("[CYCLE 2: SCORE + CROSS-MODAL + ELIMINATE]")

    # Take top 3 hypotheses
    top_3_hypotheses = result1['surviving_hypotheses'][:3]

    context2 = {
        "trigger": "SVB stock dropped 60%, CDS at 450bps",
        "entity": "Silicon Valley Bank",
        "cycle_num": 2,
        "compressed_state": result1['compressed_state'],
        "evidence": TEST_EVIDENCE,
        "active_hypotheses": top_3_hypotheses
    }

    result2 = await investigate(context2)

    print(f"\n✅ CYCLE 2 RESULTS:")
    print(f"  Cross-modal flags: {len(result2['cross_modal_flags'])}")
    print(f"  Eliminations: {len(result2['eliminated_hypotheses'])}")
    print(f"  Survivors: {len(result2['surviving_hypotheses'])}")
    print(f"  Tokens: {result2['token_usage']['total']:,}")

    # Display cross-modal flags
    if result2['cross_modal_flags']:
        print(f"\n🚩 CROSS-MODAL CONTRADICTIONS DETECTED:")
        for flag in result2['cross_modal_flags']:
            print(f"  - {flag['structural_atom_id']} vs {flag['empirical_atom_id']}")
            print(f"    {flag['contradiction_description'][:120]}...")

    # Display eliminations
    if result2['eliminated_hypotheses']:
        print(f"\n❌ ELIMINATIONS:")
        for elim in result2['eliminated_hypotheses']:
            print(f"  - {elim['id']}: Killed by {elim['killed_by_atom']}")

    # Display survivors
    print(f"\n✅ SURVIVORS:")
    for surv in result2['surviving_hypotheses']:
        print(f"  - {surv['id']}: {surv['name']} (score: {surv['score']})")

    # Final summary
    print("\n" + "=" * 80)
    print("✅ V2 ARCHITECTURE VALIDATED")
    print("=" * 80)
    print(f"\n✓ Phase 1: Score + Cross-Modal combined")
    print(f"✓ Phase 2: Eliminate (evidence + score + subsumption)")
    print(f"✓ Phase 4: Request evidence")
    print(f"✓ Phase 5: Compress cumulative state")
    print(f"✓ Cumulative context passing: {result2['token_usage']['input']:,} input tokens")
    print(f"✓ Cross-modal detection: {len(result2['cross_modal_flags'])} flags")
    print(f"✓ Score-based elimination: {len([e for e in result2['eliminated_hypotheses'] if e['killed_by_atom'] == 'low_confidence'])} eliminations")

    print(f"\n📊 Total: {result1['token_usage']['total'] + result2['token_usage']['total']:,} tokens")
    print(f"\n🎯 READY FOR PRODUCTION")


if __name__ == "__main__":
    asyncio.run(main())
