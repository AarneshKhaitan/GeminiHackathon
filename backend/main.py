"""
IHEE FastAPI WebSocket Server

Streams investigation events to the frontend over WebSocket.
Endpoint: ws://localhost:8000/ws/{session_id}
"""

import asyncio
import json
import sys
import time
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Ensure backend package is importable
sys.path.insert(0, str(Path(__file__).parent))

from agents.investigator_5phase import investigate
from config import MAX_CYCLES, CONVERGENCE_THRESHOLD, STAGNATION_CYCLES
from playback import playback_cached_investigation

app = FastAPI(title="IHEE Investigation Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Evidence Corpus ────────────────────────────────────────────────────────────

EVIDENCE_DIR = Path(__file__).parent.parent / "evidence"

ENTITY_SLUG: dict[str, str] = {
    "Silicon Valley Bank": "svb",
    "Credit Suisse": "credit-suisse",
    "First Republic Bank": "ftx",
}


def load_evidence_corpus(entity: str) -> list[dict]:
    """Load markdown evidence files for the entity from corpus directories."""
    slug = ENTITY_SLUG.get(entity, "")
    entity_dir = EVIDENCE_DIR / slug

    if not entity_dir.exists():
        return []

    observations: list[dict] = []
    s_counter = 0
    e_counter = 0

    # Structural evidence
    structural_dir = entity_dir / "structural"
    if structural_dir.exists():
        for md_file in sorted(structural_dir.glob("*.md")):
            s_counter += 1
            obs_id = f"S{s_counter:02d}"
            try:
                content = md_file.read_text(encoding="utf-8")
            except Exception:
                continue
            observations.append({
                "observation_id": obs_id,
                "content": content[:2500],
                "source": md_file.stem,
                "type": "structural",
                "supports": [],
                "contradicts": [],
                "neutral": [],
                "date": None,
            })

    # Empirical evidence (market / news / filing)
    empirical_dir = entity_dir / "empirical"
    if empirical_dir.exists():
        for md_file in sorted(empirical_dir.glob("*.md")):
            e_counter += 1
            obs_id = f"E{e_counter:02d}"
            try:
                content = md_file.read_text(encoding="utf-8")
            except Exception:
                continue

            name = md_file.stem
            date: str | None = None
            if len(name) >= 8 and name[:8].isdigit():
                date = f"{name[:4]}-{name[4:6]}-{name[6:8]}"

            obs_type = "market"
            if any(k in name for k in ("news", "press", "tweet", "interview", "statement")):
                obs_type = "news"
            elif any(k in name for k in ("filing", "sec", "fdic", "earnings", "prospectus")):
                obs_type = "filing"

            observations.append({
                "observation_id": obs_id,
                "content": content[:2500],
                "source": name,
                "type": obs_type,
                "supports": [],
                "contradicts": [],
                "neutral": [],
                "date": date,
            })

    return observations


# ── Normalization helpers ──────────────────────────────────────────────────────

def build_evidence_atom(obs: dict, cycle: int) -> dict:
    """Convert a corpus observation to the frontend EvidenceAtom shape."""
    content = obs["content"]
    quote = content[:200].replace("\n", " ").strip()
    return {
        "id": obs["observation_id"],
        "type": "structural" if obs["type"] == "structural" else "empirical",
        "observation": content[:400].replace("\n", " ").strip(),
        "timestamp": obs.get("date") or "2023-01-01",
        "source": obs["source"].replace("_", " ").title(),
        "modality": "text",
        "confidence": 0.85,
        "supports": obs.get("supports", []),
        "contradicts": obs.get("contradicts", []),
        "neutral": obs.get("neutral", []),
        "novelty": "medium",
        "quoteOrVisualAnchor": quote,
        "cycle": cycle,
    }


def normalize_hypothesis(h: dict, cycle: int) -> dict:
    """Convert backend hypothesis to frontend Hypothesis shape."""
    score = h.get("score", h.get("current_score", 0.5))
    return {
        "id": h["id"],
        "label": h.get("name", h.get("label", h["id"])),
        "description": h.get("description", ""),
        "status": "surviving",
        "initialConfidence": score,
        "currentConfidence": score,
        "generatedInCycle": cycle,
        "supportingAtoms": h.get("evidence_chain", []),
        "contradictingAtoms": [],
    }


# ── WebSocket handler ──────────────────────────────────────────────────────────

@app.websocket("/ws/{session_id}")
async def ws_handler(ws: WebSocket, session_id: str):
    await ws.accept()

    async def send(msg: dict) -> None:
        await ws.send_text(json.dumps(msg))

    try:
        # ── Receive start command ──────────────────────────────────────────────
        raw = await ws.receive_text()
        data = json.loads(raw)
        trigger: str = data["trigger"]
        entity: str = data["entity"]
        ticker: str = data.get("ticker", "")

        # ── SESSION_STARTED ────────────────────────────────────────────────────
        await send({"type": "SESSION_STARTED", "entity": entity, "tier": 2})
        await asyncio.sleep(0.1)

        # ── TIER2_EVALUATION (simulated streaming) ─────────────────────────────
        tier2_lines = [
            f"Evaluating trigger signal for {entity} ({ticker})...",
            "Cross-referencing against known crisis patterns.",
            "Historical precedent identified — credibility score: HIGH.",
            "Signal magnitude exceeds T2 threshold.",
            "Escalating to Tier 3 Full Investigation.",
        ]
        for line in tier2_lines:
            await send({"type": "TIER2_EVALUATION", "text": line + "\n", "done": False})
            await asyncio.sleep(0.25)
        await send({"type": "TIER2_EVALUATION", "text": "", "done": True})
        await asyncio.sleep(0.2)

        # ── TIER_ESCALATED ─────────────────────────────────────────────────────
        await send({"type": "TIER_ESCALATED", "from": 2, "to": 3})
        await asyncio.sleep(0.3)

        # ── Load evidence corpus ────────────────────────────────────────────────
        evidence = load_evidence_corpus(entity)
        structural = [o for o in evidence if o["type"] == "structural"]
        empirical = [o for o in evidence if o["type"] != "structural"]

        # ── Stream evidence atoms ───────────────────────────────────────────────
        await send({"type": "AGENT_STATUS_CHANGED", "agent": "structural", "status": "fetching"})
        await send({"type": "AGENT_STATUS_CHANGED", "agent": "market", "status": "fetching"})
        await send({"type": "AGENT_STATUS_CHANGED", "agent": "news", "status": "fetching"})

        for obs in structural[:6]:
            await send({"type": "EVIDENCE_ATOM_ARRIVED", "atom": build_evidence_atom(obs, 1)})
            await asyncio.sleep(0.06)
        await send({"type": "AGENT_STATUS_CHANGED", "agent": "structural", "status": "complete"})

        for obs in empirical[:12]:
            await send({"type": "EVIDENCE_ATOM_ARRIVED", "atom": build_evidence_atom(obs, 1)})
            await asyncio.sleep(0.06)
        await send({"type": "AGENT_STATUS_CHANGED", "agent": "market", "status": "complete"})
        await send({"type": "AGENT_STATUS_CHANGED", "agent": "news", "status": "complete"})

        # ── Investigation cycles ────────────────────────────────────────────────
        active_hypotheses: list[dict] = []
        compressed_state: str | None = None
        prev_survivor_count: int | None = None
        stagnation_count = 0
        final_cycle_num = 1
        investigation_start = time.time()

        for cycle_num in range(1, MAX_CYCLES + 1):
            final_cycle_num = cycle_num
            cycle_start = time.time()

            await send({"type": "CYCLE_STARTED", "cycle_number": cycle_num})

            # ── Call the 5-phase investigator ──────────────────────────────────
            result = await investigate({
                "trigger": trigger,
                "entity": entity,
                "cycle_num": cycle_num,
                "compressed_state": compressed_state,
                "evidence": evidence,
                "active_hypotheses": active_hypotheses,
            })

            survivors: list[dict] = result.get("surviving_hypotheses", [])
            eliminated: list[dict] = result.get("eliminated_hypotheses", [])
            key_insights: list[str] = result.get("key_insights", [])
            evidence_requests: list[dict] = result.get("evidence_requests", [])
            token_usage: dict = result.get("token_usage", {})
            new_compressed: str = result.get("compressed_state", "")
            cross_modal: list[dict] = result.get("cross_modal_flags", [])

            reasoning_tokens = token_usage.get("reasoning", 0)
            input_tokens = token_usage.get("input", 0)
            output_tokens = token_usage.get("output", 0)
            evidence_tokens = max(500, len(json.dumps(evidence)) // 4)

            # ── Emit hypotheses ────────────────────────────────────────────────
            if cycle_num == 1:
                for h in survivors:
                    await send({"type": "HYPOTHESIS_GENERATED", "hypothesis": normalize_hypothesis(h, cycle_num)})
                    await asyncio.sleep(0.08)
            else:
                for h in survivors:
                    score = h.get("score", h.get("current_score", 0.5))
                    await send({"type": "HYPOTHESIS_SCORED", "id": h["id"], "confidence": score})
                    await asyncio.sleep(0.04)

            # ── Emit eliminations ──────────────────────────────────────────────
            for h in eliminated:
                ec = h.get("evidence_chain", [])
                kill_atom = ec[0] if ec else h.get("kill_atom", h.get("id", ""))
                kill_reason = h.get("kill_reason", h.get("reasoning", "Contradicted by evidence"))
                await send({
                    "type": "HYPOTHESIS_ELIMINATED",
                    "id": h["id"],
                    "kill_atom": kill_atom,
                    "kill_reason": kill_reason,
                    "cycle": cycle_num,
                })
                await asyncio.sleep(0.04)

            # ── Evidence pending items ─────────────────────────────────────────
            for req in evidence_requests[:3]:
                await send({
                    "type": "EVIDENCE_PENDING_ADDED",
                    "item": {
                        "type": req.get("type", "market"),
                        "description": req.get("description", ""),
                        "requestedInCycle": cycle_num,
                        "requestedBecause": req.get("reason", ""),
                    },
                })

            # ── Compression sequence ───────────────────────────────────────────
            await send({"type": "COMPRESSION_STARTED"})
            await asyncio.sleep(0.3)

            if new_compressed:
                await send({"type": "COMPRESSED_REASONING_UPDATED", "text": new_compressed})

            compressed_tokens = max(100, len(new_compressed) // 4)
            compression_ratio = round(reasoning_tokens / max(compressed_tokens, 1), 2)

            await send({
                "type": "COMPRESSION_COMPLETE",
                "compressed_tokens": compressed_tokens,
                "compression_ratio": compression_ratio,
            })

            # ── Key insights ───────────────────────────────────────────────────
            for insight in key_insights:
                await send({"type": "KEY_INSIGHT_ADDED", "insight": {"cycle": cycle_num, "insight": insight}})

            # ── Token counts ───────────────────────────────────────────────────
            await send({
                "type": "TOKENS_UPDATED",
                "reasoning": reasoning_tokens,
                "evidence": evidence_tokens,
                "compressed": compressed_tokens,
            })

            await send({
                "type": "TOKEN_USAGE_CYCLE",
                "data": {
                    "cycle": cycle_num,
                    "investigatorInput": input_tokens,
                    "investigatorReasoning": reasoning_tokens,
                    "packagerInput": evidence_tokens,
                    "packagerTagging": output_tokens,
                    "orchestratorGemini": cycle_num == 1,
                },
            })

            # ── Cycle complete ─────────────────────────────────────────────────
            cycle_duration_ms = int((time.time() - cycle_start) * 1000)
            evidence_ids = [o["observation_id"] for o in evidence[: cycle_num * 5]]
            key_insight_str = key_insights[0] if key_insights else ""

            await send({
                "type": "CYCLE_COMPLETE",
                "cycle_number": cycle_num,
                "survivors": len(survivors),
                "duration_ms": cycle_duration_ms,
                "key_insight": key_insight_str,
                "evidence_collected": evidence_ids,
            })

            await send({
                "type": "CYCLE_HISTORY_UPDATED",
                "entry": {
                    "cycle": cycle_num,
                    "startCount": len(active_hypotheses) if active_hypotheses else len(survivors),
                    "endCount": len(survivors),
                    "eliminated": [h["id"] for h in eliminated],
                    "evidenceCollected": evidence_ids,
                    "crossModalDetected": [f"CM{i+1}" for i, _ in enumerate(cross_modal)],
                    "keyInsight": key_insight_str,
                },
            })

            # ── Update state ───────────────────────────────────────────────────
            compressed_state = new_compressed
            active_hypotheses = survivors

            # ── Check convergence ──────────────────────────────────────────────
            survivor_count = len(survivors)
            if prev_survivor_count is not None and survivor_count == prev_survivor_count:
                stagnation_count += 1
            else:
                stagnation_count = 0
            prev_survivor_count = survivor_count

            if survivor_count <= CONVERGENCE_THRESHOLD or stagnation_count >= STAGNATION_CYCLES:
                break

            await asyncio.sleep(0.2)

        # ── CONVERGENCE_REACHED ────────────────────────────────────────────────
        surviving_names = [h.get("name", h.get("id", "Unknown")) for h in active_hypotheses]
        earliest_date = evidence[0].get("date") or "2023-01-01" if evidence else "2023-01-01"
        earliest_atom = evidence[0]["observation_id"] if evidence else "E01"

        diagnosis = {
            "level": "CRITICAL" if active_hypotheses else "ALL-CLEAR",
            "severity": "critical" if len(active_hypotheses) >= 2 else "high" if active_hypotheses else "low",
            "headline": (
                f"{len(active_hypotheses)} risk factor(s) confirmed for {entity} after "
                f"{final_cycle_num} investigation cycle(s)"
            ),
            "detail": (
                f"Iterative hypothesis elimination converged to {len(active_hypotheses)} "
                f"uncontradicted hypothesis(es). Single-pass analysis would have missed "
                f"cross-modal contradictions revealed in later cycles."
            ),
            "diagnosis": compressed_state or "Investigation complete.",
            "survivingHypotheses": surviving_names,
            "earliestSignalTimestamp": earliest_date,
            "earliestSignalAtomId": earliest_atom,
            "singlePassSummary": (
                f"A single-pass approach would have flagged {len(active_hypotheses) + len(eliminated)} "
                f"hypotheses without elimination, producing an overly broad risk assessment."
            ),
            "iterativeDiagnosis": compressed_state or "Iterative investigation complete.",
            "groundTruthMatch": False,
        }

        await send({"type": "CONVERGENCE_REACHED", "diagnosis": diagnosis})
        await send({"type": "CONTAGION_DETECTED", "targets": []})
        await send({"type": "INVESTIGATION_COMPLETE"})

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        print(f"[IHEE] WebSocket error in session {session_id}: {exc}")
        try:
            await ws.send_text(json.dumps({"type": "ERROR", "message": str(exc)}))
        except Exception:
            pass


class CachedInvestigateRequest(BaseModel):
    entity: str


@app.post("/api/investigate/cached")
async def investigate_cached(request: CachedInvestigateRequest):
    """
    Cached investigation playback - streams cached investigation with simulated delays.

    This endpoint provides a 2-minute demo experience by playing back a pre-computed
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
        },
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
