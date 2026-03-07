"""
Investigator agent - V2 with PRD-aligned architecture.

Each investigation cycle makes 5 sequential Gemini calls:
1. SCORE + CROSS-MODAL - Evaluate hypotheses against evidence + detect contradictions
2. ELIMINATE - Kill contradicted hypotheses (evidence + score + subsumption)
3. FORWARD SIMULATE - Predict outcomes if hypotheses true (Cycles 3+ only)
4. REQUEST - Specify evidence needed
5. COMPRESS - Self-compress cumulative state

CUMULATIVE CONTEXT STRATEGY:
Each phase receives the FULL output from all previous phases as input.
"""

import json
from gemini.client import call_gemini
from gemini.prompts.investigation_phases_v2 import (
    build_phase1_score_and_crossmodal_prompt,
    build_phase2_elimination_prompt,
    build_phase3_forward_simulation_prompt,
    build_phase4_request_prompt,
    build_phase5_compression_prompt
)


async def investigate(context: dict) -> dict:
    """
    Run one complete 5-phase investigation cycle with cumulative context.

    Each phase is a separate Gemini call that receives ALL previous phase outputs.
    Phases: SCORE+CROSSMODAL → ELIMINATE → FORWARD SIMULATE → REQUEST → COMPRESS

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
            "forward_simulations": list[dict],
            "compressed_state": str,
            "key_insights": list[str],
            "token_usage": dict,
            "phase_outputs": dict
        }
    """

    phase_outputs = {}
    total_tokens = {"input": 0, "output": 0, "reasoning": 0, "total": 0}

    # =========================================================================
    # PHASE 1: SCORE + CROSS-MODAL - Combined scoring and contradiction detection
    # =========================================================================
    print(f"  Phase 1/5: Scoring + Cross-Modal Analysis...")
    phase1_prompt = build_phase1_score_and_crossmodal_prompt(
        cycle_num=context["cycle_num"],
        trigger=context["trigger"],
        entity=context["entity"],
        compressed_state=context.get("compressed_state"),
        evidence=context.get("evidence", []),
        active_hypotheses=context.get("active_hypotheses", [])
    )

    phase1_result = await call_gemini(phase1_prompt)
    phase1_output = phase1_result["response"]
    phase_outputs["phase1_score_crossmodal"] = phase1_output

    # Track tokens
    total_tokens["input"] += phase1_result["token_usage"]["input_tokens"]
    total_tokens["output"] += phase1_result["token_usage"]["output_tokens"]
    total_tokens["reasoning"] += phase1_result["token_usage"].get("reasoning_tokens", 0)

    # Phase 1 outputs different keys for Cycle 1 vs Cycle 2+
    if context["cycle_num"] == 1:
        hypotheses_key = "surviving_hypotheses"
        hypotheses_count = len(phase1_output.get(hypotheses_key, []))
        cross_modal_count = 0
        print(f"    ✓ {hypotheses_count} hypotheses generated")
    else:
        hypotheses_key = "scored_hypotheses"
        hypotheses_count = len(phase1_output.get(hypotheses_key, []))
        cross_modal_count = len(phase1_output.get("cross_modal_flags", []))
        print(f"    ✓ {hypotheses_count} hypotheses scored")
        print(f"    ✓ {cross_modal_count} cross-modal flags detected")

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
    forward_simulations=[],
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
            "forward_simulations": [],
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
Based on the scored hypotheses from Phase 1, identify which ones MUST be eliminated.

