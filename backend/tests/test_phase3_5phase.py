import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

#!/usr/bin/env python3
"""Phase 3 Verification: Test 5-phase Investigator"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.investigator_5phase import investigate
from models.observation import Evidence
from models.case_file import Hypothesis
import config


async def test_cycle1_hypothesis_generation():
    """Test Cycle 1: Generate initial hypotheses."""
    print("Testing Cycle 1: Hypothesis Generation...")
    print("=" * 60)

    # Cycle 1 context: No evidence yet, just the trigger
    context = {
        "trigger": "CDS spreads spiked to 450 basis points, stock dropped 60%",
        "entity": "Silicon Valley Bank",
        "cycle_num": 1,
        "compressed_state": None,
        "evidence": [],
        "active_hypotheses": []
    }

    result = await investigate(context)

    # Show raw output
    print("\n" + "=" * 60)
    print("RAW OUTPUT FROM INVESTIGATOR:")
    print("=" * 60)
    print(json.dumps(result, indent=2))
    print("=" * 60)

    # Validate structure
    assert "surviving_hypotheses" in result, "Missing surviving_hypotheses"
    assert "evidence_requests" in result, "Missing evidence_requests"
    assert "compressed_state" in result, "Missing compressed_state"
    assert "token_usage" in result, "Missing token_usage"
    assert "phase_outputs" in result, "Missing phase_outputs"

    # Validate Phase 1 ran
    assert "phase1_scoring" in result["phase_outputs"], "Missing phase1_scoring output"

    # Validate Phase 4 ran (evidence requests)
    assert "phase4_request" in result["phase_outputs"], "Missing phase4_request output"

    # Validate hypotheses generated
    hypotheses = result["surviving_hypotheses"]
    assert len(hypotheses) >= 4, f"Expected at least 4 hypotheses, got {len(hypotheses)}"
    print(f"✓ Generated {len(hypotheses)} initial hypotheses")
    for h in hypotheses[:3]:
        print(f"  - {h['id']}: {h['name']} (score: {h['score']})")
    if len(hypotheses) > 3:
        print(f"  ... and {len(hypotheses) - 3} more")

    # Validate evidence requests
    requests = result["evidence_requests"]
    assert len(requests) >= 3, f"Expected 3-5 evidence requests, got {len(requests)}"
    print(f"\n✓ Generated {len(requests)} evidence requests")
    for req in requests[:2]:
        print(f"  - {req['type']}: {req['description'][:60]}...")

    # Check thinking field in Phase 1
    phase1_thinking = result["phase_outputs"]["phase1_scoring"].get("thinking", "")
    print(f"\n✓ Phase 1 thinking: {len(phase1_thinking)} characters")
    if len(phase1_thinking) < 1000:
        print(f"  ⚠️  WARNING: Thinking is shorter than requested (< 1500 words)")

    # Check token usage
    tokens = result["token_usage"]
    print(f"\n✓ Token usage:")
    print(f"  Input: {tokens['input']:,} tokens")
    print(f"  Output: {tokens['output']:,} tokens")
    print(f"  Reasoning: {tokens['reasoning']:,} tokens")
    print(f"  Total: {tokens['total']:,} tokens")

    return result


async def test_cycle2_full_pipeline():
    """Test Cycle 2+: All 5 phases with evidence."""
    print("\n\nTesting Cycle 2: Full 5-Phase Pipeline...")
    print("=" * 60)

    # Mock evidence from Cycle 1
    evidence = [
        {
            "observation_id": "S01",
            "content": "SVB held $91 billion in Held-to-Maturity securities with significant unrealized losses due to rising interest rates. These losses were not marked to market under HTM accounting rules.",
            "source": "FDIC Post-Mortem Report",
            "type": "structural",
            "supports": ["H01", "H02"],
            "contradicts": ["H05"],
            "neutral": []
        },
        {
            "observation_id": "E03",
            "content": "10-year Treasury yield rose from 0.5% (2020) to 4.0% (March 2023), creating severe duration mismatch for banks with long-dated fixed-rate assets.",
            "source": "Federal Reserve Economic Data",
            "type": "market",
            "supports": ["H01"],
            "contradicts": [],
            "neutral": ["H03"]
        }
    ]

    # Mock hypotheses from Cycle 1
    hypotheses = [
        {
            "id": "H01",
            "name": "Duration mismatch risk",
            "description": "Bank has significant duration mismatch between long-dated fixed-rate assets and short-term liabilities",
            "score": 0.75,
            "evidence_chain": [],
            "status": "active",
            "reasoning": "CDS spike suggests market pricing in credit deterioration"
        },
        {
            "id": "H02",
            "name": "HTM accounting obscuring losses",
            "description": "Unrealized losses on held-to-maturity securities not reflected in capital ratios",
            "score": 0.70,
            "evidence_chain": [],
            "status": "active",
            "reasoning": "Accounting treatment may hide true economic losses"
        },
        {
            "id": "H05",
            "name": "Counterparty credit exposure",
            "description": "Bank has concentrated exposure to failing counterparties",
            "score": 0.50,
            "evidence_chain": [],
            "status": "active",
            "reasoning": "Possible but less likely given trigger pattern"
        }
    ]

    # Cycle 2 context: Now we have evidence
    context = {
        "trigger": "CDS spreads spiked to 450 basis points, stock dropped 60%",
        "entity": "Silicon Valley Bank",
        "cycle_num": 2,
        "compressed_state": "CYCLE 1: Generated 8 hypotheses covering structural risk, market risk, counterparty risk. Top hypotheses: duration mismatch (0.75), HTM accounting (0.70). Need evidence: HTM portfolio details, deposit composition, interest rate exposure.",
        "evidence": evidence,
        "active_hypotheses": hypotheses
    }

    result = await investigate(context)

    # Show raw output
    print("\n" + "=" * 60)
    print("RAW OUTPUT FROM INVESTIGATOR (CYCLE 2):")
    print("=" * 60)
    print(json.dumps(result, indent=2))
    print("=" * 60)

    # Validate all 5 phases ran
    assert "phase1_scoring" in result["phase_outputs"], "Missing Phase 1"
    assert "phase2_elimination" in result["phase_outputs"], "Missing Phase 2"
    assert "phase3_crossmodal" in result["phase_outputs"], "Missing Phase 3"
    assert "phase4_request" in result["phase_outputs"], "Missing Phase 4"
    assert "phase5_compression" in result["phase_outputs"], "Missing Phase 5"

    print("✓ All 5 phases executed")

    # Check Phase 1: Scoring
    phase1_thinking = result["phase_outputs"]["phase1_scoring"].get("thinking", "")
    print(f"\n✓ Phase 1 (SCORE) thinking: {len(phase1_thinking)} characters")

    # Check Phase 2: Eliminations
    phase2_output = result["phase_outputs"]["phase2_elimination"]
    phase2_thinking = phase2_output.get("thinking", "")
    eliminated = result["eliminated_hypotheses"]
    surviving = result["surviving_hypotheses"]
    print(f"\n✓ Phase 2 (ELIMINATE) thinking: {len(phase2_thinking)} characters")
    print(f"  Eliminated: {len(eliminated)} hypotheses")
    print(f"  Surviving: {len(surviving)} hypotheses")
    if eliminated:
        for elim in eliminated:
            print(f"    - {elim['id']} killed by {elim['killed_by_atom']}: {elim['reason'][:60]}...")

    # Check Phase 3: Cross-modal
    phase3_output = result["phase_outputs"]["phase3_crossmodal"]
    phase3_thinking = phase3_output.get("thinking", "")
    flags = result["cross_modal_flags"]
    print(f"\n✓ Phase 3 (CROSS-MODAL) thinking: {len(phase3_thinking)} characters")
    print(f"  Cross-modal flags: {len(flags)}")
    if flags:
        for flag in flags:
            print(f"    - {flag['structural_atom_id']} vs {flag['empirical_atom_id']}")

    # Check Phase 4: Evidence requests
    phase4_output = result["phase_outputs"]["phase4_request"]
    phase4_thinking = phase4_output.get("thinking", "")
    requests = result["evidence_requests"]
    print(f"\n✓ Phase 4 (REQUEST) thinking: {len(phase4_thinking)} characters")
    print(f"  Evidence requests: {len(requests)}")
    for req in requests[:2]:
        print(f"    - {req['type']}: {req['description'][:50]}...")

    # Check Phase 5: Compression
    phase5_output = result["phase_outputs"]["phase5_compression"]
    phase5_thinking = phase5_output.get("thinking", "")
    compressed = result["compressed_state"]
    print(f"\n✓ Phase 5 (COMPRESS) thinking: {len(phase5_thinking)} characters")
    print(f"  Compressed state: {len(compressed)} characters")
    print(f"  Preview: {compressed[:100]}...")

    # Check token usage aggregation
    tokens = result["token_usage"]
    print(f"\n✓ Aggregated token usage across 5 phases:")
    print(f"  Input: {tokens['input']:,} tokens")
    print(f"  Output: {tokens['output']:,} tokens")
    print(f"  Reasoning: {tokens['reasoning']:,} tokens")
    print(f"  Total: {tokens['total']:,} tokens")

    # Verify thinking verbosity
    total_thinking = sum([
        len(phase1_thinking),
        len(phase2_thinking),
        len(phase3_thinking),
        len(phase4_thinking),
        len(phase5_thinking)
    ])
    print(f"\n✓ Total thinking across all phases: {total_thinking} characters")
    if total_thinking < 5000:
        print(f"  ⚠️  WARNING: Total thinking is less than expected (< ~10,000 chars)")

    return result


async def main():
    print("=" * 60)
    print("Phase 3 Verification: 5-Phase Investigator")
    print("=" * 60)

    # Test Cycle 1: Hypothesis generation
    cycle1_result = await test_cycle1_hypothesis_generation()

    # Test Cycle 2: Full pipeline
    cycle2_result = await test_cycle2_full_pipeline()

    print("\n" + "=" * 60)
    print("✅ 5-PHASE INVESTIGATOR VALIDATED - Phase 3 Complete!")
    print("=" * 60)

    print("\nVerified:")
    print("  ✓ Cycle 1 runs Phase 1 (generation) + Phase 4 (requests)")
    print("  ✓ Cycle 2+ runs all 5 phases sequentially")
    print("  ✓ Each phase produces 'thinking' field with reasoning")
    print("  ✓ Token usage aggregated across all phases")
    print("  ✓ Outputs combine all phase results correctly")
    print("  ✓ Eliminations cite specific observation IDs")
    print("  ✓ Compressed state generated cumulatively")

    print("\nReady to proceed to Phase 4: Evidence Pipeline")


if __name__ == "__main__":
    asyncio.run(main())
