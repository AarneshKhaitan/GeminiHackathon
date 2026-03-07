"""
Investigation cycle prompts - 5 separate phases for detailed reasoning.

Each phase is a separate Gemini call with focused reasoning.
This gives us maximum detail and traceability at each step.

RESTRUCTURED: Each phase now uses separate fields to force detailed reasoning
instead of a single "thinking" blob that models compress.
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

    This is the first of 5 Gemini calls in a cycle.
    Focus: Detailed scoring of each hypothesis.

    RESTRUCTURED: Forces detailed reasoning through separate fields per hypothesis and evidence.
    """

    if cycle_num == 1:
        # Cycle 1: Generate initial hypotheses
        return f"""
You are a financial risk investigator analyzing a trigger signal for {entity}.

# TRIGGER SIGNAL
{trigger}

# PHASE 1: HYPOTHESIS GENERATION

Generate 8-10 competing hypotheses that could explain this trigger signal.

## OUTPUT FORMAT (JSON):

You MUST provide BOTH detailed thinking AND structured fields:

{{
  "thinking": "WRITE YOUR COMPLETE REASONING HERE - BE EXTREMELY VERBOSE:

### STEP 1: TRIGGER ANALYSIS (Write 400-600 words)
Analyze the trigger '{trigger}' in extreme detail:
- What specifically happened? Walk through each component of the signal.
- How severe is this? Compare to historical precedents.
- What are ALL possible root causes you can think of?
- What patterns does this match from financial crises?
- What makes this situation critical?
- What are immediate vs underlying factors?

[Write full detailed analysis here - DO NOT SUMMARIZE]

### STEP 2: HYPOTHESIS DEVELOPMENT (Write 200-300 words PER hypothesis)
For EACH of the 8-10 hypotheses:

H01: [Name]
- Category: [structural/market/etc]
- Causal mechanism: [Walk through step-by-step how this would cause the trigger]
- Plausibility reasoning: [Explain in detail why this is credible]
- Initial confidence: [Score] - [Explain reasoning for this number]
- Evidence to confirm: [What would prove this?]
- Evidence to disprove: [What would eliminate this?]

H02: [Name]
[Same level of detail]

[CONTINUE FOR ALL 8-10 HYPOTHESES - WRITE FULL ANALYSIS FOR EACH]

### STEP 3: HYPOTHESIS COMPARISON (Write 300-400 words)
- Which hypotheses are strongest and why?
- What patterns emerge?
- What's the key discriminating question?
- What evidence is most critical to collect first?

[Write full comparison analysis]",

  "trigger_analysis": {{
    "signal_description": "What specifically happened? Describe the trigger in detail.",
    "severity_assessment": "How severe is this signal? What's the magnitude of concern?",
    "historical_context": "What similar patterns have we seen in financial history?",
    "immediate_factors": "What are the immediate surface-level factors?",
    "underlying_causes": "What are the potential deeper structural causes?",
    "urgency_level": "How urgent is this investigation?"
  }},

  "hypothesis_development": {{
    "H01": {{
      "name": "Short descriptive name",
      "category": "One of: structural/market/counterparty/operational/regulatory/reputational/contagion",
      "description": "Full detailed description of the hypothesis",
      "causal_mechanism": "Step-by-step explanation: how would this cause the trigger? Walk through the causal chain.",
      "plausibility_reasoning": "Why is this a reasonable explanation? What makes it credible?",
      "initial_confidence": 0.85,
      "confidence_justification": "Why this specific score? What factors influenced this number?",
      "evidence_needed_to_confirm": "What specific evidence would prove this hypothesis?",
      "evidence_needed_to_disprove": "What specific evidence would eliminate this hypothesis?"
    }},
    "H02": {{
      "name": "...",
      "category": "...",
      "description": "...",
      "causal_mechanism": "...",
      "plausibility_reasoning": "...",
      "initial_confidence": 0.80,
      "confidence_justification": "...",
      "evidence_needed_to_confirm": "...",
      "evidence_needed_to_disprove": "..."
    }},
    "H03": {{ ... }},
    "H04": {{ ... }},
    "H05": {{ ... }},
    "H06": {{ ... }},
    "H07": {{ ... }},
    "H08": {{ ... }}
  }},

  "hypothesis_comparison": {{
    "most_likely_candidates": ["H01", "H02"],
    "most_likely_reasoning": "Why are these the top candidates? What distinguishes them?",
    "least_likely_candidates": ["H07", "H08"],
    "least_likely_reasoning": "Why are these less probable?",
    "key_discriminators": "What evidence would discriminate between the top candidates?"
  }},

  "surviving_hypotheses": [
    {{
      "id": "H01",
      "name": "Short name",
      "description": "Detailed description",
      "score": 0.85,
      "evidence_chain": [],
      "status": "active",
      "reasoning": "Why this hypothesis is plausible"
    }}
  ]
}}

YOU MUST GENERATE 8-10 HYPOTHESES. Fill ALL fields with detailed reasoning - no brief summaries.
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

        # Build structured template for each evidence and hypothesis
        evidence_template = {obs['observation_id']: {
            "content_summary": "Summarize the key facts from this observation",
            "source_reliability": "How reliable is this source? What's its credibility?",
            "key_facts_extracted": ["Fact 1", "Fact 2", "Fact 3"],
            "implications_for_investigation": "What does this evidence reveal about the entity's situation?",
            "hypotheses_supported": "Which hypotheses does this support and WHY? Be specific about causal links.",
            "hypotheses_contradicted": "Which hypotheses does this contradict and WHY? Explain the logical conflict.",
            "confidence_impact": "How should this evidence change our confidence in various hypotheses?"
        } for obs in evidence}

        hypothesis_template = {h['id']: {
            "hypothesis_restatement": f"Restate what {h['id']} claims in your own words",
            "current_score": h['score'],
            "evidence_supporting": {
                obs['observation_id']: f"Explain in detail WHY {obs['observation_id']} supports this hypothesis. What's the causal link?"
                for obs in evidence if h['id'] in obs.get('supports', [])
            },
            "evidence_contradicting": {
                obs['observation_id']: f"Explain in detail WHY {obs['observation_id']} contradicts this hypothesis. What's the logical conflict?"
                for obs in evidence if h['id'] in obs.get('contradicts', [])
            },
            "evidence_neutral": {
                obs['observation_id']: f"Why is {obs['observation_id']} neutral toward this hypothesis?"
                for obs in evidence if h['id'] in obs.get('neutral', [])
            },
            "score_adjustment_reasoning": "Walk through step-by-step: how does the evidence change confidence?",
            "score_calculation": "Starting score + supporting impact - contradicting impact = new score. Show your math.",
            "new_score": "Your updated confidence score",
            "new_score_justification": "Why this specific number? Explain your reasoning."
        } for h in active_hypotheses}

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

You MUST provide BOTH detailed thinking AND structured fields:

{{
  "thinking": "WRITE YOUR COMPLETE REASONING HERE - BE EXTREMELY VERBOSE:

### STEP 1: EVIDENCE ANALYSIS (Write 250-400 words PER observation)
For EACH piece of evidence:

OBSERVATION {evidence[0]['observation_id'] if evidence else 'S01'}:
- Content summary: [Summarize key facts]
- Source reliability: [Assess credibility - why trust this source?]
- Key facts extracted: [List all important facts]
- Implications: [What does this reveal about the entity's situation?]
- Hypotheses this supports: [List with detailed WHY for each]
- Hypotheses this contradicts: [List with detailed WHY for each]
- Confidence impact: [How should this change our hypothesis scores?]

[REPEAT FOR EVERY OBSERVATION - DO NOT SKIP ANY]

### STEP 2: HYPOTHESIS SCORING (Write 300-500 words PER hypothesis)
For EACH hypothesis:

HYPOTHESIS {active_hypotheses[0]['id'] if active_hypotheses else 'H01'}: {active_hypotheses[0]['name'] if active_hypotheses else 'Name'}
- Restate hypothesis: [Explain what this hypothesis claims]
- Current score: {active_hypotheses[0]['score'] if active_hypotheses else '0.0'}
- Supporting evidence detailed analysis:
  * {evidence[0]['observation_id'] if evidence else 'S01'}: [Explain in 100+ words WHY this supports. What's the causal mechanism?]
  * [Continue for ALL supporting evidence]
- Contradicting evidence detailed analysis:
  * [If any, explain in 100+ words WHY this contradicts. What's the logical conflict?]
- Neutral evidence analysis:
  * [If any, explain why neutral]
- Score adjustment step-by-step:
  * Starting: {active_hypotheses[0]['score'] if active_hypotheses else '0.0'}
  * Impact of S01: [How much to adjust? Why?]
  * Impact of other evidence: [Detail each]
  * Final calculation: [Show your math]
  * New score: [Result with justification]

[REPEAT FOR ALL {len(active_hypotheses)} HYPOTHESES]

### STEP 3: OVERALL ASSESSMENT (Write 200-300 words)
- Strongest hypotheses and why
- Weakest hypotheses and why
- Key patterns emerging
- Critical remaining questions

[Write full assessment]",

  "evidence_analysis": {evidence_template},

  "hypothesis_scoring": {hypothesis_template},

  "overall_assessment": {{
    "strongest_hypotheses": ["H01", "H02"],
    "strongest_reasoning": "Why are these the strongest after reviewing evidence?",
    "weakest_hypotheses": ["H05"],
    "weakest_reasoning": "Why have these hypotheses weakened?",
    "key_patterns": "What patterns emerge from the evidence?",
    "remaining_questions": "What critical questions remain unanswered?"
  }},

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

YOU MUST SCORE ALL {len(active_hypotheses)} HYPOTHESES. Fill EVERY field with detailed reasoning - no placeholders or brief summaries.
"""


