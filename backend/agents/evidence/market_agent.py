"""
Market data evidence retrieval agent.

Searches the empirical corpus for market-type observations (price data,
CDS spreads, stock charts) relevant to the investigator's evidence requests.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.corpus_loader import search_corpus


async def search_market(evidence_requests: list[dict], entity: str) -> list[dict]:
    """
    Search empirical corpus for market data atoms.

    Processes requests where type == "market" OR "empirical".
    Filters results to observations classified as market type.

    Args:
        evidence_requests: List of dicts with type, description, reason
        entity: Full entity name (e.g. "Credit Suisse")

    Returns:
        List of raw market observations (untagged)
    """
    market_requests = [r for r in evidence_requests if r.get("type") in ("market", "empirical")]
    if not market_requests:
        return []

    seen_ids: set[str] = set()
    results: list[dict] = []

    for req in market_requests:
        query = req.get("description", "")
        atoms = search_corpus(query, entity, corpus_type="empirical", limit=4)
        for atom in atoms:
            if atom["observation_id"] not in seen_ids:
                seen_ids.add(atom["observation_id"])
                results.append(atom)

    return results
