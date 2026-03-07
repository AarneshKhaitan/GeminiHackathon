# Product Requirements Document: Hypothesis Elimination Engine

---

## 1. Problem Statement

### Current Situation

Financial risk management today relies on pattern matching — systems that find correlations in historical data and flag anomalies when current patterns deviate from historical norms [4]. These systems operate at Tier 0/1 level: statistical heartbeats, z-scores, threshold checks. When a signal is flagged, human analysts manually investigate by reading reports, cross-referencing data, and forming judgments. The AI tools available to them are single-pass summarizers that produce generic assessments like "risk is elevated due to market volatility" [3].

The 1M context window available in models like Gemini is currently used as storage — teams dump documents in and ask for summaries. Baseline RAG is now a baseline feature [3]. If a single prompt can solve it, it is not an application [3].

### User Pain Points

- **Analysts spend hours manually investigating flagged signals** — reading filings, cross-referencing market data, checking news, forming hypotheses, and testing them one by one
- **Single-pass AI analysis produces vague, generic outputs** — "risk is elevated" tells an analyst nothing actionable [3]
- **No systematic hypothesis elimination** — analysts hold competing theories in their heads with no structured process to eliminate wrong ones against evidence
- **Cross-modal contradictions go undetected** — structural knowledge (regulatory frameworks, market mechanics) and empirical evidence (market data, filings) are analyzed separately, missing contradictions that only surface when both modalities are combined [3]
- **Contagion detection is reactive** — counterparties sharing risk profiles are identified after market prices show contagion, not before [4]
- **No audit trail** — when a risk call is made, there's no traceable reasoning chain showing which evidence supported or contradicted each hypothesis

### Business Impact

- Real risk management is hypothesis elimination, not pattern matching [4]
- The SVB collapse demonstrated that traditional risk metrics ("well-capitalized by regulatory standards") can mask catastrophic exposure ($15B in unrealized HTM losses) [4]
- A system that identifies the correct risk diagnosis 48-72 hours before market consensus provides decisive advantage [4]
- The reasoning architecture generalizes beyond finance — medical diagnosis, engineering failure analysis, intelligence assessment, scientific research

---

## 2. Proposed Solution

### Overview

A multi-agent hypothesis elimination engine that receives a trigger signal, generates competing hypotheses about what's driving the risk, then directs its own investigation — requesting specific evidence, eliminating wrong theories across multiple reasoning cycles, and converging on a diagnosis with full traceability [4].

The system consists of three core components:

- **Orchestrator Agent** — stateful lifecycle manager that creates case files, dispatches evidence agents, parses and saves compressed investigation output between cycles, and makes convergence and alert decisions [4]
- **Investigator Agent** — stateless pure reasoning engine that receives a fresh context window per cycle, scores hypotheses against tagged evidence atoms, eliminates contradicted hypotheses, self-compresses its findings at the end of each cycle, and returns survivors with new evidence requests [4]
- **Evidence Gathering Agents** — three parallel retrieval agents (structural knowledge, market data, news/filings) plus an evidence packager that tags retrieved atoms against active hypotheses [4]

The system operates across a tiering framework starting at Tier 2, building on top of existing bank infrastructure at Tier 0/1 [4].

### User Stories

**US-1: Signal Investigation**
As a risk analyst, I want to feed a trigger signal into the system so that it automatically generates competing hypotheses and investigates each one against available evidence, saving me hours of manual investigation.

**US-2: Hypothesis Elimination Traceability**
As a risk manager, I want every hypothesis elimination to cite the specific evidence atom that killed it so that I can audit the reasoning chain and trust the system's conclusions.

**US-3: Cross-Modal Contradiction Detection**
As a senior risk officer, I want the system to detect when structural knowledge (regulatory frameworks, market mechanics) contradicts empirical evidence (market data, filings) so that hidden risks masked by one modality are surfaced.

**US-4: Automated Alert Generation**
As a portfolio manager, I want the system to generate an alert when surviving hypotheses indicate critical risk so that I can take action before market consensus forms.

