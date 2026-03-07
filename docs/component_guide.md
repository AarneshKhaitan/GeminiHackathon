# Component Guide: Hypothesis Elimination Engine

This document describes every file in the project. Read this before
building or modifying any component. For architectural decisions
and build order, see CLAUDE.md. For full feature specification,
see docs/prd.md.

---

## models/state.py

LangGraph graph state as TypedDict. This is the ONLY data structure
that flows between LangGraph nodes. Every field must be
JSON-serializable since LangGraph requires it.

Fields:
- trigger_signal: string — the initial event that started investigation
- entity: string — name of entity under investigation
- current_cycle: int — which cycle the investigation is on
- max_cycles: int — maximum cycles before forced convergence
- case_file: dict — serialized Pydantic CaseFile model (see case_file.py)
- active_hypotheses: list[dict] — currently surviving hypotheses with
  id, name, score, evidence_chain, status
- eliminated_hypotheses: list[dict] — dead hypotheses with id, name,
  killed_by_atom, killed_in_cycle, reason
- evidence_requests: list[dict] — what evidence the Investigator needs
  next, each with type (structural/market/news/filing) and description
- new_evidence: list[dict] — tagged atomic observations from Evidence
  Packager, following the observation schema (see observation.py)
- raw_evidence: list[dict] — untagged evidence from retrieval agents
  before packaging
- compressed_state: string — the Investigator's self-compressed output
  from the most recent cycle. REPLACED each cycle, not appended —
  each cycle's self-compression is cumulative [3]
- cross_modal_flags: list[dict] — detected contradictions between
  structural and empirical atoms, each with structural_atom,
  empirical_atom, detected_in_cycle, contradiction description
- cycle_history: list[dict] — record per cycle with start_count,
  end_count, eliminated list, evidence_collected, cross_modal_detected
- agent_status: dict — tracks which agents have completed in current
  cycle (orchestrator, investigator, packager status)
- token_usage: dict — tracks input tokens, output tokens, reasoning
  tokens per cycle per agent
- context_windows: dict — tracks context window utilization per agent
  per cycle. Orchestrator is FIXED for entire investigation.
  Investigator and Evidence Packager are FRESH per cycle [4]

---

## models/case_file.py

Pydantic model for persistent investigation state that lives BETWEEN
cycles. The case file is the investigation's memory — it stores
everything the ephemeral context windows cannot [4].

The Orchestrator is the ONLY component that reads and writes the
case file. The Investigator does not know the case file exists [4].
The Evidence Packager does not touch the case file.

The case file stores evidence REFERENCES (atom IDs and one-line briefs),
not full evidence content. Full content lives in corpus/ files and is
loaded by the Orchestrator into the Investigator's fresh context
window each cycle [4].

The compressed_reasoning field is a single string that gets REPLACED
each cycle — not appended. Each cycle's Investigator self-compression
is cumulative, incorporating all prior cycles [3].

Key fields:
- entity: string
- tier: int (2, 3, or 4) [4]
- status: string (evaluating/investigating/converged/alert/all-clear)
- trigger: dict with event, date, magnitude, tier2_assessment
- active_hypotheses: list[Hypothesis] — survivors with scores and
  evidence chains
- eliminated_hypotheses: list[EliminatedHypothesis] — dead hypotheses
  with specific kill atom ID, cycle number, and one-line reason
- cross_modal_flags: list[CrossModalFlag] — structural atom ID,
  empirical atom ID, cycle detected, contradiction explanation [3]
- key_insights: list[Insight] — notable findings per cycle
- evidence_collected: list[EvidenceRef] — atom IDs with type, brief
  description, cycle collected, which hypotheses it supports/contradicts,
  which hypotheses it was used to eliminate
- evidence_pending: list[EvidenceRequest] — what's still needed with
  type, description, cycle requested, reason
- compressed_reasoning: string — Investigator's self-compressed output,
  replaced each cycle with cumulative summary
- forward_simulation: list[Scenario] — stretch goal, IF/THEN predictions
- cycle_history: list[CycleRecord] — per-cycle record of hypothesis
  counts, eliminations, evidence collected, cross-modal detections
- context_windows: dict — per-agent per-cycle context window tracking.
  Orchestrator section tracks FIXED window growing across investigation.
  Investigator and Packager sections track FRESH windows per cycle [4]
- token_usage: dict — aggregate and per-cycle per-agent token counts
- alert: dict — populated post-convergence only, with level
  (CRITICAL/WARNING/ALL-CLEAR), diagnosis text, surviving hypotheses,
  earliest decisive signal, ground truth match for demo
