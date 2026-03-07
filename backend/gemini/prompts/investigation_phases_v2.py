"""
Investigation cycle prompts - 5 phases aligned with PRD investigation flow.

ARCHITECTURAL CHANGE:
- Phase 1: SCORE + CROSS-MODAL (combined for integrated reasoning)
- Phase 2: ELIMINATE (evidence + score + subsumption)
- Phase 3: FORWARD SIMULATE (predict outcomes if hypotheses true)
- Phase 4: REQUEST (evidence to test predictions)
- Phase 5: COMPRESS (cumulative state)
"""


def build_phase1_score_and_crossmodal_prompt(
    cycle_num: int,
    trigger: str,
    entity: str,
    compressed_state: str | None,
    evidence: list[dict],
    active_hypotheses: list[dict]
) -> str:
    """
    PHASE 1: SCORE + CROSS-MODAL

    Score hypotheses against structural + empirical evidence.
    Detect cross-modal contradictions during scoring.
    Adjust scores based on whether hypothesis explains contradictions.
    """

    if cycle_num == 1:
        # Cycle 1: Generate initial hypotheses
        return f"""
You are a financial risk investigator analyzing a trigger signal for {entity}.

# TRIGGER SIGNAL
{trigger}

# PHASE 1: HYPOTHESIS GENERATION

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
   - Specific and testable
   - Falsifiable
   - Assigned initial score 0.0-1.0

## OUTPUT FORMAT (JSON):

{{
  "thinking": "Write detailed reasoning for hypothesis generation. Explain what each hypothesis means and why it's plausible given the trigger signal. Be thorough in your analysis.",

  "surviving_hypotheses": [
    {{
      "id": "H01",
      "name": "Short name",
      "description": "Detailed description",
      "score": 0.75,
      "evidence_chain": [],
      "status": "active",
      "reasoning": "Why this hypothesis is plausible"
    }}
  ],

  "cross_modal_flags": []
}}

Generate 8-10 hypotheses with clear reasoning.
"""

    else:
        # Cycle 2+: Score existing hypotheses + detect cross-modal contradictions

        # Separate structural and empirical evidence
        structural_evidence = [obs for obs in evidence if obs['type'] == 'structural']
        empirical_evidence = [obs for obs in evidence if obs['type'] in ['market', 'news', 'filing']]

        structural_text = "\n\n".join([
            f"## STRUCTURAL OBSERVATION {obs['observation_id']}\n"
            f"Source: {obs['source']}\n"
            f"Content: {obs['content']}\n"
            f"Tagged: Supports {obs.get('supports', [])}, Contradicts {obs.get('contradicts', [])}"
            for obs in structural_evidence
        ])

        empirical_text = "\n\n".join([
            f"## EMPIRICAL OBSERVATION {obs['observation_id']}\n"
            f"Source: {obs['source']}\n"
            f"Content: {obs['content']}\n"
            f"Tagged: Supports {obs.get('supports', [])}, Contradicts {obs.get('contradicts', [])}"
            for obs in empirical_evidence
        ])

        hypotheses_text = "\n".join([
            f"- {h['id']}: {h['name']} (score: {h['score']}) - {h['description']}"
            for h in active_hypotheses
        ])

        return f"""
You are a financial risk investigator in Cycle {cycle_num} for {entity}.

# PREVIOUS STATE
{compressed_state if compressed_state else "No previous state"}

# ACTIVE HYPOTHESES
{hypotheses_text}

# STRUCTURAL EVIDENCE ({len(structural_evidence)} observations)
{structural_text if structural_text else "No structural evidence yet"}

# EMPIRICAL EVIDENCE ({len(empirical_evidence)} observations)
{empirical_text if empirical_text else "No empirical evidence yet"}

# PHASE 1: SCORE + CROSS-MODAL ANALYSIS

Your task has TWO parts:

## PART A: SCORE HYPOTHESES
For EACH hypothesis, evaluate it against ALL evidence:
1. How well does structural evidence support/contradict it?
2. How well does empirical evidence support/contradict it?
3. Can this hypothesis EXPLAIN any cross-modal contradictions?
4. Update confidence score accordingly

## PART B: DETECT CROSS-MODAL CONTRADICTIONS
Compare structural vs empirical evidence:
- Where does structural evidence claim "X is true"?
- Where does empirical evidence show "X is false" (or vice versa)?
- Flag these contradictions - they reveal hidden risks

## SCORING BONUS:
If a hypothesis CAN explain a cross-modal contradiction → BOOST its score
If a hypothesis CANNOT explain a cross-modal contradiction → REDUCE its score

Example:
- Structural: "Bank has adequate capital (12% ratio)"
- Empirical: "CDS spiked to 450bps"
- Contradiction: Markets don't price 450bps for well-capitalized banks
- H01 "Duration mismatch hidden by HTM accounting" → EXPLAINS the contradiction → BOOST score
- H03 "Operational fraud" → DOES NOT explain why capital looks fine but market panics → REDUCE score

## OUTPUT FORMAT (JSON):

{{
  "thinking": "Write detailed reasoning:

  PART A - SCORING:
  For each hypothesis, explain how you scored it against structural evidence, empirical evidence, and whether it explains cross-modal contradictions. Show your work.

  PART B - CROSS-MODAL:
  Identify where structural and empirical evidence conflict. Explain why these contradictions matter and which hypotheses explain them vs which don't.",

  "scored_hypotheses": [
    {{
      "id": "H01",
      "name": "...",
      "description": "...",
      "score": 0.82,
      "evidence_chain": ["S01", "E03"],
      "status": "active",
      "reasoning": "Detailed reasoning including whether it explains cross-modal contradictions"
    }}
  ],

  "cross_modal_flags": [
    {{
      "structural_atom_id": "S02",
      "empirical_atom_id": "E05",
      "detected_in_cycle": {cycle_num},
      "contradiction_description": "Structural claims X, empirical shows Y, revealing hidden risk Z",
      "explained_by_hypotheses": ["H01", "H02"]
    }}
  ]
}}

Score ALL {len(active_hypotheses)} hypotheses considering cross-modal contradictions.
"""


