# Phase 1: Data Models - Foundation

**Status:** Ready for implementation
**Duration:** ~30-45 minutes
**Dependencies:** None
**Build Order:** 1 of 7

---

## Context

Foundation data structures for the entire system. All other phases depend on these schemas.

**Why This Phase:**
- Establishes data contracts between all components
- Testable in complete isolation (no API, no LangGraph)
- Quick validation win
- Pydantic provides automatic validation

**What's NOT in This Phase:**
- No Gemini API calls
- No LangGraph
- No business logic
- No agent implementations

---

## Files to Create

### 1. `backend/models/observation.py`

**Purpose:** Pydantic schema for atomic evidence observations

**Implementation Details:**
```python
from pydantic import BaseModel, Field
from typing import Literal

class Evidence(BaseModel):
    observation_id: str = Field(..., description="Unique atom ID (e.g., 'S01', 'E03')")
    content: str = Field(..., description="Full text content")
    source: str = Field(..., description="Origin (e.g., 'FDIC Report', 'SEC 10-K')")
    type: Literal["structural", "market", "news", "filing"]
    supports: list[str] = Field(default_factory=list, description="Hypothesis IDs supported")
    contradicts: list[str] = Field(default_factory=list, description="Hypothesis IDs contradicted")
    neutral: list[str] = Field(default_factory=list, description="Hypothesis IDs neutral toward")
    date: str | None = Field(default=None, description="Observation date if applicable")
```

**Why Tags Matter:** When an observation contradicts a hypothesis, elimination is traceable to this specific atom (prd.md FR-7)

**Reference:** component_guide.md lines 103-122

---

### 2. `backend/models/case_file.py`

**Purpose:** Pydantic models for persistent investigation state

**Models to Implement:**

**Hypothesis:**
```python
class Hypothesis(BaseModel):
    id: str
    name: str
    description: str
    score: float  # 0.0-1.0
    evidence_chain: list[str]  # observation IDs
    status: Literal["active", "converged"]
```

**EliminatedHypothesis:**
```python
class EliminatedHypothesis(BaseModel):
    id: str
    name: str
    killed_by_atom: str  # MUST cite specific observation_id
    killed_in_cycle: int
    reason: str  # One-line explanation
```

**CrossModalFlag:**
```python
class CrossModalFlag(BaseModel):
    structural_atom_id: str
    empirical_atom_id: str
    detected_in_cycle: int
    contradiction_description: str
```

**EvidenceRef:**
```python
class EvidenceRef(BaseModel):
    atom_id: str
    brief: str  # Short summary, NOT full content
    type: Literal["structural", "market", "news", "filing"]
    collected_in_cycle: int
```

**CycleRecord:**
```python
class CycleRecord(BaseModel):
    cycle_num: int
    hypotheses_count: int
    eliminations_count: int
    evidence_collected_count: int
    token_usage: dict[str, int]
    duration_seconds: float | None = None
```

**Alert:**
```python
class Alert(BaseModel):
    level: Literal["CRITICAL", "ALL-CLEAR", "MONITOR"]
    diagnosis: str
    surviving_hypotheses: list[dict]
    key_evidence: list[str]  # atom IDs
    recommended_actions: list[str]
```

**NetworkAlert:**
```python
class NetworkAlert(BaseModel):
    entity: str
    reason: str
    inherited_context: dict
    priority: Literal["high", "medium", "low"] = "medium"
```

**CaseFile (main model):**
```python
class CaseFile(BaseModel):
    entity: str
    tier: Literal[2, 4]
    status: Literal["pending", "investigating", "converged", "alert", "all-clear"]
    trigger: dict

    active_hypotheses: list[Hypothesis]
    eliminated_hypotheses: list[EliminatedHypothesis]
    cross_modal_flags: list[CrossModalFlag]

    key_insights: list[str]
    evidence_collected: list[EvidenceRef]
    evidence_pending: list[dict]

    compressed_reasoning: str | None  # REPLACED each cycle, not appended

    cycle_history: list[CycleRecord]
    context_windows: dict[str, dict]
    token_usage: dict[str, int]

    alert: Alert | None
    network_alerts: list[NetworkAlert]

    created_at: str | None = None
    updated_at: str | None = None
```

