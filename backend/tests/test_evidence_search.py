import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

"""
Test evidence search with sample queries.
"""

import asyncio
from utils.corpus_loader import search_corpus

async def test_evidence_search():
    """Test if evidence search works with typical queries."""

    entity = "Credit Suisse"

    test_queries = [
        "deposit outflows",
        "capital ratio CET1",
        "AT1 bonds",
        "restructuring",
        "liquidity",
        "Saudi National Bank",
        "Archegos",
        "Greensill",
    ]

    print("Testing Evidence Search")
    print("=" * 80)

    for query in test_queries:
        # Test structural
        structural = search_corpus(query, entity, "structural", limit=3)

        # Test empirical
        empirical = search_corpus(query, entity, "empirical", limit=3)

        print(f"\nQuery: '{query}'")
        print(f"  Structural: {len(structural)} results")
        if structural:
            print(f"    {structural[0]['observation_id']}: {structural[0].get('label', structural[0]['source'])[:60]}...")
        print(f"  Empirical: {len(empirical)} results")
        if empirical:
            print(f"    {empirical[0]['observation_id']}: {empirical[0].get('label', empirical[0]['source'])[:60]}...")

if __name__ == "__main__":
    asyncio.run(test_evidence_search())
