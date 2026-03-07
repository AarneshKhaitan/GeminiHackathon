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

    # Load cached investigation - use full_run file (newly generated)
    if entity.lower() == "credit suisse":
        cache_file = Path(__file__).parent / "corpus" / "cached" / "credit_suisse_full_run.json"
    else:
        cache_file = Path(__file__).parent / "corpus" / "cached" / f"{entity.lower().replace(' ', '_')}_full_run.json"

    # Fallback to demo if full_run doesn't exist
    if not cache_file.exists():
        cache_file = Path(__file__).parent / "corpus" / "cached" / "credit_suisse_demo.json"

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
        "text": "Decision: PROMOTE to Tier 3 investigation\n",
        "done": True,
    })

    await asyncio.sleep(5.0)  # Give time to see the escalation decision

    # Tier escalated
    yield sse_event("TIER_ESCALATED", {
        "from": 2,
        "to": 3,
    })

    await asyncio.sleep(3.0)  # Pause before starting investigation cycles

    # Stream cycles
    cycle_history = case_file.get("cycle_history", [])
    active_hypotheses = case_file.get("active_hypotheses", [])
    eliminated_hypotheses = case_file.get("eliminated_hypotheses", [])

    for idx, cycle_data in enumerate(cycle_history):
        cycle_num = cycle_data.get("cycle_num", idx + 1)

        # Cycle started
        yield sse_event("CYCLE_STARTED", {
            "cycle_number": cycle_num,
        })

        await asyncio.sleep(2.0)

        # Simulate reasoning phase
        yield sse_event("AGENT_STATUS_CHANGED", {
            "agent": "investigator",
            "status": "reasoning",
        })

        await asyncio.sleep(8.0)  # Longer reasoning time for demo

        # Hypotheses - show ALL in cycle 1 (active + eliminated), then score updates for subsequent cycles
        if cycle_num == 1:
            # First cycle - generate ALL hypotheses (both surviving and those that will be eliminated)
            all_hypotheses = active_hypotheses + eliminated_hypotheses
            for h in all_hypotheses:
                yield sse_event("HYPOTHESIS_GENERATED", {
                    "hypothesis": {
                        "id": h["id"],
                        "label": h.get("name", h.get("label", "")),
                        "description": h.get("description", ""),
                        "status": "surviving",
                        "initialConfidence": h.get("score", 0.5),
                        "currentConfidence": h.get("score", 0.5),
                        "generatedInCycle": cycle_num,
                        "supportingAtoms": h.get("evidence_chain", []),
                        "contradictingAtoms": [],
                    }
                })
                await asyncio.sleep(1.0)
        else:
            # Subsequent cycles - score hypotheses
            for h in active_hypotheses:
                yield sse_event("HYPOTHESIS_SCORED", {
                    "id": h["id"],
                    "confidence": h.get("score", 0.5),
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

        # Compression
        yield sse_event("COMPRESSION_STARTED", {})
        await asyncio.sleep(3.0)

        compressed_state = cycle_data.get("compressed_state", "")
        if compressed_state:
            yield sse_event("COMPRESSED_REASONING_UPDATED", {
                "text": compressed_state
            })

        token_usage = cycle_data.get("token_usage", {})
        reasoning_tokens = token_usage.get("total", 0)
        compressed_tokens = max(100, len(compressed_state) // 4)

        yield sse_event("COMPRESSION_COMPLETE", {
            "compressed_tokens": compressed_tokens,
            "compression_ratio": round(reasoning_tokens / max(compressed_tokens, 1), 2),
        })

        await asyncio.sleep(2.0)

        # Key insights
        key_insights = cycle_data.get("key_insights", [])
        for insight in key_insights:
            yield sse_event("KEY_INSIGHT_ADDED", {
                "insight": {
                    "cycle": cycle_num,
                    "insight": insight
                }
            })
            await asyncio.sleep(0.8)

        # Token usage
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