**Critical Design Notes:**
- `compressed_reasoning`: REPLACED each cycle (not appended) - cumulative self-compression from investigator (prd.md FR-6)
- `evidence_collected`: Stores atom IDs + briefs only, NOT full content (full content loaded from corpus/ files)
- `active_hypotheses`: REPLACED each cycle with survivors
- `eliminated_hypotheses`: APPENDED each cycle with new kills

**Reference:** component_guide.md lines 50-100, prd.md FR-5, FR-6

---

### 3. `backend/models/state.py`

**Purpose:** TypedDict for LangGraph graph state

**Critical Requirement:** All fields MUST be JSON-serializable (LangGraph requirement from CLAUDE.md line 81)

**Implementation:**
```python
from typing import TypedDict, Literal

class InvestigationState(TypedDict, total=False):
    """State flowing between LangGraph nodes. All fields JSON-serializable."""

    # Trigger information
    trigger_signal: dict
    entity: str

    # Cycle management
    current_cycle: int
    max_cycles: int

    # Core state
    case_file: dict  # CaseFile.model_dump()
    active_hypotheses: list[dict]
    eliminated_hypotheses: list[dict]

    # Evidence management
    evidence_requests: list[dict]
    new_evidence: list[dict]  # Tagged observations
    raw_evidence: list[dict]  # Untagged from retrieval agents

    # Reasoning state
    compressed_state: str | None
    cross_modal_flags: list[dict]
    cycle_history: list[dict]

    # Investigation control
    agent_status: dict[str, str]
    token_usage: dict[str, dict]
    context_windows: dict[str, dict]

    # Decision points
    tier2_assessment: dict | None
    convergence_decision: Literal["continue", "converge"] | None
    investigation_output: dict | None

    # Results
    alert: dict | None
    network_alerts: list[dict]
```

**Why TypedDict:** LangGraph requires dict-based state, not Pydantic models (CLAUDE.md line 81)

**Reference:** component_guide.md lines 10-47

---

### 4. `backend/models/__init__.py`

Empty file to make models/ a Python package:
```python
# Empty init file
```

---

## Verification Test

Create `backend/test_phase1.py`:

```python
#!/usr/bin/env python3
"""Phase 1 Verification: Test all data models"""

from models.observation import Evidence
from models.case_file import (
    CaseFile, Hypothesis, EliminatedHypothesis,
    CrossModalFlag, EvidenceRef, CycleRecord, Alert, NetworkAlert
)
from models.state import InvestigationState

def test_observation():
    print("Testing observation.py...")
    obs = Evidence(
        observation_id="S01",
        content="SVB held $91B of HTM securities with unrealized losses",
        source="FDIC Report",
        type="structural",
        supports=["H01", "H02"],
        contradicts=["H05"],
        neutral=["H03"],
        date="2023-03-10"
    )
    print(f"✓ Evidence model validated: {obs.observation_id}")
    return obs

def test_case_file():
    print("\nTesting case_file.py...")

    hypothesis = Hypothesis(
        id="H01",
        name="Duration mismatch",
        description="Bank has duration mismatch between assets and liabilities",
        score=0.85,
        evidence_chain=["S01", "E03"],
        status="active"
    )
    print(f"✓ Hypothesis model validated: {hypothesis.id}")

    eliminated = EliminatedHypothesis(
        id="H05",
        name="Counterparty credit risk",
        killed_by_atom="S01",
        killed_in_cycle=2,
        reason="S01 shows HTM losses, not counterparty issues"
    )
    print(f"✓ EliminatedHypothesis model validated: {eliminated.id}")

    case = CaseFile(
        entity="SVB",
        tier=4,
        status="investigating",
        trigger={"event": "CDS spike", "magnitude": 450, "date": "2023-03-08"},
        active_hypotheses=[hypothesis],
        eliminated_hypotheses=[eliminated],
        cross_modal_flags=[],
        key_insights=[],
        evidence_collected=[],
        evidence_pending=[],
        compressed_reasoning=None,
        cycle_history=[],
        context_windows={},
        token_usage={},
        alert=None,
        network_alerts=[]
    )
    print(f"✓ CaseFile model validated: {case.entity}")

    # Test serialization (critical for LangGraph)
    case_dict = case.model_dump()
    assert isinstance(case_dict, dict)
    assert case_dict["entity"] == "SVB"
    assert len(case_dict["active_hypotheses"]) == 1
    assert len(case_dict["eliminated_hypotheses"]) == 1
    print(f"✓ CaseFile serializes to dict correctly")

    return case, case_dict

def test_state(case_dict, obs):
    print("\nTesting state.py...")

    state: InvestigationState = {
        "trigger_signal": {"event": "CDS spike", "date": "2023-03-08"},
        "entity": "SVB",
        "current_cycle": 1,
        "max_cycles": 5,
        "case_file": case_dict,
        "active_hypotheses": [case_dict["active_hypotheses"][0]],
        "eliminated_hypotheses": [],
        "evidence_requests": [],
        "new_evidence": [obs.model_dump()],
        "raw_evidence": [],
        "compressed_state": None,
        "cross_modal_flags": [],
        "cycle_history": [],
        "agent_status": {"orchestrator": "ready"},
        "token_usage": {},
        "context_windows": {}
    }

    assert isinstance(state["case_file"], dict)
    assert state["entity"] == "SVB"
    assert state["current_cycle"] == 1
    print(f"✓ InvestigationState validated as TypedDict")
    print(f"✓ State contains {len(state['new_evidence'])} evidence observations")

    return state

def main():
    print("=" * 60)
    print("Phase 1 Verification: Data Models")
    print("=" * 60)

    obs = test_observation()
    case, case_dict = test_case_file()
    state = test_state(case_dict, obs)

    print("\n" + "=" * 60)
    print("✅ ALL MODELS VALIDATED - Phase 1 Complete!")
    print("=" * 60)
    print("\nVerified:")
    print("  ✓ Evidence (observation.py)")
    print("  ✓ Hypothesis, EliminatedHypothesis, CaseFile (case_file.py)")
    print("  ✓ InvestigationState (state.py)")
    print("  ✓ All models serialize to JSON-compatible dicts")
    print("  ✓ No import errors")
    print("\nReady to proceed to Phase 2: Gemini Client + Config + Utils")

if __name__ == "__main__":
    main()
```

---

## Running Verification

```bash
cd backend
python test_phase1.py
```

**Expected Output:**
```
============================================================
Phase 1 Verification: Data Models
============================================================
Testing observation.py...
✓ Evidence model validated: S01

Testing case_file.py...
✓ Hypothesis model validated: H01
✓ EliminatedHypothesis model validated: H05
✓ CaseFile model validated: SVB
✓ CaseFile serializes to dict correctly

Testing state.py...
✓ InvestigationState validated as TypedDict
✓ State contains 1 evidence observations

============================================================
✅ ALL MODELS VALIDATED - Phase 1 Complete!
============================================================

Verified:
  ✓ Evidence (observation.py)
  ✓ Hypothesis, EliminatedHypothesis, CaseFile (case_file.py)
  ✓ InvestigationState (state.py)
  ✓ All models serialize to JSON-compatible dicts
  ✓ No import errors

Ready to proceed to Phase 2: Gemini Client + Config + Utils
```

---

## Success Criteria

- [ ] All Pydantic models validate correctly
- [ ] CaseFile serializes to dict without errors
- [ ] InvestigationState accepts dict values
- [ ] No import errors
- [ ] Test script runs without exceptions
- [ ] All checkmarks (✓) appear in output

---

## Next Steps

After Phase 1 verification passes:
✅ We have solid data contracts
✅ All subsequent phases can import these models
✅ Ready for Phase 2: Gemini Client + Config + Utils

**STOP HERE and verify before proceeding to Phase 2.**
