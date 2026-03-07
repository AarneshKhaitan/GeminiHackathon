"""
Evidence Packager — orchestrates the full evidence retrieval + tagging pipeline.

Internal flow:
  1. Dispatch structural, market, and news agents in parallel (asyncio.gather)
  2. Combine and deduplicate raw results
  3. Make ONE Gemini call to tag all atoms against active hypotheses
  4. Return tagged observations ready for the investigator

This is the ONLY component that makes the evidence tagging Gemini call.
Retrieval agents never call Gemini — they only search the local corpus.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from gemini.client import call_gemini
from gemini.prompts.evidence_tagging import build_evidence_tagging_prompt
from agents.evidence.structural_agent import search_structural
from agents.evidence.market_agent import search_market
from agents.evidence.news_agent import search_news


async def gather_evidence(
    evidence_requests: list[dict],
    active_hypotheses: list[dict],
    entity: str,
) -> list[dict]:
    """
    Execute full evidence retrieval and tagging pipeline for one cycle.

    Simplified approach: Load ALL structural and empirical evidence,
    let Gemini tag it against active hypotheses.

    Args:
        evidence_requests: Evidence requests from investigator (not used - we load all)
        active_hypotheses: Current surviving hypotheses (for tagging reference)
        entity: Full entity name (e.g. "Credit Suisse")

    Returns:
        List of tagged observations, each with supports/contradicts/neutral lists.
    """
    from utils.corpus_loader import load_all_corpus

    # Load ALL evidence (no filtering)
    structural_obs = load_all_corpus(entity, "structural")
    empirical_obs = load_all_corpus(entity, "empirical")

    raw_evidence = structural_obs + empirical_obs

    if not raw_evidence:
        print("  [packager] No evidence found in corpus")
        return []

    print(f"  [packager] Loaded {len(raw_evidence)} total observations "
          f"({len(structural_obs)} structural, {len(empirical_obs)} empirical)")

    # If no active hypotheses yet, return atoms untagged (cycle 1 edge case)
    if not active_hypotheses:
        print("  [packager] No active hypotheses - returning untagged evidence")
        return raw_evidence

    # ONE Gemini call to tag all atoms against active hypotheses
    prompt = build_evidence_tagging_prompt(raw_evidence, active_hypotheses)
    result = await call_gemini(prompt)

    tagged: list[dict] = result["response"].get("tagged_observations", [])

    # Fallback: if Gemini returns empty/malformed, return raw (untagged) atoms
    if not tagged:
        print("  [packager] Warning: tagging returned empty — returning untagged atoms")
        return raw_evidence

    print(f"  [packager] Tagged {len(tagged)} observations successfully")
    return tagged
