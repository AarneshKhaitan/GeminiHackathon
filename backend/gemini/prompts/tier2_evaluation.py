"""
Tier 2 semantic evaluation prompt.

Tier 2 is a lightweight evaluation to decide if a trigger signal warrants
full investigation. Most flags die here.
"""


def build_tier2_prompt(trigger: dict) -> str:
    """
    Build Tier 2 semantic evaluation prompt.

    Args:
        trigger: Trigger signal dict with event, magnitude, entity info

    Returns:
        Prompt string for Gemini
    """
    entity = trigger.get("entity", "Unknown")
    event = trigger.get("event", "Unknown event")
    magnitude = trigger.get("magnitude", "N/A")
    date = trigger.get("date", "Unknown date")

    # Extract additional context if available
    context_items = []
    for key, value in trigger.items():
        if key not in ["entity", "event", "magnitude", "date"]:
            context_items.append(f"  - {key}: {value}")

    additional_context = "\n".join(context_items) if context_items else "  (no additional context)"

    return f"""
You are a Tier 2 financial risk evaluator. Your job is to quickly assess whether a trigger signal warrants full investigation.

# TRIGGER SIGNAL

**Entity:** {entity}
**Event:** {event}
**Magnitude:** {magnitude}
**Date:** {date}

**Additional Context:**
{additional_context}

# YOUR TASK

Perform a semantic evaluation to decide:
- **PROMOTE:** Signal is concerning enough to warrant full investigation (Tier 3)
- **DEMOTE:** Signal is likely a false positive, routine market movement, or already explained

# EVALUATION CRITERIA

**Promote if ANY of these apply:**
1. Magnitude is extreme (e.g., CDS spike >300bps, stock drop >30%, unusual volume)
2. Signal involves systemic risk indicators (liquidity, capital, contagion)
3. Multiple correlated signals for same entity
4. Entity has known structural vulnerabilities
5. Signal timing coincides with major market stress

**Demote if ALL of these apply:**
1. Magnitude within normal trading range
2. Likely explained by known events (earnings, Fed announcements)
3. No systemic risk indicators
4. Entity fundamentals appear sound

# OUTPUT FORMAT (JSON)

{{
  "thinking": "Your reasoning process here. Assess the magnitude, context, and systemic risk indicators. Explain your decision.",

  "promotes": true or false,

  "confidence": 0.0 to 1.0,

  "reasoning": "One-sentence summary of why you promote or demote this signal"
}}

**IMPORTANT:** Be conservative. When in doubt, PROMOTE. False negatives (missing a real crisis) are far more costly than false positives (investigating a non-issue).
"""
