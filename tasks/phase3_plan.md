# Phase 3: Investigator (CRITICAL PATH)

**Status:** Pending Phase 2 completion
**Duration:** ~2 hours
**Dependencies:** Phase 1 (models), Phase 2 (gemini client, parser)
**Build Order:** 3 of 7

---

## Context

**⭐ MOST IMPORTANT COMPONENT IN THE SYSTEM ⭐**

The Investigator is the core reasoning engine. It runs hypothesis elimination through iterative cycles, filling the 1M context window with thinking, not data. This component IS the product—everything else is infrastructure to support it.

**Why This Phase is Critical:**
- Demonstrates the value prop: iterative reasoning > single-pass analysis
- Implements the full investigation cycle: GENERATE → SCORE → ELIMINATE → REQUEST → SELF-COMPRESS
- Self-compression architecture saves ~200K input tokens per cycle (prd.md FR-6)
- Fresh context window per cycle prevents context rot (prd.md TR-3)

**Key Architectural Decisions (DO NOT VIOLATE):**
- Investigator is STATELESS - doesn't know about case files, cycles, tiers
- Fresh context window per cycle - discarded after each run
- Self-compresses at end of each cycle - no separate compression call
- Does NOT remember previous cycles - only knows what compressed state tells it
- Orchestrator assembles context, Investigator reasons, Orchestrator parses output

---

## Files to Create

### 1. `backend/gemini/prompts/investigation.py`

**Purpose:** THE MOST CRITICAL PROMPT IN THE ENTIRE SYSTEM

This prompt defines the full investigation cycle and directly determines system quality.

**Implementation:**

