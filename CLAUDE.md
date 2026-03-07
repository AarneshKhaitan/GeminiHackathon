# IHEE — Iterative Hypothesis Elimination Engine

Gemini 3 Singapore Hackathon, March 2026.

## Architecture

**Three-agent pipeline with strict separation:**

```
ORCHESTRATOR (stateful, QC hub)
  ↓ case file + evidence package
INVESTIGATOR (stateless, pure reasoning)
  ↓ updated case file + evidence requests
ORCHESTRATOR (validates compression quality, decides next step)
  ↓ evidence requests (prioritized, filtered)
EVIDENCE COLLECTOR (stateless, pure fetch)
  ↓ evidence atoms
ORCHESTRATOR (packages with case file)
  → back to INVESTIGATOR
```

The Orchestrator is the only agent with full visibility. It QC-checks every handoff:
- Rejects bad compressions ("you lost the key structural insight, redo")
- Prioritizes evidence requests ("get the AT1 prospectus first")
- Decides early convergence if hypotheses collapse

## Case File Format

```
entity:          "Credit Suisse Group AG"
status:          "TIER 4 — ACTIVE INVESTIGATION"
last_updated:    ISO timestamp
cycle_count:     int

hypotheses:
  surviving:
    - id, label, confidence, key_evidence[], key_contradiction[]
  eliminated:
    - id, label, eliminated_by, eliminated_at_cycle

structural_knowledge_loaded: string[]
open_evidence_requests: string[]
key_insights: string[]
cross_modal_contradictions: string[]
forward_simulation:
  - condition, outcome, confidence
```

## Tech Stack

**Backend:** Python · FastAPI · LangGraph · Gemini API
**Frontend:** Vite · React · TypeScript · Tailwind CSS v4

## Frontend Structure

```
frontend/
  src/
    types/investigation.ts   — domain types (includes CaseFile format)
    types/api.ts             — WebSocket message contract
    store/index.ts           — Zustand store
    data/svb-case.json       — Full SVB mock fixture
    hooks/useMockPlayback.ts — Mock playback ([ / ] = speed)
    components/
      layout/StatusBar/      — Persistent status bar + ContextWindowBar
      screens/
        Screen1_SignalIntake/
        Screen2_Investigation/ — 3-col: CycleTimeline | Hypotheses | Evidence
        Screen3_Convergence/
```

## WebSocket Contract

Backend fires events over `ws://localhost:8000/ws/{session_id}`:
- `SESSION_STARTED`, `TIER_ESCALATED`, `CYCLE_STARTED`
- `TOKENS_UPDATED` — fire ≥ every 500ms during reasoning (drives breathing bar)
- `HYPOTHESIS_GENERATED`, `HYPOTHESIS_SCORED`, `HYPOTHESIS_ELIMINATED`
- `EVIDENCE_ATOM_ARRIVED`, `AGENT_STATUS_CHANGED`
- `CYCLE_COMPLETE`, `COMPRESSION_STARTED`, `COMPRESSION_COMPLETE`
- `CONVERGENCE_REACHED`, `CONTAGION_DETECTED`

See `src/types/api.ts` for full union type.

## Commits

- Author: `saaiaravindhraja@gmail.com`
- No AI co-author tags
- Concise, human commit messages
- No AI/claude documentation files in commits
