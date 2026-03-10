"""
Central configuration for the hypothesis elimination engine.

Single source of truth for all settings - no hardcoded values elsewhere.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-3-pro-preview"  # Production reasoning model for hypothesis elimination (use gemini-2.5-flash for faster testing)
GEMINI_TEMPERATURE = 0.2  # Low temperature for reasoning consistency

# Investigation Lifecycle Limits
MAX_CYCLES = 8  # Maximum reasoning cycles before forced convergence (raised from 5 for evidence-driven convergence)
MAX_HYPOTHESES = 20  # Maximum hypotheses to track per investigation (raised from 10 for broader coverage)
CONVERGENCE_THRESHOLD = 2  # Converge when ≤2 hypotheses remain
STAGNATION_CYCLES = 2  # Force convergence if count unchanged for N cycles

# Corpus Paths (pre-curated evidence for hackathon demo)
BASE_DIR = Path(__file__).parent
CORPUS_STRUCTURAL_PATH = BASE_DIR / "corpus" / "structural"
CORPUS_EMPIRICAL_PATH = BASE_DIR / "corpus" / "empirical"
CACHED_FALLBACK_PATH = BASE_DIR / "corpus" / "cached" / "svb_full_run.json"

# Server-Sent Events (SSE) Configuration
SSE_HEARTBEAT_INTERVAL = 1.0  # seconds between heartbeat events

# Context Window Management
CONTEXT_WINDOW_SIZE = 1_000_000  # Gemini 2.0 Flash context window (1M tokens)
CONTEXT_ROT_THRESHOLD = 0.5  # Fresh window if utilization exceeds 50% (500K tokens)

# Tiering System Configuration
TIER2_CONFIDENCE_THRESHOLD = 0.7  # Promote to Tier 3 if confidence > 70%
TIER3_CYCLES = 2  # 1-2 quick cycles in Tier 3
TIER4_CYCLES = 5  # 4-5 deep cycles in Tier 4
