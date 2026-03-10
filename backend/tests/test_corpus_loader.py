import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

"""
Test updated corpus_loader with JSON files.
"""

from utils.corpus_loader import load_all_corpus, search_corpus, list_corpus_files


def test_load_structural():
    """Test loading structural JSON."""
    print("\n=== TEST 1: Load Structural JSON ===")

    observations = load_all_corpus("Credit Suisse", "structural")

    print(f"✓ Loaded {len(observations)} structural observations")

    if observations:
        sample = observations[0]
        print(f"\n  Sample observation:")
        print(f"    ID: {sample['observation_id']}")
        print(f"    Type: {sample['type']}")
        print(f"    Source: {sample.get('source', 'N/A')}")
        print(f"    Content length: {len(sample['content'])} chars")


def test_load_empirical():
    """Test loading empirical JSON."""
    print("\n=== TEST 2: Load Empirical JSON ===")

    observations = load_all_corpus("Credit Suisse", "empirical")

    print(f"✓ Loaded {len(observations)} empirical observations")

    if observations:
        sample = observations[0]
        print(f"\n  Sample observation:")
        print(f"    ID: {sample['observation_id']}")
        print(f"    Type: {sample['type']}")
        print(f"    Date: {sample.get('date', 'N/A')}")
        print(f"    Content length: {len(sample['content'])} chars")


def test_search():
    """Test search functionality."""
    print("\n=== TEST 3: Search Corpus ===")

    # Search for AT1 in structural
    results = search_corpus("AT1 bond PONV", "Credit Suisse", "structural", limit=3)

    print(f"✓ Found {len(results)} matches for 'AT1 bond PONV'")

    for obs in results[:2]:
        print(f"  {obs['observation_id']}: {obs.get('label', obs.get('source', 'N/A'))[:60]}...")


def test_list_ids():
    """Test listing observation IDs."""
    print("\n=== TEST 4: List Observation IDs ===")

    structural_ids = list_corpus_files("Credit Suisse", "structural")
    empirical_ids = list_corpus_files("Credit Suisse", "empirical")

    print(f"✓ Structural IDs: {len(structural_ids)}")
    print(f"  {structural_ids[:5]}...")
    print(f"✓ Empirical IDs: {len(empirical_ids)}")
    print(f"  {empirical_ids[:5]}...")


def main():
    print("=" * 80)
    print("CORPUS LOADER TEST: JSON Evidence Files")
    print("=" * 80)

    test_load_structural()
    test_load_empirical()
    test_search()
    test_list_ids()

    print("\n" + "=" * 80)
    print("✅ CORPUS LOADER WORKING WITH JSON FILES")
    print("=" * 80)


if __name__ == "__main__":
    main()
