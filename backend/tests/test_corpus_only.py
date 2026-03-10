import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

#!/usr/bin/env python3
"""Quick test of corpus loading"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.corpus_loader import load_all_corpus


def test_corpus_loading():
    """Test that we can load evidence corpus"""
    print("\n" + "="*80)
    print("TEST: Corpus Loading")
    print("="*80)

    entity = "Credit Suisse"

    structural = load_all_corpus(entity, "structural")
    empirical = load_all_corpus(entity, "empirical")

    print(f"✅ Loaded {len(structural)} structural observations")
    print(f"✅ Loaded {len(empirical)} empirical observations")
    print(f"✅ Total: {len(structural) + len(empirical)} observations")

    if len(structural) > 0:
        print(f"\n   Sample structural: {structural[0]['observation_id']}")
    if len(empirical) > 0:
        print(f"   Sample empirical: {empirical[0]['observation_id']}")

    assert len(structural) > 0, "No structural observations found"
    assert len(empirical) > 0, "No empirical observations found"

    return True


if __name__ == "__main__":
    try:
        test_corpus_loading()
        print("\n✅ TEST PASSED")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
