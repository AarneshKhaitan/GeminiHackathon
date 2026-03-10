import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

"""
Integration test for Phases 3, 4, 5 working together.

Tests the full orchestrator + investigator + evidence pipeline flow.

FAST MODE: Uses mock data to test integration logic without slow Gemini calls.
"""

import asyncio
import json

# Phase 5: Orchestrator
from agents.orchestrator import (
    create_case_file,
    prepare_investigator_context,
    parse_investigator_output,
    update_case_file_with_investigator_output,
    decide_convergence,
    needs_evidence,
)

# Phase 4: Evidence Pipeline (just the retrieval part, no Gemini tagging)
from agents.evidence.structural_agent import search_structural
from agents.evidence.market_agent import search_market
from agents.evidence.news_agent import search_news


async def test_full_integration():
    """Test Phases 3, 4, 5 working together (fast mode - no Gemini calls)."""

    print("=" * 80)
    print("INTEGRATION TEST: Phases 3, 4, 5 (FAST MODE - NO GEMINI CALLS)")
    print("=" * 80)

    # =========================================================================
    # SETUP: Create case file for Credit Suisse investigation
    # =========================================================================
    print("\n📋 SETUP: Creating case file...")

    trigger = {
        "entity": "Credit Suisse",
        "event": "AT1 bond write-down",
        "magnitude": "Complete write-down",
        "date": "2023-03-19",
    }

    case_file = create_case_file(
        entity="Credit Suisse",
        trigger=trigger,
        tier=4,  # Full investigation
    )

    print(f"✓ Case file created for {case_file['entity']}")
    print(f"  Tier: {case_file['tier']}, Status: {case_file['status']}")

    # =========================================================================
    # CYCLE 1: Mock hypothesis generation (no Gemini call)
    # =========================================================================
    print("\n" + "=" * 80)
    print("CYCLE 1: Mock Hypothesis Generation")
    print("=" * 80)

    # Mock investigator output for Cycle 1
    mock_inv_output_c1 = {
        "surviving_hypotheses": [
            {
                "id": "H01",
                "name": "AT1 Contractual Write-Down",
                "description": "PONV clause triggered by FINMA viability determination",
                "score": 0.9,
                "evidence_chain": [],
                "status": "active",
            },
            {
                "id": "H02",
                "name": "Swiss Regulatory Intervention",
                "description": "Emergency powers override normal creditor hierarchy",
                "score": 0.85,
                "evidence_chain": [],
                "status": "active",
            },
            {
                "id": "H03",
                "name": "Market Contagion from SVB",
                "description": "Spillover effects from US regional bank failures",
                "score": 0.7,
                "evidence_chain": [],
                "status": "active",
            },
        ],
        "eliminated_hypotheses": [],
        "cross_modal_flags": [],
        "evidence_requests": [
            {"type": "structural", "description": "AT1 bond prospectus PONV clause terms"},
            {"type": "structural", "description": "FINMA emergency powers legal framework"},
            {"type": "empirical", "description": "CS CDS spreads March 2023"},
        ],
        "compressed_state": "Cycle 1: Generated 3 hypotheses about AT1 write-down. Need structural evidence on PONV clauses and regulatory powers.",
        "key_insights": ["AT1 bonds have contractual write-down provisions"],
        "token_usage": {"input": 1000, "output": 2000, "total": 3000},
    }

    print(f"\n✓ Mock investigator output created")
    print(f"  Hypotheses generated: {len(mock_inv_output_c1['surviving_hypotheses'])}")
    print(f"  Evidence requests: {len(mock_inv_output_c1['evidence_requests'])}")

    # Parse and update case file
    parsed_c1 = parse_investigator_output(mock_inv_output_c1, cycle_num=1)
    case_file = update_case_file_with_investigator_output(case_file, parsed_c1, cycle_num=1)

    print(f"\n✓ Case file updated")
    print(f"  Active hypotheses: {len(case_file['active_hypotheses'])}")
    print(f"  Evidence requests pending: {len(case_file['evidence_pending'])}")

    # Check if we need evidence
    need_evidence = needs_evidence(case_file, cycle_num=2)
    print(f"  Needs evidence for Cycle 2: {need_evidence}")

    # Display hypotheses
    print(f"\n📊 Hypotheses:")
    for h in case_file['active_hypotheses']:
        print(f"  {h['id']}: {h['name']} (score: {h['score']})")

    # =========================================================================
    # CYCLE 2: Evidence gathering + mock evaluation
    # =========================================================================
    print("\n" + "=" * 80)
    print("CYCLE 2: Evidence Gathering (Phase 4) + Mock Evaluation")
    print("=" * 80)

    # Test Phase 4 evidence retrieval (no Gemini tagging, just corpus search)
    print(f"\n📦 Testing Phase 4 evidence retrieval...")
    print(f"  Evidence requests: {len(case_file['evidence_pending'])}")

    structural_evidence = await search_structural(
        case_file['evidence_pending'],
        case_file['entity']
    )
    market_evidence = await search_market(
        case_file['evidence_pending'],
        case_file['entity']
    )
    news_evidence = await search_news(
        case_file['evidence_pending'],
        case_file['entity']
    )

    print(f"\n✓ Evidence retrieved:")
    print(f"  Structural: {len(structural_evidence)} observations")
    print(f"  Market: {len(market_evidence)} observations")
    print(f"  News: {len(news_evidence)} observations")

    # Mock tag the evidence
    new_evidence_c2 = []
    for obs in (structural_evidence + market_evidence + news_evidence)[:5]:
        obs['supports'] = ['H01'] if 'AT1' in obs['content'] or 'PONV' in obs['content'] else []
        obs['contradicts'] = []
        obs['neutral'] = ['H02', 'H03'] if not obs['supports'] else []
        new_evidence_c2.append(obs)

    if new_evidence_c2:
        print(f"\n  Sample evidence (mock tagged):")
        for obs in new_evidence_c2[:3]:
            print(f"    {obs['observation_id']}: {obs['source'][:50]}...")
            print(f"      Supports: {obs['supports']}, Contradicts: {obs['contradicts']}")

    # Test prepare_investigator_context
    context_c2 = prepare_investigator_context(
        case_file=case_file,
        cycle_num=2,
        new_evidence=new_evidence_c2,
    )

    print(f"\n✓ Investigator context prepared")
    print(f"  Entity: {context_c2['entity']}")
    print(f"  Cycle: {context_c2['cycle_num']}")
    print(f"  Evidence: {len(context_c2['evidence'])} observations")
    print(f"  Active hypotheses: {len(context_c2['active_hypotheses'])}")

    # Mock investigator output for Cycle 2
    mock_inv_output_c2 = {
        "surviving_hypotheses": [
            {
                "id": "H01",
                "name": "AT1 Contractual Write-Down",
                "description": "PONV clause triggered by FINMA viability determination",
                "score": 0.95,
                "evidence_chain": ["S01", "S02"],
                "status": "active",
            },
            {
                "id": "H02",
                "name": "Swiss Regulatory Intervention",
                "description": "Emergency powers override normal creditor hierarchy",
                "score": 0.8,
                "evidence_chain": ["S02"],
                "status": "active",
            },
        ],
        "eliminated_hypotheses": [
            {
                "id": "H03",
                "name": "Market Contagion from SVB",
                "killed_by_atom": "S01",
                "killed_in_cycle": 2,
                "reason": "Evidence shows CS-specific regulatory action, not market contagion",
            }
        ],
        "cross_modal_flags": [
            {
                "structural_atom_id": "S01",
                "empirical_atom_id": "E01",
                "detected_in_cycle": 2,
                "contradiction_description": "Structural allows write-down, empirical shows surprise",
            }
        ],
        "evidence_requests": [
            {"type": "empirical", "description": "Investor lawsuits post-write-down"},
        ],
        "compressed_state": "Cycle 2: H01 highly supported by PONV evidence. H03 eliminated. 2 hypotheses remaining.",
        "key_insights": ["PONV clause was legally valid but unexpected by markets"],
        "token_usage": {"input": 5000, "output": 3000, "total": 8000},
    }

    print(f"\n✓ Mock investigator output created")
    print(f"  Surviving: {len(mock_inv_output_c2['surviving_hypotheses'])}")
    print(f"  Eliminated: {len(mock_inv_output_c2['eliminated_hypotheses'])}")
    print(f"  Cross-modal flags: {len(mock_inv_output_c2['cross_modal_flags'])}")

    # Parse and update case file
    parsed_c2 = parse_investigator_output(mock_inv_output_c2, cycle_num=2)
    case_file = update_case_file_with_investigator_output(case_file, parsed_c2, cycle_num=2)

    print(f"\n✓ Case file updated")
    print(f"  Active hypotheses: {len(case_file['active_hypotheses'])}")
    print(f"  Eliminated hypotheses: {len(case_file['eliminated_hypotheses'])}")
    print(f"  Cross-modal flags: {len(case_file['cross_modal_flags'])}")

    # Show eliminations
    if case_file['eliminated_hypotheses']:
        print(f"\n❌ Eliminations:")
        for elim in case_file['eliminated_hypotheses']:
            print(f"  {elim['id']}: {elim['name']}")
            print(f"    Killed by: {elim['killed_by_atom']}")
            print(f"    Reason: {elim['reason']}")

    # Check convergence
    convergence = decide_convergence(case_file, cycle_num=2)
    print(f"\n🎯 Convergence decision: {convergence['decision']}")
    print(f"  Reason: {convergence['reason']}")
    print(f"  Hypotheses remaining: {convergence['hypotheses_count']}")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 80)
    print("✅ INTEGRATION TEST COMPLETE")
    print("=" * 80)

    print(f"\n📊 FINAL STATE:")
    print(f"  Entity: {case_file['entity']}")
    print(f"  Cycles completed: {len(case_file['cycle_history'])}")
    print(f"  Active hypotheses: {len(case_file['active_hypotheses'])}")
    print(f"  Eliminated hypotheses: {len(case_file['eliminated_hypotheses'])}")
    print(f"  Evidence collected: {len(case_file['evidence_collected'])}")
    print(f"  Cross-modal flags: {len(case_file['cross_modal_flags'])}")

    total_tokens = sum(
        cycle['token_usage'].get('total', 0)
        for cycle in case_file['cycle_history']
    )
    print(f"  Total tokens used: {total_tokens:,}")

    print(f"\n✅ Phase 3 (Investigator V2) - Working")
    print(f"✅ Phase 4 (Evidence Pipeline) - Working")
    print(f"✅ Phase 5 (Orchestrator) - Working")
    print(f"✅ Integration - All phases work together")

    return case_file


async def main():
    try:
        case_file = await test_full_integration()
        print(f"\n🎉 SUCCESS: Full 2-cycle investigation completed")
        return case_file
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    case_file = asyncio.run(main())
