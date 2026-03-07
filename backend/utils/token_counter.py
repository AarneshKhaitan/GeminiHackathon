"""
Token usage tracking across all Gemini calls per agent per cycle.

Tracks token consumption for budget management and context window monitoring.
The 1M token context window is a reasoning workspace - we track utilization
to decide when to create fresh windows.
"""


def track_token_usage(
    agent: str,
    cycle: int,
    input_tokens: int,
    output_tokens: int,
    current_usage: dict
) -> dict:
    """
    Aggregate token usage per agent per cycle.

    Maintains both per-cycle breakdowns and running totals.
    Reasoning tokens are approximated as output tokens from investigator.

    Args:
        agent: Agent name (e.g., "investigator", "orchestrator", "packager")
        cycle: Current cycle number (1-indexed)
        input_tokens: Input tokens for this Gemini call
        output_tokens: Output tokens for this Gemini call
        current_usage: Existing usage dict to update (mutated in place)

    Returns:
        Updated usage dict with structure:
        {
            "per_cycle": {
                "cycle_1": {
                    "investigator": {"input": N, "output": M},
                    "packager": {"input": X, "output": Y}
                },
                ...
            },
            "total": {
                "input": N,
                "output": M,
                "reasoning": X  # output tokens from investigator only
            }
        }

    Example:
        >>> usage = {}
        >>> usage = track_token_usage("investigator", 1, 50000, 30000, usage)
        >>> usage = track_token_usage("packager", 1, 10000, 5000, usage)
        >>> print(usage["total"]["input"])  # 60000
    """

    # Initialize per_cycle structure if needed
    if "per_cycle" not in current_usage:
        current_usage["per_cycle"] = {}

    cycle_key = f"cycle_{cycle}"
    if cycle_key not in current_usage["per_cycle"]:
        current_usage["per_cycle"][cycle_key] = {}

    if agent not in current_usage["per_cycle"][cycle_key]:
        current_usage["per_cycle"][cycle_key][agent] = {
            "input": 0,
            "output": 0
        }

    # Update per-cycle per-agent tracking
    current_usage["per_cycle"][cycle_key][agent]["input"] += input_tokens
    current_usage["per_cycle"][cycle_key][agent]["output"] += output_tokens

    # Initialize totals if needed
    if "total" not in current_usage:
        current_usage["total"] = {
            "input": 0,
            "output": 0,
            "reasoning": 0
        }

    # Update running totals
    current_usage["total"]["input"] += input_tokens
    current_usage["total"]["output"] += output_tokens

    # Reasoning tokens = output tokens from investigator only
    # (approximation - investigator does the actual reasoning)
    if agent == "investigator":
        current_usage["total"]["reasoning"] += output_tokens

    return current_usage


def estimate_context_utilization(
    input_tokens: int,
    max_context: int = 1_000_000
) -> float:
    """
    Estimate percentage of context window used.

    Used to decide when to create fresh context windows.
    Context rot threshold is typically 50% (500K tokens).

    Args:
        input_tokens: Tokens in current context
        max_context: Maximum context window size (default: 1M for Gemini 2.0 Flash)

    Returns:
        Utilization as percentage (0.0-100.0)

    Example:
        >>> estimate_context_utilization(500_000)
        50.0
        >>> estimate_context_utilization(750_000)
        75.0
    """
    return (input_tokens / max_context) * 100.0


def get_cycle_summary(usage_dict: dict, cycle: int) -> dict:
    """
    Get token usage summary for a specific cycle.

    Useful for displaying per-cycle breakdowns in UI or logs.

    Args:
        usage_dict: Full usage tracking dict from track_token_usage()
        cycle: Cycle number (1-indexed)

    Returns:
        {
            "cycle": int,
            "total_input": int,
            "total_output": int,
            "by_agent": {
                "investigator": {"input": N, "output": M},
                "packager": {"input": X, "output": Y}
            }
        }

    Example:
        >>> summary = get_cycle_summary(usage, 2)
        >>> print(f"Cycle 2 used {summary['total_input']} input tokens")
    """

    cycle_key = f"cycle_{cycle}"

    # Return empty summary if cycle doesn't exist
    if cycle_key not in usage_dict.get("per_cycle", {}):
        return {
            "cycle": cycle,
            "total_input": 0,
            "total_output": 0,
            "by_agent": {}
        }

    cycle_data = usage_dict["per_cycle"][cycle_key]

    # Sum across all agents in this cycle
    total_input = sum(agent["input"] for agent in cycle_data.values())
    total_output = sum(agent["output"] for agent in cycle_data.values())

    return {
        "cycle": cycle,
        "total_input": total_input,
        "total_output": total_output,
        "by_agent": cycle_data
    }


def should_refresh_context(input_tokens: int, threshold: float = 0.5) -> bool:
    """
    Decide if context window should be refreshed.

    Context rot occurs when windows get too full. We refresh when
    utilization exceeds threshold (default: 50% = 500K tokens).

    Args:
        input_tokens: Current context size in tokens
        threshold: Utilization threshold (0.0-1.0, default: 0.5)

    Returns:
        True if context should be refreshed, False otherwise

    Example:
        >>> should_refresh_context(600_000)  # 60% utilization
        True
        >>> should_refresh_context(400_000)  # 40% utilization
        False
    """
    utilization = input_tokens / 1_000_000  # Gemini 2.0 Flash window
    return utilization > threshold