def build_phase2_elimination_prompt(
    scored_hypotheses: list[dict],
    evidence: list[dict],
    cycle_num: int
) -> str:
    """
    PHASE 2: ELIMINATE - Identify hypotheses that must be killed.

    Second Gemini call. Takes scored hypotheses from Phase 1.
    Focus: Finding definitive contradictions.

    RESTRUCTURED: Forces detailed elimination reasoning per hypothesis.
    """

    hypotheses_text = "\n".join([
        f"- {h['id']}: {h['name']} (score: {h['score']})"
        for h in scored_hypotheses
    ])

    evidence_ids = [obs['observation_id'] for obs in evidence]

    elimination_template = {h['id']: {
        "hypothesis_summary": f"What does {h['id']} claim?",
        "contradicting_evidence_review": "List ALL evidence that contradicts this hypothesis",
        "is_contradiction_fatal": "true/false - Does the contradiction make this hypothesis IMPOSSIBLE (not just unlikely)?",
        "elimination_reasoning": "If fatal: explain step-by-step WHY this evidence proves impossibility. If not fatal: explain why hypothesis can still survive.",
        "kill_atom_id": "If eliminated: the specific observation ID that killed it",
        "kill_atom_explanation": "If eliminated: detailed explanation of the logical impossibility"
    } for h in scored_hypotheses}

    return f"""
# PHASE 2: ELIMINATION - Identify contradicted hypotheses

You have scored hypotheses. Now identify which ones MUST be eliminated.

# SCORED HYPOTHESES
{hypotheses_text}

# AVAILABLE EVIDENCE
{', '.join(evidence_ids)}

## CRITICAL RULE
Only eliminate if evidence makes hypothesis IMPOSSIBLE, not just unlikely.
Each elimination MUST cite specific observation ID.

## OUTPUT FORMAT (JSON):

You MUST provide BOTH detailed thinking AND structured elimination analysis:

{{
  "thinking": "WRITE YOUR COMPLETE ELIMINATION REASONING - BE EXTREMELY VERBOSE:

### STEP 1: HYPOTHESIS-BY-HYPOTHESIS REVIEW (Write 200-400 words PER hypothesis)
For EACH scored hypothesis:

HYPOTHESIS {scored_hypotheses[0]['id'] if scored_hypotheses else 'H01'}: {scored_hypotheses[0]['name'] if scored_hypotheses else 'Name'}
- Current score: {scored_hypotheses[0]['score'] if scored_hypotheses else '0.0'}
- What this hypothesis claims: [Restate in detail]
- ALL contradicting evidence:
  * [List each observation that contradicts]
  * [For EACH, explain in detail WHY it contradicts]
- Is contradiction FATAL?
  * [Analyze: does evidence make this IMPOSSIBLE or just less likely?]
  * [Show step-by-step logic]
  * [Fatal = logically impossible, not just improbable]
- DECISION: ELIMINATE or KEEP?
  * [If eliminate: cite kill atom and explain logical impossibility]
  * [If keep: explain why hypothesis can still survive]

[REPEAT FOR ALL {len(scored_hypotheses)} HYPOTHESES - ANALYZE EACH ONE]

### STEP 2: ELIMINATION JUSTIFICATIONS (Write 250-400 words PER elimination)
For EACH hypothesis being eliminated:
- Hypothesis: [ID and name]
- Kill atom: [Specific observation ID]
- Why this evidence proves impossibility:
  * [Step 1: What the hypothesis predicts]
  * [Step 2: What the evidence shows]
  * [Step 3: Why these cannot both be true - the logical contradiction]
  * [Step 4: Why this is impossible, not just unlikely]
- Confidence in elimination: [How certain are we this is correct?]

[WRITE FULL ANALYSIS FOR EACH ELIMINATION]

### STEP 3: SURVIVORS ANALYSIS (Write 200-300 words)
- Which hypotheses survive and why?
- What makes them resilient despite evidence?
- What evidence would be needed to eliminate them?
- What's our confidence in the survivors?

[Write full survivor analysis]",

  "elimination_analysis": {elimination_template},

  "elimination_summary": {{
    "total_candidates_reviewed": {len(scored_hypotheses)},
    "hypotheses_eliminated": 0,
    "hypotheses_surviving": 0,
    "elimination_criteria_applied": "What standard did you use to decide fatal vs non-fatal contradictions?",
    "confidence_in_eliminations": "How confident are you that eliminated hypotheses are truly impossible?"
  }},

  "eliminated_hypotheses": [
    {{
      "id": "H05",
      "name": "...",
      "killed_by_atom": "S01",
      "killed_in_cycle": {cycle_num},
      "reason": "Specific reason this evidence makes hypothesis impossible"
    }}
  ],

  "surviving_hypotheses": [
    {{
      "id": "H01",
      "name": "...",
      "score": 0.82,
      "status": "active",
      "survival_reasoning": "Why this hypothesis survives despite any contradicting evidence"
    }}
  ]
}}

Fill ALL fields with detailed reasoning. Show your work for EVERY hypothesis.
"""