- network_alerts: list[NetworkAlert] — promoted counterparties with
  entity name, promoted tier, reason, inherited context [4]

---

## models/observation.py

Pydantic model for atomic evidence observations. Every piece of
evidence in the system follows this schema. These tags enable
principled hypothesis elimination — when an observation contradicts
a hypothesis, the elimination is traceable to this specific atom [3].

The Evidence Packager is responsible for generating these tags
using Gemini. The three retrieval agents return raw evidence
without tags. The Packager adds the tags.

Fields:
- observation_id: string — unique identifier (e.g., "S01", "E03")
- content: string — the actual evidence text
- source: string — where this evidence came from
- type: string — structural, market, news, or filing
- supports: list[string] — hypothesis IDs this evidence supports
- contradicts: list[string] — hypothesis IDs this evidence contradicts
- neutral: list[string] — hypothesis IDs this evidence is neutral toward

---

## agents/orchestrator.py

Pure logic functions for investigation lifecycle management. This file
contains NO LangGraph imports — it does not know it runs inside a
graph [5]. All functions take state dicts as input and return updated
state dicts. Testable in complete isolation without LangGraph.

The Orchestrator has a FIXED context window for the entire
investigation — it persists across all cycles, accumulating case file
state and decision logs. Never exceeds ~15-20% utilization because it
does coordination, not reasoning [4].

The Orchestrator is the ONLY component that reads and writes the
case file [4]. No other component touches it.

The Orchestrator does NOT make a Gemini call for compression. The
Investigator self-compresses [3]. The Orchestrator parses the
compressed state from the Investigator's response using utils/parser.py
(pure string parsing) and saves it to the case file.

The Orchestrator only makes Gemini calls for:
- Tier 2 semantic evaluation (one small call at investigation start)
- Alert generation post-convergence (one small call)
- Contagion detection post-convergence (one small call)
All other Orchestrator actions are pure Python logic [4].

Functions:
- evaluate_signal(trigger) — Tier 2 semantic evaluation. One Gemini
  call with minimal context (~5-10K tokens). Returns assessment and
  escalate/dismiss decision.
- create_case_file(entity, trigger) — Initializes a new CaseFile
  Pydantic model, returns as dict for LangGraph state.
- prepare_investigator_context(case_file, new_evidence) — Reads case
  file, extracts compressed_reasoning string, active hypotheses list.
  Loads full evidence content from corpus/ files for atoms referenced
  in evidence_collected. Combines with new tagged evidence from
  Packager. Assembles the complete context package for the
  Investigator's fresh context window. Returns assembled context dict.
- process_investigation_output(case_file, investigation_output) —
  Uses utils/parser.py to extract self-compressed state section from
  Investigator's response. No Gemini call. Updates case file:
  active_hypotheses REPLACED with current survivors,
  eliminated_hypotheses APPENDED with new kills,
  cross_modal_flags APPENDED with new contradictions,
  compressed_reasoning REPLACED with new cumulative self-compression,
  evidence_collected APPENDED with atom reference (ID + brief only,
  not full content), evidence_pending REPLACED with new requests,
  cycle_history APPENDED with new cycle record,
  context_windows updated with this cycle's tracking data,
  token_usage accumulated. Returns updated case file dict.
- should_continue(case_file) — Convergence detection. Pure logic, no
  Gemini call. Returns "continue" or "converge" based on: hypothesis
  count (converge if ≤2), cycle count (converge if max reached),
  stagnation (converge if count unchanged for 2 consecutive cycles),
  budget (converge if credits low).
- generate_alert(case_file) — Post-convergence. Small Gemini call.
  Evaluates surviving hypotheses. Returns CRITICAL alert with diagnosis
  if crisis hypotheses survive with high confidence. Returns ALL-CLEAR
  if all crisis hypotheses eliminated.
- detect_contagion(case_file) — Post-convergence network check. Small
  Gemini call. Based on surviving risk profile, identifies
  counterparties that should be promoted. Returns list of promoted
  entities with reasons and inherited context [4].

---

## agents/investigator.py

The core reasoning engine. Stateless — receives a context package and
reasons within a single Gemini call, then the context window is
discarded [4]. Each call runs one full investigation cycle.

The Investigator does NOT know about case files, cycles, tiers, or
persistence. From its perspective, it receives context and instructions
and returns investigation results. The Orchestrator handles everything
about lifecycle and state [4].

The Investigator gets a FRESH context window per cycle — prevents
context rot that degrades attention quality beyond ~40-60% window
utilization [4].

