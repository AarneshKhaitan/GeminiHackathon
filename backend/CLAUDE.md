## Project Context

### What We're Building
A LangGraph-based hypothesis elimination engine for financial risk
assessment. The system receives a trigger signal, generates competing
hypotheses, then directs its own investigation — requesting specific
evidence, eliminating wrong theories across multiple reasoning cycles,
and converging on a diagnosis with full traceability [3].

We use the 1M context window as a reasoning workspace, not a data
warehouse. While every other system stuffs documents into the context
and asks one question, our system runs iterative reasoning cycles —
hypothesize, score, eliminate, refine — and the context fills with
thinking, not data [3].

Demo event: SVB collapse (March 2023). The system should arrive at
the same conclusion the FDIC post-mortem published months later —
duration mismatch hidden by HTM accounting + social-media-accelerated
correlated deposit flight [4].

### Three Core Agents
1. Orchestrator — stateful lifecycle manager. Creates case files,
   decides when to fetch evidence, dispatches evidence packager,
   parses investigator self-compressed output, decides continue/converge,
   generates alerts, handles network contagion detection [4].
2. Investigator — stateless pure reasoning engine. Fresh context
   window per cycle. Scores hypotheses against evidence atoms,
   eliminates contradicted ones, self-compresses at the end of each
   cycle. Does NOT remember previous cycles — only knows what the
   compressed state tells it [4].
3. Evidence Packager — called BY the Orchestrator when new evidence
   is needed. Internally dispatches three parallel retrieval agents
   (structural, market, news), collects results, tags all atoms
   against active hypotheses using Gemini, returns tagged observations
   to the Orchestrator. The three retrieval agents are INTERNAL to
   the packager — not separate nodes in the main graph.

### Tiering System
- Tier 0/1: Statistical monitoring — banks already have this.
  Simulated by our pre-curated evidence corpus.
- Tier 2: Semantic evaluation — one Gemini call to assess if signal
  warrants investigation. Most flags die here.
- Tier 3: Initial investigation — 1-2 quick cycles. Decides whether
  to promote to Tier 4 or demote back to Tier 2.
- Tier 4: Full investigation — 4-5 deep reasoning cycles. This is
  our core product [4].

### Context Window Architecture
- Fresh context window per investigator cycle — prevents context rot [4]
- Persistent state lives in case files, not context windows [4]
- Investigator self-compresses at end of each cycle
- Tiered compression: ~20-30K after cycle 1 ramping to ~75-100K
  after cycle 4 — grows as investigation accumulates findings
- Context rot threshold ~400-500K tokens — we stay well below this

### Evidence Corpus
- Pre-curated evidence corpus for hackathon demo — agents do real
  retrieval logic but search pre-prepared local files
