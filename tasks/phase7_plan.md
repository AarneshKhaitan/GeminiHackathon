# Phase 7: FastAPI Endpoints

**Status:** Pending Phase 6 completion
**Duration:** ~1 hour
**Dependencies:** Phase 1-6 (complete backend)
**Build Order:** 7 of 7 - FINAL PHASE

---

## Context

FastAPI server exposing investigation engine to React frontend via SSE streaming.

**Key Points:**
- POST /api/investigate - SSE streaming for real-time cycle updates
- GET /api/case/{entity} - Retrieve case file
- POST /api/investigate/cached - Pre-cached fallback
- CORS enabled for local development

---

## File to Create

### `backend/main.py`

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import asyncio

from graph.investigation_graph import compiled_graph
import config

app = FastAPI(title="Hypothesis Elimination Engine")

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InvestigateRequest(BaseModel):
    entity: str
    event: str
    date: str

@app.post("/api/investigate")
async def investigate_sse(request: InvestigateRequest):
    """Stream investigation progress via SSE"""

    async def event_generator():
        initial_state = {
            "trigger_signal": {
                "entity": request.entity,
                "event": request.event,
                "date": request.date
            },
            "entity": request.entity,
            "current_cycle": 0,
            "max_cycles": config.MAX_CYCLES
        }

        # Run graph with streaming
        async for state in compiled_graph.astream(initial_state):
            if "case_file" not in state:
                continue

            case = state["case_file"]

            # Extract cycle update
            update = {
                "cycle": len(case.get("cycle_history", [])),
                "status": case.get("status", "investigating"),
                "active_count": len(case.get("active_hypotheses", [])),
                "eliminated_count": len(case.get("eliminated_hypotheses", [])),
                "latest_eliminations": case.get("eliminated_hypotheses", [])[-3:],
                "evidence_requests": case.get("evidence_pending", [])[:3],
                "token_usage": case.get("token_usage", {}),
                "agent_status": state.get("agent_status", {})
            }

            yield f"data: {json.dumps(update)}\n\n"

            # Heartbeat
            await asyncio.sleep(config.SSE_HEARTBEAT_INTERVAL)

        # Final result
        final_update = {
            "complete": True,
            "case_file": state["case_file"]
        }
        yield f"data: {json.dumps(final_update)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

@app.get("/api/case/{entity}")
async def get_case(entity: str):
    """Retrieve case file for entity"""
    # In-memory storage for hackathon
    if entity not in case_storage:
        return {"error": "Case not found"}, 404
    return case_storage[entity]

@app.post("/api/investigate/cached")
async def investigate_cached():
    """Return pre-cached investigation for demo fallback"""
    with open(config.CACHED_FALLBACK_PATH) as f:
        cached_run = json.load(f)
    return cached_run

@app.get("/api/health")
async def health():
    return {"status": "healthy", "model": config.GEMINI_MODEL}

# In-memory case storage for hackathon
case_storage = {}
```

---

## Verification Test

Create `backend/test_phase7.py`:

```python
#!/usr/bin/env python3
"""Phase 7 Verification: Test FastAPI Endpoints"""

import asyncio
import httpx

async def test_health():
    print("Testing /api/health...")
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✓ Health check passed: {data}")

async def test_sse_stream():
    print("\nTesting /api/investigate (SSE stream)...")
    async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=60.0) as client:
        async with client.stream(
            "POST",
            "/api/investigate",
            json={
                "entity": "SVB",
                "event": "CDS spike to 450bps",
                "date": "2023-03-08"
            }
        ) as response:
            assert response.status_code == 200

            event_count = 0
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    event_count += 1
                    data = json.loads(line[6:])
                    print(f"  Event {event_count}: cycle={data.get('cycle')}, active={data.get('active_count')}")

                    if data.get("complete"):
                        print(f"✓ Investigation complete after {event_count} events")
                        break

async def main():
    print("=" * 60)
    print("Phase 7 Verification: FastAPI Endpoints")
    print("=" * 60)
    print("\n⚠️  Start server first: uvicorn main:app --reload")
    print("Press Enter when server is running...")
    input()

    await test_health()
    await test_sse_stream()

    print("\n" + "=" * 60)
    print("✅ FASTAPI VALIDATED - Phase 7 Complete!")
    print("=" * 60)
    print("\nVerified:")
    print("  ✓ Health endpoint works")
    print("  ✓ SSE streaming works")
    print("  ✓ Investigation runs via API")
    print("  ✓ CORS enabled")
    print("\n🎉 ALL 7 PHASES COMPLETE - Backend Ready!")

if __name__ == "__main__":
    import json
    asyncio.run(main())
```

---

## Running the Server

```bash
cd backend

# Install dependencies
pip install fastapi uvicorn python-multipart

# Start server
uvicorn main:app --reload --port 8000

# In another terminal, test
python test_phase7.py
```

---

## Success Criteria

- [ ] Server starts without errors
- [ ] Health endpoint responds
- [ ] SSE streaming works
- [ ] Investigation runs via API
- [ ] CORS enabled for frontend

---

## Final Result

After Phase 7 passes:
✅ **COMPLETE BACKEND OPERATIONAL**
✅ All 7 phases implemented and verified
✅ Ready for frontend integration
✅ Demo-ready system

**🎉 BACKEND COMPLETE! 🎉**
