# IHEE - Iterative Hypothesis Elimination Engine

> Real-time financial risk investigation using iterative reasoning with Gemini 2.5 Flash

## Quick Start

### Prerequisites
- Python 3.12+ with virtual environment activated
- Node.js 18+ with npm
- Gemini API key configured in `.env`

### Start Everything
```bash
./start.sh
```

This will:
1. Start backend on http://localhost:8000
2. Start frontend on http://localhost:5173
3. Display status and URLs

### Stop Everything
```bash
./stop.sh
```

### Manual Start

#### Backend
```bash
cd backend
source ../venv/bin/activate
python3 main.py
```

#### Frontend
```bash
cd frontend
npm run dev
```

## Using the Application

### 1. Open Browser
Navigate to http://localhost:5173

### 2. Select Trigger Event
Choose from:
- **Silicon Valley Bank (SIVB)** - 4.2σ magnitude
- **Credit Suisse (CS)** - 3.8σ magnitude ⭐ **Recommended** (complete evidence corpus)
- **First Republic Bank (FRC)** - 5.1σ magnitude

### 3. Choose Mode

#### MOCK Mode (Instant Demo)
- Pre-recorded investigation playback
- No API calls
- Speed controls: `[` slower, `]` faster
- Perfect for demos and testing UI

#### LIVE Mode (Real Investigation)
- Real-time Gemini API calls
- 5-phase reasoning per cycle
- 8-12 minutes for full investigation
- Watch real hypothesis elimination

### 4. Watch Investigation Flow

**Screen 1: Signal Intake**
- Tier 2 semantic evaluation streams in
- Escalates to Tier 3 if credible

**Screen 2: Investigation** (3-column layout)
- **Left**: Cycle timeline (vertical progress)
- **Center**: Hypotheses (surviving vs eliminated)
- **Right**: Evidence atoms or token usage

**Screen 3: Convergence**
- Final diagnosis
- Surviving hypotheses
- Single-pass vs iterative comparison
- Contagion detection

## Architecture

### Three-Agent Pipeline
```
ORCHESTRATOR (stateful QC hub)
  ↓ case file + evidence package
INVESTIGATOR (stateless reasoning)
  ↓ updated case file + evidence requests
ORCHESTRATOR (validates compression)
  ↓ evidence requests (filtered)
EVIDENCE COLLECTOR (stateless fetch)
  ↓ evidence atoms
ORCHESTRATOR (packages with case file)
  → back to INVESTIGATOR
```

### 5-Phase Investigation Cycle
Each cycle makes 5 separate Gemini calls:
1. **SCORE** - Evaluate hypotheses against evidence
2. **ELIMINATE** - Kill contradicted hypotheses
3. **CROSS-MODAL** - Flag structural vs empirical contradictions
4. **REQUEST** - Specify evidence needed for next cycle
5. **COMPRESS** - Self-compress cumulative state

### Context Window Strategy
- **Investigator**: Fresh 1M context window per cycle (stateless)
- **Orchestrator**: Fixed context accumulates case file (stateful)
- **Evidence Packager**: Fresh window per run (stateless)

## WebSocket API

### Connect
```
ws://localhost:8000/ws/{session_id}
```

### Start Investigation
```json
{
  "trigger": "Signal description",
  "entity": "Credit Suisse",
  "ticker": "CS"
}
```

### Message Types

See `frontend/src/types/api.ts` for full type definitions:
- Session: `SESSION_STARTED`, `TIER_ESCALATED`
- Cycle: `CYCLE_STARTED`, `CYCLE_COMPLETE`
- Hypotheses: `HYPOTHESIS_GENERATED`, `HYPOTHESIS_SCORED`, `HYPOTHESIS_ELIMINATED`
- Evidence: `EVIDENCE_ATOM_ARRIVED`, `AGENT_STATUS_CHANGED`
- Compression: `COMPRESSION_STARTED`, `COMPRESSED_REASONING_UPDATED`, `COMPRESSION_COMPLETE`
- Convergence: `CONVERGENCE_REACHED`, `INVESTIGATION_COMPLETE`
- Tokens: `TOKENS_UPDATED`, `TOKEN_USAGE_CYCLE`

## Testing

### Integration Tests
```bash
# Test backend startup
bash test_backend_startup.sh

# Test WebSocket connection
source venv/bin/activate
python3 test_websocket.py

# Test full investigation flow (8-12 min)
python3 test_credit_suisse.py
```

### Manual Testing
1. Start backend: `cd backend && source ../venv/bin/activate && python3 main.py`
2. Start frontend: `cd frontend && npm run dev`
3. Open http://localhost:5173
4. Select Credit Suisse trigger
5. Toggle between MOCK and LIVE modes

## Project Structure

