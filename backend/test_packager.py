#!/usr/bin/env python3
"""Test evidence packager with logging"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agents.evidence.packager import gather_evidence


async def test_packager():
    """Test packager with sample hypotheses"""
    print("Testing evidence packager...")

    evidence_requests = [
        {"type": "structural", "description": "Capital ratios"},
        {"type": "empirical", "description": "Market data"},
    ]

    hypotheses = [
        {"id": "H01", "name": "Test hypothesis 1", "score": 0.8},
        {"id": "H02", "name": "Test hypothesis 2", "score": 0.6},
    ]

    result = await gather_evidence(
        evidence_requests=evidence_requests,
        active_hypotheses=hypotheses,
        entity="Credit Suisse"
    )

    print(f"\n✅ Packager returned {len(result)} observations")
    print(f"✅ Check backend/logs/ for detailed log")

if __name__ == "__main__":
    asyncio.run(test_packager())
