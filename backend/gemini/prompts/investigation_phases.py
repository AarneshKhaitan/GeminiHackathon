"""
Investigation cycle prompts - 5 separate phases for detailed reasoning.

SIMPLIFIED VERSION: Uses cumulative context passing but simpler prompt structure.
Each phase requests detailed "thinking" field without complex structured templates.
"""


def build_phase1_scoring_prompt(
    cycle_num: int,
    trigger: str,
    entity: str,
    compressed_state: str | None,
    evidence: list[dict],
    active_hypotheses: list[dict]
) -> str:
    """
    PHASE 1: SCORE - Evaluate each hypothesis against all evidence.
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
  "thinking": "Write your detailed reasoning here. Explain your thought process for generating these hypotheses. Be thorough but natural - no need to force a specific word count. Explain what each hypothesis means and why it's plausible given the trigger signal.",

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
  ]
}}

Generate 8-10 hypotheses with clear reasoning.
"""

    else:
        # Cycle 2+: Score existing hypotheses
        evidence_text = "\n\n".join([
            f"## OBSERVATION {obs['observation_id']}\n"
            f"Type: {obs['type']}\n"
            f"Source: {obs['source']}\n"
            f"Content: {obs['content']}\n"
            f"Tagged: Supports {obs.get('supports', [])}, Contradicts {obs.get('contradicts', [])}"
            for obs in evidence
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

# NEW EVIDENCE
{evidence_text}

# PHASE 1: SCORING - Evaluate hypotheses against evidence

Your task: For EACH hypothesis, evaluate it against EVERY piece of evidence and update its confidence score.

## OUTPUT FORMAT (JSON):

{{
  "thinking": "Write detailed reasoning for your scoring decisions. For each hypothesis, explain how the evidence affects your confidence. Show your work - explain which evidence supports, which contradicts, and how you're updating the scores.",

  "scored_hypotheses": [
    {{
      "id": "H01",
      "name": "...",
      "description": "...",
      "score": 0.82,
      "evidence_chain": ["S01", "E03"],
      "status": "active",
      "reasoning": "Detailed reasoning for this score"
    }}
  ]
}}

Score ALL {len(active_hypotheses)} hypotheses with detailed reasoning.
"""


def build_phase2_elimination_prompt(
    scored_hypotheses: list[dict],
    evidence: list[dict],
    cycle_num: int
) -> str:
    """
    PHASE 2: ELIMINATE - Identify hypotheses that must be killed.
    """

    hypotheses_text = "\n".join([
        f"- {h['id']}: {h['name']} (score: {h['score']})"
        for h in scored_hypotheses
    ])

    evidence_ids = [obs['observation_id'] for obs in evidence]

    return f"""
# PHASE 2: ELIMINATION - Identify contradicted hypotheses

You have scored hypotheses. Now identify which ones MUST be eliminated.

# SCORED HYPOTHESES
{hypotheses_text}

# AVAILABLE EVIDENCE
{', '.join(evidence_ids)}

## ELIMINATION CRITERIA

Eliminate a hypothesis if ANY of these conditions are met:

1. **Evidence-Based Elimination (IMPOSSIBLE):**
   - Evidence directly contradicts the hypothesis
   - Makes hypothesis logically IMPOSSIBLE, not just unlikely
   - Must cite specific observation ID as "kill atom"

2. **Score-Based Elimination (UNLIKELY):**
   - Hypothesis score drops below 0.2
   - Indicates hypothesis has become highly implausible
   - Cite "low_confidence" as reason

## OUTPUT FORMAT (JSON):

{{
  "thinking": "For each hypothesis, analyze elimination criteria:

  1. Evidence-based: Does contradicting evidence make it IMPOSSIBLE (not just unlikely)? If yes, cite the kill atom.
  2. Score-based: Did the score drop below 0.2? If yes, eliminate due to low confidence.

  Explain your elimination decisions step-by-step. Show why evidence proves logical impossibility OR why score indicates hypothesis is no longer viable.",

  "eliminated_hypotheses": [
    {{
      "id": "H05",
      "name": "...",
      "killed_by_atom": "S01",  // Use "S01" for evidence-based OR "low_confidence" for score-based
      "killed_in_cycle": {cycle_num},
      "reason": "Evidence S01 shows X which directly contradicts hypothesis claim of Y" // OR "Score dropped to 0.15, below 0.2 threshold"
    }}
  ],
      "reason": "Specific reason this evidence makes hypothesis impossible"
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


def build_phase3_crossmodal_prompt(
    surviving_hypotheses: list[dict],
    evidence: list[dict],
    cycle_num: int
) -> str:
    """
    PHASE 3: CROSS-MODAL - Flag structural vs empirical contradictions.
    """

    structural_evidence = [obs for obs in evidence if obs['type'] == 'structural']
    empirical_evidence = [obs for obs in evidence if obs['type'] in ['market', 'news', 'filing']]

    return f"""
# PHASE 3: CROSS-MODAL ANALYSIS - Find structural vs empirical contradictions

Compare structural knowledge against empirical observations.

# STRUCTURAL EVIDENCE ({len(structural_evidence)} observations)
{chr(10).join([f"- {obs['observation_id']}: {obs['content'][:150]}..." for obs in structural_evidence])}

# EMPIRICAL EVIDENCE ({len(empirical_evidence)} observations)
{chr(10).join([f"- {obs['observation_id']}: {obs['content'][:150]}..." for obs in empirical_evidence])}

## TASK
Find contradictions where:
- Structural evidence says one thing (e.g., "adequate capital")
- Empirical evidence shows another (e.g., "CDS at 450bps")

## OUTPUT FORMAT (JSON):

{{
  "thinking": "Analyze each structural claim against empirical reality. Where do they conflict? Explain why these contradictions matter and what hidden risks they reveal.",

  "cross_modal_flags": [
    {{
      "structural_atom_id": "S02",
      "empirical_atom_id": "E05",
      "detected_in_cycle": {cycle_num},
      "contradiction_description": "Detailed explanation of contradiction"
    }}
  ]
}}

Identify all cross-modal contradictions with clear explanations.
"""


def build_phase4_request_prompt(
    surviving_hypotheses: list[dict],
    evidence_collected: list[str],
    cycle_num: int
) -> str:
    """
    PHASE 4: REQUEST - Specify evidence needed for next cycle.
    """

    hypotheses_text = "\n".join([
        f"- {h['id']}: {h['name']} (score: {h['score']})"
        for h in surviving_hypotheses
    ])

    return f"""
# PHASE 4: EVIDENCE REQUESTS - What evidence do we need next?

# SURVIVING HYPOTHESES
{hypotheses_text}

# EVIDENCE ALREADY COLLECTED
{', '.join(evidence_collected)}

## TASK
Identify 3-5 pieces of SPECIFIC evidence that would discriminate between survivors.

## OUTPUT FORMAT (JSON):

{{
  "thinking": "Explain what evidence would best discriminate between surviving hypotheses. What's the crux question? What specific data would answer it? Be concrete and specific.",

  "evidence_requests": [
    {{
      "type": "structural",
      "description": "Specific evidence needed (be exact, not vague)",
      "reason": "How this would discriminate hypotheses"
    }}
  ]
}}

Specify 3-5 critical evidence requests with clear reasoning.
"""


def build_phase5_compression_prompt(
    cycle_num: int,
    all_phase_outputs: dict,
    previous_compressed_state: str | None
) -> str:
    """
    PHASE 5: COMPRESS - Self-compress cumulative state.
    """

    return f"""
# PHASE 5: SELF-COMPRESSION - Create cumulative compressed state

You've completed Cycle {cycle_num} analysis across 4 phases. Now compress ALL findings.

# PREVIOUS COMPRESSED STATE
{previous_compressed_state if previous_compressed_state else "No previous state (first cycle)"}

# THIS CYCLE'S OUTPUTS
- Scored hypotheses: {len(all_phase_outputs.get('scored_hypotheses', []))}
- Eliminations: {len(all_phase_outputs.get('eliminated_hypotheses', []))}
- Cross-modal flags: {len(all_phase_outputs.get('cross_modal_flags', []))}
- Evidence requests: {len(all_phase_outputs.get('evidence_requests', []))}

## TASK
Produce a CUMULATIVE compressed state incorporating:
- ALL prior cycles' findings
- This cycle's new findings
- Current crux question
- What evidence is still needed

## OUTPUT FORMAT (JSON):

{{
  "thinking": "Explain your compression strategy. What information are you preserving vs discarding? How are you balancing detail vs brevity?",

  "compressed_state": "CYCLE {cycle_num} CUMULATIVE STATE: Write compressed state here incorporating ALL prior cycles and this cycle's findings. Include: surviving hypotheses with scores, key eliminations with kill atoms, cross-modal flags, crux question, evidence still needed, historical context from all prior cycles.",

  "key_insights": [
    "Important insight 1 from this cycle",
    "Important insight 2 from this cycle"
  ]
}}

Create comprehensive compressed state with clear reasoning.
"""
