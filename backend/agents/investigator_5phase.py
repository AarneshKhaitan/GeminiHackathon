"""
Investigator agent - Core reasoning engine with 5-phase analysis.

Each investigation cycle makes 5 separate Gemini calls:
1. SCORE - Evaluate hypotheses against evidence
2. ELIMINATE - Kill contradicted hypotheses
3. CROSS-MODAL - Flag structural vs empirical contradictions
4. REQUEST - Specify evidence needed
5. COMPRESS - Self-compress cumulative state

CUMULATIVE CONTEXT STRATEGY:
Each phase receives the FULL output from all previous phases as input.
This leverages the 1M token input limit to maximize reasoning detail.
- Phase 1: Base context
- Phase 2: Base + Phase 1 full output
- Phase 3: Base + Phase 1 + Phase 2 outputs
- Phase 4: Base + Phase 1 + 2 + 3 outputs
- Phase 5: Base + Phase 1 + 2 + 3 + 4 outputs

This gives maximum detail and traceability at each reasoning step.
"""

import json
from gemini.client import call_gemini
from gemini.prompts.investigation_phases import (
    build_phase1_scoring_prompt,
    build_phase2_elimination_prompt,
    build_phase3_crossmodal_prompt,
    build_phase4_request_prompt,
    build_phase5_compression_prompt
)


