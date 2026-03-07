#!/usr/bin/env python3
"""Quick test to verify logging works"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import setup_logger
from utils.corpus_loader import load_all_corpus

def test_logging():
    """Test basic logging functionality"""
    logger = setup_logger("test", log_to_file=True)

    logger.info("Starting logging test")
    logger.info("Loading corpus...")

    structural = load_all_corpus("Credit Suisse", "structural")
    empirical = load_all_corpus("Credit Suisse", "empirical")

    logger.info(f"Loaded {len(structural)} structural observations")
    logger.info(f"Loaded {len(empirical)} empirical observations")
    logger.info("Test complete")

    print("\n✅ Logging test passed! Check backend/logs/ for log file.")

if __name__ == "__main__":
    test_logging()
