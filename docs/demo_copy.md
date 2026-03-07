# Demo Copy & Implementation Guide

**Purpose:** Exact copy + implementation code for the demo video. No voiceover — the UI is the pitch.
**Video length:** ~65 seconds (can trim to 60 by speeding up Screen 2 playback)
**Audience:** Hackathon judges (technical, not necessarily finance)

---

## Overview of Changes

1. **New:** `Screen0_ColdOpen` component — staggered text animation, problem statement, CTA button
2. **Store:** Expand `activeScreen` union to include `-1` for cold open
3. **App.tsx:** Add Screen 0 routing
4. **Screen 1:** Copy changes (subtitle, pipeline labels, eval panel, escalation)
5. **Screen 2:** Copy changes (banner text, breathing chart label)
6. **Screen 3:** Copy changes (comparison panels, bottom narrative)

---

## 1. New File: `Screen0_ColdOpen.tsx`

Create at: `frontend/src/components/screens/Screen0_ColdOpen/ColdOpenScreen.tsx`

```tsx
import { motion } from 'framer-motion'
import { useStore } from '../../../store'

const lines = [
  { text: 'Every risk system today does the same thing.', delay: 0 },
  { text: 'Data in. Summary out. Single pass. One shot.', delay: 1.5 },
  {
    text: 'Detecting that something is wrong is a solved problem.',
    delay: 3.5,
  },
  {
    text: 'ML models, statistical signals, anomaly detection — these work.',
    delay: 4.5,
  },
  { text: 'The hard problem is what comes next.', delay: 7, highlight: true },
  {
    text: 'When evidence contradicts itself. When context grows across cycles.',
    delay: 8.5,
  },
  { text: 'When you need to reason, not summarize.', delay: 9.5 },
]

const TITLE_DELAY = 11.5
const TAGLINE_DELAY = 12.5
const BUTTON_DELAY = 13.5

export function ColdOpenScreen() {
  const setActiveScreen = useStore((s) => s.setActiveScreen)

  return (
    <div
      className="h-full flex flex-col items-center justify-center p-10"
      style={{ backgroundColor: '#0C0A07' }}
    >
      <div className="max-w-xl space-y-1">
        {/* Staggered narrative lines */}
        {lines.map(({ text, delay, highlight }) => (
          <motion.p
            key={text}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay, duration: 0.6, ease: 'easeOut' }}
            className="text-[11px] font-mono leading-relaxed"
            style={{ color: highlight ? '#EDE4D4' : '#8C7A5E' }}
          >
            {text}
          </motion.p>
        ))}

        {/* Title block */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: TITLE_DELAY, duration: 0.6 }}
          className="pt-8"
        >
          <div
            className="tracking-[0.35em] mb-2"
            style={{
              fontFamily: 'Syne, sans-serif',
              fontWeight: 700,
              fontSize: '10px',
              color: '#4A3D2A',
            }}
          >
            ITERATIVE HYPOTHESIS ELIMINATION ENGINE
          </div>
        </motion.div>

        <motion.p
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: TAGLINE_DELAY, duration: 0.6, ease: 'easeOut' }}
          style={{
            fontFamily: 'Syne, sans-serif',
            fontWeight: 800,
            fontSize: '1.25rem',
            color: '#EDE4D4',
          }}
        >
          This system doesn't summarize. It investigates.
        </motion.p>

        {/* CTA button */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: BUTTON_DELAY, duration: 0.5 }}
          className="pt-6"
        >
          <button
            onClick={() => setActiveScreen(0)}
            className="text-[9px] font-mono tracking-wider px-4 py-2 transition-colors"
            style={{
              border: '1px solid #2E2820',
              backgroundColor: '#161310',
              color: '#C8912A',
              cursor: 'pointer',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#C8912A'
              e.currentTarget.style.backgroundColor = '#2D1E07'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = '#2E2820'
              e.currentTarget.style.backgroundColor = '#161310'
            }}
          >
            BEGIN INVESTIGATION →
          </button>
        </motion.div>
      </div>
    </div>
  )
}
```

---

## 2. Store Change: `frontend/src/store/index.ts`

### 2a. Expand `activeScreen` type

**Find:**
```ts
  activeScreen: 0 | 1 | 2
```
**Replace with:**
```ts
  activeScreen: -1 | 0 | 1 | 2
```

### 2b. Expand `setActiveScreen` type

**Find:**
```ts
  setActiveScreen: (screen: 0 | 1 | 2) => void
```
**Replace with:**
```ts
  setActiveScreen: (screen: -1 | 0 | 1 | 2) => void
```

### 2c. Change default `activeScreen` to `-1`

**Find:**
```ts
    activeScreen: 0,
```
**Replace with:**
```ts
    activeScreen: -1,
```

### 2d. Change `resetInvestigation` to go back to cold open

**Find (inside `resetInvestigation`):**
```ts
      s.activeScreen = 0
```
**Replace with:**
```ts
      s.activeScreen = -1
```

---

## 3. App.tsx Change: `frontend/src/App.tsx`

