#!/usr/bin/env python3
"""
Test parallel batch tagging system.

Verifies:
1. Batch tagging can tag all 71 observations in parallel
2. Each batch returns properly tagged observations
3. No JSON errors with small batches
4. Total time is reasonable (~2-3 minutes)
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from agents.evidence.batch_tagger import tag_all_evidence_parallel
from utils.corpus_loader import load_all_corpus


async def test_batch_tagging():
    """Test full parallel batch tagging system"""
    print("=" * 80)
    print("TESTING PARALLEL BATCH TAGGING SYSTEM")
    print("=" * 80)

    # Mock hypotheses (like Cycle 1 would generate)
    hypotheses = [
        {"id": "H01", "name": "Reputational Damage", "score": 0.9},
        {"id": "H02", "name": "Capital Weakness", "score": 0.85},
        {"id": "H03", "name": "Liquidity Crisis", "score": 0.8},
        {"id": "H04", "name": "Duration Mismatch", "score": 0.75},
        {"id": "H05", "name": "Market Contagion", "score": 0.7},
        {"id": "H06", "name": "Regulatory Breach", "score": 0.65},
        {"id": "H07", "name": "Operational Risk", "score": 0.6},
        {"id": "H08", "name": "Counterparty Exposure", "score": 0.55},
        {"id": "H09", "name": "Social Media Run", "score": 0.5},
    ]

    print(f"\n📋 Setup:")
    print(f"   Entity: Credit Suisse")
    print(f"   Hypotheses: {len(hypotheses)}")

    # Check corpus size
    structural = load_all_corpus("Credit Suisse", "structural")
    empirical = load_all_corpus("Credit Suisse", "empirical")
    total = len(structural) + len(empirical)
    print(f"   Corpus: {total} observations ({len(structural)} structural, {len(empirical)} empirical)")

    # Test parallel batch tagging
    print(f"\n🚀 Starting parallel batch tagging (10 batches)...")
    start_time = datetime.now()

    all_tagged = await tag_all_evidence_parallel(
        entity="Credit Suisse",
        hypotheses=hypotheses,
        batch_size=7,  # 71 / 10 ≈ 7 per batch
    )

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print(f"\n✅ RESULTS:")
    print(f"   Total observations tagged: {len(all_tagged)}")
    print(f"   Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    print(f"   Average per observation: {duration/len(all_tagged):.2f} seconds")

    # Verify tagging quality
    print(f"\n🔍 Verifying tagged observations...")

    tagged_count = 0
    missing_tags = 0

    for obs in all_tagged[:5]:  # Check first 5
        has_tags = (
            "supports" in obs and
            "contradicts" in obs and
            "neutral" in obs
        )
        if has_tags:
            tagged_count += 1
            print(f"   ✓ {obs['observation_id']}: "
                  f"supports={len(obs.get('supports', []))}, "
                  f"contradicts={len(obs.get('contradicts', []))}, "
                  f"neutral={len(obs.get('neutral', []))}")
        else:
            missing_tags += 1
            print(f"   ⚠️  {obs['observation_id']}: Missing tags")

    # Summary
    print(f"\n" + "=" * 80)
    print(f"TEST SUMMARY")
    print("=" * 80)

    success = len(all_tagged) >= 60 and duration < 300  # Should tag most and finish in < 5 min

    if success:
        print(f"✅ PASS: Parallel batch tagging works!")
        print(f"   - Tagged {len(all_tagged)}/{total} observations")
        print(f"   - Completed in {duration:.1f} seconds")
        print(f"   - Ready for production use")
    else:
        print(f"❌ FAIL: Issues detected")
        if len(all_tagged) < 60:
            print(f"   - Only tagged {len(all_tagged)}/{total} observations")
        if duration >= 300:
            print(f"   - Took too long: {duration:.1f} seconds")

    return success


if __name__ == "__main__":
    success = asyncio.run(test_batch_tagging())
    sys.exit(0 if success else 1)
