"""
Phase 7: FastAPI REST Endpoints with SSE Streaming

Exposes the LangGraph investigation engine to the frontend.

Endpoints:
- POST /api/investigate — Live LangGraph execution with SSE streaming
- POST /api/investigate/cached — Pre-cached demo fallback (1-min)
- GET /api/case/{entity} — Get current case file
- GET /api/health — Health check

Hybrid Mode:
- Demo mode: Use cached results for 1-min demo
- Judge mode: Run full LangGraph with real Gemini API calls
"""

import asyncio
import json
import time
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Phase 6: LangGraph
from graph.investigation_graph import compiled_graph

# Playback
from playback import playback_cached_investigation

# Config
from config import MAX_CYCLES, CONVERGENCE_THRESHOLD

# =============================================================================
# FASTAPI APP
# =============================================================================

app = FastAPI(
    title="IHEE Investigation Engine",
    description="Iterative Hypothesis Elimination Engine - Phase 7",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hackathon demo - allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class InvestigateRequest(BaseModel):
    entity: str
    trigger: dict
    mode: str = "demo"  # "demo" or "judge"


class CachedInvestigateRequest(BaseModel):
    entity: str


# =============================================================================
# CACHED FALLBACK
# =============================================================================

CACHED_DIR = Path(__file__).parent / "corpus" / "cached"


def load_cached_run(entity: str) -> dict | None:
    """Load pre-cached investigation run from corpus/cached/"""
    cache_file = CACHED_DIR / f"{entity.lower().replace(' ', '_')}_full_run.json"

    if not cache_file.exists():
        # Try SVB fallback
        cache_file = CACHED_DIR / "svb_full_run.json"

    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text())
        except Exception:
            return None

    return None


# =============================================================================
# SSE EVENT HELPERS
# =============================================================================

def sse_event(event_type: str, data: dict) -> str:
    """Format SSE event message."""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


async def sse_heartbeat() -> str:
    """SSE keepalive message."""
    return ": heartbeat\n\n"


# =============================================================================
# LANGGRAPH EXECUTION WITH SSE STREAMING
# =============================================================================

async def stream_investigation(
    entity: str,
    trigger: dict,
    mode: str = "demo"
) -> AsyncIterator[str]:
    """
    Execute LangGraph investigation and stream progress via SSE.

    Args:
        entity: Entity name (e.g., "Credit Suisse")
        trigger: Trigger signal dict
        mode: "demo" (fast) or "judge" (full API calls)

    Yields:
        SSE-formatted event strings
    """

    # Session started
    yield sse_event("SESSION_STARTED", {
        "entity": entity,
        "tier": 2,
        "mode": mode,
    })

    await asyncio.sleep(0.1)

    # Initialize state
    initial_state = {
        "trigger_signal": trigger,
        "entity": entity,
        "current_cycle": 0,
        "max_cycles": MAX_CYCLES,
    }

    # Tier 2 evaluation started
    yield sse_event("TIER2_EVALUATION", {
        "text": f"Evaluating trigger signal for {entity}...\n",
        "done": False,
    })

    await asyncio.sleep(0.2)

    try:
        # Execute LangGraph
        # NOTE: LangGraph streams events internally
        # For now, we run synchronously and emit events at node boundaries

        # Stream events during execution
        async for event in execute_graph_with_streaming(initial_state):
            yield event

        # Investigation complete
        yield sse_event("INVESTIGATION_COMPLETE", {
            "status": "success",
        })

    except Exception as e:
        yield sse_event("ERROR", {
            "message": str(e),
            "type": "investigation_error",
        })