**Find:**
```tsx
import { SignalIntakeScreen } from './components/screens/Screen1_SignalIntake/SignalIntakeScreen'
```
**Add above it:**
```tsx
import { ColdOpenScreen } from './components/screens/Screen0_ColdOpen/ColdOpenScreen'
```

**Find (inside the `<AnimatePresence>`):**
```tsx
        {activeScreen === 0 && (
          <motion.div
            key="screen1"
```
**Add above it:**
```tsx
        {activeScreen === -1 && (
          <motion.div
            key="screen0"
            variants={screenVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.2, ease: 'easeOut' }}
            className="h-full overflow-hidden"
          >
            <ColdOpenScreen />
          </motion.div>
        )}

```

---

## 4. AppShell Change: Hide StatusBar on Cold Open

**File:** `frontend/src/components/layout/AppShell.tsx`

**Find:**
```tsx
export function AppShell({ children, tierActive }: AppShellProps) {
```
**Add after it:**
```tsx
  const activeScreen = useStore((s) => s.activeScreen)
```

**Find:**
```tsx
      <StatusBar t3Active={tierActive === 3} />
```
**Replace with:**
```tsx
      {activeScreen !== -1 && <StatusBar t3Active={tierActive === 3} />}
```

---

## 5. Screen 1 Copy Changes: `SignalIntakeScreen.tsx`

**File:** `frontend/src/components/screens/Screen1_SignalIntake/SignalIntakeScreen.tsx`

### 5a. Subtitle

**Find:**
```tsx
          Events are evaluated for severity before initiating investigation.
          Most signals are dismissed at T2. Only credible crises escalate to T3.
```
**Replace with:**
```tsx
          A market signal arrives that can't be explained away.
          The system evaluates severity, then decides: dismiss or investigate.
```

### 5b. Pipeline — T2 box label

**Find:**
```tsx
          <span style={{ color: '#8C7A5E' }}>SEMANTIC EVAL</span>
```
**Replace with:**
```tsx
          <span style={{ color: '#8C7A5E' }}>EVALUATE</span>
```

### 5c. Pipeline — T3 box label

**Find:**
```tsx
          <span style={{ color: '#8C7A5E' }}>FULL INVESTIGATION</span>
          <span style={{ color: '#4A3D2A' }}>4-5 DEEP CYCLES</span>
```
**Replace with:**
```tsx
          <span style={{ color: '#8C7A5E' }}>DEEP INVESTIGATION</span>
          <span style={{ color: '#4A3D2A' }}>4-5 CYCLES</span>
```

### 5d. T2 eval panel header

**Find:**
```tsx
                  T2 — SEMANTIC EVALUATION
```
**Replace with:**
```tsx
                  SIGNAL EVALUATION
```

### 5e. Escalation banner — main text

**Find:**
```tsx
                        ↑ ESCALATE → T3 FULL INVESTIGATION
```
**Replace with:**
```tsx
                        ↑ ESCALATE — Signal warrants deep investigation
```

### 5f. Escalation banner — subtitle

**Find:**
```tsx
                        4-5 deep reasoning cycles · Iterative hypothesis elimination
```
**Replace with:**
```tsx
                        Generating competing hypotheses · Testing against structural evidence · Eliminating what's impossible
```

---

## 6. Screen 2 Copy Changes: `InvestigationScreen.tsx`

**File:** `frontend/src/components/screens/Screen2_Investigation/InvestigationScreen.tsx`

### 6a. T3 banner — title

**Find:**
```tsx
              T3 — FULL INVESTIGATION
```
**Replace with:**
```tsx
              DEEP INVESTIGATION
```

### 6b. T3 banner — subtitle

**Find:**
```tsx
              4-5 deep reasoning cycles · Orchestrator + Investigator + Evidence Packager
```
**Replace with:**
```tsx
              Generating hypotheses · Scoring against evidence · Eliminating what's structurally impossible
```

---

## 7. Screen 2 Copy Changes: `ContextBreathingChart.tsx`

**File:** `frontend/src/components/screens/Screen2_Investigation/ContextBreathingChart.tsx`

### 7a. Add workspace label below the header row

**Find:**
```tsx
      {/* Per-cycle rows */}
      <div className="space-y-1.5">
```
**Add above it:**
```tsx
      {/* Workspace label */}
      <div className="mb-2 text-[8px] font-mono" style={{ color: '#4A3D2A' }}>
        Context window as workspace — each cycle loads fresh evidence into a clean window
      </div>

```

---

## 8. Screen 3 Copy Changes: `ConvergenceScreen.tsx`

**File:** `frontend/src/components/screens/Screen3_Convergence/ConvergenceScreen.tsx`

### 8a. Single-pass panel header

**Find:**
```tsx
                  <span className="text-[8px] font-mono tracking-wider" style={{ color: '#4A3D2A' }}>SINGLE-PASS ANALYSIS</span>
```
**Replace with:**
```tsx
                  <span className="text-[8px] font-mono tracking-wider" style={{ color: '#4A3D2A' }}>SINGLE-PASS AI</span>
```

### 8b. Single-pass panel footer

