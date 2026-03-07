# Demo Test Checklist

## Setup
1. Start backend: `cd backend && uvicorn main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Open browser: http://localhost:5173

## Demo Flow Verification

### Screen 0: Cold Open (14 seconds)
- [ ] Staggered text animation appears line by line
- [ ] "ITERATIVE HYPOTHESIS ELIMINATION ENGINE" title appears
- [ ] "This system doesn't summarize. It investigates." tagline
- [ ] "BEGIN INVESTIGATION →" button appears
- [ ] Click button transitions to Screen 1

### Screen 1: Signal Intake
- [ ] System architecture diagram shows T2 → T3 flow
- [ ] Credit Suisse trigger card is displayed
- [ ] Click Credit Suisse card
- [ ] Tier 2 evaluation panel appears
- [ ] Text streams: "Evaluating trigger signal..." (3s)
- [ ] Text streams: "Signal magnitude: CHF 110.5 billion..." (3s)
- [ ] Text streams: "Decision: PROMOTE to Tier 3 investigation" (5s)
- [ ] Escalation decision box appears with "↑ ESCALATE" (3s)
- [ ] Auto-transitions to Screen 2 (Investigation)

### Screen 2: Investigation (~90 seconds)
- [ ] "DEEP INVESTIGATION" banner appears at top
- [ ] Left panel: Cycle Timeline shows cycles

#### Cycle 1 (25-30s)
- [ ] Cycle 1 node appears as "ACTIVE"
- [ ] "REASONING..." status shows (8s)
- [ ] **10 hypotheses appear** (H01-H10) with descriptions
- [ ] All hypotheses show as "surviving" initially
- [ ] **2 eliminations**: H08 and H09 marked with ✗
- [ ] Eliminated cards auto-expand showing:
  - Kill atom ID (e.g., "E20_SEC_Filings_Current")
  - Kill reason (full paragraph explanation)
  - Cycle number
- [ ] Compression indicator shows
- [ ] 4 key insights appear in right panel
- [ ] Cycle 1 completes, shows "8 surviving · 2 eliminated"

#### Cycle 2 (25-30s)
- [ ] Cycle 2 node appears as "ACTIVE"
- [ ] 8 hypotheses scored (confidence updates)
- [ ] **3 eliminations**: H04, H05, H10 marked with ✗
- [ ] Each elimination shows detailed kill reason
- [ ] Compression occurs
- [ ] 4 key insights added
- [ ] Cycle 2 completes, shows "5 surviving · 5 eliminated"

#### Cycle 3 (25-30s)
- [ ] Cycle 3 node appears as "ACTIVE"
- [ ] 5 hypotheses scored
- [ ] **2 eliminations**: H06, H07 marked with ✗
- [ ] Kill reasons displayed
- [ ] Compression occurs
- [ ] 4 key insights added
- [ ] Cycle 3 completes, shows "3 surviving · 7 eliminated"

#### Right Panel Tabs
- [ ] **Evidence tab**: Shows evidence atoms (if any)
- [ ] **Reasoning tab**:
  - Shows all 12 key insights (4 per cycle)
  - Shows cumulative compressed reasoning
  - Reasoning text is detailed and readable
- [ ] **Tokens tab**: Shows token usage breakdown

### Screen 3: Convergence (3s display)
- [ ] Auto-transitions from Screen 2
- [ ] Critical alert banner appears
- [ ] Headline: "3 risk factors identified for Credit Suisse"
- [ ] Iterative diagnosis shows full paragraph
- [ ] Shows 3 surviving hypotheses: H01, H02, H03
- [ ] Each surviving hypothesis shows full description
- [ ] Elimination timeline visible
- [ ] Context window visualization shown

## Key Data Points to Verify

### Hypothesis Count Timeline
- Start: 10 hypotheses
- After Cycle 1: 8 survivors (eliminated H08, H09)
- After Cycle 2: 5 survivors (eliminated H04, H05, H10)
- After Cycle 3: 3 survivors (eliminated H06, H07)
- Final: H01, H02, H03 survive

### Elimination Details Must Show
1. **H08 (Cycle 1)**: "SEC Investigation" - Eliminated by E20_SEC_Filings_Current
2. **H09 (Cycle 1)**: "Derivative Book Losses" - Eliminated by S08_Derivative_Fair_Value
3. **H04 (Cycle 2)**: "AT1 Write-down Risk" - Eliminated by S01_AT1_Prospectus_2019
4. **H05 (Cycle 2)**: "Regulatory Capital Breach" - Eliminated by E06_Q4_Earnings_Capital
5. **H10 (Cycle 2)**: "Swiss Regulatory Intervention" - Eliminated by E12_FINMA_Statements
6. **H06 (Cycle 3)**: "Liquidity Crisis" - Eliminated by E10_Liquidity_Coverage_Ratio
7. **H07 (Cycle 3)**: "Counterparty Exposure" - Eliminated by S13_Annual_Report_20F

### Final Surviving Hypotheses
1. **H01**: "Reputational Crisis Post-Archegos/Greensill" (94% confidence)
2. **H02**: "Restructuring Plan Failed to Restore Confidence" (89% confidence)
3. **H03**: "Wealth Management Client De-risking" (87% confidence)

## Performance Timing
- **Total demo duration**: ~110 seconds (1:50)
- **Tier 2 evaluation**: ~16 seconds
- **Per cycle**: ~25-30 seconds
- **3 cycles**: ~75-90 seconds
- **Convergence**: ~3 seconds

## Common Issues to Check
- [ ] All text is readable (not too fast)
- [ ] Eliminated cards are expanded by default
- [ ] Kill reasons are full paragraphs, not truncated
- [ ] Descriptions show on surviving hypotheses
- [ ] Compressed reasoning shows detailed text
- [ ] No UI flickering or jank
- [ ] Smooth transitions between screens
- [ ] All 10 hypotheses appear in Cycle 1 (not just 3)

## Success Criteria
✅ All 10 hypotheses visible in Cycle 1
✅ Progressive elimination across 3 cycles (2→3→2 pattern)
✅ Detailed kill reasons displayed and readable
✅ Final diagnosis shows 3 survivors
✅ Total runtime ~2 minutes
✅ No missing data or empty panels