**US-5: Network Contagion Detection**
As a systemic risk analyst, I want the system to automatically identify counterparties sharing the surviving risk profile so that potential contagion is flagged proactively before market prices show it [4].

**US-6: Investigation Audit Trail**
As a compliance officer, I want a complete case file documenting every cycle's reasoning — which hypotheses survived, which were eliminated, which evidence was used — so that risk decisions are fully auditable.

### Success Metrics

| Metric | Target |
|---|---|
| Hypothesis generation per trigger | 8-10 competing hypotheses |
| Elimination traceability | 100% of eliminations cite specific evidence atom |
| Cycle convergence | Converge to 2-3 survivors within 4-5 cycles |
| Reasoning depth per cycle | 150K+ tokens of reasoning traces per cycle |
| Cross-modal contradictions detected | At least 1 per investigation (when present in evidence) |
| Diagnosis accuracy (vs ground truth) | Surviving hypotheses match known post-mortem findings |
| Alert latency | Diagnosis reached within minutes, not hours or days |

---

## 3. Requirements

### Functional Requirements

**FR-1: Tier 2 — Semantic Signal Evaluation**
- System receives a trigger signal from Tier 0/1 infrastructure
- Single Gemini call evaluates whether signal warrants investigation
- Decision: dismiss (remain at Tier 2) or escalate (promote to Tier 3)
- Evaluation considers signal magnitude, historical context, entity profile

**FR-2: Tier 3 — Initial Investigation**
- Orchestrator creates a case file for the flagged entity
- Investigator generates 8-10 competing hypotheses from the trigger signal
- 1-2 quick reasoning cycles against available evidence
- Obvious impossibilities eliminated with cited evidence atoms
- Decision: demote to Tier 2 (all crisis hypotheses eliminated) or promote to Tier 4 (crisis hypotheses surviving)

**FR-3: Tier 4 — Full Hypothesis Elimination Engine**
- 4-5 deep reasoning cycles with fresh context window per cycle [4]
- Each cycle follows the loop: score against evidence → eliminate contradicted hypotheses → generate evidence requests → self-compress findings
- Investigator produces compressed state as final section of each cycle's output (tiered compression: 20-30K after cycle 1 ramping to 75-100K after cycle 4)
- Orchestrator parses compressed state section and saves to case file — no separate compression call needed
- Evidence agents dispatched in parallel between cycles to fetch requested evidence
- Cross-modal contradiction detection between structural and empirical atoms [3]
- Convergence when hypothesis count drops to 2-3 or maximum cycles reached

**FR-4: Evidence Gathering Pipeline**
- Three parallel agents: structural knowledge, market data, news/filings
- Evidence packager formats all retrieved evidence into atomic observations
- Each atom tagged with supports/contradicts/neutral for every active hypothesis
- Agents search pre-curated corpus based on investigator's specific evidence requests [4]

**FR-5: Case File Management**
- Persistent memory across cycles storing: active hypotheses with scores, eliminated hypotheses with kill reasons, evidence collected, evidence pending, compressed reasoning state, cycle history
- Updated by orchestrator after each cycle
- Serves as complete audit trail of investigation

**FR-6: Self-Compression Between Cycles**
- The Investigator self-compresses at the end of each cycle's reasoning output, producing a clearly delimited COMPRESSED STATE section within its response [7]
- The Orchestrator extracts this self-compressed state using `utils/parser.py` through pure string parsing — no separate Gemini compression call is needed [6]
- The Orchestrator saves the extracted compressed state to `case_file.compressed_reasoning`, REPLACING the previous cycle's compressed state (not appending) since each cycle's self-compression is cumulative, incorporating all prior cycles [4]
- Self-compression size scales with investigation complexity (tiered compression): ~20-30K tokens after Cycle 1 ramping to ~75-100K tokens after Cycle 4+ [7]
- The self-compressed state preserves: surviving hypotheses with updated confidence scores, eliminated hypotheses with specific kill atom IDs and one-line reasons, cross-modal contradictions detected, evidence needed for next cycle, crux question going into next cycle [3]
- The self-compressed state discards: verbose intermediate reasoning paths, detailed scoring of already-eliminated hypotheses, redundant evidence descriptions, analysis steps that led to obvious conclusions
- This design saves one large Gemini call (~200K input tokens) per cycle compared to a separate orchestrator-driven compression approach, reducing both API credit usage and inter-cycle latency [7]
- The compressed state is loaded into the next cycle's fresh context window by the Orchestrator's `prepare_investigator_context()` function as part of the Investigator's flat context package [4]
**FR-7: Alert System**
- Post-convergence evaluation of surviving hypotheses
- If surviving hypotheses indicate critical risk → alert triggered with diagnosis summary
- If all crisis hypotheses eliminated → all-clear report generated
- Alert includes: surviving hypotheses, confidence scores, evidence chains, earliest decisive signal timestamp