def build_phase3_crossmodal_prompt(
    surviving_hypotheses: list[dict],
    evidence: list[dict],
    cycle_num: int
) -> str:
    """
    PHASE 3: CROSS-MODAL - Flag structural vs empirical contradictions.

    Third Gemini call. Takes survivors from Phase 2.
    Focus: Finding contradictions between structural and empirical evidence.

    RESTRUCTURED: Forces detailed cross-modal analysis.
    """

    structural_evidence = [obs for obs in evidence if obs['type'] == 'structural']
    empirical_evidence = [obs for obs in evidence if obs['type'] in ['market', 'news', 'filing']]

    structural_template = {obs['observation_id']: {
        "structural_claim": "What does this structural evidence claim about the entity?",
        "expected_empirical_signals": "If this structural claim is accurate, what should we see in market data, news, filings?",
        "contradicting_empirical_evidence": "Which empirical observations contradict this structural claim?",
        "contradiction_severity": "How severe is the contradiction? Minor discrepancy or major red flag?"
    } for obs in structural_evidence}

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

You MUST provide BOTH detailed thinking AND structured cross-modal analysis:

{{
  "thinking": "WRITE YOUR COMPLETE CROSS-MODAL REASONING - BE EXTREMELY VERBOSE:

### STEP 1: STRUCTURAL CLAIMS ANALYSIS (Write 200-300 words PER structural observation)
For EACH structural observation:

{structural_evidence[0]['observation_id'] if structural_evidence else 'S01'}:
- What does this structural evidence claim?
- What does it say about the entity's official/regulatory status?
- If this claim is accurate, what should we see in market data?
- If this claim is accurate, what should we see in news/filings?
- What empirical signals would CONFIRM this structural claim?
- What empirical signals would CONTRADICT this structural claim?

[REPEAT FOR ALL STRUCTURAL OBSERVATIONS]

### STEP 2: EMPIRICAL REALITY ANALYSIS (Write 200-300 words PER empirical observation)
For EACH empirical observation:

{empirical_evidence[0]['observation_id'] if empirical_evidence else 'E01'}:
- What does this empirical data show?
- What does this reveal about the ACTUAL state of the entity?
- Which structural claims does this confirm?
- Which structural claims does this contradict?
- What's the magnitude of any discrepancy?

[REPEAT FOR ALL EMPIRICAL OBSERVATIONS]

### STEP 3: CONTRADICTION DETECTION (Write 300-500 words PER contradiction)
For EACH structural vs empirical contradiction found:
- Structural atom: [ID and what it claims]
- Empirical atom: [ID and what it shows]
- The contradiction explained step-by-step:
  * [What the structural evidence says should be true]
  * [What the empirical data actually shows]
  * [Why these cannot both be true simultaneously]
  * [What this discrepancy reveals about hidden risks]
- Severity assessment: [How critical is this contradiction?]
- Implications for investigation: [What does this tell us?]

[ANALYZE ALL CONTRADICTIONS IN DETAIL]

### STEP 4: SUMMARY (Write 200-300 words)
- How many contradictions found?
- Which is most critical and why?
- What do these contradictions reveal overall?
- How should this affect our investigation strategy?

[Write full summary]",

  "structural_claims_analysis": {structural_template},

  "empirical_reality_analysis": {{
{chr(10).join([f'''    "{obs['observation_id']}": {{
      "empirical_observation": "What does this empirical data show?",
      "implied_reality": "What does this reveal about the true state of the entity?",
      "structural_claims_supported": "Which structural claims does this confirm?",
      "structural_claims_contradicted": "Which structural claims does this contradict?"
    }}''' for obs in empirical_evidence])}
  }},

  "contradiction_detection": {{
{chr(10).join([f'''    "pair_{i+1}": {{
      "structural_atom_id": "S0X",
      "empirical_atom_id": "E0X",
      "structural_claim": "What the structural evidence claims",
      "empirical_reality": "What the empirical data shows",
      "contradiction_explanation": "Explain step-by-step WHY these conflict",
      "hidden_risk_revealed": "What does this contradiction tell us about hidden risks?",
      "severity": "critical/high/medium/low"
    }}''' for i in range(max(len(structural_evidence), 3))])}
  }},

  "cross_modal_summary": {{
    "total_structural_claims": {len(structural_evidence)},
    "total_empirical_observations": {len(empirical_evidence)},
    "contradictions_found": 0,
    "most_critical_contradiction": "Which contradiction is most concerning and why?",
    "implications": "What do these contradictions reveal about the investigation?"
  }},

  "cross_modal_flags": [
    {{
      "structural_atom_id": "S02",
      "empirical_atom_id": "E05",
      "detected_in_cycle": {cycle_num},
      "contradiction_description": "Detailed explanation of contradiction"
    }}
  ]
}}

