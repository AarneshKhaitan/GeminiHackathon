"""
Corpus loader — reads evidence from JSON files in evidence/{entity}/ directories.

Evidence is organized as:
  evidence/{entity_slug}/structural.json   — permanent domain knowledge
  evidence/{entity_slug}/empirical.json    — time-stamped market/news/filing data

Returns dicts matching the Evidence model schema with empty tag lists
(tags are added by the packager via a Gemini call).
"""

import json
from pathlib import Path
from typing import Literal

EVIDENCE_DIR = Path(__file__).parent.parent.parent / "evidence"  # project_root/evidence/

ENTITY_SLUG: dict[str, str] = {
    "Silicon Valley Bank": "svb",
    "Credit Suisse": "credit-suisse",
    "First Republic Bank": "ftx",
}


def _get_entity_json_file(entity: str, corpus_type: Literal["structural", "empirical"]) -> Path:
    """
    Get JSON file path for entity and corpus type.

    Args:
        entity: Full entity name e.g. "Credit Suisse"
        corpus_type: "structural" or "empirical"

    Returns:
        Path to {entity_slug}/{corpus_type}.json
    """
    slug = ENTITY_SLUG.get(entity, entity.lower().replace(" ", "-"))
    return EVIDENCE_DIR / slug / f"{corpus_type}.json"


def load_all_corpus(entity: str, corpus_type: Literal["structural", "empirical"]) -> list[dict]:
    """
    Load all evidence observations from JSON file for an entity/type.

    Args:
        entity: Full entity name e.g. "Credit Suisse"
        corpus_type: "structural" or "empirical"

    Returns:
        List of observation dicts (supports/contradicts/neutral already in JSON)
    """
    json_file = _get_entity_json_file(entity, corpus_type)

    if not json_file.exists():
        return []

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            observations = json.load(f)

        # Ensure all observations have required fields
        for obs in observations:
            obs.setdefault("supports", [])
            obs.setdefault("contradicts", [])
            obs.setdefault("neutral", [])

        return observations

    except Exception as e:
        print(f"Error loading {json_file}: {e}")
        return []


def search_corpus(
    query: str,
    entity: str,
    corpus_type: Literal["structural", "empirical"],
    limit: int = 5,
) -> list[dict]:
    """
    Keyword search across observations for an entity/type.

    Splits query into terms; returns observations where ANY term appears in content.

    Args:
        query: Search terms from an evidence request description
        entity: Full entity name
        corpus_type: "structural" or "empirical"
        limit: Max results to return

    Returns:
        List of matching observation dicts
    """
    all_observations = load_all_corpus(entity, corpus_type)

    if not all_observations:
        return []

    query_terms = [t for t in query.lower().split() if len(t) > 2]
    if not query_terms:
        return []

    results = []

    for obs in all_observations:
        content = obs.get("content", "").lower()

        if any(term in content for term in query_terms):
            results.append(obs)

            if len(results) >= limit:
                break

    return results


def list_corpus_files(entity: str, corpus_type: Literal["structural", "empirical"]) -> list[str]:
    """
    Return list of observation IDs for an entity/type.

    Args:
        entity: Full entity name
        corpus_type: "structural" or "empirical"

    Returns:
        List of observation IDs (e.g., ["S01", "S02", ...])
    """
    observations = load_all_corpus(entity, corpus_type)
    return [obs["observation_id"] for obs in observations]
