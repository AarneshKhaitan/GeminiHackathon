# UI Design: Hypothesis Elimination Engine

This needs to look like a **mission control center for AI-driven financial investigation** — think Bloomberg terminal meets NASA flight control. Every element should feel like it has purpose and urgency.

---

## Screen Architecture

The app has **three main screens** that flow sequentially, plus a persistent status bar:

```
┌─────────────────────────────────────────────────────────┐
│  PERSISTENT: Orchestrator Status Bar (always visible)    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  SCREEN 1: Signal Intake + Tier 2 Evaluation            │
│            (entry point — trigger arrives)                │
│                                                          │
│  SCREEN 2: Live Investigation Dashboard                  │
│            (the main show — cycles run here)              │
│                                                          │
│  SCREEN 3: Convergence + Alert Output                    │
│            (final diagnosis + network contagion)          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Persistent Element: Orchestrator Status Bar

This stays at the top of every screen. It's the **heartbeat of the system** — judges always know what's happening:

```
┌─────────────────────────────────────────────────────────────────┐
│  🎯 ORCHESTRATOR                                                │
│                                                                  │
│  Entity: SVB          Tier: ██ 4              Cycle: 3 of 5    │
│  Signal: -60% stock   Status: INVESTIGATING   Budget: 72%      │
│                                                                  │
│  Context Window: [██████████████░░░░░░░░░░░░░░] 45%            │
│                   Reasoning: 38%  Evidence: 5%  Compressed: 2%  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Components for Status Bar

| Component | What It Shows |
|---|---|
| Entity badge | Name of entity under investigation |
| Tier indicator | Current tier with color — Tier 2 (yellow), Tier 3 (orange), Tier 4 (red) — animates when tier changes |
| Cycle counter | Current cycle of max cycles |
| Status label | EVALUATING → INVESTIGATING → CONVERGING → ALERT or ALL-CLEAR |
| Budget meter | API credit usage as percentage |
| Context window bar | The breathing visualization — segmented by reasoning tokens, evidence tokens, compressed state tokens [3] |

The context window bar is your **signature visual differentiator** [3]. It should be a segmented horizontal bar with three colors:

```
Context Window Segments:
  ████ Blue (#2563EB)   = Reasoning tokens
  ████ Green (#059669)  = Evidence tokens  
  ████ Purple (#7C3AED) = Compressed state from prior cycles
  ░░░░ Gray (#E5E7EB)   = Available space
```

As each cycle runs, the blue reasoning section **grows in real-time** — judges watch the system thinking. Between cycles, the bar **compresses** (shrinks) and then refills with new reasoning in the next cycle. This is the breathing pattern [3].

---

## Screen 1: Signal Intake + Tier 2 Evaluation

This is the **opening screen** — clean, minimal, dramatic. The trigger arrives and the system evaluates it:

```
┌─────────────────────────────────────────────────────────────────┐
│  🎯 ORCHESTRATOR  |  Entity: —  |  Tier: —  |  Status: IDLE    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                                                                  │
│                    ┌────────────────────────┐                    │
│                    │                        │                    │
│                    │   ⚡ SIGNAL INTAKE      │                    │
│                    │                        │                    │
│                    │   Select a trigger:    │                    │
│                    │                        │                    │
│                    │   [SVB — March 2023]   │  ← sample button  │
│                    │   [Custom trigger...]  │                    │
│                    │                        │                    │
│                    └────────────────────────┘                    │
│                                                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

After clicking the SVB trigger, the screen transforms with an **animation sequence**:

```
┌─────────────────────────────────────────────────────────────────┐
│  🎯 ORCHESTRATOR  |  Entity: SVB  |  Tier: ██ 2  |  EVALUATING │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  ⚡ INCOMING SIGNAL                                      │    │
│  │                                                          │    │
│  │  Entity:    Silicon Valley Bank (SVB)                    │    │
│  │  Event:     Stock price dropped 60% after hours          │    │
│  │  Date:      March 8, 2023                                │    │
│  │  Magnitude: 4.2σ event (extreme)                        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  🔍 TIER 2: SEMANTIC EVALUATION                         │    │
│  │                                                          │    │
│  │  Analyzing signal...                                     │    │
│  │  ████████████░░░░░░░░░░░░░░░░░░░░ 35%                  │    │
│  │                                                          │    │
│  │  Assessment: "60% single-day decline is a 4+ sigma      │    │
│  │  event. Inconsistent with routine sector rotation.       │    │
│  │  Multiple causal pathways possible. Warrants             │    │
│  │  investigation."                                         │    │
│  │                                                          │    │
│  │  Decision: ⬆️ ESCALATE TO TIER 3                        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

