"""
Evidence Selector - intelligently matches evidence requests to observations.

Uses ChromaDB vector database for semantic similarity search to match
investigator's evidence requests against available observations.
"""

import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.logger import get_logger

logger = get_logger("selector")

# Lazy load ChromaDB
_chroma_client = None
_collection = None
_indexed_observations = set()


def get_chroma_client():
    """Lazy load ChromaDB client."""
    global _chroma_client
    if _chroma_client is None:
        try:
            import chromadb
            from chromadb.config import Settings

            logger.info("Initializing ChromaDB client...")
            _chroma_client = chromadb.Client(Settings(
                anonymized_telemetry=False,
                allow_reset=True
            ))
            logger.info("✓ ChromaDB client initialized")
        except ImportError:
            logger.error("chromadb not installed! Install with: pip install chromadb")
            raise
    return _chroma_client


def get_or_create_collection(entity: str):
    """Get or create ChromaDB collection for entity."""
    global _collection

    client = get_chroma_client()
    collection_name = f"evidence_{entity.lower().replace(' ', '_')}"

    # Get or create collection
    _collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"entity": entity}
    )

    return _collection


def index_observations(observations: list[dict], entity: str):
    """Index observations in ChromaDB."""
    global _indexed_observations

    collection = get_or_create_collection(entity)

    # Filter out already indexed
    to_index = [obs for obs in observations if obs['observation_id'] not in _indexed_observations]

    if not to_index:
        logger.info(f"All {len(observations)} observations already indexed")
        return

    logger.info(f"Indexing {len(to_index)} observations in ChromaDB...")

    # Prepare data for ChromaDB
    ids = [obs['observation_id'] for obs in to_index]
    documents = [obs.get('content', '') for obs in to_index]
    metadatas = [{
        'type': obs.get('type', 'unknown'),
        'observation_id': obs['observation_id']
    } for obs in to_index]

    # Add to collection (ChromaDB will auto-generate embeddings)
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    # Mark as indexed
    _indexed_observations.update(ids)

    logger.info(f"✓ Indexed {len(to_index)} observations (total: {len(_indexed_observations)})")