- Three categories: structural atoms (Vatsal's domain knowledge),
  market data (pre-downloaded from FRED/Yahoo), news/filings
  (pre-curated articles and SEC excerpts)
- Live API collection is a stretch goal if time permits
- Pre-cached complete SVB demo run at corpus/cached/svb_full_run.json
  as invisible fallback

## Architectural Decisions (DO NOT VIOLATE)

1. orchestrator.py contains PURE LOGIC FUNCTIONS — no LangGraph
   imports. investigation_graph.py does ALL LangGraph wiring.
   ONLY investigation_graph.py imports LangGraph.

2. Investigator SELF-COMPRESSES at the end of each cycle. There is
   NO separate compression Gemini call. The orchestrator parses the
   compressed state from the investigator's response and saves it
   to the case file.

3. Fresh context window per cycle. The investigator is STATELESS.
   It does not remember previous cycles. It only knows what the
   compressed state tells it [4].

4. TypedDict for LangGraph graph state (models/state.py). Pydantic
   for data models and validation (models/case_file.py,
   models/observation.py). Dict as interchange format between them.

5. Orchestrator decides IF new evidence is needed. If yes, it calls
   the Evidence Packager. The Packager internally dispatches three
   parallel agents (structural, market, news), collects results,
   tags atoms using Gemini, and returns tagged observations to the
   Orchestrator. The three agents are INTERNAL to the packager.

6. Pre-curated evidence corpus — agents do real retrieval but search
   local files. Live API collection is stretch goal only.

7. Every eliminated hypothesis must cite the SPECIFIC evidence atom
   that killed it. No vague eliminations.

8. Each component must be testable in isolation WITHOUT LangGraph.

9. Orchestrator has a FIXED context window for the entire
   investigation — it persists across all cycles, accumulating
   case file state and decision logs. It does coordination, not reasoning [4].

   All other agents (Investigator, Evidence Packager, three
   retrieval agents) get FRESH context windows per run —
   discarded after each cycle/execution [4].

## Build Order (STRICT)

1. models/ — state.py, case_file.py, observation.py
2. gemini/ — client.py with retry logic and cached fallback
3. agents/investigator.py — CRITICAL PATH, most important component [3]
4. agents/evidence/ — packager.py (owns retrieval + tagging),
   structural_agent.py, market_agent.py, news_agent.py
5. agents/orchestrator.py — pure logic functions
6. graph/investigation_graph.py — LangGraph wiring
7. main.py — FastAPI endpoints with SSE streaming

## Project Structure

```
backend/
├── main.py                          # FastAPI entry point
├── config.py                        # API keys, settings
├── models/
│   ├── state.py                     # TypedDict — LangGraph state
│   ├── case_file.py                 # Pydantic — case file model
│   └── observation.py               # Pydantic — observation schema
├── agents/
│   ├── orchestrator.py              # Pure logic functions (NO LangGraph)
│   ├── investigator.py              # Stateless reasoning engine
│   └── evidence/
│       ├── packager.py              # Owns retrieval + tagging pipeline
│       ├── structural_agent.py      # Structural knowledge retrieval
│       ├── market_agent.py          # Market data retrieval
│       └── news_agent.py            # News and filing retrieval
├── graph/
│   └── investigation_graph.py       # ONLY file importing LangGraph
├── gemini/
│   ├── client.py                    # Gemini API wrapper with fallback
│   └── prompts/
│       ├── tier2_evaluation.py      # Tier 2 prompt
│       ├── investigation.py         # Investigator reasoning prompt
│       └── evidence_tagging.py      # Packager tagging prompt
├── corpus/
│   ├── structural/                  # Vatsal's structural atoms
│   ├── empirical/                   # Market data + news
│   └── cached/                      # Pre-computed fallback
│       └── svb_full_run.json
└── utils/
    ├── token_counter.py             # Token usage tracking
    └── parser.py                    # Parse compressed state from output
```

## Key Conventions

- All agent functions are async
- All Gemini calls return parsed JSON with token usage tracking
- Every Gemini call has a fallback to cached response
- Observation schema: {observation_id, content, source, type,
  supports: [hypothesis_ids], contradicts: [hypothesis_ids],
  neutral: [hypothesis_ids]}
- Hypothesis schema: {id, name, score, evidence_chain, status}
- Case file stores compressed_reasoning as string — the
  self-compressed output from the investigator
- Frontend receives updates via Server-Sent Events (SSE)
- The delta between single-pass analysis and iterative reasoning
  is the core demo value [3]

## Reference Documents

When building or modifying a component, reference these documents:

- **docs/component_guide.md** — Detailed descriptions of every file
  in the project. What each file does, what it receives, what it
  returns, how it connects to other components. READ THIS before
  building or modifying any component.

- **docs/prd.md** — Full product requirements document. Feature
  specifications, observation schema, tiering system, evidence
  corpus structure, demo event details, success metrics. Reference
  for understanding the WHY behind architectural decisions.


## Workflow Orchestration

### 1. Plan Mode Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately - don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

### 2. Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution

### 3. Self-Improvement Loop
- After ANY correction from the user: update tasks/lessons.md with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant project

### 4. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

### 5. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes - don't over-engineer
- Challenge your own work before presenting it

### 6. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests - then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how

## Task Management

1. **Plan First**: Write plan to tasks/todo.md with checkable items
2. **Verify Plan**: Check in before starting implementation
3. **Track Progress**: Mark items complete as you go
4. **Explain Changes**: High-level summary at each step
5. **Document Results**: Add review section to tasks/todo.md
6. **Capture Lessons**: Update tasks/lessons.md after corrections

## Core Principles

- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.

## Git Commit Rules

- **NEVER** include `Co-Authored-By` lines referencing Claude, Anthropic, or any AI assistant in commit messages.
- All commits must appear as solely authored by the user's own git username and email.
- Do not add any metadata, tags, or references that indicate AI involvement in commits.