The tier indicator in the status bar **animates from 2 to 3** — a visual escalation. Then the screen transitions to Screen 2.

### Components for Screen 1

| Component | Purpose |
|---|---|
| Signal intake card | Displays the trigger event with entity, event description, date, magnitude |
| Sample trigger buttons | Pre-loaded demo events (SVB primary, backup if needed) |
| Tier 2 evaluation panel | Shows Gemini's semantic assessment with loading animation |
| Escalation decision | Animated transition from EVALUATE to ESCALATE with tier change |

---

## Screen 2: Live Investigation Dashboard

This is **the main show** — where judges spend most of the demo time. It's a **three-column layout** with the investigation timeline on the left, hypothesis status in the center, and evidence/reasoning on the right:

```
┌─────────────────────────────────────────────────────────────────┐
│  🎯 ORCHESTRATOR  |  SVB  |  Tier: ██ 4  |  Cycle: 3 of 5     │
│  Context: [████████████████░░░░░░░░░░░░░░] 52%                 │
│           Reasoning: 42%  Evidence: 7%  Compressed: 3%          │
├──────────────┬──────────────────────────┬───────────────────────┤
│              │                          │                       │
│  CYCLE       │  HYPOTHESIS STATUS       │  EVIDENCE +           │
│  TIMELINE    │                          │  REASONING            │
│              │                          │                       │
│  ┌────────┐  │  ┌────────────────────┐  │  ┌─────────────────┐ │
│  │Cycle 1 │  │  │ ✅ H2: Duration    │  │  │ LATEST EVIDENCE │ │
│  │10 → 7  │  │  │    mismatch       │  │  │                 │ │
│  │        │  │  │    Score: 0.91     │  │  │ E10: SVB HTM    │ │
│  └───┬────┘  │  │    ████████████░░  │  │  │ portfolio had   │ │
│      │       │  └────────────────────┘  │  │ $15B unrealized │ │
│  ┌───┴────┐  │  ┌────────────────────┐  │  │ losses          │ │
│  │Cycle 2 │  │  │ ✅ H5: Deposit     │  │  │                 │ │
│  │7 → 4   │  │  │    flight          │  │  │ Supports: H2,H7│ │
│  │        │  │  │    Score: 0.85     │  │  │ Contradicts: H1 │ │
│  └───┬────┘  │  │    ██████████░░░░  │  │  └─────────────────┘ │
│      │       │  └────────────────────┘  │                       │
│  ┌───┴────┐  │  ┌────────────────────┐  │  ┌─────────────────┐ │
│  │Cycle 3 │  │  │ ❌ H1: Routine     │  │  │ CROSS-MODAL     │ │
│  │4 → ?   │  │  │    correction      │  │  │ CONTRADICTION   │ │
│  │ ⏳      │  │  │    KILLED Cycle 1  │  │  │                 │ │
│  └────────┘  │  │    by atom E01     │  │  │ ⚠️ S04 says     │ │
│              │  └────────────────────┘  │  │ "well-           │ │
│  ┌────────┐  │  ┌────────────────────┐  │  │ capitalized"    │ │
│  │Cycle 4 │  │  │ ❌ H8: Crypto      │  │  │ BUT E10 shows  │ │
│  │pending │  │  │    contagion       │  │  │ $15B hidden     │ │
│  └────────┘  │  │    KILLED Cycle 1  │  │  │ losses          │ │
│              │  │    by atom S03     │  │  └─────────────────┘ │
│  ┌────────┐  │  └────────────────────┘  │                       │
│  │Cycle 5 │  │  ┌────────────────────┐  │  ┌─────────────────┐ │
│  │pending │  │  │ ❌ H3: Credit risk  │  │  │ EVIDENCE        │ │
│  └────────┘  │  │    KILLED Cycle 2  │  │  │ REQUESTS        │ │
│              │  │    by atom E05     │  │  │                 │ │
│              │  └────────────────────┘  │  │ 📡 Fetching:    │ │
│              │  ┌────────────────────┐  │  │ - Social media  │ │
│              │  │ ❌ H4: Regulatory   │  │  │   activity      │ │
│              │  │    KILLED Cycle 2  │  │  │ - CDS spread    │ │
│              │  │    by atom S04     │  │  │   data          │ │
│              │  │    ⚠️ CROSS-MODAL  │  │  │                 │ │
│              │  └────────────────────┘  │  │ Structural ✅   │ │
│              │                          │  │ Market    ⏳    │ │
│              │  ... more hypotheses ... │  │ News      ✅   │ │
│              │                          │  └─────────────────┘ │
├──────────────┴──────────────────────────┴───────────────────────┤
│  CONTEXT WINDOW BREATHING                                       │
│                                                                  │
│  Cycle 1  [████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░] 38%       │
│  Cycle 2  [██████████████████░░░░░░░░░░░░░░░░░░░░░] 52%       │
│  Cycle 3  [████████████████████████░░░░░░░░░░░░░░░] 65% ← NOW │
│                                                                  │
│  ████ Reasoning  ████ Evidence  ████ Compressed  ░░░░ Available │
└─────────────────────────────────────────────────────────────────┘
```

