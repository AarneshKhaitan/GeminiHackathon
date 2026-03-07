# Score-Based Elimination Feature

## Overview
Added automatic elimination of hypotheses with confidence scores below 0.2 threshold.

## Implementation

### Phase 2: Elimination Logic
**Two elimination criteria:**

1. **Evidence-Based Elimination (Gemini decides):**
   - Evidence directly contradicts hypothesis
   - Makes hypothesis logically IMPOSSIBLE
   - Cites specific observation ID as kill atom
   - Example: `killed_by_atom: "S01"`

2. **Score-Based Elimination (Automatic post-processing):**
   - Hypothesis score drops below 0.2
   - Indicates hypothesis is highly implausible
   - Automatically eliminated after Phase 1 scoring
   - Example: `killed_by_atom: "low_confidence"`

### Code Location
`backend/agents/investigator_5phase.py` - Phase 2 post-processing:
```python
# After Gemini returns elimination decisions
for hyp in surviving:
    if hyp.get("score", 1.0) < 0.2:
        # Eliminate due to low confidence
        low_score_eliminations.append({
            "id": hyp["id"],
            "name": hyp["name"],
            "killed_by_atom": "low_confidence",
            "killed_in_cycle": context["cycle_num"],
            "reason": f"Score {hyp['score']:.2f} dropped below 0.2 threshold"
        })
```

### Prompt Updates
`backend/gemini/prompts/investigation_phases.py` - Phase 2 prompt:
```
## ELIMINATION CRITERIA

Eliminate a hypothesis if ANY of these conditions are met:

1. Evidence-Based Elimination (IMPOSSIBLE):
   - Evidence directly contradicts the hypothesis
   - Makes hypothesis logically IMPOSSIBLE, not just unlikely
   - Must cite specific observation ID as "kill atom"

2. Score-Based Elimination (UNLIKELY):
   - Hypothesis score drops below 0.2
   - Indicates hypothesis has become highly implausible
   - Cite "low_confidence" as reason
```

## Test Results

### Test Case: 3 Hypotheses with Different Scores
```python
H01: score 0.85  →  Survives ✅
H02: score 0.15  →  Eliminated (< 0.2) ✅
H03: score 0.20  →  Initially at threshold, but Gemini rescored to 0.10 based on contradicting evidence, then eliminated ✅
```

### Output Format
```
Phase 2/5: Identifying eliminations...
  ✓ 2 total eliminations:
    - 0 evidence-based (from Gemini)
    - 2 score-based (< 0.2 threshold)
  ✓ 1 survivors
```

### Elimination Record
```json
{
  "id": "H02",
  "name": "Weak hypothesis",
  "killed_by_atom": "low_confidence",
  "killed_in_cycle": 2,
  "reason": "Score 0.15 dropped below 0.2 threshold, indicating hypothesis is highly implausible"
}
```

## Rationale

### Why 0.2 Threshold?
- **0.0-0.2:** Highly implausible, not worth tracking
- **0.2-0.5:** Weak but possible, keep monitoring
- **0.5-0.8:** Plausible, active investigation
- **0.8-1.0:** Strong confidence, likely explanation

### Why Automatic Post-Processing?
**Option 1: Let Gemini decide everything**
- Pro: Single source of truth
- Con: Model might be inconsistent about score threshold

**Option 2: Automatic post-processing (CHOSEN)**
- Pro: Deterministic, consistent elimination
- Pro: Clear separation of concerns (Gemini scores, we apply threshold)
- Pro: Easy to adjust threshold without prompt engineering
- Con: Logic split between model and code

## Integration with Existing System

### Compatible with Evidence-Based Elimination
Both elimination types coexist:
1. Gemini eliminates based on evidence contradictions
2. Post-processing eliminates based on low scores
3. Both appear in `eliminated_hypotheses` list with appropriate `killed_by_atom`

### Traceable in Case File
```python
{
  "eliminated_hypotheses": [
    {"id": "H03", "killed_by_atom": "S01", "reason": "Evidence contradiction"},
    {"id": "H05", "killed_by_atom": "low_confidence", "reason": "Score 0.15 < 0.2"}
  ]
}
```

## Usage

### For Investigators
No changes needed - automatic elimination based on scores returned from Phase 1.

### For Orchestrator (Phase 5)
When checking convergence:
```python
# Count survivors (already excludes low-scoring hypotheses)
num_survivors = len(surviving_hypotheses)

if num_survivors <= 2:
    # Converged!
    pass
```

### For Frontend
Display eliminations with different styling:
```javascript
if (elim.killed_by_atom === "low_confidence") {
  // Score-based: Gray out, show "Eliminated (Low Confidence)"
} else {
  // Evidence-based: Show kill atom citation
}
```

## Future Enhancements

### Configurable Threshold
```python
# In config.py
ELIMINATION_SCORE_THRESHOLD = 0.2  # Default

# In investigator
if hyp.get("score", 1.0) < config.ELIMINATION_SCORE_THRESHOLD:
    # Eliminate
```

### Gradual Threshold
Different thresholds per cycle:
```python
# Cycle 1-2: Keep threshold at 0.1 (more lenient)
# Cycle 3-4: Raise to 0.2 (more aggressive)
# Cycle 5+: Raise to 0.3 (force convergence)
```

### Warning Before Elimination
Track "at risk" hypotheses (0.2-0.3 range):
```python
{
  "at_risk_hypotheses": [
    {"id": "H07", "score": 0.25, "warning": "Close to elimination threshold"}
  ]
}
```

---

**Status:** ✅ Implemented and tested
**Files Modified:**
- `backend/agents/investigator_5phase.py`
- `backend/gemini/prompts/investigation_phases.py`
- `backend/test_score_elimination.py` (new test)
