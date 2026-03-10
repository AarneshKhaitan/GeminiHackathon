"""
Test evidence selector quality improvements:
1. Similarity threshold filtering (reject negative scores)
2. Quality metrics logging
"""

import sys
import os

# Fix path - go up to project root first, then add backend
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_path)

import asyncio
from utils.corpus_loader import load_all_corpus
from agents.evidence.selector import select_evidence_for_requests


async def test_selector_quality():
    """Test that selector rejects low-quality matches and logs quality metrics."""

    entity = "Credit Suisse"

    # Load corpus (both structural and empirical)
    print("Loading corpus...")
    structural_obs = load_all_corpus(entity, "structural")
    empirical_obs = load_all_corpus(entity, "empirical")
    observations = structural_obs + empirical_obs
    print(f"Loaded {len(observations)} observations ({len(structural_obs)} structural, {len(empirical_obs)} empirical)\n")

    # Test evidence requests
    evidence_requests = [
        {
            "type": "structural",
            "description": "Basel III Common Equity Tier 1 (CET1) capital requirements and regulatory minimums for systemically important banks"
        },
        {
            "type": "empirical",
            "description": "Credit Suisse CDS spreads during Q4 2022 and Q1 2023 compared to peer banks UBS and Deutsche Bank"
        },
        {
            "type": "empirical",
            "description": "Deposit outflow data for Credit Suisse in March 2023, daily withdrawal amounts and customer segment breakdown"
        }
    ]

    print("Testing Evidence Selector Quality Improvements")
    print("=" * 80)
    print(f"\nEvidence requests: {len(evidence_requests)}")
    for i, req in enumerate(evidence_requests, 1):
        print(f"  {i}. [{req['type']}] {req['description'][:70]}...")

    print("\n" + "=" * 80)
    print("SELECTOR OUTPUT:")
    print("=" * 80 + "\n")

    # Call selector
    selected = await select_evidence_for_requests(
        evidence_requests=evidence_requests,
        available_observations=observations,
        already_gathered=[]
    )

    print("\n" + "=" * 80)
    print("RESULTS:")
    print("=" * 80)
    print(f"\nSelected observations: {len(selected)}")

    if selected:
        print("\nSelected IDs:")
        for obs in selected:
            print(f"  - {obs['observation_id']}: {obs['source'][:60]}...")
    else:
        print("  (No observations selected)")

    print("\n✓ Test complete")
    print("\nExpected behavior:")
    print("  - All selected observations should have similarity > 0.05")
    print("  - Should see 'REJECTED (negative)' or 'REJECTED (below threshold)' in logs")
    print("  - Should see quality metrics: avg similarity, range, rejected count")


if __name__ == "__main__":
    asyncio.run(test_selector_quality())