Identify ALL cross-modal contradictions with detailed reasoning.
"""


def build_phase4_request_prompt(
    surviving_hypotheses: list[dict],
    evidence_collected: list[str],
    cycle_num: int
) -> str:
    """
    PHASE 4: REQUEST - Specify evidence needed for next cycle.

    Fourth Gemini call. Takes survivors from Phase 3.
    Focus: Identifying discriminating evidence.

    RESTRUCTURED: Forces detailed reasoning for each evidence request.
    """

    hypotheses_text = "\n".join([
        f"- {h['id']}: {h['name']} (score: {h['score']})"
        for h in surviving_hypotheses
    ])

    # Build pairwise comparison template
    hypothesis_pairs = []
    for i, h1 in enumerate(surviving_hypotheses):
        for h2 in surviving_hypotheses[i+1:]:
            hypothesis_pairs.append(f"{h1['id']}_vs_{h2['id']}")

    discrimination_template = {pair: {
        "hypothesis_1": pair.split("_vs_")[0],
        "hypothesis_2": pair.split("_vs_")[1],
        "key_difference": "What's the key difference between these hypotheses?",
        "crux_question": "What's the one question that would discriminate between them?",
        "evidence_needed": "What specific evidence would answer this crux question?",
        "expected_outcome_if_h1": "If H1 is true, what would we expect to see?",
        "expected_outcome_if_h2": "If H2 is true, what would we expect to see?"
    } for pair in hypothesis_pairs[:5]}  # Limit to top 5 pairs

    return f"""
