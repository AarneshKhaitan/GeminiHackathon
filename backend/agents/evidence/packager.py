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
from utils.logger import get_logger

logger = get_logger("packager")


async def gather_evidence(
    evidence_requests: list[dict],
    active_hypotheses: list[dict],
    entity: str,
    already_gathered: list[str] = None,
) -> list[dict]:
    """
    Execute full evidence retrieval and tagging pipeline for one cycle.

    Simplified approach: Load ALL structural and empirical evidence,
    filter out already-gathered observations, then limit to 30 and
    let Gemini tag against active hypotheses.

    Args:
        evidence_requests: Evidence requests from investigator (not used - we load all)
        active_hypotheses: Current surviving hypotheses (for tagging reference)
        entity: Full entity name (e.g. "Credit Suisse")
        already_gathered: List of observation IDs already used in previous cycles

    Returns:
        List of tagged observations, each with supports/contradicts/neutral lists.
    """
    from utils.corpus_loader import load_all_corpus

    if already_gathered is None:
        already_gathered = []

    logger.info(f"Gathering evidence for {entity}: {len(evidence_requests)} requests, {len(active_hypotheses)} active hypotheses, {len(already_gathered)} already gathered")

    # Load ALL evidence (no filtering)
    structural_obs = load_all_corpus(entity, "structural")
    empirical_obs = load_all_corpus(entity, "empirical")

    raw_evidence = structural_obs + empirical_obs

    if not raw_evidence:
        print("  [packager] No evidence found in corpus")
        logger.warning(f"No evidence found for {entity}")
        return []

    # Filter out already-gathered evidence to avoid duplicates
    if already_gathered:
        raw_evidence = [
            obs for obs in raw_evidence
            if obs['observation_id'] not in already_gathered
        ]
        logger.info(f"Filtered to {len(raw_evidence)} new observations (excluded {len(already_gathered)} already gathered)")

    # Filter based on investigator's evidence requests
    # Prioritize evidence matching request types and keywords
    if evidence_requests and raw_evidence:
        filtered_evidence = []
        requested_types = set()
        keywords = []

        for req in evidence_requests:
            req_type = req.get('type', '').lower()
            if req_type:
                requested_types.add(req_type)
            desc = req.get('description', '').lower()
            if desc:
                keywords.extend([w for w in desc.split() if len(w) > 4])

        # Prioritize matching observations
        for obs in raw_evidence:
            obs_type = obs.get('type', '').lower()
            content = obs.get('content', '').lower()

            # Check type match
            type_match = obs_type in requested_types or not requested_types

            # Check keyword match
            keyword_match = any(kw in content for kw in keywords) if keywords else False

            if type_match or keyword_match:
                if keyword_match:
                    filtered_evidence.insert(0, obs)  # Keyword matches first
                else:
                    filtered_evidence.append(obs)

        if filtered_evidence:
            raw_evidence = filtered_evidence
            logger.info(f"Filtered to {len(raw_evidence)} observations matching evidence requests")
        else:
            logger.info("No evidence matched requests, using all available")

    print(f"  [packager] Loaded {len(raw_evidence)} total observations "
          f"({len(structural_obs)} structural, {len(empirical_obs)} empirical)")
    logger.info(f"Loaded {len(raw_evidence)} observations ({len(structural_obs)} structural, {len(empirical_obs)} empirical)")

    if not raw_evidence:
        print("  [packager] All observations already gathered - returning empty")
        logger.warning("All observations already gathered in previous cycles")
        return []

    # If no active hypotheses yet, return atoms untagged (cycle 1 edge case)
    if not active_hypotheses:
        print("  [packager] No active hypotheses - returning untagged evidence")
        logger.info("No active hypotheses - returning untagged evidence")
        return raw_evidence[:15]  # Limit to 15

    # LIMIT evidence to prevent Gemini JSON parsing errors
    # Too many observations causes malformed JSON responses
    # Reduced to 15 to handle growing context in later cycles and ensure valid JSON
    MAX_EVIDENCE_PER_BATCH = 15
    evidence_subset = raw_evidence[:MAX_EVIDENCE_PER_BATCH]

    print(f"  [packager] Limiting to {len(evidence_subset)} observations for tagging (max {MAX_EVIDENCE_PER_BATCH})")
    logger.info(f"Limiting to {len(evidence_subset)} observations for tagging (max {MAX_EVIDENCE_PER_BATCH})")

    # ONE Gemini call to tag limited atoms against active hypotheses
    prompt = build_evidence_tagging_prompt(evidence_subset, active_hypotheses)
    logger.info(f"Calling Gemini to tag {len(evidence_subset)} observations against {len(active_hypotheses)} hypotheses")
    result = await call_gemini(prompt)

    # Handle both response formats:
    # 1. {"tagged_observations": [...]} - expected format
    # 2. [...] - direct array (Gemini sometimes does this)
    response = result["response"]
    if isinstance(response, list):
        # Gemini returned array directly
        tagged = response
        logger.warning("Gemini returned observations as direct array instead of wrapped object")
    elif isinstance(response, dict):
        # Expected format
        tagged = response.get("tagged_observations", [])
    else:
        # Unknown format
        logger.error(f"Unexpected response format: {type(response)}")
        tagged = []

    # Fallback: if Gemini returns empty/malformed, return raw (untagged) atoms
    if not tagged:
        print("  [packager] Warning: tagging returned empty — returning untagged atoms")
        logger.warning("Tagging returned empty - returning untagged atoms")
        return evidence_subset

    print(f"  [packager] Tagged {len(tagged)} observations successfully")
    logger.info(f"Successfully tagged {len(tagged)} observations")
    return tagged