def build_phase2_elimination_prompt(
    scored_hypotheses: list[dict],
    evidence: list[dict],
    cross_modal_flags: list[dict],
    cycle_num: int
) -> str:
    """
    PHASE 2: ELIMINATE

    Three elimination criteria:
    1. Evidence-based: Evidence makes hypothesis IMPOSSIBLE
    2. Score-based: Score < 0.2 (highly implausible)
    3. Subsumption: One hypothesis logically contains another
    """

    hypotheses_text = "\n".join([
        f"- {h['id']}: {h['name']} (score: {h['score']})"
        for h in scored_hypotheses
    ])

    evidence_ids = [obs['observation_id'] for obs in evidence]

    cross_modal_text = ""
    if cross_modal_flags:
        cross_modal_text = "\n\n# CROSS-MODAL CONTRADICTIONS\n" + "\n".join([
            f"- {flag['structural_atom_id']} vs {flag['empirical_atom_id']}: {flag['contradiction_description']}"
            for flag in cross_modal_flags
        ])

    return f"""
# PHASE 2: ELIMINATION

You have scored hypotheses. Now identify which ones MUST be eliminated.

# SCORED HYPOTHESES
{hypotheses_text}

# AVAILABLE EVIDENCE
{', '.join(evidence_ids)}
{cross_modal_text}

## ELIMINATION CRITERIA

Eliminate a hypothesis if ANY of these conditions are met:

1. **Evidence-Based Elimination:**
   - Evidence directly contradicts hypothesis
   - Makes hypothesis logically IMPOSSIBLE (not just unlikely)
   - Must cite specific observation ID as kill atom

2. **Score-Based Elimination:**
   - Hypothesis score below 0.2
   - Indicates hypothesis is highly implausible
   - Cite "low_confidence" as reason

3. **Subsumption Elimination:**
   - One hypothesis logically contains another
   - Example: "Duration mismatch + HTM accounting" subsumes "Duration mismatch alone"
   - Eliminate the weaker/narrower hypothesis
   - Cite "subsumed_by_H0X" as reason

## OUTPUT FORMAT (JSON):

{{
  "thinking": "For each hypothesis, analyze elimination criteria:

  1. Evidence-based: Does contradicting evidence make it IMPOSSIBLE? If yes, cite kill atom.
  2. Score-based: Is score below 0.2? If yes, eliminate due to low confidence.
  3. Subsumption: Is this hypothesis a subset of another? If yes, eliminate the weaker one.
  4. Cross-modal: Can this hypothesis explain the contradictions? If not, consider eliminating.

  Explain your elimination decisions step-by-step.",

  "eliminated_hypotheses": [
    {{
      "id": "H05",
      "name": "...",
      "killed_by_atom": "S01",  // Or "low_confidence" or "subsumed_by_H02"
      "killed_in_cycle": {cycle_num},
      "reason": "Specific reason for elimination"
    }}
  ],

  "surviving_hypotheses": [
    {{
      "id": "H01",
      "name": "...",
      "score": 0.82,
      "status": "active"
    }}
  ]
}}

Provide thorough elimination analysis with clear reasoning.
"""


