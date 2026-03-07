# Phase 2: Gemini Client + Config + Utils

**Status:** Pending Phase 1 completion
**Duration:** ~45 minutes
**Dependencies:** Phase 1 (models)
**Build Order:** 2 of 7

---

## Context

Central configuration, Gemini API wrapper with retry/fallback, and utility functions for parsing and token tracking.

**Why This Phase:**
- Gemini client used by Investigator, Orchestrator, and Evidence Packager
- Config centralizes all settings (no hardcoded values)
- Parser extracts self-compressed state (no separate Gemini call needed)
- Token counter tracks usage for budget management

**What's NOT in This Phase:**
- No agent implementations yet
- No LangGraph
- No prompts (those come with each agent)

---

## Files to Create

### 1. `backend/config.py`

**Purpose:** Single source of truth for all configuration

**Implementation:**
```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash-exp"
GEMINI_TEMPERATURE = 0.2

# Investigation limits
MAX_CYCLES = 5
MAX_HYPOTHESES = 10
CONVERGENCE_THRESHOLD = 2  # Converge when ≤2 hypotheses remain
STAGNATION_CYCLES = 2  # Force convergence if count unchanged for N cycles

# Paths
BASE_DIR = Path(__file__).parent
CORPUS_STRUCTURAL_PATH = BASE_DIR / "corpus" / "structural"
CORPUS_EMPIRICAL_PATH = BASE_DIR / "corpus" / "empirical"
CACHED_FALLBACK_PATH = BASE_DIR / "corpus" / "cached" / "svb_full_run.json"

# SSE streaming
SSE_HEARTBEAT_INTERVAL = 1.0  # seconds

# Context window limits
CONTEXT_WINDOW_SIZE = 1_000_000  # Gemini 2.0 Flash context window
CONTEXT_ROT_THRESHOLD = 0.5  # Fresh window if utilization exceeds 50%
```

**Reference:** component_guide.md lines 498-517

---

### 2. `backend/gemini/client.py`

**Purpose:** Gemini API wrapper with retry logic, fallback, and token tracking

**Key Features:**
- JSON response format enforcement
- 3 retry attempts with exponential backoff
- Token usage tracking (input + output)
- Fallback to cached JSON on failure

**Implementation:**
```python
import json
import time
from typing import Any
import google.generativeai as genai
from pathlib import Path

import config

# Configure Gemini
genai.configure(api_key=config.GEMINI_API_KEY)

class GeminiClient:
    """Wrapper for all Gemini API calls with retry and fallback"""

    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name=config.GEMINI_MODEL,
            generation_config={
                "temperature": config.GEMINI_TEMPERATURE,
                "response_mime_type": "application/json"
            }
        )

    async def call(
        self,
        prompt: str,
        schema: dict | None = None,
        fallback_path: str | None = None,
        max_retries: int = 3
    ) -> dict:
        """
        Make Gemini API call with retry logic and fallback.

        Args:
            prompt: The prompt to send
            schema: Optional JSON schema for validation
            fallback_path: Path to cached JSON if API fails
            max_retries: Number of retry attempts

        Returns:
            {
                "response": <parsed JSON response>,
                "token_usage": {
                    "input_tokens": int,
                    "output_tokens": int,
                    "total_tokens": int
                }
            }
        """

        for attempt in range(max_retries):
            try:
                response = await self.model.generate_content_async(prompt)

                # Parse JSON response
                try:
                    parsed = json.loads(response.text)
                except json.JSONDecodeError:
                    # Try to extract JSON from markdown code blocks
                    text = response.text
                    if "```json" in text:
                        text = text.split("```json")[1].split("```")[0].strip()
                    elif "```" in text:
                        text = text.split("```")[1].split("```")[0].strip()
                    parsed = json.loads(text)

                # Validate against schema if provided
                if schema:
                    self._validate_schema(parsed, schema)

                # Extract token usage
                token_usage = {
                    "input_tokens": response.usage_metadata.prompt_token_count,
                    "output_tokens": response.usage_metadata.candidates_token_count,
                    "total_tokens": response.usage_metadata.total_token_count
                }

                return {
                    "response": parsed,
                    "token_usage": token_usage
                }

            except Exception as e:
                print(f"Gemini API attempt {attempt + 1} failed: {e}")

                if attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    # All retries failed, try fallback
                    if fallback_path:
                        print(f"All retries failed, using fallback: {fallback_path}")
                        return self._load_fallback(fallback_path)
                    else:
                        raise Exception(f"Gemini API failed after {max_retries} attempts: {e}")

    def _validate_schema(self, data: dict, schema: dict):
        """Basic schema validation (can be expanded)"""
        # TODO: Implement proper JSON schema validation if needed
        pass

    def _load_fallback(self, fallback_path: str) -> dict:
        """Load pre-cached response from file"""
        with open(fallback_path, 'r') as f:
            cached = json.load(f)

        return {
            "response": cached,
            "token_usage": {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0
            },
            "from_cache": True
        }

