# Phase 4: Evidence Pipeline

**Status:** Pending Phase 3 completion
**Duration:** ~1.5 hours
**Dependencies:** Phase 1 (models), Phase 2 (gemini client), Phase 3 (investigator)
**Build Order:** 4 of 7

---

## Context

Evidence gathering pipeline with 3 parallel retrieval agents + packager that tags all atoms against active hypotheses.

**Why This Phase:**
- Feeds the Investigator with tagged evidence for each cycle
- Three agents search in parallel (asyncio.gather) for speed
- Packager makes ONE Gemini call to tag all collected atoms
- Pre-curated corpus for hackathon (live APIs stretch goal)

**Key Architectural Decisions:**
- Three retrieval agents are INTERNAL to packager.py (not separate LangGraph nodes)
- Agents return raw evidence without tags
- Packager adds tags via single Gemini call
- Corpus loader searches pre-prepared local JSON files

---

## Files to Create

### 1. `backend/utils/corpus_loader.py`

**Purpose:** Load evidence from corpus/ JSON files

**Implementation:**

```python
import json
from pathlib import Path
from typing import Literal
import config

def load_corpus_file(atom_id: str, corpus_type: Literal["structural", "empirical"]) -> dict:
    """
    Load single corpus file by atom ID.

    Args:
        atom_id: e.g., "S01", "E03"
        corpus_type: "structural" or "empirical"

    Returns:
        dict with id, content, type, source, date
    """

    if corpus_type == "structural":
        base_path = config.CORPUS_STRUCTURAL_PATH
    else:
        base_path = config.CORPUS_EMPIRICAL_PATH

    file_path = base_path / f"{atom_id}.json"

    if not file_path.exists():
        raise FileNotFoundError(f"Corpus file not found: {file_path}")

    with open(file_path) as f:
        return json.load(f)

def search_corpus(
    query: str,
    corpus_type: Literal["structural", "empirical"],
    limit: int = 5
) -> list[dict]:
    """
    Search corpus files by keyword matching.

    Args:
        query: search terms from evidence request description
        corpus_type: "structural" or "empirical"
        limit: max results to return

    Returns:
        list of dicts with atom_id and content
    """

    if corpus_type == "structural":
        base_path = config.CORPUS_STRUCTURAL_PATH
    else:
        base_path = config.CORPUS_EMPIRICAL_PATH

    results = []
    query_lower = query.lower()
    query_terms = query_lower.split()

    # Search all JSON files in corpus directory
    for file_path in sorted(base_path.glob("*.json")):
        try:
            with open(file_path) as f:
                data = json.load(f)

            # Simple keyword matching
            content_lower = data["content"].lower()
            if any(term in content_lower for term in query_terms):
                results.append({
                    "atom_id": data["id"],
                    "content": data["content"],
                    "source": data.get("source", "Unknown"),
                    "type": data.get("type", corpus_type),
                    "date": data.get("date")
                })

            if len(results) >= limit:
                break
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Skipping malformed file {file_path}: {e}")
            continue

    return results

def list_all_corpus_files(corpus_type: Literal["structural", "empirical"]) -> list[str]:
    """
    List all corpus file IDs.

    Args:
        corpus_type: "structural" or "empirical"

    Returns:
        list of atom IDs
    """

    if corpus_type == "structural":
        base_path = config.CORPUS_STRUCTURAL_PATH
    else:
        base_path = config.CORPUS_EMPIRICAL_PATH

    return [f.stem for f in sorted(base_path.glob("*.json"))]
```

---

### 2. `backend/agents/evidence/structural_agent.py`

**Purpose:** Search corpus/structural/ for domain knowledge atoms

**Implementation:**

```python
from utils.corpus_loader import search_corpus

async def search_structural(evidence_requests: list[dict]) -> list[dict]:
    """
    Search structural knowledge corpus.

    Args:
        evidence_requests: list of dicts with type, description, reason

    Returns:
        list of raw observations (untagged)
    """

    structural_requests = [
        req for req in evidence_requests
        if req.get("type") == "structural"
    ]

    if not structural_requests:
        return []

    results = []

    for req in structural_requests:
        query = req["description"]
        atoms = search_corpus(query, corpus_type="structural", limit=3)

        for atom in atoms:
            results.append({
                "observation_id": atom["atom_id"],
                "content": atom["content"],
                "source": atom["source"],
                "type": "structural",
                "date": atom.get("date")
            })

    return results
```