def build_phase3_forward_simulation_prompt(
    surviving_hypotheses: list[dict],
    evidence: list[dict],
    cycle_num: int
) -> str:
    """
    PHASE 3: FORWARD SIMULATE (Cycles 3+ only)

    Given surviving hypotheses and evidence:
    - Predict what would happen next if each hypothesis is true
    - Use structural rules + empirical patterns
    - Output testable predictions
    """

    hypotheses_text = "\n".join([
        f"- {h['id']}: {h['name']} (score: {h['score']})" + (f" - {h['description']}" if 'description' in h else "")
        for h in surviving_hypotheses
    ])

    return f"""
# PHASE 3: FORWARD SIMULATION

You have {len(surviving_hypotheses)} surviving hypotheses. Now simulate forward:
"Given the evidence we have AND the structural rules in play, what would happen next if each hypothesis is true?"

# SURVIVING HYPOTHESES
{hypotheses_text}

# EVIDENCE COLLECTED
{len(evidence)} observations available

## TASK

For EACH surviving hypothesis, perform forward simulation:

1. **Apply Structural Rules:**
   - Given this hypothesis + known rules (accounting, regulations, market mechanics)
   - What are the logical consequences?

2. **Project Empirical Patterns:**
   - Given this hypothesis + observed trends
   - What would we expect to see next in market data, behavior, filings?

3. **Generate Testable Predictions:**
   - Specific, falsifiable predictions
   - Evidence that would confirm or contradict

## EXAMPLE

**Hypothesis: "Duration mismatch + HTM accounting hiding losses"**

Forward Simulation:
- Structural consequences: As rates rise, unrealized losses increase but aren't marked to market
- Empirical predictions:
  * Deposit outflows as customers seek higher yields elsewhere
  * Widening gap between regulatory capital and market valuation
  * Forced asset sales if liquidity stressed (crystallizing losses)
  * Rating agency downgrades once losses disclosed
- Testable: "If we get Q1 earnings, we should see HTM unrealized loss disclosure increasing"

## OUTPUT FORMAT (JSON):

{{
  "thinking": "For each surviving hypothesis, walk through the forward simulation:

  1. What structural rules apply?
  2. What empirical patterns are relevant?
  3. What are the logical next steps?
  4. What specific predictions can we make?

  Be detailed in your forward reasoning.",

  "forward_simulations": [
    {{
      "hypothesis_id": "H01",
      "hypothesis_name": "...",
      "structural_consequences": "Given accounting rules X and Y, the consequence is...",
      "empirical_predictions": [
        "Deposit outflows of 10-20% over next 30 days",
        "CDS spreads widen further to 600bps",
        "Stock continues downward pressure"
      ],
      "testable_evidence": [
        "Daily deposit flow data",
        "HTM portfolio mark-to-market as of latest date",
        "Customer sentiment surveys"
      ],
      "confidence_in_simulation": 0.75
    }}
  ]
}}

Simulate forward for ALL {len(surviving_hypotheses)} surviving hypotheses.
"""


