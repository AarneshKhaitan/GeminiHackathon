# Lessons Learned - Self-Improvement Loop

## Purpose

Document mistakes and corrections to prevent repeating them. After ANY user correction, add an entry here.

---

## Template

```
### [Date] - [Issue Title]

**What went wrong:**
[Description of the mistake]

**User correction:**
[What the user said]

**Root cause:**
[Why did this happen]

**Rule for future:**
[Specific rule to prevent recurrence]
```

---

## Lessons

### 2026-03-07 - Build Order Confusion

**What went wrong:**
Initially created a single massive plan file instead of separate phase plans. Also had build order that put Orchestrator before Investigator.

**User correction:**
"it should follow the build structure/order" → pointed to CLAUDE.md lines 107-116 showing Investigator comes BEFORE Orchestrator. Also requested separate plan files for each phase.

**Root cause:**
Didn't carefully verify plan against CLAUDE.md build order. Assumed old phase ordering from initial draft.

**Rule for future:**
- ALWAYS verify build order against CLAUDE.md lines 107-116
- Investigator (Phase 3) comes BEFORE Orchestrator (Phase 5)
- Create separate plan files when user requests them, not one monolithic file

---

### 2026-03-07 - Insufficient Plan Detail

**What went wrong:**
Created brief phase plans (~200 lines) instead of detailed ones like Phase 1 example.

**User correction:**
"these are not detailed"

**Root cause:**
Tried to save tokens by making plans concise, but user wanted comprehensive implementation specs.

**Rule for future:**
- Each phase plan should be as detailed as Phase 1 plan (~500+ lines)
- Include complete code examples with proper signatures
- Include full verification test scripts
- Include expected output examples
- Don't sacrifice detail to save tokens

---

### 2026-03-07 - Token Counter & Corpus Loader Placement

**What went wrong:**
Initially unclear which phase should contain token_counter.py and corpus_loader.py.

**User correction:**
"in which plan will the token parser and corpus loader be implemented?"

**Root cause:**
Original comprehensive plan had these in "Phase 8" but that didn't align with the 7-phase structure.

**Rule for future:**
- utils/parser.py → Phase 2 (needed by Orchestrator)
- utils/token_counter.py → Phase 2 (needed by all Gemini-calling components)
- utils/corpus_loader.py → Phase 4 (needed by evidence retrieval agents)

---

## How to Use This File

1. After any user correction, immediately add an entry
2. Write specific, actionable rules
3. Review this file at start of new sessions
4. Update rules if they prove insufficient

---

## Success Metrics

Track mistake reduction over time:
- Session 1: [count] corrections needed
- Session 2: [count] corrections needed
- Goal: Decrease over time
