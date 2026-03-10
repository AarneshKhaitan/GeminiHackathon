"""
Batch Evidence Tagging - Tag all corpus evidence once in parallel batches.

Called at investigation start to pre-tag all available evidence against
initial hypotheses. Results are cached and reused across cycles.
"""

import asyncio
from utils.corpus_loader import load_all_corpus
from gemini.client import call_gemini
from gemini.prompts.evidence_tagging import build_evidence_tagging_prompt
from utils.logger import get_logger

logger = get_logger("batch_tagger")


async def tag_single_batch(
    observations: list[dict],
    hypotheses: list[dict],
    batch_num: int = 1,
) -> list[dict]:
    """
    Tag a batch of observations against hypotheses.

    Args:
        observations: List of observations to tag
        hypotheses: Active hypotheses to tag against
        batch_num: Batch number for logging (default: 1)

    Returns:
        List of tagged observations
    """
    logger.info(f"Batch {batch_num}: Tagging {len(observations)} observations against {len(hypotheses)} hypotheses")

    prompt = build_evidence_tagging_prompt(observations, hypotheses)
    result = await call_gemini(prompt)

    # Handle both response formats
    response = result["response"]
    if isinstance(response, list):
        tagged = response
        logger.warning(f"Batch {batch_num}: Gemini returned direct array")
    elif isinstance(response, dict):
        tagged = response.get("tagged_observations", [])
    else:
        logger.error(f"Batch {batch_num}: Unexpected response format")
        tagged = []

    logger.info(f"Batch {batch_num}: Tagged {len(tagged)} observations successfully")
    return tagged


# Alias for backward compatibility
tag_batch = tag_single_batch


async def tag_all_evidence_parallel(
    entity: str,
    hypotheses: list[dict],
    batch_size: int = 12,
) -> list[dict]:
    """
    Tag all corpus evidence in parallel batches.

    Called once at investigation start. Splits corpus into batches
    and tags them in parallel to minimize total time.

    Args:
        entity: Entity name (e.g., "Credit Suisse")
        hypotheses: Initial hypotheses from Cycle 1
        batch_size: Observations per batch (default: 12)

    Returns:
        List of all tagged observations
    """
    logger.info(f"Starting parallel evidence tagging for {entity}")

    # Load all evidence
    structural_obs = load_all_corpus(entity, "structural")
    empirical_obs = load_all_corpus(entity, "empirical")
    all_evidence = structural_obs + empirical_obs

    if not all_evidence:
        logger.warning(f"No evidence found for {entity}")
        return []

    logger.info(f"Loaded {len(all_evidence)} observations ({len(structural_obs)} structural, {len(empirical_obs)} empirical)")

    # Split into batches
    batches = []
    for i in range(0, len(all_evidence), batch_size):
        batch = all_evidence[i:i + batch_size]
        batches.append(batch)

    logger.info(f"Split into {len(batches)} batches of ~{batch_size} observations each")

    # Tag all batches in parallel
    print(f"  [batch_tagger] Tagging {len(all_evidence)} observations in {len(batches)} parallel batches...")

    tasks = [
        tag_batch(batch, hypotheses, i + 1)
        for i, batch in enumerate(batches)
    ]

    batch_results = await asyncio.gather(*tasks, return_exceptions=True)

    # Combine results
    all_tagged = []
    failed_batches = 0

    for i, result in enumerate(batch_results):
        if isinstance(result, Exception):
            logger.error(f"Batch {i + 1} failed: {result}")
            failed_batches += 1
            # Add untagged observations from failed batch
            all_tagged.extend(batches[i])
        else:
            all_tagged.extend(result)

    logger.info(f"Parallel tagging complete: {len(all_tagged)} observations tagged, {failed_batches} batches failed")
    print(f"  [batch_tagger] ✓ Tagged {len(all_tagged)} observations ({failed_batches} batches failed)")

    return all_tagged