def build_phase4_request_prompt(
    surviving_hypotheses: list[dict],
    forward_simulations: list[dict],
    evidence_collected: list[str],
    cycle_num: int
) -> str:
    """
    PHASE 4: REQUEST

    Use forward simulations to guide evidence requests.
    Request evidence that tests predictions from competing hypotheses.
    """

    hypotheses_text = "\n".join([
        f"- {h['id']}: {h['name']} (score: {h['score']})"
        for h in surviving_hypotheses
    ])

    simulations_text = "\n\n".join([
        f"## {sim['hypothesis_id']}: {sim['hypothesis_name']}\n"
        f"Predictions: {', '.join(sim.get('empirical_predictions', []))}\n"
        f"Testable via: {', '.join(sim.get('testable_evidence', []))}"
        for sim in forward_simulations
    ])

    return f"""
# PHASE 4: EVIDENCE REQUESTS

You have forward simulations showing what each hypothesis predicts.
Now request evidence to TEST these predictions.

# SURVIVING HYPOTHESES
{hypotheses_text}

# FORWARD SIMULATIONS
{simulations_text}

# EVIDENCE ALREADY COLLECTED
{', '.join(evidence_collected)}

## TASK

Identify 3-5 pieces of SPECIFIC evidence that would:
1. Test predictions from forward simulations
2. Discriminate between competing hypotheses
3. Confirm or contradict expected patterns

## PRIORITIZATION

Highest priority evidence:
- Tests predictions from HIGH-confidence hypotheses
- Discriminates between top 2-3 candidates
- Available/obtainable (not hypothetical)

## OUTPUT FORMAT (JSON):

{{
  "thinking": "Explain evidence request strategy:

  1. What predictions are most critical to test?
  2. What evidence would discriminate between top hypotheses?
  3. Why prioritize these specific requests?

  Show your reasoning for each evidence request.",

  "evidence_requests": [
    {{
      "type": "structural",
      "description": "Specific evidence needed (be exact, not vague)",
      "reason": "Tests prediction X from hypothesis Y vs prediction Z from hypothesis W",
      "tests_hypothesis": ["H01", "H02"],
      "expected_if_h01": "Would show...",
      "expected_if_h02": "Would show..."
    }}
  ]
}}

Request 3-5 critical pieces of evidence with clear testing strategy.
"""


def build_phase5_compression_prompt(
    cycle_num: int,
    all_phase_outputs: dict,
    previous_compressed_state: str | None
) -> str:
    """
    PHASE 5: COMPRESS

    Self-compress cumulative state incorporating all prior cycles.
    """

    return f"""
# PHASE 5: SELF-COMPRESSION

You've completed Cycle {cycle_num} analysis across 4 phases. Now compress ALL findings.

# PREVIOUS COMPRESSED STATE
{previous_compressed_state if previous_compressed_state else "No previous state (first cycle)"}

# THIS CYCLE'S OUTPUTS
- Scored hypotheses: {len(all_phase_outputs.get('scored_hypotheses', []))}
- Cross-modal flags: {len(all_phase_outputs.get('cross_modal_flags', []))}
- Eliminations: {len(all_phase_outputs.get('eliminated_hypotheses', []))}
- Forward simulations: {len(all_phase_outputs.get('forward_simulations', []))}
- Evidence requests: {len(all_phase_outputs.get('evidence_requests', []))}

## TASK

Produce a CUMULATIVE compressed state incorporating:
- ALL prior cycles' findings
- This cycle's new findings
- Cross-modal contradictions detected
- Forward simulation predictions
- Current crux question
- What evidence is still needed

## OUTPUT FORMAT (JSON):

{{
  "thinking": "Explain compression strategy:

  1. What information must be preserved?
  2. What can be safely discarded?
  3. How are you balancing detail vs brevity?

  Focus on preserving critical decision points and eliminations.",

  "compressed_state": "CYCLE {cycle_num} CUMULATIVE STATE: Write compressed state here incorporating ALL prior cycles and this cycle's findings. Include: surviving hypotheses with scores, key eliminations with kill atoms, cross-modal contradictions, forward simulation insights, crux question, evidence still needed, historical context.",

  "key_insights": [
    "Important insight 1 from this cycle",
    "Important insight 2 from this cycle"
  ]
}}

Create comprehensive compressed state with clear reasoning.
"""