```python
def build_investigation_prompt(
    cycle_num: int,
    trigger: str,
    entity: str,
    compressed_state: str | None,
    evidence: list[dict],
    active_hypotheses: list[dict]
) -> str:
    """
    Build investigation cycle prompt.

    Cycle 1: Generate initial hypotheses
    Cycle 2+: Score, eliminate, request evidence, self-compress

    Args:
        cycle_num: Current cycle number (1-indexed)
        trigger: Initial trigger signal
        entity: Entity being investigated
        compressed_state: Self-compressed state from previous cycle
        evidence: List of tagged evidence observations
        active_hypotheses: Currently surviving hypotheses

    Returns:
        Complete prompt string
    """

    if cycle_num == 1:
        # CYCLE 1: Generate initial hypotheses
        return f"""
You are a financial risk investigator analyzing a trigger signal for {entity}.

# TRIGGER SIGNAL
{trigger}

# YOUR TASK - CYCLE 1: HYPOTHESIS GENERATION

Generate 8-10 competing hypotheses that could explain this trigger signal.

## Requirements:
1. Cover diverse causal categories:
   - Structural risk (capital, liquidity, duration mismatch, concentration)
   - Market risk (rates, FX, equity, credit spreads)
   - Counterparty risk (exposure to failing entities)
   - Operational risk (fraud, systems failure, key person)
   - Regulatory/legal risk (violations, investigations)
   - Reputational risk (social media, news)
   - Contagion/systemic risk (correlated exposures)

2. Each hypothesis must be:
   - Specific and testable against evidence
   - Falsifiable (possible to eliminate with contradicting evidence)
   - Assigned initial confidence score 0.0-1.0 based on trigger signal

3. DO NOT:
   - Generate vague hypotheses like "general market stress"
   - Overlap significantly between hypotheses
   - Assume evidence you don't have

## OUTPUT FORMAT (JSON):
{{
  "reasoning_trace": "Your detailed reasoning process...",
  "surviving_hypotheses": [
    {{
      "id": "H01",
      "name": "Short descriptive name",
      "description": "Detailed explanation of the hypothesis",
      "score": 0.75,
      "evidence_chain": [],
      "status": "active",
      "reasoning": "Why this hypothesis is plausible given the trigger"
    }},
    ...8-10 hypotheses...
  ],
  "eliminated_hypotheses": [],
  "cross_modal_flags": [],
  "evidence_requests": [
    {{
      "type": "structural",
      "description": "Specific evidence needed",
      "reason": "How it would discriminate hypotheses"
    }},
    {{
      "type": "market",
      "description": "Specific data needed",
      "reason": "How it would discriminate hypotheses"
    }},
    ...3-5 requests...
  ],
  "key_insights": [
    "Important finding 1",
    "Important finding 2"
  ],
  "compressed_state": "INITIAL STATE: Generated {{N}} hypotheses for {entity}. Trigger: {trigger}. Need evidence to begin elimination. Priority: {{list top 3 hypotheses}} because {{reasoning}}."
}}

Generate your response now.
"""

    else:
        # CYCLE 2+: Score, eliminate, request evidence, self-compress
        evidence_text = "\n\n".join([
            f"## OBSERVATION {obs['observation_id']}\n"
            f"Type: {obs['type']}\n"
            f"Source: {obs['source']}\n"
            f"Content: {obs['content']}\n"
            f"Supports: {obs.get('supports', [])}\n"
            f"Contradicts: {obs.get('contradicts', [])}\n"
            f"Neutral: {obs.get('neutral', [])}"
            for obs in evidence
        ])

        hypotheses_text = "\n".join([
            f"- {h['id']}: {h['name']} (score: {h['score']}) - {h['description']}"
            for h in active_hypotheses
        ])

        return f"""
You are a financial risk investigator in Cycle {cycle_num} of investigation for {entity}.

# PREVIOUS STATE (COMPRESSED)
{compressed_state if compressed_state else "No previous state"}

# ACTIVE HYPOTHESES
{hypotheses_text}

# EVIDENCE COLLECTED
{evidence_text}

# YOUR TASK - CYCLE {cycle_num}: HYPOTHESIS ELIMINATION

Execute the full investigation cycle:

## PHASE 1: SCORE
- Evaluate EVERY active hypothesis against EVERY evidence observation
- For each hypothesis-observation pair, assess: supports/contradicts/neutral
- Update confidence scores based on evidence
- CITE SPECIFIC OBSERVATION IDs in your reasoning

## PHASE 2: ELIMINATE
- Kill any hypothesis where evidence DIRECTLY CONTRADICTS it
- Each elimination MUST cite:
  - Exact observation ID that killed it
  - One-line reason explaining the contradiction
- DO NOT eliminate hypotheses just because they have low scores
- ONLY eliminate when evidence proves them IMPOSSIBLE

## PHASE 3: CROSS-MODAL CHECK
- Compare structural observations (banking rules, accounting standards) against empirical observations (market data, news)
- Flag any contradictions where structural knowledge conflicts with empirical evidence
- These contradictions are HIGH PRIORITY - they reveal hidden risks

## PHASE 4: REQUEST EVIDENCE
- Based on surviving hypotheses, identify what SPECIFIC evidence would discriminate between them
- Request 3-5 pieces of evidence with:
  - Type: structural/market/news/filing
  - Description: EXACTLY what you need (not vague requests)
  - Reason: How it would help eliminate or confirm hypotheses

## PHASE 5: SELF-COMPRESS
- Produce cumulative compressed state incorporating ALL prior cycles
- PRESERVE: surviving hypotheses with scores, eliminated hypotheses with kill atoms, cross-modal flags, evidence needed, crux question
- DISCARD: verbose reasoning, redundant evidence descriptions, obvious conclusions
- Target size: ~20-30K tokens (cycle 1) ramping to ~75-100K tokens (cycle 4+)

## OUTPUT FORMAT (JSON):
{{
  "reasoning_trace": "Your detailed reasoning for this cycle...",
  "surviving_hypotheses": [
    {{
      "id": "H01",
      "name": "...",
      "description": "...",
      "score": 0.85,
      "evidence_chain": ["S01", "E03", ...],
      "status": "active",
      "reasoning": "Why this still survives after this cycle's evidence"
    }},
    ...
  ],
  "eliminated_hypotheses": [
    {{
      "id": "H05",
      "name": "...",
      "killed_by_atom": "S01",
      "killed_in_cycle": {cycle_num},
      "reason": "S01 shows HTM losses, not counterparty exposure"
    }},
    ...
  ],
  "cross_modal_flags": [
    {{
      "structural_atom_id": "S02",
      "empirical_atom_id": "E05",
      "detected_in_cycle": {cycle_num},
      "contradiction_description": "S02 states regulatory capital adequate, but E05 shows unrealized losses not marked"
    }},
    ...
  ],
  "evidence_requests": [
    {{
      "type": "structural",
      "description": "HTM accounting treatment for unrealized losses",
      "reason": "Would confirm if losses were properly disclosed"
    }},
    ...
  ],
  "key_insights": [
    "New important findings from this cycle"
  ],
  "compressed_state": "CYCLE {cycle_num} STATE: {{surviving_count}} hypotheses remain. Eliminated {{eliminated_count}} this cycle. Key finding: {{insight}}. Crux question: {{what discriminates survivors}}. Evidence needed: {{priority requests}}. Historical context: {{brief summary of all prior eliminations and key evidence}}."
}}

CRITICAL REQUIREMENTS:
- EVERY elimination cites a SPECIFIC observation ID
- Cross-modal contradictions are FLAGGED explicitly
- Compressed state is CUMULATIVE (incorporates all prior cycles)
- Evidence requests are SPECIFIC (not vague)

Generate your response now.
"""


def build_hypothesis_generation_instruction() -> str:
    """Instruction for generating diverse initial hypotheses"""
    return """
Generate hypotheses across ALL causal categories:

1. **Structural Risk**
   - Capital adequacy, leverage, liquidity coverage
   - Duration mismatch (asset/liability mismatch)
   - Concentration risk (sector, geography, counterparty)
   - Balance sheet composition (HTM securities, loan book)

2. **Market Risk**
   - Interest rate exposure (rising rates, inverted curve)
   - Credit spread widening
   - Equity market exposure
   - FX exposure

3. **Counterparty Risk**
   - Exposure to failing entities
   - Contagion from correlated defaults
   - Derivative counterparty risk

4. **Operational Risk**
   - Fraud, embezzlement
   - Systems failure, cyber attack
   - Key person risk (CEO departure, scandal)

5. **Regulatory/Legal Risk**
   - Violations, investigations, fines
   - Regulatory capital changes
   - Legal judgments, class actions

6. **Reputational Risk**
   - Social media runs
   - News coverage driving deposit flight
   - Loss of confidence

7. **Contagion/Systemic Risk**
   - Correlated exposures across institutions
   - Network effects, interconnectedness
   - Sector-wide stress

Generate 8-10 hypotheses covering diverse categories. Avoid duplicates.
"""
```