**FR-8: Network-Aware Contagion Detection**
- After convergence, orchestrator checks which counterparties share the surviving risk profile [4]
- Matching counterparties auto-promote to Tier 2 with new case files
- Inherited context from parent investigation informs new case files

**FR-9: Observation Schema**
- Every piece of evidence formatted as an atomic observation
- Fields: observation ID, content, source, type, supports (list of hypothesis IDs), contradicts (list of hypothesis IDs), neutral (list of hypothesis IDs)
- Schema enables programmatic merge candidate detection (stretch goal)

**FR-10: Hypothesis Merging (Stretch Goal)**
- Post-final-cycle synthesis step only — not within the cycle loop
- Merge trigger: both hypotheses survive all cycles, complementary evidence support, no contradicting observations, plausible causal link cited to specific structural atom
- Produces composite theories that explain more than component hypotheses alone

### Technical Requirements

**TR-1: Agent Orchestration**
- LangGraph for agent orchestration and cycle management [2]
- Orchestrator as top-level graph managing investigator calls and evidence dispatch
- Conditional edges for convergence detection (hypothesis count threshold, max cycle count, stagnation detection, budget check)

**TR-2: Gemini API Integration**
- Gemini 2.0 Flash via Google AI Studio for all reasoning calls [3]
- JSON response format enforced via generation config
- Low temperature (0.2) for structured output reliability
- Retry logic with exponential backoff for failed calls
- Schema validation on every Gemini response

**TR-3: Fresh Context Windows**
- Each investigator cycle receives a fresh context window [4]
- Prevents context rot that degrades attention quality beyond 40-60% window utilization
- Context loaded per cycle: compressed state + structural docs + new evidence + instructions
- Maximum loaded context per cycle: ~160K tokens leaving 840K+ for reasoning

**TR-4: Token Budget Management**
- Track token usage per cycle
- Self-compression targets embedded in investigator output: ~20-30K (cycle 1) ramping to ~75-100K (cycle 4+)
- Reasoning space per cycle: ~250K+ tokens minimum (includes reasoning + compressed state section)
- No separate compression calls — investigator self-compresses, saving one large Gemini call (~200K input) per cycle
- Total budget across 4-5 cycles: well within $80 API credits (4 team members × $20) [1]

**TR-5: Cached Fallback System**
- Pre-computed complete demo run for SVB event cached as JSON
- Invisible switch — UI looks identical whether live or cached
- Fallback triggered automatically if Gemini API latency exceeds threshold or returns invalid response

**TR-6: Parallel Evidence Agent Execution**
- Three evidence agents execute concurrently using asyncio.gather
- Evidence packager runs after all three agents complete
- Tagging step uses Gemini to assess each atom against active hypotheses

**TR-7: Backend Infrastructure**
- Python + FastAPI for API layer
- LangGraph for agent orchestration [2]
- NumPy for confidence scoring and statistical analysis
- Pandas for evidence corpus management
- No database — case files stored in memory as structured dictionaries
- No authentication, no deployment — run locally, demo from laptop

**TR-8: Frontend Infrastructure**
- React + TypeScript for UI
- Plotly.js for investigation dashboard charts
- Tailwind CSS for styling
- Components: orchestrator status bar, hypothesis cards, cycle timeline, context window visualization, alert display

