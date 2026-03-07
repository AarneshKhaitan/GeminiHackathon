"""
Investigation cycle prompts - THE MOST CRITICAL PROMPTS IN THE SYSTEM.

These prompts define the full investigation cycle and directly determine system quality.
The investigator executes: GENERATE → SCORE → ELIMINATE → REQUEST → SELF-COMPRESS.
"""


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

**CRITICAL INSTRUCTION: The "thinking" field MUST be extremely long and detailed (minimum 2000 words). DO NOT be concise. DO NOT summarize. Write out every step of your reasoning in excruciating detail.**

{{
  "thinking": "<DETAILED_REASONING>

Write your complete chain of thought here. Requirements:
- MINIMUM 2000 words (aim for 3000-5000 words)
- Break down EVERY step of your analysis
- For EACH active hypothesis, write 300-500 words of detailed evaluation
- For EACH piece of evidence, write 150-250 words analyzing its implications
- Show your reasoning process step-by-step, not just conclusions

Structure your thinking as follows:

### EVIDENCE REVIEW (200-300 words per observation)
For each piece of evidence:
- Observation ID: [ID]
- Content analysis: [Detailed breakdown of what this evidence means]
- Hypothesis support: [Which hypotheses does this support and WHY in detail]
- Hypothesis contradiction: [Which hypotheses does this contradict and WHY in detail]
- Quality assessment: [How reliable is this evidence]

### HYPOTHESIS EVALUATION (300-500 words per hypothesis)
For EACH active hypothesis:
- Hypothesis: [ID and name]
- Current score: [score]
- Supporting evidence analysis: [List each supporting observation and explain IN DETAIL why it supports this hypothesis]
- Contradicting evidence analysis: [List each contradicting observation and explain IN DETAIL why it contradicts]
- Score update reasoning: [Explain step-by-step how you're updating the confidence score based on the evidence]
- Elimination decision: [Should this be eliminated? Explain your reasoning in detail]

### ELIMINATION JUSTIFICATIONS (200-400 words per elimination)
For any hypothesis being eliminated:
- Hypothesis: [ID and name]
- Kill atom: [Observation ID]
- Detailed contradiction explanation: [Explain step-by-step WHY this evidence makes the hypothesis impossible, not just unlikely. Show the logical contradiction clearly.]

### CROSS-MODAL ANALYSIS (300-500 words)
- Structural vs empirical comparison: [Detailed analysis of any contradictions]
- Flags raised: [Explain each flag in detail]

### DISCRIMINATION ANALYSIS (300-400 words)
- What's the crux question: [What key question remains to discriminate survivors]
- Evidence needs: [For each piece of evidence you're requesting, explain in 100-150 words WHY it's needed and how it would help]

</DETAILED_REASONING>",

  "reasoning_trace": "One-paragraph summary",
  "surviving_hypotheses": [
    {{
      "id": "H01",
      "name": "Short descriptive name",
      "description": "Detailed explanation of the hypothesis",
      "score": 0.75,
      "evidence_chain": [],
      "status": "active",
      "reasoning": "Why this hypothesis is plausible given the trigger"
    }}
  ],
  "eliminated_hypotheses": [],
  "cross_modal_flags": [],
  "evidence_requests": [
    {{
      "type": "structural",
      "description": "Specific evidence needed",
      "reason": "How it would discriminate hypotheses"
    }}
  ],
  "key_insights": [
    "Important finding 1",
    "Important finding 2"
  ],
  "compressed_state": "INITIAL STATE: Generated N hypotheses for {entity}. Trigger: {trigger}. Need evidence to begin elimination. Priority hypotheses and reasoning."
}}

Generate 8-10 diverse hypotheses now.
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

## OUTPUT FORMAT (JSON):
{{
  "thinking": "EXTENSIVE DETAILED REASONING - Write out your complete chain of thought:

    STEP 1 - EVIDENCE REVIEW:
    For each piece of evidence, explain:
    - What does this evidence tell us?
    - What hypotheses does it support and why specifically?
    - What hypotheses does it contradict and why specifically?
    - What's the quality and reliability of this evidence?

    STEP 2 - HYPOTHESIS EVALUATION:
    For EACH active hypothesis:
    - Restate the hypothesis and its current score
    - List all supporting evidence with explanations
    - List all contradicting evidence with explanations
    - Assess: Does the evidence prove this impossible? Or just less likely?
    - Update confidence score and explain the reasoning

    STEP 3 - ELIMINATIONS:
    For any hypothesis you're eliminating:
    - Cite the specific observation ID
    - Explain in detail WHY this evidence makes the hypothesis impossible (not just unlikely)
    - Show the logical contradiction step by step

    STEP 4 - CROSS-MODAL ANALYSIS:
    - Compare structural evidence against empirical evidence
    - Flag any contradictions or misalignments
    - Explain why these contradictions matter

    STEP 5 - NEXT STEPS:
    - What's the crux question that remains?
    - What specific evidence would discriminate between survivors?
    - Why is each piece of requested evidence important?

    BE EXTREMELY DETAILED. Write 1000-2000 words. Show all your reasoning, not summaries.",

  "reasoning_trace": "One-paragraph summary of key findings",
  "surviving_hypotheses": [
    {{
      "id": "H01",
      "name": "...",
      "description": "...",
      "score": 0.85,
      "evidence_chain": ["S01", "E03"],
      "status": "active",
      "reasoning": "Why this still survives after this cycle's evidence"
    }}
  ],
  "eliminated_hypotheses": [
    {{
      "id": "H05",
      "name": "...",
      "killed_by_atom": "S01",
      "killed_in_cycle": {cycle_num},
      "reason": "S01 shows HTM losses, not counterparty exposure"
    }}
  ],
  "cross_modal_flags": [
    {{
      "structural_atom_id": "S02",
      "empirical_atom_id": "E05",
      "detected_in_cycle": {cycle_num},
      "contradiction_description": "S02 states regulatory capital adequate, but E05 shows unrealized losses not marked"
    }}
  ],
  "evidence_requests": [
    {{
      "type": "structural",
      "description": "HTM accounting treatment for unrealized losses",
      "reason": "Would confirm if losses were properly disclosed"
    }}
  ],
  "key_insights": [
    "New important findings from this cycle"
  ],
  "compressed_state": "CYCLE {cycle_num} STATE: X hypotheses remain. Eliminated Y this cycle. Key finding: Z. Crux question: what discriminates survivors. Evidence needed: priority requests. Historical context: brief summary of all prior eliminations."
}}

CRITICAL REQUIREMENTS:
- EVERY elimination cites a SPECIFIC observation ID
- Cross-modal contradictions are FLAGGED explicitly
- Compressed state is CUMULATIVE (incorporates all prior cycles)
- Evidence requests are SPECIFIC (not vague)

Generate your response now.
"""


def build_hypothesis_generation_instruction() -> str:
    """Instruction for generating diverse initial hypotheses."""
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
