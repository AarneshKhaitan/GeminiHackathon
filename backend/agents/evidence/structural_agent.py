"""
Structural evidence retrieval agent.

Searches the structural corpus (permanent domain knowledge: regulations,
prospectus clauses, capital structure rules) for atoms relevant to
the investigator's evidence requests.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.corpus_loader import search_corpus


async def search_structural(evidence_requests: list[dict], entity: str) -> list[dict]:
    """
    Search structural corpus for requested evidence atoms.

    Only processes requests where type == "structural".
    Returns raw untagged observations; tagging done by packager.

    Args:
        evidence_requests: List of dicts with type, description, reason
        entity: Full entity name (e.g. "Credit Suisse")

    Returns:
        List of raw structural observations (untagged)
    """
    structural_requests = [r for r in evidence_requests if r.get("type") == "structural"]
    if not structural_requests:
        return []

    seen_ids: set[str] = set()
    results: list[dict] = []

    for req in structural_requests:
        query = req.get("description", "")
        atoms = search_corpus(query, entity, corpus_type="structural", limit=3)
        for atom in atoms:
            if atom["observation_id"] not in seen_ids:
                seen_ids.add(atom["observation_id"])
                results.append(atom)

    return results