# Singleton instance
_client = None

def get_client() -> GeminiClient:
    """Get or create GeminiClient singleton"""
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client

async def call_gemini(
    prompt: str,
    schema: dict | None = None,
    fallback_path: str | None = None
) -> dict:
    """Convenience function for making Gemini calls"""
    client = get_client()
    return await client.call(prompt, schema, fallback_path)
```

**Reference:** component_guide.md lines 383-405

---

### 3. `backend/gemini/__init__.py`

Empty init file:
```python
# Empty init file
```

---

### 4. `backend/utils/parser.py`

**Purpose:** Parse Investigator's self-compressed state (pure string parsing, no Gemini call)

**Implementation:**
```python
import json
import re

def parse_compressed_state(output: str) -> str | None:
    """
    Extract self-compressed state from investigator output.

    Investigator outputs compressed state between delimiters:
    === COMPRESSED STATE ===
    { ... json ... }
    === END COMPRESSED STATE ===

    Args:
        output: Full investigator output text

    Returns:
        Extracted compressed state string, or None if not found
    """

    # Look for delimited section
    pattern = r"===\s*COMPRESSED STATE\s*===(.*?)===\s*END COMPRESSED STATE\s*==="
    match = re.search(pattern, output, re.DOTALL | re.IGNORECASE)

    if match:
        compressed = match.group(1).strip()
        return compressed

    return None

def parse_investigation_output(output: dict) -> dict:
    """
    Parse full investigation output into structured components.

    Args:
        output: Dict with investigation results

    Returns:
        {
            "surviving_hypotheses": [...],
            "eliminated_hypotheses": [...],
            "cross_modal_flags": [...],
            "evidence_requests": [...],
            "key_insights": [...],
            "compressed_state": str
        }
    """

    return {
        "surviving_hypotheses": output.get("surviving_hypotheses", []),
        "eliminated_hypotheses": output.get("eliminated_hypotheses", []),
        "cross_modal_flags": output.get("cross_modal_flags", []),
        "evidence_requests": output.get("evidence_requests", []),
        "key_insights": output.get("key_insights", []),
        "compressed_state": output.get("compressed_state", None)
    }

def extract_json_from_markdown(text: str) -> dict:
    """
    Extract JSON from markdown code blocks if Gemini returns it that way.

    Args:
        text: Text potentially containing ```json ... ``` blocks

    Returns:
        Parsed JSON dict
    """

    # Try direct JSON parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code block
    if "```json" in text:
        json_text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        json_text = text.split("```")[1].split("```")[0].strip()
    else:
        json_text = text

    return json.loads(json_text)
```

**Reference:** component_guide.md lines 569-584

---

### 5. `backend/utils/token_counter.py`

**Purpose:** Track token usage across all Gemini calls per agent per cycle

**Implementation:**
```python
def track_token_usage(
    agent: str,
    cycle: int,
    input_tokens: int,
    output_tokens: int,
    current_usage: dict
) -> dict:
    """
    Aggregate token usage per agent per cycle.

    Args:
        agent: Agent name (e.g., "investigator", "orchestrator", "packager")
        cycle: Current cycle number
        input_tokens: Input tokens for this call
        output_tokens: Output tokens for this call
        current_usage: Existing usage dict to update

    Returns:
        Updated usage dict with structure:
        {
            "per_cycle": {
                "cycle_1": {
                    "investigator": {"input": N, "output": M},
                    "packager": {"input": X, "output": Y}
                },
                ...
            },
            "total": {"input": N, "output": M, "reasoning": X}
        }
    """

    if "per_cycle" not in current_usage:
        current_usage["per_cycle"] = {}

    cycle_key = f"cycle_{cycle}"
    if cycle_key not in current_usage["per_cycle"]:
        current_usage["per_cycle"][cycle_key] = {}

    if agent not in current_usage["per_cycle"][cycle_key]:
        current_usage["per_cycle"][cycle_key][agent] = {
            "input": 0,
            "output": 0
        }

    # Update per-cycle per-agent tracking
    current_usage["per_cycle"][cycle_key][agent]["input"] += input_tokens
    current_usage["per_cycle"][cycle_key][agent]["output"] += output_tokens

    # Update running totals
    if "total" not in current_usage:
        current_usage["total"] = {"input": 0, "output": 0, "reasoning": 0}

    current_usage["total"]["input"] += input_tokens
    current_usage["total"]["output"] += output_tokens

    # Reasoning tokens = output tokens (approximate)
    if agent == "investigator":
        current_usage["total"]["reasoning"] += output_tokens

    return current_usage