**Reference:** component_guide.md lines 283-305

---

### 3. `backend/agents/evidence/market_agent.py`

**Purpose:** Search corpus/empirical/ for market data

**Implementation:**

```python
from utils.corpus_loader import search_corpus

async def search_market(evidence_requests: list[dict]) -> list[dict]:
    """
    Search market data corpus.

    Args:
        evidence_requests: list of dicts with type, description, reason

    Returns:
        list of raw observations (untagged)
    """

    market_requests = [
        req for req in evidence_requests
        if req.get("type") == "market"
    ]

    if not market_requests:
        return []

    results = []

    for req in market_requests:
        query = req["description"]
        atoms = search_corpus(query, corpus_type="empirical", limit=3)

        for atom in atoms:
            # Filter for market data type
            if atom.get("type") in ["market", "market_data"]:
                results.append({
                    "observation_id": atom["atom_id"],
                    "content": atom["content"],
                    "source": atom["source"],
                    "type": "market",
                    "date": atom.get("date")
                })

    return results
```

**Reference:** component_guide.md lines 307-322

---

### 4. `backend/agents/evidence/news_agent.py`

**Purpose:** Search corpus/empirical/ for news and filing excerpts

**Implementation:**

```python
from utils.corpus_loader import search_corpus

async def search_news(evidence_requests: list[dict]) -> list[dict]:
    """
    Search news and filing corpus.

    Args:
        evidence_requests: list of dicts with type, description, reason

    Returns:
        list of raw observations (untagged)
    """

    news_requests = [
        req for req in evidence_requests
        if req.get("type") in ["news", "filing"]
    ]

    if not news_requests:
        return []

    results = []

    for req in news_requests:
        query = req["description"]
        atoms = search_corpus(query, corpus_type="empirical", limit=3)

        for atom in atoms:
            # Filter for news/filing type
            if atom.get("type") in ["news", "filing"]:
                results.append({
                    "observation_id": atom["atom_id"],
                    "content": atom["content"],
                    "source": atom["source"],
                    "type": atom.get("type", "news"),
                    "date": atom.get("date")
                })

    return results
```

**Reference:** component_guide.md lines 324-340

---

### 5. `backend/gemini/prompts/evidence_tagging.py`

**Purpose:** Prompt for tagging evidence against hypotheses

**Implementation:**

```python
def build_evidence_tagging_prompt(
    raw_evidence: list[dict],
    active_hypotheses: list[dict]
) -> str:
    """
    Build prompt for Evidence Packager tagging step.

    Args:
        raw_evidence: Untagged observations from retrieval agents
        active_hypotheses: Current survivors with names and scores

    Returns:
        Prompt string for Gemini
    """

    evidence_text = "\n\n".join([
        f"## OBSERVATION {obs['observation_id']}\n"
        f"Type: {obs['type']}\n"
        f"Source: {obs['source']}\n"
        f"Content: {obs['content']}"
        for obs in raw_evidence
    ])

    hypotheses_text = "\n".join([
        f"- {h['id']}: {h['name']} (current score: {h['score']})"
        for h in active_hypotheses
    ])

    return f"""
You are tagging evidence observations against active hypotheses in a financial risk investigation.

# ACTIVE HYPOTHESES
{hypotheses_text}

# RAW EVIDENCE TO TAG
{evidence_text}

# YOUR TASK: TAG EACH OBSERVATION

For each observation, assess its relationship to EACH hypothesis:
- **supports**: observation provides evidence FOR the hypothesis
- **contradicts**: observation provides evidence AGAINST the hypothesis (disproves it)
- **neutral**: observation is irrelevant or ambiguous toward the hypothesis

Consider BOTH direct and indirect relationships. An observation may:
- Support multiple hypotheses
- Contradict multiple hypotheses
- Support some and contradict others

Be precise: an observation that CONTRADICTS a hypothesis is the basis for elimination.

# OUTPUT FORMAT (JSON):
{{
  "tagged_observations": [
    {{
      "observation_id": "S01",
      "content": "...",
      "source": "...",
      "type": "structural",
      "supports": ["H01", "H02"],
      "contradicts": ["H05", "H07"],
      "neutral": ["H03", "H04", "H06"],
      "date": "2023-03-10",
      "tagging_reasoning": "Brief explanation of tagging decisions"
    }},
    ...for all observations...
  ]
}}

Generate your response now.
"""
```

