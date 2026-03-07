# Credit Suisse Demo - Quick Reference

## Cached Investigation Run

**Status:** ✅ Cached investigation complete (forcing 3 cycles minimum)

**Cache File:** `backend/corpus/cached/credit_suisse_full_run.json`

**Trigger:**
- **Event:** Q4 2022 earnings reveal CHF 110.5B deposit outflows
- **Date:** February 9, 2023
- **Magnitude:** CHF 110.5 billion (8% of AUM)

## Frontend Integration

### Endpoint for Demo Playback

```
POST /api/investigate/cached
Content-Type: application/json

{
  "entity": "Credit Suisse"
}
```

**Response:** Server-Sent Events (SSE) stream

**Duration:** ~1 minute (simulated with delays)

### Event Sequence

1. `SESSION_STARTED` - Investigation begins
2. `TIER2_EVALUATION` - Tier 2 semantic check (progressive text)
3. `TIER_ESCALATED` - Promoted to Tier 4
4. **Per Cycle (3 cycles):**
   - `CYCLE_STARTED`
   - `AGENT_STATUS_CHANGED` - Investigator reasoning
   - `HYPOTHESIS_GENERATED` (cycle 1) or `HYPOTHESIS_SCORED` (cycles 2-3)
   - `HYPOTHESIS_ELIMINATED` (if any)
   - `COMPRESSION_STARTED`
   - `COMPRESSED_REASONING_UPDATED`
   - `COMPRESSION_COMPLETE`
   - `KEY_INSIGHT_ADDED` (if any)
   - `TOKENS_UPDATED`
   - `CYCLE_COMPLETE`
5. `CONVERGENCE_REACHED` - Final diagnosis
6. `INVESTIGATION_COMPLETE` - Done

### Timing

- **Tier 2 evaluation:** 0.8s
- **Per cycle:** ~2.5s
  - Reasoning simulation: 1.5s
  - Hypothesis processing: 0.3s
  - Compression: 0.5s
- **Total:** ~60 seconds

## What the Demo Shows

✅ **Real LangGraph execution** (cached result)
✅ **Real Gemini-generated hypotheses** (9 hypotheses)
✅ **Multi-cycle investigation** (3 cycles minimum)
✅ **Convergence detection** (stagnation after 3 cycles)
✅ **Token usage tracking** (~50K tokens total)
✅ **Compressed reasoning** (per cycle)

⚠️ **Known Limitations:**
- No evidence retrieved (evidence search issue)
- No hypothesis eliminations (because no evidence)
- All 9 hypotheses survive

## Real vs. Cached Modes

| Mode | Endpoint | Duration | Use Case |
|------|----------|----------|----------|
| **Cached** | `POST /api/investigate/cached` | ~1 min | Demo presentation (fast) |
| **Live** | `POST /api/investigate` | 3-5 min | Judge evaluation (real) |

## Frontend Example

```typescript
const response = await fetch('http://localhost:8000/api/investigate/cached', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ entity: 'Credit Suisse' })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  const events = chunk.split('\n\n');

  for (const event of events) {
    if (event.startsWith('event:')) {
      const [eventLine, dataLine] = event.split('\n');
      const eventType = eventLine.replace('event: ', '');
      const data = JSON.parse(dataLine.replace('data: ', ''));

      handleEvent(eventType, data);
    }
  }
}
```

## Testing Playback

```bash
cd backend
source ../venv/bin/activate
python playback.py
```

This will output the SSE stream to console for verification.

## Starting the Server

```bash
cd backend
source ../venv/bin/activate
python main_phase7.py
```

Server runs on `http://localhost:8000`

Endpoints:
- `GET /api/health` - Health check
- `POST /api/investigate/cached` - Cached playback (1 min)
- `POST /api/investigate` - Live LangGraph (3-5 min)
- `GET /api/case/{entity}` - Get case file

## Hypothesis Names (from cached run)

1. **H01:** Reputational Erosion & Loss of Trust (0.90)
2. **H02:** Perceived Liquidity/Solvency Risk (0.80)
3. **H03:** Market Signal of Increased Default Risk (0.85)
4. **H04:** Ineffective Restructuring Plan & Communication (0.90)
5. **H05:** Regulatory/Legal Pressure & Investigations (0.70)
6. **H06:** Targeted De-risking by Wealth Management Clients (0.85)
7. **H07:** Contagion from Broader Market Distress (0.60)
8. **H08:** Undisclosed Operational Failure (0.50)
9. **H09:** Asset-Liability Mismatch Perception (0.70)

All survived (no eliminations due to evidence retrieval issue).