async def select_evidence_for_requests(
    evidence_requests: list[dict],
    available_observations: list[dict],
    already_gathered: list[str] = None,
) -> list[dict]:
    """
    Use ChromaDB semantic search to select observations matching evidence requests.

    Args:
        evidence_requests: Investigator's specific evidence requests with descriptions
        available_observations: Pre-tagged observations to select from
        already_gathered: Observation IDs already used in previous cycles

    Returns:
        List of selected observations that best match the requests
    """

    if not evidence_requests:
        logger.info("No evidence requests - returning empty")
        return []

    if not available_observations:
        logger.info("No available observations - returning empty")
        return []

    # Filter out already-gathered first
    if already_gathered:
        available_observations = [
            obs for obs in available_observations
            if obs['observation_id'] not in already_gathered
        ]
        logger.info(f"Filtered to {len(available_observations)} observations (excluded {len(already_gathered)} already gathered)")

    # Log what investigator is requesting
    logger.info(f"Evidence requests from investigator:")
    for i, req in enumerate(evidence_requests):
        logger.info(f"  {i+1}. [{req.get('type', 'any')}] {req.get('description', 'N/A')[:100]}")

    # Separate structural and empirical
    structural_obs = [obs for obs in available_observations if obs['observation_id'].startswith('S')]
    empirical_obs = [obs for obs in available_observations if obs['observation_id'].startswith('E')]

    logger.info(f"Available: {len(structural_obs)} structural, {len(empirical_obs)} empirical")

    # Index observations in ChromaDB (only indexes new ones)
    entity = "Credit Suisse"  # TODO: Pass entity as parameter
    index_observations(available_observations, entity)

    collection = get_or_create_collection(entity)

    selected_observations = []
    selected_ids = set()
    rejected_count = 0
    collected_distances = []

    # Similarity threshold filtering
    MIN_SIMILARITY_THRESHOLD = 0.05  # Require at least 5% similarity

    # For each request, query ChromaDB for best matches
    for req_idx, req in enumerate(evidence_requests):
        req_type = req.get('type', '').lower()
        req_desc = req.get('description', '')

        # Query ChromaDB for top matches (filter by ID prefix after retrieval)
        # We'll get more results and filter by observation_id prefix
        n_results = 15  # Get more results to ensure we have enough after filtering

        logger.info(f"  Request {req_idx+1}: Querying for {req_type.upper() or 'ALL'} observations")

        # Query ChromaDB (no metadata filter - we'll filter by observation_id prefix)
        results = collection.query(
            query_texts=[req_desc],
            n_results=n_results,
            include=['distances', 'metadatas']
        )

        # Process results
        if results and results['ids'] and results['ids'][0]:
            matches_for_request = 0
            for obs_id, distance in zip(results['ids'][0], results['distances'][0]):
                # Convert distance to similarity
                similarity = 1 - distance

                # Filter by observation_id prefix based on request type
                if req_type == 'structural' and not obs_id.startswith('S'):
                    continue
                elif req_type == 'empirical' and not obs_id.startswith('E'):
                    continue

                # Skip if already selected or already gathered
                if obs_id in selected_ids or obs_id in (already_gathered or []):
                    continue

                # QUALITY FILTER: Only accept positive similarity above threshold
                if similarity <= 0.0:
                    logger.info(f"    ✗ {obs_id} (similarity: {similarity:.3f}) - REJECTED (negative)")
                    rejected_count += 1
                    continue

                if similarity < MIN_SIMILARITY_THRESHOLD:
                    logger.info(f"    ✗ {obs_id} (similarity: {similarity:.3f}) - REJECTED (below threshold {MIN_SIMILARITY_THRESHOLD})")
                    rejected_count += 1
                    continue

                # Find the actual observation object
                obs = next((o for o in available_observations if o['observation_id'] == obs_id), None)
                if obs:
                    selected_observations.append(obs)
                    selected_ids.add(obs_id)
                    collected_distances.append(distance)
                    logger.info(f"    ✓ {obs_id} (similarity: {similarity:.3f})")
                    matches_for_request += 1

                    # Stop after 3 matches per request
                    if matches_for_request >= 3:
                        break

            # FALLBACK: If structural request found no matches, try without type filter
            if req_type == 'structural' and matches_for_request == 0:
                logger.warning(f"    ⚠️  No structural matches found, trying fallback search...")
                # Get structural observations directly by prefix
                structural_candidates = [o for o in available_observations
                                        if o['observation_id'].startswith('S')
                                        and o['observation_id'] not in selected_ids
                                        and o['observation_id'] not in (already_gathered or [])]
                if structural_candidates:
                    # Take first 2 structural observations as fallback
                    for obs in structural_candidates[:2]:
                        selected_observations.append(obs)
                        selected_ids.add(obs['observation_id'])
                        collected_distances.append(0.5)  # Neutral distance for fallback
                        logger.info(f"    ✓ {obs['observation_id']} (fallback - structural)")
                        matches_for_request += 1

    logger.info(f"Selected {len(selected_observations)} observations: {[o['observation_id'] for o in selected_observations]}")

    # Add quality metrics logging
    if selected_observations:
        similarities = [1 - distance for distance in collected_distances]
        avg_similarity = sum(similarities) / len(similarities)
        min_similarity = min(similarities)
        max_similarity = max(similarities)

        logger.info(f"  Quality metrics:")
        logger.info(f"    Avg similarity: {avg_similarity:.3f}")
        logger.info(f"    Range: [{min_similarity:.3f}, {max_similarity:.3f}]")
        logger.info(f"    Rejected: {rejected_count} (negative or below threshold)")

        # Evidence exhaustion warnings
        if avg_similarity < 0.15:
            logger.warning(f"    ⚠️  Low average similarity ({avg_similarity:.3f}) - evidence corpus may be exhausted")

        if max_similarity < 0.25:
            logger.warning(f"    ⚠️  Best match only {max_similarity:.3f} - struggling to find relevant evidence")
    else:
        # No observations selected at all
        logger.warning(f"  ⚠️  NO OBSERVATIONS SELECTED - evidence corpus exhausted for these requests")

    logger.info(f"Returning {len(selected_observations)} matched observations")

    return selected_observations