async def investigate(context: dict) -> dict:
    """
    Run one complete 5-phase investigation cycle with cumulative context.

    Each phase is a separate Gemini call that receives ALL previous phase outputs.
    Phases: SCORE → ELIMINATE → CROSS-MODAL → REQUEST → COMPRESS

    Args:
        context: {
            "trigger": str,
            "entity": str,
            "cycle_num": int,
            "compressed_state": str | None,
            "evidence": list[dict],
            "active_hypotheses": list[dict]
        }

    Returns:
        {
            "surviving_hypotheses": list[dict],
            "eliminated_hypotheses": list[dict],
            "cross_modal_flags": list[dict],
            "evidence_requests": list[dict],
            "compressed_state": str,
            "key_insights": list[str],
            "token_usage": dict,
            "phase_outputs": dict  # Detailed outputs from each phase
        }
    """

    phase_outputs = {}
    total_tokens = {"input": 0, "output": 0, "reasoning": 0, "total": 0}

    # =========================================================================
    # PHASE 1: SCORE - Evaluate hypotheses against evidence
    # =========================================================================
    print(f"  Phase 1/5: Scoring hypotheses...")
    phase1_prompt = build_phase1_scoring_prompt(
        cycle_num=context["cycle_num"],
        trigger=context["trigger"],
        entity=context["entity"],
        compressed_state=context.get("compressed_state"),
        evidence=context.get("evidence", []),
        active_hypotheses=context.get("active_hypotheses", [])
    )

    phase1_result = await call_gemini(phase1_prompt)
    phase1_output = phase1_result["response"]
    phase_outputs["phase1_scoring"] = phase1_output

    # Track tokens
    total_tokens["input"] += phase1_result["token_usage"]["input_tokens"]
    total_tokens["output"] += phase1_result["token_usage"]["output_tokens"]
    total_tokens["reasoning"] += phase1_result["token_usage"].get("reasoning_tokens", 0)

    # Phase 1 outputs different keys for Cycle 1 vs Cycle 2+
    hypotheses_key = "surviving_hypotheses" if context["cycle_num"] == 1 else "scored_hypotheses"
    hypotheses_count = len(phase1_output.get(hypotheses_key, []))

    print(f"    ✓ {hypotheses_count} hypotheses {('generated' if context['cycle_num'] == 1 else 'scored')}")
    print(f"    ✓ Phase 1 output: {len(json.dumps(phase1_output))} chars")
    print(f"    ✓ Token usage: {phase1_result['token_usage']['input_tokens']} in, {phase1_result['token_usage']['output_tokens']} out")

    # For Cycle 1, we only do Phase 1 (hypothesis generation) and Phase 4 (evidence requests)
    if context["cycle_num"] == 1:
        # PHASE 4: REQUEST - Evidence needs for cycle 2
        print(f"  Phase 4/5: Requesting evidence...")

        # Build prompt with Phase 1 full output as context
        phase4_prompt = f"""
# PHASE 4: EVIDENCE REQUESTS

You have just completed Phase 1 (Hypothesis Generation) for {context["entity"]}.

# PHASE 1 COMPLETE OUTPUT
Here is the FULL output from Phase 1:
{json.dumps(phase1_output, indent=2)}

# YOUR TASK
Based on the hypotheses generated in Phase 1, identify 3-5 pieces of SPECIFIC evidence needed to begin testing these hypotheses in Cycle 2.

{build_phase4_request_prompt(
    surviving_hypotheses=phase1_output.get("surviving_hypotheses", []),
    evidence_collected=[],
    cycle_num=context["cycle_num"]
)}
"""

        phase4_result = await call_gemini(phase4_prompt)
        phase4_output = phase4_result["response"]
        phase_outputs["phase4_request"] = phase4_output

        total_tokens["input"] += phase4_result["token_usage"]["input_tokens"]
        total_tokens["output"] += phase4_result["token_usage"]["output_tokens"]
        total_tokens["reasoning"] += phase4_result["token_usage"].get("reasoning_tokens", 0)

        print(f"    ✓ {len(phase4_output.get('evidence_requests', []))} evidence requests")
        print(f"    ✓ Token usage: {phase4_result['token_usage']['input_tokens']} in, {phase4_result['token_usage']['output_tokens']} out")

        # Simple compression for cycle 1
        compressed_state = f"CYCLE 1: Generated {len(phase1_output.get('surviving_hypotheses', []))} hypotheses. Need evidence: {[r.get('description', '') for r in phase4_output.get('evidence_requests', [])[:3]]}"

        total_tokens["total"] = total_tokens["input"] + total_tokens["output"]

        return {
            "surviving_hypotheses": phase1_output.get("surviving_hypotheses", []),
            "eliminated_hypotheses": [],
            "cross_modal_flags": [],
            "evidence_requests": phase4_output.get("evidence_requests", []),
            "compressed_state": compressed_state,
            "key_insights": [],
            "token_usage": total_tokens,
            "phase_outputs": phase_outputs
        }

    # =========================================================================
    # PHASE 2: ELIMINATE - Kill contradicted hypotheses
    # =========================================================================
    print(f"  Phase 2/5: Identifying eliminations...")

    # Build prompt with Phase 1 FULL CONTEXT (input + output)
    phase2_prompt = f"""
# PHASE 2: ELIMINATION

You are in Cycle {context["cycle_num"]} for {context["entity"]}.

# PHASE 1 COMPLETE CONTEXT

## Phase 1 Input (The Original Task)
{phase1_prompt}

## Phase 1 Output (The Results)
{json.dumps(phase1_output, indent=2)}

# YOUR TASK
Based on the scored hypotheses from Phase 1, identify which ones MUST be eliminated due to contradicting evidence.

{build_phase2_elimination_prompt(
    scored_hypotheses=phase1_output.get("scored_hypotheses", []),
    evidence=context.get("evidence", []),
    cycle_num=context["cycle_num"]
)}
"""

    phase2_result = await call_gemini(phase2_prompt)
    phase2_output = phase2_result["response"]
    phase_outputs["phase2_elimination"] = phase2_output

    total_tokens["input"] += phase2_result["token_usage"]["input_tokens"]
    total_tokens["output"] += phase2_result["token_usage"]["output_tokens"]
    total_tokens["reasoning"] += phase2_result["token_usage"].get("reasoning_tokens", 0)

    # Post-process: Add score-based eliminations (score < 0.2)
    eliminated = list(phase2_output.get("eliminated_hypotheses", []))
    surviving = list(phase2_output.get("surviving_hypotheses", []))

    # Check each survivor's score
    low_score_eliminations = []
    final_survivors = []

    for hyp in surviving:
        if hyp.get("score", 1.0) < 0.2:
            # Eliminate due to low confidence
            low_score_eliminations.append({
                "id": hyp["id"],
                "name": hyp["name"],
                "killed_by_atom": "low_confidence",
                "killed_in_cycle": context["cycle_num"],
                "reason": f"Score {hyp['score']:.2f} dropped below 0.2 threshold, indicating hypothesis is highly implausible"
            })
        else:
            final_survivors.append(hyp)

    # Merge eliminations
    eliminated.extend(low_score_eliminations)

    # Update phase2_output with final lists
    phase2_output["eliminated_hypotheses"] = eliminated
    phase2_output["surviving_hypotheses"] = final_survivors

    gemini_eliminations = len(phase2_output.get("eliminated_hypotheses", [])) - len(low_score_eliminations)
    print(f"    ✓ {len(eliminated)} total eliminations:")
    print(f"      - {gemini_eliminations} evidence-based (from Gemini)")
    print(f"      - {len(low_score_eliminations)} score-based (< 0.2 threshold)")
    print(f"    ✓ {len(final_survivors)} survivors")
    print(f"    ✓ Token usage: {phase2_result['token_usage']['input_tokens']} in, {phase2_result['token_usage']['output_tokens']} out")

    # =========================================================================
    # PHASE 3: CROSS-MODAL - Flag contradictions
    # =========================================================================
    print(f"  Phase 3/5: Cross-modal analysis...")

    # Build prompt with Phase 1 + 2 FULL CONTEXT (inputs + outputs)
    phase3_prompt = f"""
# PHASE 3: CROSS-MODAL ANALYSIS

You are in Cycle {context["cycle_num"]} for {context["entity"]}.

# COMPLETE CONTEXT FROM PREVIOUS PHASES

## Phase 1 Input
{phase1_prompt}

## Phase 1 Output
{json.dumps(phase1_output, indent=2)}

## Phase 2 Input
{phase2_prompt}

## Phase 2 Output
{json.dumps(phase2_output, indent=2)}

# YOUR TASK
Based on the surviving hypotheses from Phase 2, identify contradictions between structural and empirical evidence.

{build_phase3_crossmodal_prompt(
    surviving_hypotheses=phase2_output.get("surviving_hypotheses", []),
    evidence=context.get("evidence", []),
    cycle_num=context["cycle_num"]
)}
"""

    phase3_result = await call_gemini(phase3_prompt)
    phase3_output = phase3_result["response"]
    phase_outputs["phase3_crossmodal"] = phase3_output

    total_tokens["input"] += phase3_result["token_usage"]["input_tokens"]
    total_tokens["output"] += phase3_result["token_usage"]["output_tokens"]
    total_tokens["reasoning"] += phase3_result["token_usage"].get("reasoning_tokens", 0)

    print(f"    ✓ {len(phase3_output.get('cross_modal_flags', []))} cross-modal flags")
    print(f"    ✓ Token usage: {phase3_result['token_usage']['input_tokens']} in, {phase3_result['token_usage']['output_tokens']} out")

    # =========================================================================
    # PHASE 4: REQUEST - Evidence needs
    # =========================================================================
    print(f"  Phase 4/5: Requesting evidence...")

    # Build prompt with Phase 1 + 2 + 3 FULL CONTEXT (inputs + outputs)
    evidence_collected = [obs['observation_id'] for obs in context.get("evidence", [])]
    phase4_prompt = f"""
# PHASE 4: EVIDENCE REQUESTS

You are in Cycle {context["cycle_num"]} for {context["entity"]}.

# COMPLETE CONTEXT FROM ALL PREVIOUS PHASES

## Phase 1 Input
{phase1_prompt}

## Phase 1 Output
{json.dumps(phase1_output, indent=2)}

## Phase 2 Input
{phase2_prompt}

## Phase 2 Output
{json.dumps(phase2_output, indent=2)}

## Phase 3 Input
{phase3_prompt}

## Phase 3 Output
{json.dumps(phase3_output, indent=2)}

# YOUR TASK
Based on all previous phases, identify what SPECIFIC evidence is needed to discriminate between surviving hypotheses.

{build_phase4_request_prompt(
    surviving_hypotheses=phase2_output.get("surviving_hypotheses", []),
    evidence_collected=evidence_collected,
    cycle_num=context["cycle_num"]
)}
"""

    phase4_result = await call_gemini(phase4_prompt)
    phase4_output = phase4_result["response"]
    phase_outputs["phase4_request"] = phase4_output

    total_tokens["input"] += phase4_result["token_usage"]["input_tokens"]
    total_tokens["output"] += phase4_result["token_usage"]["output_tokens"]
    total_tokens["reasoning"] += phase4_result["token_usage"].get("reasoning_tokens", 0)

    print(f"    ✓ {len(phase4_output.get('evidence_requests', []))} evidence requests")
    print(f"    ✓ Token usage: {phase4_result['token_usage']['input_tokens']} in, {phase4_result['token_usage']['output_tokens']} out")

    # =========================================================================
    # PHASE 5: COMPRESS - Self-compress state
    # =========================================================================
    print(f"  Phase 5/5: Compressing state...")

    # Build prompt with ALL previous phase FULL CONTEXT (inputs + outputs)
    all_phase_outputs = {
        "scored_hypotheses": phase1_output.get("scored_hypotheses", []),
        "eliminated_hypotheses": phase2_output.get("eliminated_hypotheses", []),
        "surviving_hypotheses": phase2_output.get("surviving_hypotheses", []),
        "cross_modal_flags": phase3_output.get("cross_modal_flags", []),
        "evidence_requests": phase4_output.get("evidence_requests", [])
    }

    phase5_prompt = f"""
# PHASE 5: SELF-COMPRESSION

You are in Cycle {context["cycle_num"]} for {context["entity"]}.

# COMPLETE CONTEXT FROM ALL PHASES (INPUT + OUTPUT FOR EACH)

## Phase 1 Context
### Input:
{phase1_prompt}
### Output:
{json.dumps(phase1_output, indent=2)}

## Phase 2 Context
### Input:
{phase2_prompt}
### Output:
{json.dumps(phase2_output, indent=2)}

## Phase 3 Context
### Input:
{phase3_prompt}
### Output:
{json.dumps(phase3_output, indent=2)}

## Phase 4 Context
### Input:
{phase4_prompt}
### Output:
{json.dumps(phase4_output, indent=2)}

# YOUR TASK
Compress ALL findings from this cycle into a cumulative compressed state.

{build_phase5_compression_prompt(
    cycle_num=context["cycle_num"],
    all_phase_outputs=all_phase_outputs,
    previous_compressed_state=context.get("compressed_state")
)}
"""

    phase5_result = await call_gemini(phase5_prompt)
    phase5_output = phase5_result["response"]
    phase_outputs["phase5_compression"] = phase5_output

    total_tokens["input"] += phase5_result["token_usage"]["input_tokens"]
    total_tokens["output"] += phase5_result["token_usage"]["output_tokens"]
    total_tokens["reasoning"] += phase5_result["token_usage"].get("reasoning_tokens", 0)
    total_tokens["total"] = total_tokens["input"] + total_tokens["output"]

    print(f"    ✓ Compressed state: {len(phase5_output.get('compressed_state', ''))} chars")
    print(f"    ✓ Token usage: {phase5_result['token_usage']['input_tokens']} in, {phase5_result['token_usage']['output_tokens']} out")

    # =========================================================================
    # RETURN COMBINED OUTPUTS
    # =========================================================================
    print(f"  ✓ Total tokens: {total_tokens['input']:,} in, {total_tokens['output']:,} out, {total_tokens['reasoning']:,} reasoning")

    return {
        "surviving_hypotheses": phase2_output.get("surviving_hypotheses", []),
        "eliminated_hypotheses": phase2_output.get("eliminated_hypotheses", []),
        "cross_modal_flags": phase3_output.get("cross_modal_flags", []),
        "evidence_requests": phase4_output.get("evidence_requests", []),
        "compressed_state": phase5_output.get("compressed_state", ""),
        "key_insights": phase5_output.get("key_insights", []),
        "token_usage": total_tokens,
        "phase_outputs": phase_outputs
    }
