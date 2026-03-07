# Investigator V2 - Quick Reference

## Usage

```python
from agents.investigator_v2 import investigate

# Cycle 1: Generate hypotheses
result = await investigate({
    "trigger": "SVB stock dropped 60%, CDS at 450bps",
    "entity": "Silicon Valley Bank",
    "cycle_num": 1,
    "compressed_state": None,
    "evidence": [],
    "active_hypotheses": []
})

# Cycle 2+: Score, eliminate, request
result = await investigate({
    "trigger": original_trigger,
    "entity": entity_name,
    "cycle_num": 2,
    "compressed_state": result_from_cycle_1["compressed_state"],
    "evidence": evidence_observations,
    "active_hypotheses": result_from_cycle_1["surviving_hypotheses"]
})
```

## Output Structure

```python
{
    "surviving_hypotheses": [
        {
            "id": "H01",
            "name": "Duration mismatch + HTM accounting",
            "score": 0.95,
            "status": "active",
            "evidence_chain": ["S01", "S02", "E01"]
        }
    ],

    "eliminated_hypotheses": [
        {
            "id": "H05",
            "name": "Counterparty credit risk",
            "killed_by_atom": "low_confidence",  # or "S01" for evidence-based
            "killed_in_cycle": 2,
            "reason": "Score 0.15 below 0.2 threshold"
        }
    ],

    "cross_modal_flags": [
        {
            "structural_atom_id": "S01",
            "empirical_atom_id": "E01",
            "detected_in_cycle": 2,
            "contradiction_description": "Regulatory capital adequate but CDS spike indicates hidden risk"
        }
    ],

    "forward_simulations": [  # Only in Cycle 3+
        {
            "hypothesis_id": "H01",
            "hypothesis_name": "Duration mismatch + HTM accounting",
            "structural_consequences": "Unrealized losses increase with rising rates...",
            "empirical_predictions": ["Deposit outflows", "Forced asset sales"],
            "testable_evidence": ["HTM mark-to-market disclosure", "Daily deposit data"],
            "confidence_in_simulation": 0.85
        }
    ],

    "evidence_requests": [
        {
            "type": "structural",
            "description": "HTM portfolio mark-to-market valuation",
            "reason": "Tests prediction from forward simulation",
            "tests_hypothesis": ["H01", "H02"]
        }
    ],

    "compressed_state": "CYCLE 2: H01 (0.95), H02 (0.80) surviving. Cross-modal: S01 vs E01...",

    "key_insights": ["Duration mismatch explains cross-modal contradiction"],

    "token_usage": {
        "input": 29639,
        "output": 10337,
        "reasoning": 2642,
        "total": 39976
    },

    "phase_outputs": {
        "phase1_score_crossmodal": {...},
        "phase2_elimination": {...},
        "phase3_forward_sim": {...},  # Only Cycle 3+
        "phase4_request": {...},
        "phase5_compression": {...}
    }
}
```

## Cycle-Specific Behavior

### Cycle 1:
- **Executes:** Phase 1 (generate) + Phase 4 (request)
- **Skips:** Phase 2, 3, 5
- **Returns:** 8-10 hypotheses, 3-5 evidence requests

### Cycles 2+:
- **Executes:** Phase 1 (score) + Phase 2 (eliminate) + Phase 4 (request) + Phase 5 (compress)
- **Skips:** Phase 3 (forward sim)
- **Returns:** Scored hypotheses, eliminations, cross-modal flags, requests, compressed state

### Cycles 3+:
- **Executes:** All 5 phases
- **Adds:** Phase 3 (forward simulation)
- **Returns:** Everything including forward_simulations

## Performance

- **Cycle 1:** ~15K tokens, ~45 seconds
- **Cycle 2:** ~40K tokens, ~2:15 minutes
- **Cycle 3+:** ~50K tokens, ~2:30 minutes

Total for 2 cycles: **~3:30 minutes**

## Key Features

✅ **Cross-Modal Detection:** Structural vs empirical contradictions
✅ **Score-Based Elimination:** Auto-eliminates hypotheses < 0.2
✅ **Forward Simulation:** Predicts outcomes (Cycle 3+)
✅ **Cumulative Context:** Each phase sees all previous outputs
✅ **Token Tracking:** Input, output, reasoning separated

## Migration from V1

```python
# OLD (investigator_5phase.py)
from agents.investigator_5phase import investigate

# NEW (investigator_v2.py)
from agents.investigator_v2 import investigate

# API is identical, output structure is same
# V2 adds: cross_modal_flags in Phase 1, forward_simulations in Phase 3
```

## Testing

```bash
# Quick validation (2 cycles)
cd backend
source ../venv/bin/activate
python test_v2_quick.py

# Full test suite (3 cycles)
python test_investigator_v2.py
```

## Troubleshooting

### "KeyError: 'description'"
Fixed in v2 - hypothesis dict from Phase 2 may not include 'description'

### "Invalid control character"
Handled by robust JSON parsing in gemini/client.py

### Slow performance
- Check API key quota
- Verify using gemini-2.5-flash (faster than 3.1-pro)
- Consider reducing output verbosity if needed

## Integration Checklist

- [ ] Update orchestrator to import from `agents.investigator_v2`
- [ ] Pass forward_simulations to evidence packager (Cycle 3+)
- [ ] Store cross_modal_flags in case file
- [ ] Display cross-modal contradictions in frontend
- [ ] Handle forward_simulations in alert generation
