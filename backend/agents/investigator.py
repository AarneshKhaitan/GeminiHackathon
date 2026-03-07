"""
Investigator agent - Core reasoning engine (CRITICAL PATH).

The investigator is the MOST IMPORTANT component in the system.
It performs iterative hypothesis elimination through fresh-context reasoning cycles.

Key Architecture:
- STATELESS: Fresh context window per cycle (prevents context rot)
- SELF-COMPRESSING: Compresses state at end of each cycle
- NO MEMORY: Only knows what compressed state tells it
- PURE FUNCTION: Receives context dict, returns results dict

The investigator fills the 1M context window with THINKING, not data.
This is the core value prop: iterative reasoning > single-pass analysis.
"""

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

    The investigator executes the full investigation cycle:
    1. SCORE: Evaluate hypotheses against evidence
    2. ELIMINATE: Kill contradicted hypotheses with citations
    3. CROSS-MODAL: Flag structural vs empirical contradictions
    4. REQUEST: Specify evidence needed for next cycle
    5. SELF-COMPRESS: Produce cumulative compressed state

    Args:
        context: {
            "trigger": str - Initial trigger signal,
            "entity": str - Entity being investigated,
            "cycle_num": int - Current cycle number (1-indexed),
            "compressed_state": str | None - Self-compressed state from previous cycle,
            "evidence": list[dict] - Tagged evidence observations,
            "active_hypotheses": list[dict] - Currently surviving hypotheses
        }

    Returns:
        {
            "reasoning_trace": str - Detailed reasoning for this cycle,
            "surviving_hypotheses": list[dict] - Hypotheses still under evaluation,
            "eliminated_hypotheses": list[dict] - Killed hypotheses with citations,
            "cross_modal_flags": list[dict] - Structural vs empirical contradictions,
            "evidence_requests": list[dict] - Specific evidence needed next,
            "compressed_state": str - Cumulative self-compressed state,
            "key_insights": list[str] - Important findings from this cycle,
            "token_usage": dict - Input/output/total tokens used
        }

    Example:
        >>> context = {
        ...     "trigger": "SVB CDS spreads spiked to 450bps",
        ...     "entity": "SVB",
        ...     "cycle_num": 1,
        ...     "compressed_state": None,
        ...     "evidence": [],
        ...     "active_hypotheses": []
        ... }
        >>> result = await investigate(context)
        >>> print(len(result["surviving_hypotheses"]))  # 8-10 initial hypotheses
    """

    # Build investigation prompt
    prompt = build_investigation_prompt(
        cycle_num=context["cycle_num"],
        trigger=context["trigger"],
        entity=context["entity"],
        compressed_state=context.get("compressed_state"),
        evidence=context.get("evidence", []),
        active_hypotheses=context.get("active_hypotheses", [])
    )

    # Call Gemini via LangChain client (from Phase 2)
    # Use cached fallback for cycle 1 if API fails (demo robustness)
    result = await call_gemini(
        prompt=prompt,
        fallback_path=str(config.CACHED_FALLBACK_PATH) if context["cycle_num"] == 1 else None
    )

    # Parse response (already JSON from Gemini)
    investigation_output = result["response"]
    token_usage = result["token_usage"]

    # Add token usage to output
    investigation_output["token_usage"] = token_usage

    # Return complete investigation output
    # Orchestrator will parse this and update case file
    return investigation_output