# PHASE 4: EVIDENCE REQUESTS - What evidence do we need next?

# SURVIVING HYPOTHESES
{hypotheses_text}

# EVIDENCE ALREADY COLLECTED
{', '.join(evidence_collected)}

## TASK
Identify 3-5 pieces of SPECIFIC evidence that would discriminate between survivors.

## OUTPUT FORMAT (JSON):

You MUST provide BOTH detailed thinking AND structured evidence requests:

{{
  "thinking": "WRITE YOUR COMPLETE EVIDENCE REQUEST REASONING - BE EXTREMELY VERBOSE:

### STEP 1: INVESTIGATION STATE ASSESSMENT (Write 300-400 words)
- How many hypotheses survive? [{len(surviving_hypotheses)}]
- Which are the top 2-3 candidates and why?
- What's the biggest remaining uncertainty?
- What's THE crux question that would discriminate between top candidates?
- Why is this the crux - explain in detail?

[Write full state assessment]

### STEP 2: PAIRWISE DISCRIMINATION ANALYSIS (Write 250-350 words PER pair)
For EACH pair of competing hypotheses:

{surviving_hypotheses[0]['id'] if surviving_hypotheses else 'H01'} vs {surviving_hypotheses[1]['id'] if len(surviving_hypotheses) > 1 else 'H02'}:
- Key difference between these hypotheses:
  * [What does H01 claim that H02 doesn't?]
  * [What's the fundamental disagreement?]
- Crux question:
  * [What's THE question that discriminates between them?]
  * [Why is this question the crux?]
- Evidence needed:
  * [What SPECIFIC evidence would answer this question?]
  * [Be exact - not vague]
- Expected outcomes:
  * [If H01 true: what would we see in this evidence?]
  * [If H02 true: what would we see instead?]
  * [How would we know which is correct?]

[REPEAT FOR ALL HYPOTHESIS PAIRS]

### STEP 3: EVIDENCE REQUEST PRIORITIZATION (Write 300-400 words PER request)
For EACH piece of evidence you're requesting:

REQUEST 1:
- Type: [structural/market/news/filing]
- Exact description: [Be SPECIFIC - what exactly do we need?]
- Why this evidence: [What question does it answer?]
- Target hypotheses: [Which hypotheses does this discriminate?]
- Discrimination power explained in detail:
  * [If we get evidence showing X, how does that affect hypotheses?]
  * [If we get evidence showing Y, how does that affect hypotheses?]
  * [Walk through the logic step-by-step]
- Priority justification: [Why is this critical/high/medium priority?]
- Expected timeline: [How quickly can we get this?]

[REPEAT FOR ALL 3-5 EVIDENCE REQUESTS]

### STEP 4: OVERALL STRATEGY (Write 200-300 words)
- What's our evidence collection strategy?
- Which evidence should we prioritize first and why?
- What's our confidence that this evidence will discriminate?
- What's our backup plan if this evidence is inconclusive?

[Write full strategy]",

  "investigation_state": {{
    "surviving_count": {len(surviving_hypotheses)},
    "top_candidates": ["List top 2-3 hypothesis IDs"],
    "main_uncertainty": "What's the biggest remaining question?",
    "current_crux": "What's THE key question that discriminates between top candidates?"
  }},

  "pairwise_discrimination": {discrimination_template},

  "evidence_requests_detailed": {{
    "request_1": {{
      "priority": "critical/high/medium/low",
      "type": "structural/market/news/filing",
      "description": "EXACT evidence needed - be specific, not vague",
      "target_hypotheses": ["H01", "H02"],
      "discrimination_power": "How would this evidence help eliminate or confirm specific hypotheses?",
      "expected_if_h01_true": "If H01 is true, what would this evidence show?",
      "expected_if_h02_true": "If H02 is true, what would this evidence show?",
      "reasoning": "Why is this evidence critical right now?"
    }},
    "request_2": {{
      "priority": "...",
      "type": "...",
      "description": "...",
      "target_hypotheses": ["..."],
      "discrimination_power": "...",
      "expected_if_h0X_true": "...",
      "expected_if_h0Y_true": "...",
      "reasoning": "..."
    }},
    "request_3": {{ ... }}
  }},

  "evidence_requests": [
    {{
      "type": "structural",
      "description": "Specific evidence needed (be exact, not vague)",
      "reason": "How this would discriminate hypotheses"
    }}
  ]
}}

Specify 3-5 critical evidence requests with detailed discrimination reasoning.
"""


def build_phase5_compression_prompt(
    cycle_num: int,
    all_phase_outputs: dict,
    previous_compressed_state: str | None
) -> str:
    """
    PHASE 5: COMPRESS - Self-compress cumulative state.

    Fifth and final Gemini call. Takes outputs from Phases 1-4.
    Focus: Cumulative compression incorporating all prior cycles.

    RESTRUCTURED: Forces structured compression with separate preservation/discard decisions.
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

You MUST provide BOTH detailed thinking AND structured compression:

{{
  "thinking": "WRITE YOUR COMPLETE COMPRESSION REASONING - BE EXTREMELY VERBOSE:

### STEP 1: WHAT TO PRESERVE (Write 400-600 words)
Review ALL information from this cycle and previous cycles:

SURVIVING HYPOTHESES:
For EACH surviving hypothesis:
- Why is this hypothesis still important?
- What key evidence supports it?
- What remaining questions exist about it?
- Why must we preserve this in compressed state?

[Analyze each survivor in detail]

ELIMINATED HYPOTHESES:
For EACH eliminated hypothesis:
- Why remember this elimination?
- What lesson did we learn?
- How does this inform our understanding?
- Why preserve this vs discarding it?

[Analyze each elimination in detail]

CROSS-MODAL FLAGS:
For EACH contradiction:
- Why is this contradiction important?
- What hidden risk does it reveal?
- How does it affect our investigation?
- Why must we preserve this?

[Analyze each flag in detail]

CRUX QUESTION:
- What's THE key remaining question?
- Why is this the crux?
- What evidence would answer it?
- Why is this critical to preserve?

[Write full crux analysis]

### STEP 2: WHAT TO DISCARD (Write 300-400 words)
Identify information we can safely remove:

REDUNDANT DETAILS:
- What details are repeated unnecessarily?
- What can be stated once instead of multiple times?
- Why is it safe to remove these?

[List and justify discarding]

OBVIOUS CONCLUSIONS:
- What's already clear and doesn't need repeating?
- What's implied by other preserved information?
- Why waste space on these?

[List and justify discarding]

VERBOSE REASONING:
- What verbose reasoning can be summarized?
- What step-by-step logic can be compressed to conclusions?
- What's the trade-off in losing this detail?

[List and justify discarding]

### STEP 3: COMPRESSION STRATEGY (Write 300-400 words)
Explain your compression approach:
- What percentage of detail are you preserving? (estimate)
- What areas get the most detail and why?
- What areas get compressed most and why?
- What trade-offs are you making?
- How are you balancing compression vs information retention?
- What's your confidence that compressed state is sufficient?

[Write full strategy explanation]

### STEP 4: HISTORICAL CONTEXT (Write 200-300 words)
Summarize progression across ALL cycles:
- Cycle 1: [What happened?]
- Cycle 2: [What happened?]
- [Continue for all cycles]
- How has investigation evolved?
- What's the trajectory?
- What patterns emerge?

[Write full historical summary]

### STEP 5: FINAL COMPRESSED STATE (Write 400-600 words)
Now write the actual compressed state incorporating:
- ALL surviving hypotheses with scores
- Key eliminations with kill atoms
- Cross-modal flags
- Crux question
- Evidence needed
- Historical progression
- Key insights

[Write full compressed state - this will go in compressed_state field]",

  "compression_decisions": {{
    "information_to_preserve": {{
      "surviving_hypotheses": {{
{chr(10).join([f'''        "H0{i+1}": {{
          "name": "...",
          "score": 0.0,
          "why_preserve": "Why is this hypothesis still important?",
          "key_evidence": ["Which evidence supports this?"],
          "remaining_questions": "What questions remain about this hypothesis?"
        }}''' for i in range(3)])}
      }},
      "eliminated_hypotheses": {{
{chr(10).join([f'''        "H0{i+5}": {{
          "killed_by": "Atom ID",
          "why_preserve": "Why remember this elimination?",
          "lesson_learned": "What did this elimination teach us?"
        }}''' for i in range(2)])}
      }},
      "cross_modal_flags": {{
        "flag_1": {{
          "structural_vs_empirical": "S02 vs E05",
          "why_preserve": "Why is this contradiction important?",
          "implication": "What does this reveal?"
        }}
      }},
      "crux_question": {{
        "question": "What's THE key remaining question?",
        "why_critical": "Why is this the crux?",
        "evidence_needed": "What evidence would answer this?"
      }}
    }},

    "information_to_discard": {{
      "redundant_details": ["What can we safely remove?"],
      "obvious_conclusions": ["What's already clear and doesn't need repeating?"],
      "verbose_reasoning": ["What reasoning can be summarized?"],
      "compression_rationale": "Why is it safe to discard these details?"
    }},

    "compression_strategy": {{
      "preservation_ratio": "What percentage of detail are we preserving?",
      "focus_areas": "What areas get the most detail?",
      "trade_offs": "What trade-offs are we making in compression?"
    }}
  }},

  "historical_context": {{
    "cycle_1_summary": "Brief: what happened in Cycle 1?",
    "cycle_2_summary": "Brief: what happened in Cycle 2?",
    "cycle_progression": "How has the investigation evolved?",
    "eliminated_count_total": 0,
    "surviving_count_current": 0
  }},

  "compressed_state": "CYCLE {cycle_num} CUMULATIVE STATE: [Write compressed state here incorporating ALL prior cycles and this cycle's findings. Include: surviving hypotheses with scores, key eliminations with kill atoms, cross-modal flags, crux question, evidence still needed, historical progression]",

  "key_insights": [
    "Important insight 1 from this cycle",
    "Important insight 2 from this cycle",
    "Important insight 3 from this cycle"
  ]
}}

Create comprehensive compressed state with detailed preservation/discard reasoning.
"""