Each cycle the Investigator executes these phases:
- PHASE 1 — GENERATE (Cycle 1 only): Generate 8-10 initial hypotheses
  from the trigger signal.
- PHASE 2 — SCORE: Evaluate each active hypothesis against every
  evidence atom. For each hypothesis-atom pair, assess whether the
  atom supports, contradicts, or is neutral. Cite specific atom IDs.
- PHASE 3 — ELIMINATE: Kill any hypothesis where an evidence atom
  directly contradicts it. For each elimination, cite the exact atom
  ID that killed it and explain why in one sentence. Check for
  cross-modal contradictions where structural atoms and empirical
  atoms disagree — flag these explicitly [3].
- PHASE 4 — REQUEST EVIDENCE: Based on surviving hypotheses, identify
  what specific evidence would help discriminate between them. Generate
  a list of evidence requests with type and description.
- PHASE 5 — SELF-COMPRESS: At the end of the response, produce a
  COMPRESSED STATE section containing: surviving hypotheses with
  updated confidence scores, eliminated hypotheses with kill atom and
  one-line reason, cross-modal contradictions detected, evidence
  needed for next cycle, crux question going into next cycle. This
  self-compression is CUMULATIVE — the Investigator sees prior
  compressed state in its context and produces a new compressed state
  that incorporates everything from all prior cycles [3].

The function should:
1. Receive the context package assembled by the Orchestrator
   (compressed state + evidence + hypotheses + instructions)
2. Call Gemini with the full assembled prompt
3. Parse the JSON response
4. Return both the full investigation output AND the self-compressed
   state section extracted separately so the Orchestrator can save
   it to the case file without parsing the full reasoning trace

Return schema:
{
  "reasoning_trace": "full detailed reasoning",
  "surviving_hypotheses": [...],
  "eliminated_hypotheses": [...],
  "cross_modal_flags": [...],
  "evidence_requests": [...],
  "compressed_state": "the self-compressed summary",
  "key_insights": [...],
  "token_usage": {"input": int, "output": int, "reasoning": int}
}

---

## agents/evidence/packager.py

Owns the entire evidence retrieval and tagging pipeline. Called BY
the Orchestrator when new evidence is needed. The Orchestrator decides
IF evidence should be fetched — the Packager only executes the
retrieval [4].

The Packager gets a FRESH context window per run — discarded after
each evidence gathering round.

The three retrieval agents (structural, market, news) are INTERNAL
to the Packager. They are NOT separate nodes in the main LangGraph
graph. The Packager dispatches all three in parallel using
asyncio.gather, collects their raw results, then makes ONE Gemini
call to tag all collected evidence against active hypotheses [3].

