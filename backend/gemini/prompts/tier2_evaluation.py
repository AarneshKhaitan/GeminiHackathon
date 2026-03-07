"""
Tier 2 semantic evaluation prompt.

Decides whether a market signal warrants escalation to full investigation
or can be safely dismissed as normal market noise.
"""


def build_tier2_prompt(trigger: dict) -> str:
    """
    Build prompt for Tier 2 semantic signal evaluation.

    The trigger signal has already passed Tier 1 (quantitative thresholds).
    Tier 2 applies semantic reasoning to decide if escalation is warranted.

    Args:
        trigger: Signal dict with entity, event, magnitude, date, description

    Returns:
        Prompt string for call_gemini()
    """
    entity = trigger.get("entity", "unknown entity")
    event = trigger.get("event", "unknown event")
    magnitude = trigger.get("magnitude", "N/A")
    date = trigger.get("date", "unknown date")
    description = trigger.get("description", "")

    return f"""
You are a Tier 2 semantic evaluation system for financial risk intelligence.

A market signal has been detected. Evaluate whether it warrants escalation to full investigation.

# TRIGGER SIGNAL
Entity: {entity}
Event: {event}
Magnitude/Severity: {magnitude}
Date: {date}
Additional Context: {description}

# EVALUATION CRITERIA

Escalate to full investigation if ANY of:
- Systemic risk indicators (CDS spike >200bps, equity drop >20%, credit rating action)
- Regulatory intervention signals (emergency powers, forced merger, FDIC/FINMA action)
- Confidence crisis indicators (bank run rumors, deposit outflows, executive departures)
- Counterparty contagion signals (correlated market moves across multiple institutions)
- Structural failure signals (capital breach, liquidity shortfall, covenant violations)

Dismiss if:
- Normal market volatility within expected ranges (minor fluctuation, sector rotation)
- Isolated operational incident with no systemic implications
- Macro-driven move affecting all entities equally without entity-specific risk
- Event already priced in by markets with stabilization

# OUTPUT FORMAT (JSON):
{{
  "assessment": "One clear paragraph explaining your evaluation and key risk factors identified",
  "decision": "escalate",
  "confidence": 0.0,
  "key_risk_factors": ["list", "of", "specific", "risks"],
  "recommended_tier": 3
}}

Where:
- "decision" must be exactly "escalate" or "dismiss"
- "confidence" is 0.0 to 1.0 (confidence in the decision)
- "recommended_tier" is 3 (quick 1-2 cycle investigation) or 4 (deep 4-5 cycle investigation)

Provide only the JSON, no additional text.
"""