**Reference:** component_guide.md lines 423-452, prd.md FR-6

---

### 2. `backend/agents/investigator.py`

**Purpose:** Stateless reasoning engine with fresh context window per cycle

**Implementation:**

```python
import asyncio
from gemini.client import call_gemini
from gemini.prompts.investigation import build_investigation_prompt
from utils.parser import parse_investigation_output
import config

async def investigate(context: dict) -> dict:
    """
    Run one complete investigation cycle.

    Stateless function - context window discarded after each call.
    Does NOT know about case files, cycles, tiers, or persistence.

    Args:
        context: {
            "trigger": str,
            "entity": str,
            "cycle_num": int,
            "compressed_state": str | None,
            "evidence": list[dict],  # Tagged observations
            "active_hypotheses": list[dict]
        }

    Returns:
        {
            "reasoning_trace": str,
            "surviving_hypotheses": list[dict],
            "eliminated_hypotheses": list[dict],
            "cross_modal_flags": list[dict],
            "evidence_requests": list[dict],
            "compressed_state": str,
            "key_insights": list[str],
            "token_usage": dict
        }
    """

    # Build prompt
    prompt = build_investigation_prompt(
        cycle_num=context["cycle_num"],
        trigger=context["trigger"],
        entity=context["entity"],
        compressed_state=context.get("compressed_state"),
        evidence=context.get("evidence", []),
        active_hypotheses=context.get("active_hypotheses", [])
    )

    # Call Gemini
    result = await call_gemini(
        prompt=prompt,
        fallback_path=str(config.CACHED_FALLBACK_PATH) if context["cycle_num"] == 1 else None
    )

    # Parse response
    investigation_output = result["response"]
    token_usage = result["token_usage"]

    # Add token usage to output
    investigation_output["token_usage"] = token_usage

    return investigation_output
```

