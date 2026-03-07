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

    Args:
        evidence_requests: Evidence requests from investigator Phase 4 output
            Each has: type, description, reason
        active_hypotheses: Current surviving hypotheses (for tagging reference)
            Each has: id, name, score
        entity: Full entity name (e.g. "Credit Suisse")

    Returns:
        List of tagged observations, each with supports/contradicts/neutral lists.
        Returns [] if no evidence found (no Gemini call made).
    """

    # Dispatch all three retrieval agents in parallel
    structural_results, market_results, news_results = await asyncio.gather(
        search_structural(evidence_requests, entity),
        search_market(evidence_requests, entity),
        search_news(evidence_requests, entity),
    )

    # Combine and deduplicate by observation_id
    seen: set[str] = set()
    raw_evidence: list[dict] = []

    for obs in structural_results + market_results + news_results:
        if obs["observation_id"] not in seen:
            seen.add(obs["observation_id"])
            raw_evidence.append(obs)

    if not raw_evidence:
        print("  [packager] No evidence found for requests — skipping Gemini tagging call")
        return []

    print(f"  [packager] Retrieved {len(raw_evidence)} unique atoms "
          f"({len(structural_results)} structural, {len(market_results)} market, "
          f"{len(news_results)} news) — tagging via Gemini...")

    # If no active hypotheses yet, return atoms untagged (cycle 1 edge case)
    if not active_hypotheses:
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
