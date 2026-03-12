"""
Cached investigation playback with simulated streaming.

Loads cached investigation and streams it progressively to frontend
with delays to simulate real-time reasoning.
"""

import asyncio
import json
from pathlib import Path
from typing import AsyncIterator


def sse_event(event_type: str, data: dict) -> str:
    """Format SSE event message."""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


async def playback_cached_investigation(entity: str) -> AsyncIterator[str]:
    """
    Stream cached investigation with simulated delays.

    Args:
        entity: Entity name (e.g., "Credit Suisse")

    Yields:
        SSE-formatted event strings
    """

    # Load cached investigation - use full_run file only
    cache_file = Path(__file__).parent / "corpus" / "cached" / f"{entity.lower().replace(' ', '_')}_full_run.json"

    if not cache_file.exists():
        yield sse_event("ERROR", {"message": f"No cached investigation for {entity}"})
        return

    with open(cache_file, 'r') as f:
        cached_data = json.load(f)

    case_file = cached_data.get("case_file", {})
    trigger = cached_data.get("trigger", {})
    metadata = cached_data.get("metadata", {})

    # Session started
    yield sse_event("SESSION_STARTED", {
        "entity": entity,
        "tier": 2,
        "mode": "cached",
    })

    await asyncio.sleep(2.0)

    # Tier 2 evaluation
    yield sse_event("TIER2_EVALUATION", {
        "text": f"Evaluating trigger signal for {entity}...\n",
        "done": False,
    })

    await asyncio.sleep(3.0)

    yield sse_event("TIER2_EVALUATION", {
        "text": f"Signal magnitude: {trigger.get('magnitude', 'N/A')}\n",
        "done": False,
    })

    await asyncio.sleep(3.0)

    yield sse_event("TIER2_EVALUATION", {
        "text": "Decision: PROMOTE to Tier 4 investigation\n",
        "done": True,
    })

    await asyncio.sleep(5.0)  # Give time to see the escalation decision

    # Tier escalated
    yield sse_event("TIER_ESCALATED", {
        "from": 2,
        "to": 4,
    })

    await asyncio.sleep(3.0)  # Pause before starting investigation cycles

    # Stream cycles
    cycle_history = case_file.get("cycle_history", [])
    active_hypotheses = case_file.get("active_hypotheses", [])
    eliminated_hypotheses = case_file.get("eliminated_hypotheses", [])
    evidence_collected = case_file.get("evidence_collected", [])
    cross_modal_flags = case_file.get("cross_modal_flags", [])
    evidence_pending = case_file.get("evidence_pending", [])

    for idx, cycle_data in enumerate(cycle_history):
        cycle_num = cycle_data.get("cycle_num", idx + 1)

        # Cycle started
        yield sse_event("CYCLE_STARTED", {
            "cycle_number": cycle_num,
        })

        await asyncio.sleep(2.0)

        # Stream evidence atoms collected in this cycle
        cycle_evidence = [atom for atom in evidence_collected if atom.get("collected_in_cycle") == cycle_num]
        for atom in cycle_evidence:
            atom_id = atom.get("atom_id", "")
            atom_type_from_cache = atom.get("type", "market")  # market, filing, news from cache
            brief = atom.get("brief", "")

            # Determine type (empirical vs structural) from atom_id
            if atom_id.startswith("E"):
                atom_type = "empirical"
                source = "Market Data / Filing"
                evidence_type = atom_type_from_cache  # Use cached type: market, filing, or news
            elif atom_id.startswith("S"):
                atom_type = "structural"
                source = "Structural Knowledge"
                evidence_type = "structural"
            else:
                atom_type = "empirical"
                source = "Unknown"
                evidence_type = "market"

            yield sse_event("EVIDENCE_ATOM_ARRIVED", {
                "atom": {
                    "id": atom_id,
                    "type": atom_type,
                    "evidenceType": evidence_type,
                    "observation": brief[:500] if brief else f"Evidence atom {atom_id}",
                    "brief": brief,
                    "timestamp": None,
                    "source": source,
                    "modality": "text",
                    "confidence": 0.85,
                    "supports": [],
                    "contradicts": [],
                    "neutral": [],
                    "novelty": "medium",
                    "cycle": cycle_num,
                }
            })
            await asyncio.sleep(0.5)

        # Simulate reasoning phase
        yield sse_event("AGENT_STATUS_CHANGED", {
            "agent": "investigator",
            "status": "reasoning",
        })

        await asyncio.sleep(8.0)  # Longer reasoning time for demo

        # Hypotheses - show ALL in cycle 1 (no scores), then score updates for subsequent cycles
        if cycle_num == 1:
            # First cycle - generate ALL hypotheses (both surviving and those that will be eliminated)
            # No initial scores - just generate them
            all_hypotheses = active_hypotheses + eliminated_hypotheses
            for h in all_hypotheses:
                yield sse_event("HYPOTHESIS_GENERATED", {
                    "hypothesis": {
                        "id": h["id"],
                        "label": h.get("name", h.get("label", "")),
                        "description": h.get("description", ""),
                        "status": "surviving",
                        "initialConfidence": -1,  # -1 means "not yet scored"
                        "currentConfidence": -1,  # -1 means "not yet scored"
                        "generatedInCycle": cycle_num,
                        "supportingAtoms": h.get("evidence_chain", []),
                        "contradictingAtoms": [],
                    }
                })
                await asyncio.sleep(1.0)
        else:
            # Subsequent cycles - score hypotheses with their actual scores from cache
            for h in active_hypotheses:
                yield sse_event("HYPOTHESIS_SCORED", {
                    "id": h["id"],
                    "confidence": h.get("score", 0.5),
                })
                await asyncio.sleep(0.8)

            # Also score eliminated hypotheses if they're still around in this cycle
            for h in eliminated_hypotheses:
                # If not yet eliminated, show their declining score
                if h.get("killed_in_cycle", 999) > cycle_num:
                    # Calculate declining score based on cycle (starts at 0.5, declines)
                    declining_score = max(0.3, 0.5 - (cycle_num - 1) * 0.05)
                    yield sse_event("HYPOTHESIS_SCORED", {
                        "id": h["id"],
                        "confidence": declining_score,
                    })
                    await asyncio.sleep(0.8)

        # Eliminations (show all eliminations that happened in this cycle)
        for h in eliminated_hypotheses:
            if h.get("killed_in_cycle") == cycle_num:
                yield sse_event("HYPOTHESIS_ELIMINATED", {
                    "id": h["id"],
                    "kill_atom": h.get("killed_by_atom", "N/A"),
                    "kill_reason": h.get("reason", "Contradicted by evidence"),
                    "cycle": cycle_num,
                })
                await asyncio.sleep(1.0)

        # Cross-modal contradictions detected in this cycle
        cycle_cross_modal = [flag for flag in cross_modal_flags if flag.get("detected_in_cycle") == cycle_num]
        for flag in cycle_cross_modal:
            yield sse_event("CROSS_MODAL_DETECTED", {
                "structuralAtomId": flag.get("structural_atom_id", ""),
                "empiricalAtomId": flag.get("empirical_atom_id", ""),
                "cycle": cycle_num,
                "description": flag.get("contradiction_description", "Structural vs empirical conflict detected"),
            })
            await asyncio.sleep(0.8)

        # Evidence pending requests from this cycle
        cycle_pending = [req for req in evidence_pending if any(h in req.get("tests_hypothesis", []) for h in [hyp["id"] for hyp in active_hypotheses])]
        for req in cycle_pending[:2]:  # Limit to avoid spam
            yield sse_event("EVIDENCE_PENDING_ADDED", {
                "item": {
                    "type": req.get("type", "empirical"),
                    "description": req.get("description", ""),
                    "requestedInCycle": cycle_num,
                    "requestedBecause": req.get("reason", ""),
                }
            })
            await asyncio.sleep(0.6)

        # Compression
        yield sse_event("COMPRESSION_STARTED", {})
        await asyncio.sleep(3.0)

        compressed_state = cycle_data.get("compressed_state", "")
        if compressed_state:
            yield sse_event("COMPRESSED_REASONING_UPDATED", {
                "text": compressed_state
            })

        # Token usage calculations
        token_usage = cycle_data.get("token_usage", {})
        input_tokens = token_usage.get("input", 0)
        output_tokens = token_usage.get("output", 0)
        reasoning_tokens = token_usage.get("reasoning", 0)
        total_tokens = token_usage.get("total", 0)
        compressed_tokens = max(100, len(compressed_state) // 4)

        yield sse_event("COMPRESSION_COMPLETE", {
            "compressed_tokens": compressed_tokens,
            "compression_ratio": round(reasoning_tokens / max(compressed_tokens, 1), 2),
        })

        await asyncio.sleep(2.0)

        # Key insights - read from case_file.key_insights and filter by relevance to current cycle
        all_key_insights = case_file.get("key_insights", [])
        # Stream 1-2 key insights per cycle (distribute them across cycles)
        insights_per_cycle = max(1, len(all_key_insights) // len(cycle_history))
        start_idx = (cycle_num - 1) * insights_per_cycle
        end_idx = start_idx + insights_per_cycle
        cycle_insights = all_key_insights[start_idx:end_idx]

        for insight in cycle_insights:
            yield sse_event("KEY_INSIGHT_ADDED", {
                "insight": {
                    "cycle": cycle_num,
                    "insight": insight
                }
            })
            await asyncio.sleep(0.8)

        # Token usage - detailed per-cycle breakdown
        yield sse_event("TOKEN_USAGE_CYCLE", {
            "data": {
                "cycle": cycle_num,
                "investigatorInput": input_tokens,
                "investigatorReasoning": reasoning_tokens,
                "packagerInput": 0,
                "packagerTagging": output_tokens,
                "orchestratorGemini": False,
            }
        })

        yield sse_event("TOKENS_UPDATED", {
            "reasoning": reasoning_tokens,
            "evidence": 0,
            "compressed": compressed_tokens,
        })

        # Cycle complete
        hypotheses_count = cycle_data.get("hypotheses_count", len(active_hypotheses))

        yield sse_event("CYCLE_COMPLETE", {
            "cycle_number": cycle_num,
            "survivors": hypotheses_count,
            "duration_ms": 2000,  # Simulated
            "key_insight": "",
            "evidence_collected": [],
        })

        await asyncio.sleep(2.0)

    # Convergence reached
    alert = case_file.get("alert", {})
    active_hypotheses = case_file.get("active_hypotheses", [])

    yield sse_event("CONVERGENCE_REACHED", {
        "diagnosis": {
            "level": alert.get("level", "CRITICAL"),
            "severity": alert.get("severity", "critical"),
            "headline": f"{len(active_hypotheses)} risk factors identified for {entity}",
            "diagnosis": case_file.get("compressed_reasoning", "Investigation complete."),
            "survivingHypotheses": [h["name"] for h in active_hypotheses],
            "iterativeDiagnosis": f"Completed {len(cycle_history)}-cycle investigation. {len(active_hypotheses)} hypotheses survived.",
        },
    })

    await asyncio.sleep(3.0)

    # Investigation complete
    yield sse_event("INVESTIGATION_COMPLETE", {
        "status": "success",
        "total_cycles": len(cycle_history),
        "total_tokens": metadata.get("total_tokens", 0),
        "duration_seconds": metadata.get("duration_seconds", 0),
    })


if __name__ == "__main__":
    # Test playback
    import sys

    async def test():
        print("Testing cached playback...")
        async for event in playback_cached_investigation("Credit Suisse"):
            sys.stdout.write(event)
            sys.stdout.flush()

    asyncio.run(test())