**Reference:** component_guide.md lines 191-249

---

### 3. `backend/agents/__init__.py`

Empty init file:
```python
# Empty init file
```

---

## Verification Test

Create `backend/test_phase3.py`:

```python
#!/usr/bin/env python3
"""Phase 3 Verification: Test Investigator"""

import asyncio
from agents.investigator import investigate

async def test_cycle1_generation():
    print("Testing Cycle 1: Hypothesis Generation...")

    context = {
        "trigger": "SVB CDS spreads spiked to 450bps on March 8, 2023. Stock price fell 60%. Deposit outflows accelerated.",
        "entity": "SVB",
        "cycle_num": 1,
        "compressed_state": None,
        "evidence": [],
        "active_hypotheses": []
    }

    result = await investigate(context)

    # Verify structure
    assert "surviving_hypotheses" in result
    assert "eliminated_hypotheses" in result
    assert "evidence_requests" in result
    assert "compressed_state" in result
    assert "token_usage" in result

    # Verify hypothesis generation
    hypotheses = result["surviving_hypotheses"]
    assert len(hypotheses) >= 8, f"Expected ≥8 hypotheses, got {len(hypotheses)}"
    assert len(hypotheses) <= 10, f"Expected ≤10 hypotheses, got {len(hypotheses)}"

    # Verify each hypothesis has required fields
    for h in hypotheses:
        assert "id" in h
        assert "name" in h
        assert "description" in h
        assert "score" in h
        assert 0.0 <= h["score"] <= 1.0

    print(f"✓ Generated {len(hypotheses)} hypotheses")
    print(f"✓ Token usage: {result['token_usage']['input_tokens']} in, {result['token_usage']['output_tokens']} out")

    # Print sample hypotheses
    print(f"\nSample hypotheses:")
    for h in hypotheses[:3]:
        print(f"  {h['id']}: {h['name']} (score: {h['score']})")

    return result

async def test_cycle2_elimination():
    print("\n\nTesting Cycle 2: Scoring and Elimination...")

    # Mock evidence contradicting specific hypotheses
    evidence = [
        {
            "observation_id": "S01",
            "content": "SVB held $91B of HTM securities with $15B unrealized losses due to rising interest rates. These losses were not marked on the balance sheet per HTM accounting rules.",
            "source": "FDIC Post-Mortem Report",
            "type": "structural",
            "supports": ["H01", "H02"],  # Duration mismatch hypotheses
            "contradicts": ["H07", "H08"],  # Counterparty/fraud hypotheses
            "neutral": ["H03", "H04"]
        },
        {
            "observation_id": "E01",
            "content": "SVB stock price fell 60% in one day on March 9, 2023. CDS spreads reached 450bps. Deposit outflows exceeded $42B in 24 hours.",
            "source": "Market Data (Bloomberg)",
            "type": "market",
            "supports": ["H01", "H06"],  # Duration mismatch + bank run
            "contradicts": [],
            "neutral": ["H03", "H04", "H05"]
        }
    ]

    # Use hypotheses from cycle 1
    cycle1_result = await test_cycle1_generation()

    context = {
        "trigger": "SVB CDS spike",
        "entity": "SVB",
        "cycle_num": 2,
        "compressed_state": cycle1_result["compressed_state"],
        "evidence": evidence,
        "active_hypotheses": cycle1_result["surviving_hypotheses"]
    }

    result = await investigate(context)

    # Verify eliminations
    assert len(result["eliminated_hypotheses"]) > 0, "Expected some eliminations in cycle 2"

    # Verify each elimination cites specific evidence
    for elim in result["eliminated_hypotheses"]:
        assert "killed_by_atom" in elim
        assert "reason" in elim
        assert "killed_in_cycle" in elim
        assert elim["killed_in_cycle"] == 2
        assert elim["killed_by_atom"] in ["S01", "E01"]

    print(f"✓ Eliminated {len(result['eliminated_hypotheses'])} hypotheses")
    print(f"✓ All eliminations cite specific evidence atoms")

    # Print eliminations
    print(f"\nEliminations:")
    for elim in result["eliminated_hypotheses"]:
        print(f"  {elim['id']}: killed by {elim['killed_by_atom']} - {elim['reason']}")

    # Verify compressed state updated
    assert result["compressed_state"] != cycle1_result["compressed_state"]
    assert "CYCLE 2" in result["compressed_state"] or "cycle 2" in result["compressed_state"].lower()

    print(f"\n✓ Compressed state updated (length: {len(result['compressed_state'])} chars)")

    return result

async def main():
    print("=" * 60)
    print("Phase 3 Verification: Investigator (CRITICAL PATH)")
    print("=" * 60)

    cycle1_result = await test_cycle1_generation()
    cycle2_result = await test_cycle2_elimination()

    print("\n" + "=" * 60)
    print("✅ INVESTIGATOR VALIDATED - Phase 3 Complete!")
    print("=" * 60)
    print("\nVerified:")
    print(f"  ✓ Cycle 1: Generated {len(cycle1_result['surviving_hypotheses'])} hypotheses")
    print(f"  ✓ Cycle 2: Eliminated {len(cycle2_result['eliminated_hypotheses'])} hypotheses")
    print("  ✓ All eliminations cite specific evidence atoms")
    print("  ✓ Compressed state grows cumulatively across cycles")
    print("  ✓ Evidence requests generated for next cycle")
    print("  ✓ Token usage tracked per cycle")
    print("\nReady to proceed to Phase 4: Evidence Pipeline")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Running Verification

```bash
cd backend
python test_phase3.py
```

**Expected Output:**
```
============================================================
Phase 3 Verification: Investigator (CRITICAL PATH)
============================================================
Testing Cycle 1: Hypothesis Generation...
✓ Generated 9 hypotheses
✓ Token usage: 1247 in, 2834 out