{build_phase2_elimination_prompt(
    scored_hypotheses=phase1_output.get("scored_hypotheses", []),
    evidence=context.get("evidence", []),
    cross_modal_flags=phase1_output.get("cross_modal_flags", []),
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

    gemini_eliminations = len(eliminated) - len(low_score_eliminations)
    print(f"    ✓ {len(eliminated)} total eliminations:")
    print(f"      - {gemini_eliminations} evidence/subsumption-based (from Gemini)")
    print(f"      - {len(low_score_eliminations)} score-based (< 0.2 threshold)")
    print(f"    ✓ {len(final_survivors)} survivors")
    print(f"    ✓ Token usage: {phase2_result['token_usage']['input_tokens']} in, {phase2_result['token_usage']['output_tokens']} out")

    # =========================================================================
    # PHASE 3: FORWARD SIMULATE - Predict outcomes (Cycles 3+ only)
    # =========================================================================
    forward_simulations = []

    if context["cycle_num"] >= 3:
        print(f"  Phase 3/5: Forward simulation...")

        # Build prompt with Phase 1 + 2 FULL CONTEXT
        phase3_prompt = f"""
# PHASE 3: FORWARD SIMULATION

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
Simulate forward: what happens next if each surviving hypothesis is true?

{build_phase3_forward_simulation_prompt(
    surviving_hypotheses=phase2_output.get("surviving_hypotheses", []),
    evidence=context.get("evidence", []),
    cycle_num=context["cycle_num"]
)}
"""

        phase3_result = await call_gemini(phase3_prompt)
        phase3_output = phase3_result["response"]
        phase_outputs["phase3_forward_sim"] = phase3_output

        total_tokens["input"] += phase3_result["token_usage"]["input_tokens"]
        total_tokens["output"] += phase3_result["token_usage"]["output_tokens"]
        total_tokens["reasoning"] += phase3_result["token_usage"].get("reasoning_tokens", 0)

        forward_simulations = phase3_output.get("forward_simulations", [])

        print(f"    ✓ {len(forward_simulations)} forward simulations")
        print(f"    ✓ Token usage: {phase3_result['token_usage']['input_tokens']} in, {phase3_result['token_usage']['output_tokens']} out")
    else:
        print(f"  Phase 3/5: Forward simulation (skipped - Cycle {context['cycle_num']} < 3)")

    # =========================================================================
    # PHASE 4: REQUEST - Evidence needs
    # =========================================================================
    print(f"  Phase 4/5: Requesting evidence...")

    # Build prompt with all previous phases
    evidence_collected = [obs['observation_id'] for obs in context.get("evidence", [])]

    if context["cycle_num"] >= 3:
        # Include forward simulations
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

## Phase 3 Output (Forward Simulations)
{json.dumps(phase_outputs.get("phase3_forward_sim", {}), indent=2)}

# YOUR TASK
Based on all previous phases, identify SPECIFIC evidence to test the predictions from forward simulation.

{build_phase4_request_prompt(
    surviving_hypotheses=phase2_output.get("surviving_hypotheses", []),
    forward_simulations=forward_simulations,
    evidence_collected=evidence_collected,
    cycle_num=context["cycle_num"]
)}
"""
    else:
        # No forward simulations yet
        phase4_prompt = f"""
# PHASE 4: EVIDENCE REQUESTS

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
Based on all previous phases, identify SPECIFIC evidence to discriminate between surviving hypotheses.

{build_phase4_request_prompt(
    surviving_hypotheses=phase2_output.get("surviving_hypotheses", []),
    forward_simulations=[],
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

    # Build prompt with ALL previous phase FULL CONTEXT
    all_phase_outputs = {
        "scored_hypotheses": phase1_output.get("scored_hypotheses", []),
        "cross_modal_flags": phase1_output.get("cross_modal_flags", []),
        "eliminated_hypotheses": phase2_output.get("eliminated_hypotheses", []),
        "surviving_hypotheses": phase2_output.get("surviving_hypotheses", []),
        "forward_simulations": forward_simulations,
        "evidence_requests": phase4_output.get("evidence_requests", [])
    }

    # Build comprehensive context string
    if context["cycle_num"] >= 3:
        full_context = f"""
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
### Output:
{json.dumps(phase_outputs.get("phase3_forward_sim", {}), indent=2)}

## Phase 4 Context
### Output:
{json.dumps(phase4_output, indent=2)}
"""
    else:
        full_context = f"""
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

## Phase 4 Context
### Output:
{json.dumps(phase4_output, indent=2)}
"""

    phase5_prompt = f"""
# PHASE 5: SELF-COMPRESSION

You are in Cycle {context["cycle_num"]} for {context["entity"]}.

# COMPLETE CONTEXT FROM ALL PHASES (INPUT + OUTPUT FOR EACH)

{full_context}

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
        "cross_modal_flags": phase1_output.get("cross_modal_flags", []),
        "forward_simulations": forward_simulations,
        "evidence_requests": phase4_output.get("evidence_requests", []),
        "compressed_state": phase5_output.get("compressed_state", ""),
        "key_insights": phase5_output.get("key_insights", []),
        "token_usage": total_tokens,
        "phase_outputs": phase_outputs
    }
