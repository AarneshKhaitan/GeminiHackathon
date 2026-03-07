"""
News and filing evidence retrieval agent.

Searches the empirical corpus for news articles, press releases, interviews,
and regulatory filings relevant to the investigator's evidence requests.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.corpus_loader import search_corpus


async def search_news(evidence_requests: list[dict], entity: str) -> list[dict]:
    """
    Search empirical corpus for news and filing atoms.

    Processes requests where type in ["news", "filing", "empirical"].

    Args:
        evidence_requests: List of dicts with type, description, reason
        entity: Full entity name (e.g. "Credit Suisse")

    Returns:
        List of raw news/filing observations (untagged)
    """
    news_requests = [r for r in evidence_requests if r.get("type") in ("news", "filing", "empirical")]
    if not news_requests:
        return []

    seen_ids: set[str] = set()
    results: list[dict] = []

    for req in news_requests:
        query = req.get("description", "")
        atoms = search_corpus(query, entity, corpus_type="empirical", limit=4)
        for atom in atoms:
            if atom["observation_id"] not in seen_ids:
                seen_ids.add(atom["observation_id"])
                results.append(atom)

    return results