### Left Column: Cycle Timeline

A **vertical timeline** showing each cycle as a node. Completed cycles show hypothesis count reduction. Current cycle pulses. Future cycles are grayed out:

| Cycle State | Visual Treatment |
|---|---|
| Completed | Solid node with "10 → 7" reduction count, green checkmark |
| Active | Pulsing node with spinner, highlighted border |
| Pending | Grayed out node, dashed border |

Between each cycle node, show a **thin connector line** with a small compression icon indicating the orchestrator compressed and dispatched evidence agents between cycles.

### Center Column: Hypothesis Status

This is the **most important visual element**. Each hypothesis is a card:

**Surviving hypothesis card:**
```
┌────────────────────────────────────────┐
│ ✅ H2: Duration mismatch in HTM        │
│                                        │
│ Score: 0.91                            │
│ ████████████████████░░░  (91%)         │
│                                        │
│ Key evidence: E09, E10, S02, S05      │
│ "HTM portfolio holds $15B in           │
│  unrealized losses hidden by           │
│  accounting classification"            │
└────────────────────────────────────────┘
```

Design: White background, left green border (#059669), subtle shadow, confidence bar filled in green.

**Eliminated hypothesis card:**
```
┌────────────────────────────────────────┐
│ ❌ H8: Crypto sector contagion         │
│                                        │
│ ELIMINATED — Cycle 1                   │
│ Killed by: S03                         │
│ "SVB crypto exposure was <2% of        │
│  total assets per filing data"         │
└────────────────────────────────────────┘
```

Design: Light gray background, left red border (#DC2626), strikethrough on hypothesis name, collapsed by default (click to expand kill reason).

**Cross-modal contradiction flag:**
```
┌────────────────────────────────────────┐
│ ⚠️ CROSS-MODAL CONTRADICTION           │
│                                        │
│ Structural: S04 — "SVB passed all      │
│ regulatory stress tests"               │
│                                        │
│ Empirical: E10 — "$15B unrealized      │
│ losses not captured by regulatory      │
│ metrics"                               │
│                                        │
│ "Regulatory framework could not see    │
│  the actual risk exposure"             │
└────────────────────────────────────────┘
```

Design: Amber (#D97706) left border, amber background tint, pulsing warning icon. This card should **stand out visually** — it's the "how did they think of that" moment [3].

### Right Column: Evidence + Reasoning

Two sections stacked:

**Latest evidence section** — shows the most recently collected evidence atoms with their hypothesis tags (supports/contradicts/neutral). New atoms animate in as evidence agents return results.

**Evidence requests section** — shows what the investigator has requested for the next cycle, with status indicators for each evidence agent (structural ✅, market ⏳, news ✅).

### Bottom Section: Context Window Breathing

A **multi-row visualization** showing context window usage across all cycles [3]. Each row represents one cycle's context window:

```
Cycle 1  [████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░] 38%
Cycle 2  [██████████████████░░░░░░░░░░░░░░░░░░░░░] 52%
Cycle 3  [████████████████████████░░░░░░░░░░░░░░░] 65% ← ACTIVE
Cycle 4  [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] pending
Cycle 5  [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] pending
```

Each bar is segmented with the three colors (reasoning blue, evidence green, compressed purple). The active cycle's bar **animates in real-time** as the investigator reasons — the blue section grows as tokens are generated [3]. Between cycles, a brief **compression animation** shows the bar shrinking before the next cycle begins.

This visualization alone differentiates you from every other hackathon team [3].

### Components for Screen 2

| Component | Technology |
|---|---|
| Cycle timeline | Custom React component with CSS animations |
| Hypothesis cards | React cards with conditional styling (surviving/eliminated/flagged) |
| Confidence bars | Plotly.js horizontal bar or custom CSS bar |
| Evidence atom cards | React cards with color-coded tags |
| Cross-modal contradiction card | Highlighted card with amber styling |
| Evidence agent status | Simple status indicators with spinner/checkmark |
| Context window breathing | Plotly.js stacked horizontal bar chart or custom SVG |
| Transitions between cycles | CSS animations with loading states |

---

## Screen 3: Convergence + Alert Output

After the final cycle, the dashboard transitions to the **convergence screen**. This is the payoff — the diagnosis and alert:

```
┌─────────────────────────────────────────────────────────────────┐
│  🎯 ORCHESTRATOR  |  SVB  |  Tier: ██ 4  |  CONVERGED          │
│  Context: [████████████████████████████░░░] 78% (final cycle)   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  🚨 CRITICAL RISK ALERT                                 │    │
│  │                                                          │    │
│  │  DIAGNOSIS:                                              │    │
│  │  Structural vulnerability (duration mismatch hidden      │    │
│  │  by HTM accounting) triggered by behavioral contagion    │    │
│  │  (social-media-accelerated correlated deposit flight     │    │
│  │  among concentrated VC-backed client base)               │    │
│  │                                                          │    │
│  │  Decisive signal detected: 48-72 hours before            │    │
│  │  market consensus                                        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌──────────────────────┐  ┌────────────────────────────────┐   │
│  │ SURVIVING HYPOTHESES │  │ ELIMINATION SUMMARY            │   │
│  │                      │  │                                │   │
│  │ ★ H2: Duration       │  │ Cycle 1: 10 → 7               │   │
│  │   mismatch           │  │   ✗ H1  (E01)                 │   │
│  │   Confidence: 0.94   │  │   ✗ H8  (S03)                 │   │
│  │   ████████████████░  │  │   ✗ H10 (E04)                 │   │
│  │                      │  │                                │   │
│  │ ★ H5: Correlated     │  │ Cycle 2: 7 → 4                │   │
│  │   deposit flight     │  │   ✗ H3  (E05)                 │   │
│  │   Confidence: 0.89   │  │   ✗ H4  (S04) ⚠️ cross-modal │   │
│  │   ██████████████░░░  │  │   ✗ H9  (subsumed by H2)     │   │
│  │                      │  │                                │   │
│  │ Evidence chains:     │  │ Cycle 3: 4 → 3                │   │
│  │ H2: E09→E10→S02→S05 │  │   ✗ H6  (merged into H5)     │   │
│  │ H5: E07→E08→S08→S11 │  │                                │   │
│  │                      │  │ Cycle 4: 3 → 2 CONVERGED      │   │
│  └──────────────────────┘  └────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  📡 NETWORK CONTAGION DETECTION                         │    │
│  │                                                          │    │
│  │  Counterparties sharing risk profile:                    │    │
│  │                                                          │    │
│  │  First Republic    ⬆️ PROMOTED TO TIER 2                │    │
│  │  Reason: Similar depositor concentration profile         │    │
│  │                                                          │    │
│  │  Signature Bank    ⬆️ PROMOTED TO TIER 2                │    │
│  │  Reason: Similar narrative exposure                      │    │
│  │                                                          │    │
│  │  Regional banks    👁️ WATCH LIST                        │    │
│  │  Reason: HTM portfolio concentration above threshold     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  CONTEXT WINDOW HISTORY                                  │    │
│  │                                                          │    │
│  │  C1 [████████████░░░░░░░░░░░░░░░░░░░] 38%  210K tokens │    │
│  │  C2 [██████████████████░░░░░░░░░░░░░] 52%  285K tokens │    │
│  │  C3 [████████████████████████░░░░░░░] 65%  340K tokens │    │
│  │  C4 [██████████████████████████████░] 78%  395K tokens │    │
│  │                                                          │    │
│  │  Total reasoning tokens: 1.23M across 4 cycles          │    │
│  │  Total evidence tokens:  89K                            │    │
│  │  Compression ratio: 94% (raw reasoning → structured)    │    │
│  │                                                          │    │
│  │  ████ Reasoning  ████ Evidence  ████ Compressed         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Components for Screen 3

| Component | Purpose |
|---|---|
| Alert banner | Red (#DC2626) full-width banner with diagnosis text — the first thing judges see |
| Surviving hypothesis cards | Enlarged cards showing final confidence scores and complete evidence chains |
| Elimination summary | Compact timeline showing every elimination across all cycles with cited atoms |
| Network contagion panel | Shows promoted counterparties with reasons — the cascade detection moment [4] |
| Context window history | Complete breathing visualization across all cycles with token counts [3] |
| Compression ratio stat | Shows total reasoning tokens vs compressed state — proves the system thought hard |

---

## Animation and Transition Design

The transitions between states are what make the demo feel **alive**:

### Tier Escalation Animation
When the orchestrator promotes from Tier 2 → 3 → 4, the tier indicator in the status bar:
- Pulses briefly
- Color shifts (yellow → orange → red)
- Number increments with a brief scale-up effect

### Hypothesis Elimination Animation
When a hypothesis is eliminated:
- Card briefly flashes red
- Confidence bar drains to zero
- Card collapses with a smooth slide animation
- Kill reason appears as the card settles into its collapsed state
- Eliminated card moves to the bottom of the list with strikethrough styling

### Evidence Arrival Animation
When evidence agents return new atoms:
- Atom cards slide in from the right
- Tags (supports/contradicts/neutral) appear with color coding
- If an atom contradicts a hypothesis, a brief connecting line flashes between the atom and the doomed hypothesis card

### Context Window Growth Animation
During active reasoning:
- The blue reasoning section of the context bar grows smoothly in real-time
- Token count increments beside the bar
- Between cycles, a compression animation shows the bar shrinking (blue → purple transition) before the next cycle begins fresh

### Alert Trigger Animation
When the final cycle converges and alert fires:
- Screen transition with a brief flash effect
- Alert banner slides down from the top
- Surviving hypothesis cards enlarge and center
- Network contagion panel fades in below

---

## Making It Look Cool: Design System

### Typography

| Element | Font | Size | Weight |
|---|---|---|---|
| Status bar labels | Inter or SF Mono | 14px | 600 |
| Hypothesis names | Inter | 18px | 700 |
| Scores and metrics | SF Mono (monospace) | 16px | 500 |
| Evidence content | Inter | 14px | 400 |
| Alert diagnosis | Inter | 20px | 700 |
| Section headers | Inter | 16px | 600 |

### Color System

| Element | Color | Hex |
|---|---|---|
| Surviving hypothesis border | Green | #059669 |
| Eliminated hypothesis border | Red | #DC2626 |
| Cross-modal contradiction | Amber | #D97706 |
| Reasoning tokens | Blue | #2563EB |
| Evidence tokens | Green | #10B981 |
| Compressed state tokens | Purple | #7C3AED |
| Alert banner background | Deep red | #991B1B |
| Alert banner text | White | #FFFFFF |
| Card backgrounds | White | #FFFFFF |
| Page background | Very dark navy | #0F172A |
| Text primary | White | #F8FAFC |
| Text secondary | Light gray | #94A3B8 |

### The Dark Theme Is Essential

Use a **dark background** (#0F172A) with light text and colored cards. This creates the mission control / Bloomberg terminal aesthetic that makes the demo feel serious and professional. Light mode looks like a homework assignment. Dark mode looks like a command center.

### Card Design

All cards should have:
- Subtle border radius (8px)
- Thin left color border (4px) indicating status
- Very slight background elevation (dark gray #1E293B on dark navy #0F172A)
- Subtle box shadow for depth
- Consistent internal padding (16px)

### Glassmorphism Effect (Optional but Stunning)

For the alert banner and cross-modal contradiction cards, consider a subtle glassmorphism effect:
- Semi-transparent background with backdrop blur
- Creates a layered depth effect
- Makes critical elements feel like they're floating above the dashboard

---

## Responsive Layout for Projector

The demo will be projected. Design for this:

| Constraint | Solution |
|---|---|
| Font must be readable from back of room | Minimum 14px, prefer 16-18px for key elements |
| Colors must have high contrast | Dark background + bright accent colors |
| Layout must not feel cramped | Generous padding, clear visual hierarchy |
| Three-column layout on wide screen | Use CSS grid with responsive breakpoints |
| Status bar always visible | Sticky position at top |

---

## Component Summary

| Screen | Components |
|---|---|
| **Persistent Status Bar** | Entity badge, Tier indicator (animated), Cycle counter, Status label, Budget meter, Context window segmented bar [3] |
| **Screen 1: Signal Intake** | Signal intake card, Sample trigger buttons, Tier 2 evaluation panel with loading animation, Escalation decision with tier transition animation |
| **Screen 2: Investigation** | Cycle timeline (vertical, animated nodes), Hypothesis cards (surviving/eliminated/flagged), Confidence bars, Evidence atom cards with color-coded tags, Cross-modal contradiction card (amber highlight), Evidence agent status indicators, Context window breathing visualization (multi-row, animated) [3], Evidence requests panel |
| **Screen 3: Convergence** | Alert banner (red, full-width), Surviving hypothesis cards (enlarged, with evidence chains), Elimination summary timeline, Network contagion panel with promoted counterparties [4], Context window history with token counts and compression ratio |

---

**Dark theme. Mission control aesthetic. Animated transitions. Context window breathing. Every elimination traced to a specific atom. Build it to look like the future of risk intelligence.**