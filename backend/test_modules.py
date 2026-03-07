#!/usr/bin/env python3
"""
Modular Backend Tests
Test each component independently without full investigation run
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from gemini.client import call_gemini
from gemini.prompts.investigation_phases_v2 import (
    build_phase1_score_and_crossmodal_prompt,
    build_phase2_elimination_prompt,
)
from agents.evidence.packager import gather_evidence
from utils.corpus_loader import load_all_corpus


# ============================================================================
# TEST 1: Corpus Loading
# ============================================================================
async def test_corpus_loading():
    """Test that we can load evidence corpus"""
    print("\n" + "="*80)
    print("TEST 1: Corpus Loading")
    print("="*80)

    entity = "Credit Suisse"

    structural = load_all_corpus(entity, "structural")
    empirical = load_all_corpus(entity, "empirical")

    print(f"✅ Loaded {len(structural)} structural observations")
    print(f"✅ Loaded {len(empirical)} empirical observations")
    print(f"✅ Total: {len(structural) + len(empirical)} observations")

    if len(structural) > 0:
        print(f"\n   Sample structural: {structural[0]['observation_id']}")
    if len(empirical) > 0:
        print(f"   Sample empirical: {empirical[0]['observation_id']}")

    assert len(structural) > 0, "No structural observations found"
    assert len(empirical) > 0, "No empirical observations found"

    return True


# ============================================================================
# TEST 2: Phase 1 - Hypothesis Generation (Cycle 1)
# ============================================================================
async def test_phase1_generation():
    """Test hypothesis generation in cycle 1"""
    print("\n" + "="*80)
    print("TEST 2: Phase 1 - Hypothesis Generation (Cycle 1)")
    print("="*80)

    context = {
        "entity": "Credit Suisse",
        "trigger": {
            "event": "Q4 2022 earnings reveal CHF 110.5 billion deposit outflows",
            "date": "2023-02-09",
            "magnitude": "CHF 110.5 billion"
        },
        "cycle_num": 1,
        "evidence": [],
        "surviving_hypotheses": [],
        "cross_modal_flags": []
    }

    prompt = build_phase1_score_and_crossmodal_prompt(
        cycle_num=context["cycle_num"],
        trigger=context["trigger"],
        entity=context["entity"],
        compressed_state=None,
        evidence=context["evidence"],
        active_hypotheses=context["surviving_hypotheses"]
    )

    print(f"📝 Calling Gemini for hypothesis generation...")
    result = await call_gemini(prompt)

    response = result["response"]
    # Cycle 1 returns "surviving_hypotheses" not "scored_hypotheses"
    hypotheses = response.get("surviving_hypotheses", [])

    print(f"\n✅ Generated {len(hypotheses)} hypotheses")

    for h in hypotheses[:3]:  # Show first 3
        print(f"   - {h['id']}: {h['name']} (score: {h.get('score', 'N/A')})")

    print(f"\n📊 Token usage: {result['token_usage']['input_tokens']} in, {result['token_usage']['output_tokens']} out")

    assert len(hypotheses) >= 5, f"Expected at least 5 hypotheses, got {len(hypotheses)}"
    assert all('id' in h and 'name' in h and 'score' in h for h in hypotheses), "Missing required fields"

    return hypotheses


# ============================================================================
# TEST 3: Evidence Tagging
# ============================================================================
async def test_evidence_tagging(hypotheses):
    """Test evidence gathering and tagging"""
    print("\n" + "="*80)
    print("TEST 3: Evidence Tagging")
    print("="*80)

    evidence_requests = [
        {"type": "structural", "description": "Capital structure and regulatory filings", "reason": "Test structural evidence"},
        {"type": "empirical", "description": "Market data and news articles", "reason": "Test empirical evidence"},
    ]

    print(f"📝 Gathering and tagging evidence...")

    tagged_evidence = await gather_evidence(
        evidence_requests=evidence_requests,
        active_hypotheses=hypotheses[:5],  # Use first 5 hypotheses
        entity="Credit Suisse"
    )

    print(f"\n✅ Retrieved {len(tagged_evidence)} tagged observations")

    if len(tagged_evidence) > 0:
        sample = tagged_evidence[0]
        print(f"\n   Sample observation: {sample['observation_id']}")
        print(f"   Supports: {len(sample.get('supports', []))} hypotheses")
        print(f"   Contradicts: {len(sample.get('contradicts', []))} hypotheses")
        print(f"   Neutral: {len(sample.get('neutral', []))} hypotheses")

    assert len(tagged_evidence) > 0, "No evidence returned"
    assert len(tagged_evidence) <= 30, f"Should limit to 30, got {len(tagged_evidence)}"

    return tagged_evidence


# ============================================================================
# TEST 4: Phase 2 - Elimination Logic
# ============================================================================
async def test_phase2_elimination(hypotheses, evidence):
    """Test elimination phase with conservative logic"""
    print("\n" + "="*80)
    print("TEST 4: Phase 2 - Elimination Logic")
    print("="*80)

    # Give some hypotheses low scores to test elimination
    test_hypotheses = []
    for i, h in enumerate(hypotheses[:8]):
        h_copy = h.copy()
        if i < 2:
            h_copy['score'] = 0.05  # Very low - should eliminate
        elif i < 5:
            h_copy['score'] = 0.25  # Low but above threshold - should keep
        else:
            h_copy['score'] = 0.65  # Good score - should keep
        test_hypotheses.append(h_copy)

    cross_modal_flags = []

    prompt = build_phase2_elimination_prompt(
        scored_hypotheses=test_hypotheses,
        evidence=evidence[:10],  # Use subset
        cross_modal_flags=cross_modal_flags,
        cycle_num=2
    )

    print(f"📝 Calling Gemini for elimination analysis...")
    print(f"   Input: {len(test_hypotheses)} hypotheses")
    print(f"   Scores: {[h['score'] for h in test_hypotheses]}")

    result = await call_gemini(prompt)
    response = result["response"]

    eliminated = response.get("eliminated_hypotheses", [])
    surviving = response.get("surviving_hypotheses", [])

    # Apply score-based elimination (< 0.15)
    low_score_eliminations = []
    final_survivors = []

    for h in surviving:
        if h.get("score", 1.0) < 0.15:
            low_score_eliminations.append({
                "id": h["id"],
                "name": h["name"],
                "reason": f"Score {h['score']:.2f} below 0.15 threshold"
            })
        else:
            final_survivors.append(h)

    total_eliminated = len(eliminated) + len(low_score_eliminations)

    print(f"\n✅ Elimination results:")
    print(f"   - Gemini eliminated: {len(eliminated)}")
    print(f"   - Score eliminated (< 0.15): {len(low_score_eliminations)}")
    print(f"   - Total eliminated: {total_eliminated}")
    print(f"   - Survivors: {len(final_survivors)}")

    print(f"\n📊 Token usage: {result['token_usage']['input_tokens']} in, {result['token_usage']['output_tokens']} out")

    # Assertions
    assert len(final_survivors) > 0, "FAIL: All hypotheses eliminated! Logic too aggressive."
    assert len(final_survivors) >= 3, f"Expected at least 3 survivors, got {len(final_survivors)}"
    assert total_eliminated >= 1, "Expected at least 1 elimination"

    print(f"\n✅ PASS: Elimination logic is balanced")
    print(f"   Kept {len(final_survivors)}/{len(test_hypotheses)} hypotheses")

    return final_survivors, eliminated + low_score_eliminations


# ============================================================================
# TEST 5: JSON Serialization
# ============================================================================
async def test_json_serialization(hypotheses, eliminated):
    """Test that we can serialize results without errors"""
    print("\n" + "="*80)
    print("TEST 5: JSON Serialization")
    print("="*80)

    from datetime import datetime

    case_file = {
        "entity": "Credit Suisse",
        "tier": 4,
        "status": "investigating",
        "timestamp": datetime.now().isoformat(),
        "active_hypotheses": hypotheses,
        "eliminated_hypotheses": eliminated,
        "cycle_history": [
            {
                "cycle_num": 1,
                "timestamp": datetime.now().isoformat(),
                "hypotheses_count": len(hypotheses),
            }
        ]
    }

    try:
        json_str = json.dumps(case_file, indent=2, ensure_ascii=False, default=str)
        print(f"✅ JSON serialization successful")
        print(f"   Size: {len(json_str)} bytes")

        # Try to parse it back
        parsed = json.loads(json_str)
        print(f"✅ JSON parsing successful")
        print(f"   Active hypotheses: {len(parsed['active_hypotheses'])}")
        print(f"   Eliminated hypotheses: {len(parsed['eliminated_hypotheses'])}")

        return True

    except Exception as e:
        print(f"❌ JSON serialization failed: {e}")
        raise


# ============================================================================
# RUN ALL TESTS
# ============================================================================
async def run_all_tests():
    """Run all modular tests"""
    print("\n" + "="*80)
    print("MODULAR BACKEND TESTS")
    print("="*80)
    print("Testing backend components independently...")

    try:
        # Test 1: Corpus loading
        await test_corpus_loading()

        # Test 2: Hypothesis generation
        hypotheses = await test_phase1_generation()

        # Test 3: Evidence tagging
        evidence = await test_evidence_tagging(hypotheses)

        # Test 4: Elimination logic
        survivors, eliminated = await test_phase2_elimination(hypotheses, evidence)

        # Test 5: JSON serialization
        await test_json_serialization(survivors, eliminated)

        # Summary
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80)
        print(f"✅ Corpus loading: OK")
        print(f"✅ Hypothesis generation: {len(hypotheses)} hypotheses")
        print(f"✅ Evidence tagging: {len(evidence)} observations")
        print(f"✅ Elimination logic: {len(survivors)} survivors, {len(eliminated)} eliminated")
        print(f"✅ JSON serialization: OK")
        print(f"\n🎉 Backend is functional and ready!")

        return True

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