def estimate_context_utilization(
    input_tokens: int,
    max_context: int = 1_000_000
) -> float:
    """
    Estimate percentage of context window used.

    Args:
        input_tokens: Tokens in input
        max_context: Maximum context window size

    Returns:
        Utilization as percentage (0.0-100.0)
    """
    return (input_tokens / max_context) * 100

def get_cycle_summary(usage_dict: dict, cycle: int) -> dict:
    """
    Get token usage summary for a specific cycle.

    Args:
        usage_dict: Full usage tracking dict
        cycle: Cycle number

    Returns:
        {
            "cycle": int,
            "total_input": int,
            "total_output": int,
            "by_agent": {...}
        }
    """

    cycle_key = f"cycle_{cycle}"
    if cycle_key not in usage_dict.get("per_cycle", {}):
        return {
            "cycle": cycle,
            "total_input": 0,
            "total_output": 0,
            "by_agent": {}
        }

    cycle_data = usage_dict["per_cycle"][cycle_key]

    total_input = sum(agent["input"] for agent in cycle_data.values())
    total_output = sum(agent["output"] for agent in cycle_data.values())

    return {
        "cycle": cycle,
        "total_input": total_input,
        "total_output": total_output,
        "by_agent": cycle_data
    }
```

**Reference:** component_guide.md lines 548-566

---

### 6. `backend/utils/__init__.py`

Empty init file:
```python
# Empty init file
```

---

## Verification Test

Create `backend/test_phase2.py`:

```python
#!/usr/bin/env python3
"""Phase 2 Verification: Test Gemini client, config, and utils"""

import asyncio
import json
from gemini.client import call_gemini, get_client
from utils.parser import parse_compressed_state, parse_investigation_output, extract_json_from_markdown
from utils.token_counter import track_token_usage, estimate_context_utilization, get_cycle_summary
import config

async def test_config():
    print("Testing config.py...")
    assert config.GEMINI_API_KEY is not None, "GEMINI_API_KEY not set"
    assert config.GEMINI_MODEL == "gemini-2.0-flash-exp"
    assert config.GEMINI_TEMPERATURE == 0.2
    assert config.MAX_CYCLES == 5
    print(f"✓ Config loaded: model={config.GEMINI_MODEL}, temp={config.GEMINI_TEMPERATURE}")
    print(f"✓ Paths configured: {config.CORPUS_STRUCTURAL_PATH.exists()=}")

async def test_gemini_client():
    print("\nTesting gemini/client.py...")

    # Simple test prompt
    prompt = """
    Generate a JSON response with 3 competing hypotheses about why a bank's CDS spreads might spike.
    Return in this format:
    {
        "hypotheses": [
            {"id": "H01", "name": "...", "description": "..."},
            {"id": "H02", "name": "...", "description": "..."},
            {"id": "H03", "name": "...", "description": "..."}
        ]
    }
    """

    result = await call_gemini(prompt)

    assert "response" in result
    assert "token_usage" in result
    assert "hypotheses" in result["response"]
    assert len(result["response"]["hypotheses"]) == 3

    print(f"✓ Gemini call successful")
    print(f"✓ Token usage: {result['token_usage']['input_tokens']} in, {result['token_usage']['output_tokens']} out")
    print(f"✓ Generated {len(result['response']['hypotheses'])} hypotheses")

    return result

def test_parser():
    print("\nTesting utils/parser.py...")

    # Test compressed state extraction
    test_output = """
    Some reasoning here about the hypotheses...

    Based on the evidence, I eliminate H03 and H05.

    === COMPRESSED STATE ===
    {
        "surviving": ["H01", "H02", "H04"],
        "eliminated": [
            {"id": "H03", "killed_by": "S01", "reason": "contradicted by evidence"},
            {"id": "H05", "killed_by": "E02", "reason": "empirical data shows otherwise"}
        ],
        "crux": "Need market data to discriminate between H01 and H02"
    }
    === END COMPRESSED STATE ===

    More text after...
    """

    compressed = parse_compressed_state(test_output)
    assert compressed is not None
    assert "surviving" in compressed

    parsed = json.loads(compressed)
    assert len(parsed["surviving"]) == 3
    assert len(parsed["eliminated"]) == 2

    print(f"✓ Parser extracted compressed state successfully")
    print(f"✓ Compressed state: {len(parsed['surviving'])} surviving, {len(parsed['eliminated'])} eliminated")

    # Test JSON extraction from markdown
    markdown_text = """
    ```json
    {"test": "value", "number": 42}
    ```
    """
    extracted = extract_json_from_markdown(markdown_text)
    assert extracted["test"] == "value"
    assert extracted["number"] == 42
    print(f"✓ JSON extraction from markdown works")