**Find:**
```tsx
                    Generic pattern-matching output
```
**Replace with:**
```tsx
                    "Risk is elevated. Recommend hedging exposure."
```

### 8c. Iterative panel header

**Find:**
```tsx
                  <span className="text-[8px] font-mono tracking-wider" style={{ color: '#2E9E72' }}>ITERATIVE HYPOTHESIS ELIMINATION</span>
```
**Replace with:**
```tsx
                  <span className="text-[8px] font-mono tracking-wider" style={{ color: '#2E9E72' }}>IHEE — 4 CYCLES</span>
```

### 8d. Iterative panel footer

**Find:**
```tsx
                    Specific causal chain with evidence citations
```
**Replace with:**
```tsx
                    Identified structural resolution path before market consensus
```

### 8e. Context window narrative (bottom of page)

**Find:**
```tsx
            The context window fills with reasoning during each cycle, then compresses between cycles — preserving
            surviving hypotheses, elimination chains, and cross-modal contradictions while discarding raw reasoning.
            Reasoning tokens consumed 4x more context than evidence data. This is inference-time compute, not storage.
```
**Replace with:**
```tsx
            Early cycles load the rules. Middle cycles test against reality. Late cycles simulate forward —
            what resolution path is structurally possible? The context window is a workspace for reasoning,
            not a database for storage.
```

---

## 9. Optional: Final Frame Component

Create at: `frontend/src/components/screens/Screen4_Closing/ClosingScreen.tsx`

Only needed if you want a clean ending card after convergence. Can also just hold on Screen 3.

```tsx
import { motion } from 'framer-motion'

export function ClosingScreen() {
  return (
    <div
      className="h-full flex flex-col items-center justify-center p-10 gap-4"
      style={{ backgroundColor: '#0C0A07' }}
    >
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8 }}
        className="text-center"
      >
        <div
          className="tracking-[0.35em] mb-4"
          style={{
            fontFamily: 'Syne, sans-serif',
            fontWeight: 800,
            fontSize: '1.25rem',
            color: '#EDE4D4',
          }}
        >
          IHEE
        </div>
        <p className="text-[10px] font-mono leading-relaxed mb-6" style={{ color: '#8C7A5E' }}>
          Financial risk is a hypothesis elimination problem,
          <br />
          not a pattern matching problem.
        </p>
        <p className="text-[8px] font-mono" style={{ color: '#4A3D2A' }}>
          Built with Gemini · March 2026
        </p>
      </motion.div>
    </div>
  )
}
```

If used, add `activeScreen === 3` routing in `App.tsx` and expand the union to `-1 | 0 | 1 | 2 | 3`.

---

## Video Timing Reference

| Time | Screen | What Judges See |
|---|---|---|
| 0–3s | Screen 0 | "Every risk system..." / "Data in. Summary out." |
| 3–6s | Screen 0 | "Detecting is solved... ML models, anomaly detection" |
| 6–10s | Screen 0 | "The hard problem is what comes next." (hook) |
| 10–13s | Screen 0 | Title + tagline + button appears |
| ~13s | Screen 0 → 1 | Button click |
| 14–17s | Screen 1 | Credit Suisse trigger selected, evaluation streams |
| ~18s | Screen 1 | Escalation fires |
| ~19s | Screen 1 → 2 | Auto-transition to investigation |
| 19–49s | Screen 2 | Hypotheses appear, get eliminated, cycles progress |
| ~49s | Screen 2 → 3 | Convergence reached |
| 49–54s | Screen 3 | Diagnosis lands, alert banner |
| 54–59s | Screen 3 | Side-by-side comparison (let judges read) |
| 59–65s | Screen 3 | Hold on narrative + contagion |

**If you need exactly 60s:** Use the playback speed control (◀ ▶ in status bar) to speed up Screen 2 mock playback when recording.

---

## Implementation Checklist

- [ ] **Create** `frontend/src/components/screens/Screen0_ColdOpen/ColdOpenScreen.tsx` (Section 1)
- [ ] **Edit** `frontend/src/store/index.ts` — 4 find/replace changes (Section 2a–2d)
- [ ] **Edit** `frontend/src/App.tsx` — import + add Screen 0 block (Section 3)
- [ ] **Edit** `frontend/src/components/layout/AppShell.tsx` — hide StatusBar on cold open (Section 4)
- [ ] **Edit** `frontend/src/components/screens/Screen1_SignalIntake/SignalIntakeScreen.tsx` — 6 string replacements (Section 5a–5f)
- [ ] **Edit** `frontend/src/components/screens/Screen2_Investigation/InvestigationScreen.tsx` — 2 string replacements (Section 6a–6b)
- [ ] **Edit** `frontend/src/components/screens/Screen2_Investigation/ContextBreathingChart.tsx` — add workspace label (Section 7a)
- [ ] **Edit** `frontend/src/components/screens/Screen3_Convergence/ConvergenceScreen.tsx` — 5 string replacements (Section 8a–8e)
- [ ] **Optional:** Create `ClosingScreen.tsx` + wire routing (Section 9)
