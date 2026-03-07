"""
Evidence tagging prompt — labels each atom with supports/contradicts/neutral
lists relative to the active hypotheses. Used by the Evidence Packager.
"""


def build_evidence_tagging_prompt(
    raw_evidence: list[dict],
    active_hypotheses: list[dict],
) -> str:
    """
    Build prompt for the Evidence Packager tagging step.

    The packager makes ONE Gemini call to tag all collected atoms at once.
    Tags enable traceable hypothesis elimination in the investigator.

    Args:
        raw_evidence: Untagged observations from retrieval agents
        active_hypotheses: Current survivors with id, name, score

    Returns:
        Prompt string for call_gemini()
    """

    evidence_text = "\n\n".join([
        f"## OBSERVATION {obs['observation_id']}\n"
        f"Type: {obs['type']}\n"
        f"Source: {obs['source']}\n"
        f"Date: {obs.get('date') or 'unknown'}\n"
        f"Content: {obs['content'][:800]}"
        for obs in raw_evidence
    ])

    hypotheses_text = "\n".join([
        f"- {h['id']}: {h.get('name', h['id'])} (score: {h.get('score', '?')})"
        for h in active_hypotheses
    ])

    hypothesis_ids = [h["id"] for h in active_hypotheses]

    return f"""
You are tagging evidence observations against active hypotheses in a financial risk investigation.

# ACTIVE HYPOTHESES
{hypotheses_text}

# EVIDENCE OBSERVATIONS TO TAG
{evidence_text}

# TASK
For each observation, classify its relationship to EACH hypothesis:
- "supports": observation provides evidence FOR the hypothesis being true
- "contradicts": observation provides evidence AGAINST the hypothesis (disproves or undermines it)
- "neutral": observation is irrelevant or ambiguous for this hypothesis

An observation may support some hypotheses and contradict others simultaneously.
A contradiction is the basis for hypothesis elimination — be precise.

# OUTPUT FORMAT (JSON):
{{
  "tagged_observations": [
    {{
      "observation_id": "S01",
      "content": "original content unchanged",
      "source": "original source unchanged",
      "type": "structural",
      "date": "2023-03-15",
      "supports": ["H01", "H02"],
      "contradicts": ["H05"],
      "neutral": {[hid for hid in hypothesis_ids if hid not in ['H01','H02','H05']]},
      "tagging_reasoning": "One sentence explaining key tagging decisions"
    }}
  ]
}}

Tag all {len(raw_evidence)} observations. Every hypothesis ID must appear in exactly one list per observation.
Valid hypothesis IDs: {hypothesis_ids}
"""