```
.
├── backend/
│   ├── main.py                    # FastAPI + WebSocket server
│   ├── config.py                  # Configuration
│   ├── agents/
│   │   ├── orchestrator.py        # Pure logic functions
│   │   ├── investigator_5phase.py # 5-phase reasoning engine
│   │   └── evidence/              # Evidence collectors
│   ├── gemini/
│   │   ├── client.py              # Gemini API wrapper
│   │   └── prompts/               # Prompt templates
│   └── models/                    # Data models
├── frontend/
│   ├── src/
│   │   ├── App.tsx                # Main app
│   │   ├── store/                 # Zustand state management
│   │   ├── hooks/                 # useWebSocket, useMockPlayback
│   │   ├── components/
│   │   │   ├── layout/            # StatusBar, AppShell
│   │   │   └── screens/           # 3 main screens
│   │   └── types/                 # TypeScript types
│   └── package.json
├── evidence/
│   ├── credit-suisse/
│   │   ├── structural/            # 8 structural evidence files
│   │   └── empirical/             # 28 empirical evidence files
│   └── ftx/                       # Alternative entity
├── start.sh                       # Start backend + frontend
├── stop.sh                        # Stop all servers
└── INTEGRATION_TEST_RESULTS.md   # Test results
```

## Evidence Corpus

Pre-curated evidence for hackathon demo:

### Credit Suisse (Recommended)
- **Structural**: 8 files (AT1 prospectus, FINMA powers, Swiss legislation)
- **Empirical**: 28 files (market data, news, regulatory filings)
- **Total**: 36 evidence atoms

### FTX
- **Structural**: 7 files (token mechanics, corporate structure, ToS)
- **Empirical**: 22 files (market data, news, interviews)
- **Total**: 29 evidence atoms

## Performance

### Cycle 1 (Hypothesis Generation)
- Duration: ~30 seconds
- Hypotheses: 8-10 generated
- Evidence: All structural + empirical atoms loaded

### Cycle 2+ (Scoring & Elimination)
- Duration: 120-180 seconds per cycle
- 5 phases: SCORE → ELIMINATE → CROSS-MODAL → REQUEST → COMPRESS
- Hypotheses: 1-3 eliminated per cycle
- Compression: 20-30K → 75-100K tokens (grows with findings)

### Full Investigation
- Cycles: 3-5 cycles until convergence
- Duration: 8-12 minutes
- Convergence: ≤2 hypotheses or 2 cycles without change

## Configuration

### Backend (`backend/config.py`)
```python
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_TEMPERATURE = 0.2
MAX_CYCLES = 5
CONVERGENCE_THRESHOLD = 2
STAGNATION_CYCLES = 2
```

### Frontend (`frontend/src/hooks/useWebSocket.ts`)
```typescript
const WS_BASE = 'ws://localhost:8000'
```

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Kill process on port 5173 (frontend)
lsof -ti:5173 | xargs kill -9
```

### WebSocket Connection Failed
- Ensure backend is running: `curl http://localhost:8000/docs`
- Check backend logs: `tail -f /tmp/ihee-backend.log`
- Verify CORS settings in `backend/main.py`

### Investigation Timeout
- Gemini API calls take 2-3 minutes per cycle
- Use MOCK mode for instant demo
- Check API key: `grep GEMINI_API_KEY .env`

### Frontend Won't Load
- Check frontend logs: `tail -f /tmp/ihee-frontend.log`
- Verify dependencies: `cd frontend && npm install`
- Check Vite dev server: `curl http://localhost:5173`

## API Endpoints

### HTTP
- `GET /` - Root endpoint
- `GET /docs` - OpenAPI documentation

### WebSocket
- `WS /ws/{session_id}` - Investigation WebSocket connection

## Environment Variables

Create `.env` in project root:
```bash
GEMINI_API_KEY=your_api_key_here
```

## Development

### Backend Development
```bash
cd backend
source ../venv/bin/activate

# Run tests
python3 test_phase3.py
python3 test_orchestrator.py

# Start server with reload
python3 run.py
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Tech Stack

**Backend**
- Python 3.12
- FastAPI (Web framework)
- LangChain Google GenAI (Gemini integration)
- WebSockets (Real-time communication)

**Frontend**
- TypeScript
- React 19
- Vite (Build tool)
- Zustand (State management)
- Framer Motion (Animations)
- Tailwind CSS v4 (Styling)

**AI Model**
- Gemini 2.5 Flash
- 1M token context window
- JSON mode for structured output

## License

Gemini 3 Singapore Hackathon Project - March 2026

## Authors

- saaiaravindhraja@gmail.com

## Commit Guidelines

- Concise, human commit messages
- No AI co-author tags
- Author: saaiaravindhraja@gmail.com