**Reference:** component_guide.md lines 455-470

---

### 6. `backend/agents/evidence/packager.py`

**Purpose:** Owns entire evidence retrieval + tagging pipeline

**Implementation:**

```python
import asyncio
from gemini.client import call_gemini
from gemini.prompts.evidence_tagging import build_evidence_tagging_prompt
from agents.evidence.structural_agent import search_structural
from agents.evidence.market_agent import search_market
from agents.evidence.news_agent import search_news

async def gather_evidence(
    evidence_requests: list[dict],
    active_hypotheses: list[dict]
) -> list[dict]:
    """
    Execute full evidence retrieval and tagging pipeline.

    INTERNAL to this function:
    - Dispatch 3 retrieval agents in parallel
    - Collect all raw results
    - Tag via ONE Gemini call
    - Return tagged observations

    Args:
        evidence_requests: list from investigator with type, description, reason
        active_hypotheses: current survivors (for tagging reference)

    Returns:
        list of tagged atomic observations following observation schema
    """

    # Dispatch all three agents in parallel
    structural_results, market_results, news_results = await asyncio.gather(
        search_structural(evidence_requests),
        search_market(evidence_requests),
        search_news(evidence_requests)
    )

    # Combine all raw evidence
    raw_evidence = structural_results + market_results + news_results

    if not raw_evidence:
        print("Warning: No evidence found for requests")
        return []

    # Tag all atoms in ONE Gemini call
    prompt = build_evidence_tagging_prompt(raw_evidence, active_hypotheses)
    result = await call_gemini(prompt)

    tagged_observations = result["response"]["tagged_observations"]

    return tagged_observations
```

**Reference:** component_guide.md lines 251-281

---

### 7. `backend/agents/evidence/__init__.py`

Empty init file:
```python
# Empty init file
```

---

## Verification Test

Create `backend/test_phase4.py`:

```python
#!/usr/bin/env python3
"""Phase 4 Verification: Test Evidence Pipeline"""

import asyncio
import json
from pathlib import Path
from agents.evidence.packager import gather_evidence
from utils.corpus_loader import search_corpus, list_all_corpus_files
import config

async def test_corpus_loader():
    print("Testing utils/corpus_loader.py...")

    # Test listing files
    structural_files = list_all_corpus_files("structural")
    empirical_files = list_all_corpus_files("empirical")

    print(f"✓ Found {len(structural_files)} structural corpus files")
    print(f"✓ Found {len(empirical_files)} empirical corpus files")

    # Test search
    results = search_corpus("HTM securities", corpus_type="structural", limit=3)
    assert len(results) > 0, "Expected search results for 'HTM securities'"
    print(f"✓ Search returned {len(results)} results for 'HTM securities'")

async def test_evidence_pipeline():
    print("\n\nTesting full evidence pipeline...")

    # Mock evidence requests from investigator
    evidence_requests = [
        {
            "type": "structural",
            "description": "HTM accounting treatment unrealized losses",
            "reason": "Confirm if losses were properly disclosed"
        },
        {
            "type": "market",
            "description": "SVB stock price CDS spreads March 2023",
            "reason": "Assess market perception of risk"
        },
        {
            "type": "news",
            "description": "SVB deposit outflows bank run",
            "reason": "Check for correlated deposit flight"
        }
    ]

    # Mock active hypotheses for tagging
    active_hypotheses = [
        {
            "id": "H01",
            "name": "Duration mismatch + rising rates",
            "description": "Bank has duration mismatch with HTM losses",
            "score": 0.85
        },
        {
            "id": "H02",
            "name": "Deposit concentration risk",
            "description": "Concentrated deposit base vulnerable to flight",
            "score": 0.80
        },
        {
            "id": "H05",
            "name": "Counterparty credit exposure",
            "description": "Exposure to failing counterparties",
            "score": 0.60
        }
    ]

    # Run evidence gathering
    tagged_observations = await gather_evidence(evidence_requests, active_hypotheses)

    # Verify results
    assert len(tagged_observations) > 0, "Expected tagged observations"

    print(f"✓ Gathered {len(tagged_observations)} tagged observations")

    # Verify each observation has required fields
    for obs in tagged_observations:
        assert "observation_id" in obs
        assert "content" in obs
        assert "source" in obs
        assert "type" in obs
        assert "supports" in obs
        assert "contradicts" in obs
        assert "neutral" in obs

        # Verify tags reference active hypotheses
        all_tags = obs["supports"] + obs["contradicts"] + obs["neutral"]
        for tag in all_tags:
            assert tag in ["H01", "H02", "H05"], f"Invalid hypothesis ID: {tag}"

    print(f"✓ All observations have required fields and valid tags")

    # Print sample
    print(f"\nSample tagged observation:")
    sample = tagged_observations[0]
    print(f"  ID: {sample['observation_id']}")
    print(f"  Type: {sample['type']}")
    print(f"  Supports: {sample['supports']}")
    print(f"  Contradicts: {sample['contradicts']}")

    return tagged_observations

async def main():
    print("=" * 60)
    print("Phase 4 Verification: Evidence Pipeline")
    print("=" * 60)

    await test_corpus_loader()
    tagged_obs = await test_evidence_pipeline()

    print("\n" + "=" * 60)
    print("✅ EVIDENCE PIPELINE VALIDATED - Phase 4 Complete!")
    print("=" * 60)
    print("\nVerified:")
    print("  ✓ Corpus loader searches local files")
    print("  ✓ Three retrieval agents run in parallel")
    print(f"  ✓ Packager tags {len(tagged_obs)} observations via single Gemini call")
    print("  ✓ All observations have supports/contradicts/neutral tags")
    print("  ✓ Tags reference active hypothesis IDs")
    print("\nReady to proceed to Phase 5: Orchestrator")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Setup Corpus Files

Before running verification, create sample corpus files:

```bash
mkdir -p backend/corpus/structural backend/corpus/empirical backend/corpus/cached
```

**backend/corpus/structural/S01.json:**
```json
{
  "id": "S01",
  "content": "HTM (held-to-maturity) securities under GAAP do not require marking unrealized losses on the balance sheet. Banks can carry HTM securities at amortized cost even when market value has declined significantly due to rising interest rates.",
  "source": "GAAP Accounting Standards",
  "type": "structural",
  "date": "2023-01-01"
}
```

**backend/corpus/empirical/E01.json:**
```json
{
  "id": "E01",
  "content": "SVB stock price fell from $267 to $106 (-60%) on March 9, 2023. CDS spreads spiked to 450bps. Trading was halted multiple times.",
  "source": "Bloomberg Terminal",
  "type": "market",
  "date": "2023-03-09"
}
```

---

## Running Verification

```bash
cd backend
python test_phase4.py
```

**Expected Output:**
```
============================================================
Phase 4 Verification: Evidence Pipeline
============================================================
Testing utils/corpus_loader.py...
✓ Found 5 structural corpus files
✓ Found 8 empirical corpus files
✓ Search returned 2 results for 'HTM securities'

Testing full evidence pipeline...
✓ Gathered 6 tagged observations
✓ All observations have required fields and valid tags

Sample tagged observation:
  ID: S01
  Type: structural
  Supports: ['H01']
  Contradicts: ['H05']

============================================================
✅ EVIDENCE PIPELINE VALIDATED - Phase 4 Complete!
============================================================

Verified:
  ✓ Corpus loader searches local files
  ✓ Three retrieval agents run in parallel
  ✓ Packager tags 6 observations via single Gemini call
  ✓ All observations have supports/contradicts/neutral tags
  ✓ Tags reference active hypothesis IDs

Ready to proceed to Phase 5: Orchestrator
```

---

## Success Criteria

- [ ] Corpus loader searches local JSON files
- [ ] Three agents dispatch in parallel (asyncio.gather)
- [ ] All agents return raw untagged evidence
- [ ] Packager makes ONE Gemini call to tag all atoms
- [ ] Tagged observations have supports/contradicts/neutral lists
- [ ] Tags reference active hypothesis IDs
- [ ] No import errors

---

## Next Steps

After Phase 4 verification passes:
✅ Evidence pipeline operational
✅ Can feed Investigator with tagged evidence each cycle
✅ Ready for Phase 5: Orchestrator (lifecycle management)

**STOP HERE and verify before proceeding to Phase 5.**