def test_token_counter():
    print("\nTesting utils/token_counter.py...")

    usage = {}

    # Simulate cycle 1
    usage = track_token_usage("investigator", 1, 50000, 30000, usage)
    usage = track_token_usage("packager", 1, 10000, 5000, usage)

    # Simulate cycle 2
    usage = track_token_usage("investigator", 2, 60000, 35000, usage)
    usage = track_token_usage("packager", 2, 12000, 6000, usage)

    assert usage["total"]["input"] == 132000
    assert usage["total"]["output"] == 76000

    print(f"✓ Token tracking: {usage['total']['input']} total input tokens")
    print(f"✓ Token tracking: {usage['total']['output']} total output tokens")

    # Test cycle summary
    cycle1_summary = get_cycle_summary(usage, 1)
    assert cycle1_summary["total_input"] == 60000
    assert cycle1_summary["total_output"] == 35000
    print(f"✓ Cycle 1 summary: {cycle1_summary['total_input']} in, {cycle1_summary['total_output']} out")

    # Test context utilization
    utilization = estimate_context_utilization(50000, 1_000_000)
    assert utilization == 5.0
    print(f"✓ Context utilization calculation: 50K tokens = {utilization}%")

async def main():
    print("=" * 60)
    print("Phase 2 Verification: Gemini Client + Config + Utils")
    print("=" * 60)

    await test_config()
    await test_gemini_client()
    test_parser()
    test_token_counter()

    print("\n" + "=" * 60)
    print("✅ ALL COMPONENTS VALIDATED - Phase 2 Complete!")
    print("=" * 60)
    print("\nVerified:")
    print("  ✓ config.py loads all settings")
    print("  ✓ gemini/client.py makes API calls with retry")
    print("  ✓ utils/parser.py extracts compressed state")
    print("  ✓ utils/token_counter.py tracks usage per agent per cycle")
    print("\nReady to proceed to Phase 3: Investigator (CRITICAL PATH)")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Running Verification

```bash
# Set API key
export GEMINI_API_KEY="your-api-key-here"

# Run test
cd backend
python test_phase2.py
```

**Expected Output:**
```
============================================================
Phase 2 Verification: Gemini Client + Config + Utils
============================================================
Testing config.py...
✓ Config loaded: model=gemini-2.0-flash-exp, temp=0.2
✓ Paths configured: config.CORPUS_STRUCTURAL_PATH.exists()=True

Testing gemini/client.py...
✓ Gemini call successful
✓ Token usage: 245 in, 187 out
✓ Generated 3 hypotheses

Testing utils/parser.py...
✓ Parser extracted compressed state successfully
✓ Compressed state: 3 surviving, 2 eliminated
✓ JSON extraction from markdown works

Testing utils/token_counter.py...
✓ Token tracking: 132000 total input tokens
✓ Token tracking: 76000 total output tokens
✓ Cycle 1 summary: 60000 in, 35000 out
✓ Context utilization calculation: 50K tokens = 5.0%

============================================================
✅ ALL COMPONENTS VALIDATED - Phase 2 Complete!
============================================================

Verified:
  ✓ config.py loads all settings
  ✓ gemini/client.py makes API calls with retry
  ✓ utils/parser.py extracts compressed state
  ✓ utils/token_counter.py tracks usage per agent per cycle

Ready to proceed to Phase 3: Investigator (CRITICAL PATH)
```

---

## Success Criteria

- [ ] Config loads from environment variables
- [ ] Gemini client makes successful API calls
- [ ] Retry logic works (test by simulating failure)
- [ ] Token usage tracked correctly
- [ ] Parser extracts delimited compressed state
- [ ] JSON extraction from markdown works
- [ ] No import errors
- [ ] Test script runs without exceptions

---

## Dependencies for Next Phases

Phase 2 provides:
- ✅ `call_gemini()` - Used by Investigator, Orchestrator, Evidence Packager
- ✅ `config.MAX_CYCLES` - Used by Orchestrator convergence logic
- ✅ `parse_compressed_state()` - Used by Orchestrator to extract investigator output
- ✅ `track_token_usage()` - Used by all agents for budget tracking

---

## Next Steps

After Phase 2 verification passes:
✅ Gemini integration ready
✅ Token tracking infrastructure in place
✅ Config centralized
✅ Ready for Phase 3: Investigator (CRITICAL PATH)

**STOP HERE and verify before proceeding to Phase 3.**