async def execute_graph_with_streaming(initial_state: dict) -> AsyncIterator[str]:
    """
    Execute LangGraph and stream progress events.

    This wraps the graph execution and emits SSE events at key points.
    """

    # Track state
    case_file = None
    current_cycle = 0

    # Execute graph (async)
    result = await compiled_graph.ainvoke(initial_state)

    # Extract final state
    case_file = result.get("case_file", {})
    tier2_decision = result.get("tier2_decision", {})

    # Emit tier2 decision
    if tier2_decision:
        decision = tier2_decision.get("decision", "demote")
        confidence = tier2_decision.get("confidence", 0.0)

        yield sse_event("TIER2_EVALUATION", {
            "text": f"Decision: {decision} (confidence: {confidence})\n",
            "done": True,
        })

        await asyncio.sleep(0.2)

        if decision == "promote":
            yield sse_event("TIER_ESCALATED", {
                "from": 2,
                "to": 4,
            })

            await asyncio.sleep(0.3)

    # If investigation was demoted, stop here
    if not case_file:
        yield sse_event("INVESTIGATION_DEMOTED", {
            "reason": "Tier 2 evaluation determined signal does not warrant investigation",
        })
        return

    # Stream case file cycles
    cycle_history = case_file.get("cycle_history", [])

    for cycle_data in cycle_history:
        cycle_num = cycle_data.get("cycle_num", 0)

        # Cycle started
        yield sse_event("CYCLE_STARTED", {
            "cycle_number": cycle_num,
        })

        await asyncio.sleep(0.1)

        # Hypotheses (surviving)
        surviving = cycle_data.get("surviving_hypotheses", [])
        eliminated = cycle_data.get("eliminated_hypotheses", [])

        for h in surviving:
            yield sse_event("HYPOTHESIS_SCORED", {
                "id": h["id"],
                "confidence": h.get("score", 0.5),
            })

            await asyncio.sleep(0.05)

        # Eliminations
        for h in eliminated:
            yield sse_event("HYPOTHESIS_ELIMINATED", {
                "id": h["id"],
                "kill_atom": h.get("killed_by_atom", ""),
                "kill_reason": h.get("reason", ""),
                "cycle": cycle_num,
            })

            await asyncio.sleep(0.05)

        # Token usage
        token_usage = cycle_data.get("token_usage", {})
        if token_usage:
            yield sse_event("TOKENS_UPDATED", {
                "reasoning": token_usage.get("total", 0),
                "evidence": 0,
                "compressed": 0,
            })

        # Cycle complete
        yield sse_event("CYCLE_COMPLETE", {
            "cycle_number": cycle_num,
            "survivors": len(surviving),
            "duration_ms": 1000,  # Mock duration
            "key_insight": cycle_data.get("key_insights", [""])[0] if cycle_data.get("key_insights") else "",
        })

        await asyncio.sleep(0.2)

    # Convergence reached
    alert = case_file.get("alert", {})

    yield sse_event("CONVERGENCE_REACHED", {
        "diagnosis": {
            "level": alert.get("level", "MONITOR"),
            "severity": alert.get("severity", "medium"),
            "headline": alert.get("summary", "Investigation complete"),
            "diagnosis": case_file.get("compressed_reasoning", ""),
            "survivingHypotheses": [h["name"] for h in case_file.get("active_hypotheses", [])],
        },
    })


# =============================================================================
# REST ENDPOINTS
# =============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "IHEE Investigation Engine",
        "version": "1.0.0",
        "langgraph": "compiled",
    }


@app.post("/api/investigate")
async def investigate_live(request: InvestigateRequest):
    """
    Live LangGraph investigation with SSE streaming.

    Args:
        request: InvestigateRequest with entity, trigger, mode

    Returns:
        StreamingResponse with SSE events
    """

    return StreamingResponse(
        stream_investigation(
            entity=request.entity,
            trigger=request.trigger,
            mode=request.mode,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable proxy buffering
        }
    )


@app.post("/api/investigate/cached")
async def investigate_cached(request: CachedInvestigateRequest):
    """
    Cached investigation playback - streams cached investigation with simulated delays.

    This endpoint provides a 1-minute demo experience by playing back a pre-computed
    investigation with realistic timing delays to simulate real-time reasoning.

    Args:
        request: CachedInvestigateRequest with entity

    Returns:
        StreamingResponse with SSE events
    """

    return StreamingResponse(
        playback_cached_investigation(entity=request.entity),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@app.get("/api/case/{entity}")
async def get_case_file(entity: str):
    """
    Get current case file for an entity.

    NOTE: This requires a persistent store (Redis/DB).
    For Phase 7, we return a mock response.

    Args:
        entity: Entity name

    Returns:
        Case file JSON
    """

    # TODO: Implement persistent case file storage
    return {
        "entity": entity,
        "status": "NOT_FOUND",
        "message": "Case file storage not yet implemented. Use /api/investigate to start a new investigation.",
    }


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    print("=" * 80)
    print("IHEE Investigation Engine - Phase 7")
    print("=" * 80)
    print("LangGraph: ✓ Compiled")
    print("Endpoints:")
    print("  POST /api/investigate — Live investigation with SSE")
    print("  POST /api/investigate/cached — Cached demo fallback")
    print("  GET /api/case/{entity} — Get case file")
    print("  GET /api/health — Health check")
    print("=" * 80)
    print("Starting server on http://localhost:8000")
    print("=" * 80)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