The Packager receives:
- evidence_requests: list of dicts with type and description (from
  the Investigator's output, passed through by the Orchestrator)
- active_hypotheses: list of current survivors (for tagging reference)

The Packager returns:
- list of tagged atomic observations following the observation schema
  (observation.py) — each with observation_id, content, source, type,
  supports, contradicts, neutral

The Orchestrator then:
1. Extracts atom IDs and briefs for the case file (references only)
2. Passes full tagged atoms to the Investigator's next context window [4]

---

## agents/evidence/structural_agent.py

Searches the corpus/structural/ directory for domain knowledge atoms
relevant to evidence requests. Called internally by the Evidence
Packager — not directly by the Orchestrator or LangGraph graph.

Receives: evidence requests of type "structural" with descriptions.
Returns: raw file contents as list of dicts with atom_id and content.
No tagging — the Packager handles tagging after all agents return.

For the hackathon, this searches Vatsal's pre-curated structural
atoms — banking rules, HTM accounting standards, PONV clauses,
regulatory frameworks, market mechanics, ownership caps. These are
domain knowledge atoms that don't change day-to-day [4].

Retrieval method: semantic similarity or keyword matching against
request descriptions. Simple but functional for hackathon.

Live API collection (e.g., fetching regulatory documents in real-time)
is a stretch goal.

---

## agents/evidence/market_agent.py

Searches the corpus/empirical/ directory for market data relevant to
evidence requests. Called internally by the Evidence Packager.

Receives: evidence requests of type "market_data" with descriptions.
Returns: raw data as list of dicts with atom_id and content.
No tagging — Packager handles tagging.

For the hackathon, this searches pre-downloaded market data — stock
prices, CDS spreads, Treasury yields, VIX, bank sector ETF data,
deposit flow data. Sources: FRED, Yahoo Finance, pre-downloaded
as local files.

Live API collection is a stretch goal.

---

## agents/evidence/news_agent.py

Searches the corpus/empirical/ directory for news articles and filing
excerpts relevant to evidence requests. Called internally by the
Evidence Packager.

Receives: evidence requests of type "news" or "filing" with descriptions.
Returns: raw content as list of dicts with atom_id and content.
No tagging — Packager handles tagging.

For the hackathon, this searches pre-curated news articles and SEC
filing excerpts — 10-K risk sections, capital raise announcements,
rating agency actions, central bank statements, analyst reports.

Live API collection is a stretch goal.

---

## graph/investigation_graph.py

The ONLY file in the project that imports LangGraph [5]. Imports pure
functions from orchestrator.py, investigator.py, and packager.py.
Wires them into a StateGraph with nodes and conditional edges.

Every other agent file is a plain Python module with async functions
that take state and return state. This means if LangGraph gives
trouble during the hackathon, you can fall back to a simple async
loop calling the same functions without rewriting any logic [2].

Nodes:
- tier2_evaluate — calls orchestrator.evaluate_signal
- create_case — calls orchestrator.create_case_file
- investigate — calls investigator with context assembled by
  orchestrator.prepare_investigator_context
- process_output — calls orchestrator.process_investigation_output
  to parse self-compressed state and update case file
- check_convergence — calls orchestrator.should_continue
- gather_evidence — calls packager which internally dispatches
  three parallel agents and returns tagged observations
- increment_cycle — increments cycle counter in state
- generate_alert — calls orchestrator.generate_alert and
  orchestrator.detect_contagion

Conditional edges:
- After tier2_evaluate: escalate → create_case, dismiss → END
- After check_convergence: continue → gather_evidence, converge →
  generate_alert

Flow:
tier2_evaluate → create_case → investigate → process_output →
check_convergence → (gather_evidence → increment_cycle → investigate)
OR (generate_alert → END)

Exports a compiled graph that can be invoked with a trigger signal
and returns the complete investigation state including case file [4].

---

## gemini/client.py

Gemini API wrapper used by all components that make Gemini calls —
Investigator (heavy reasoning), Orchestrator (Tier 2 evaluation,
alert generation, contagion detection), and Evidence Packager
(atom tagging) [3].

Uses Gemini 2.0 Flash via Google AI Studio. Enforces JSON response
format with response_mime_type set to application/json. Temperature
set to 0.2 for reliable structured output.

Includes retry logic with 3 attempts and exponential backoff for
failed or malformed responses. Strict JSON schema validation on
every response — if validation fails, retry.

Tracks token usage per call — input tokens and output tokens.
Returns token counts alongside the response so the Orchestrator
can update context window tracking in the case file.

Has a fallback method that loads pre-cached JSON from a file path
if the API call fails or times out. Critical for demo reliability —
the frontend looks identical whether live or cached [4].

---

## gemini/prompts/tier2_evaluation.py

Prompt template for Tier 2 semantic signal evaluation. This is a
small, fast Gemini call made by the Orchestrator at the start of
investigation [4].

Input loaded into prompt: trigger signal + basic entity information.
Instructs Gemini to assess whether the signal is routine (dismiss)
or warrants investigation (escalate). Should consider signal
magnitude, historical context, entity profile.

Output: JSON with assessment reasoning and escalate/dismiss decision.

---

## gemini/prompts/investigation.py

The most critical prompt in the entire system. Defines the full
investigation cycle that the Investigator executes: GENERATE (Cycle 1
only) → SCORE → ELIMINATE → CROSS-MODAL CHECK → EVIDENCE REQUEST →
SELF-COMPRESS [3].

Must instruct Gemini to:
- Score every active hypothesis against every evidence atom
- Cite specific atom IDs for every scoring decision
- Kill hypotheses contradicted by evidence, citing the exact atom
- Detect cross-modal contradictions between structural and empirical
  atoms [3]
- Generate specific evidence requests to discriminate between survivors
- Self-compress at the end with cumulative summary covering all
  prior cycles

The self-compression instruction must specify that the compressed
state section should be clearly delimited (=== COMPRESSED STATE ===
and === END COMPRESSED STATE ===) so utils/parser.py can extract it
reliably.

For Cycle 1, the prompt must also instruct hypothesis generation from
the trigger signal — 8-10 competing explanations covering different
causal categories.

This prompt directly determines the quality of the entire system's
reasoning. Spend significant time testing and iterating on this
prompt [3].

---

## gemini/prompts/evidence_tagging.py

Prompt template for the Evidence Packager's tagging step. This is a
focused Gemini call that classifies evidence against hypotheses.

Input: raw retrieved evidence from three agents + list of active
hypotheses with names and current scores.

Instructs Gemini to assess each evidence-hypothesis pair and tag
with supports/contradicts/neutral. Must consider both direct and
indirect relationships. An atom that contradicts a hypothesis is
the basis for elimination — this tagging must be accurate [3].

Output: JSON list of tagged atomic observations following the
observation schema defined in models/observation.py.

---

## main.py

FastAPI entry point exposing the investigation engine to the frontend.
This is the API layer that the React frontend calls.

Endpoints:
- POST /api/investigate — receives trigger signal (entity name +
  event description). Runs the full LangGraph investigation. Streams
  progress updates via Server-Sent Events (SSE) so the frontend can
  show each cycle progressing in real-time. Each SSE event contains:
  current cycle, hypothesis status, latest eliminations, evidence
  requests, context window token usage, agent status.
- GET /api/case/{entity} — returns the current case file for an
  entity as JSON.
- POST /api/investigate/cached — returns pre-cached investigation
  results from corpus/cached/svb_full_run.json for demo fallback.
  Same response format as the live endpoint. Frontend looks identical
  whether live or cached [4].
- GET /api/health — health check endpoint.

CORS middleware allowing all origins. No authentication. Runs locally
on laptop for hackathon demo.

---

## config.py

Central configuration — single source of truth for all configurable
values. No hardcoded values in other files — everything references
config.

Fields:
- GEMINI_API_KEY: string — from environment variable
- GEMINI_MODEL: string — "gemini-2.0-flash"
- GEMINI_TEMPERATURE: float — 0.2 for reliable structured output
- MAX_CYCLES: int — default 5
- MAX_HYPOTHESES: int — default 10
- CONVERGENCE_THRESHOLD: int — hypothesis count to trigger convergence
- STAGNATION_CYCLES: int — consecutive unchanged cycles before forced
  convergence
- CORPUS_STRUCTURAL_PATH: string — path to corpus/structural/
- CORPUS_EMPIRICAL_PATH: string — path to corpus/empirical/
- CACHED_FALLBACK_PATH: string — path to corpus/cached/svb_full_run.json
- SSE_HEARTBEAT_INTERVAL: int — seconds between SSE keepalive messages

---

## corpus/

Pre-curated evidence for the demo events. This simulates what a
bank's Tier 0/1 infrastructure would produce — market data feeds,
news aggregation, filing monitors [4]. Our system starts at Tier 2,
building on top of this pre-existing data.

corpus/structural/ — Vatsal's domain knowledge atoms. Files named
by atom ID (S01_capital_requirements.txt, S02_htm_accounting.txt,
etc.). Each file contains one atomic piece of structural knowledge
about banking rules, regulatory frameworks, market mechanics,
accounting standards. These atoms don't change day-to-day — they
are domain knowledge, not time-series data.

corpus/empirical/ — Market data and news. Files named by atom ID
(E01_svb_stock_march8.txt, E03_cds_spreads.txt, etc.). Each file
contains one atomic piece of empirical evidence — a price movement,
a filing excerpt, a news article, a data point.

corpus/cached/ — Pre-computed complete investigation runs for demo
fallback. svb_full_run.json contains the full investigation state
after all cycles including case file, all hypotheses, all
eliminations, all evidence, context window tracking. If the live
API fails during demo, the system seamlessly switches to this
cached result [4].

---

## utils/token_counter.py

Tracks token usage across all Gemini calls per agent per cycle.
The Gemini client (gemini/client.py) returns token counts with
every response. This utility aggregates them.

Provides:
- Per-call tracking: input tokens, output tokens
- Per-cycle aggregation: investigator tokens, packager tokens,
  orchestrator tokens
- Running totals: total input, total output, total reasoning
- Context window utilization estimates: what percentage of each
  agent's context window was used per cycle

These numbers feed into:
- The case file's context_windows and token_usage sections
- The frontend's context window breathing visualization [3]
- The Orchestrator's budget tracking for convergence decisions

---

## utils/parser.py

Parses the Investigator's self-compressed state from its full
response. The Investigator produces a COMPRESSED STATE section
delimited by === COMPRESSED STATE === and === END COMPRESSED STATE ===
at the end of its reasoning output.

This utility extracts that section cleanly so the Orchestrator can
save it to the case file without processing the full reasoning
trace. Pure string parsing — no Gemini call needed [4].

Also provides helper functions to parse the Investigator's full
JSON response into structured components: surviving_hypotheses,
eliminated_hypotheses, cross_modal_flags, evidence_requests,
key_insights. These parsed components are what the Orchestrator
uses to update the case file fields [4].