Sample hypotheses:
  H01: Duration mismatch + rising rates (score: 0.85)
  H02: Deposit concentration risk (score: 0.80)
  H03: Counterparty credit exposure (score: 0.60)

Testing Cycle 2: Scoring and Elimination...
✓ Eliminated 2 hypotheses
✓ All eliminations cite specific evidence atoms

Eliminations:
  H07: killed by S01 - S01 shows HTM losses, not counterparty exposure
  H08: killed by S01 - No evidence of fraud, structural balance sheet risk

✓ Compressed state updated (length: 1842 chars)

============================================================
✅ INVESTIGATOR VALIDATED - Phase 3 Complete!
============================================================

Verified:
  ✓ Cycle 1: Generated 9 hypotheses
  ✓ Cycle 2: Eliminated 2 hypotheses
  ✓ All eliminations cite specific evidence atoms
  ✓ Compressed state grows cumulatively across cycles
  ✓ Evidence requests generated for next cycle
  ✓ Token usage tracked per cycle

Ready to proceed to Phase 4: Evidence Pipeline
```

---

## Success Criteria

- [ ] Cycle 1 generates 8-10 hypotheses covering diverse categories
- [ ] Cycle 2+ eliminates hypotheses with cited evidence atoms
- [ ] Every elimination has `killed_by_atom` field with observation ID
- [ ] Compressed state grows cumulatively across cycles
- [ ] Evidence requests are specific (not vague)
- [ ] Token usage tracked per cycle
- [ ] Fresh context window per cycle (stateless function)
- [ ] No import errors

---

## What This Enables

With Investigator working:
- ✅ Core reasoning engine operational
- ✅ Can test full hypothesis elimination cycles
- ✅ Self-compression architecture validated
- ✅ Ready to build evidence retrieval (Phase 4)
- ✅ Value prop demonstrated: iterative reasoning works

---

## Next Steps

After Phase 3 verification passes:
✅ Most critical component complete
✅ Can now build evidence pipeline to feed the investigator
✅ Ready for Phase 4: Evidence Agents + Packager

**STOP HERE and verify before proceeding to Phase 4.**
