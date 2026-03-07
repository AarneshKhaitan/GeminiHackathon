"""
Parser utilities for extracting structured data from Investigator output.

CRITICAL: The Investigator SELF-COMPRESSES at the end of each cycle.
There is NO separate compression Gemini call. The parser just extracts
the delimited compressed state from the investigator's response.

Delimited format expected:
    === COMPRESSED STATE ===
    { ... json ... }
    === END COMPRESSED STATE ===
"""

import json
import re


def parse_compressed_state(output: str) -> str | None:
    """
    Extract self-compressed state from investigator output.

    The investigator outputs compressed state between delimiters.
    This function extracts it via regex pattern matching.

    Args:
        output: Full investigator output text

    Returns:
        Extracted compressed state string (JSON), or None if not found

    Example:
        >>> text = "Reasoning... === COMPRESSED STATE === {...} === END ..."
        >>> compressed = parse_compressed_state(text)
        >>> data = json.loads(compressed)
    """

    # Look for delimited section (case-insensitive, multiline)
    pattern = r"===\s*COMPRESSED STATE\s*===(.*?)===\s*END COMPRESSED STATE\s*==="
    match = re.search(pattern, output, re.DOTALL | re.IGNORECASE)

    if match:
        compressed = match.group(1).strip()
        return compressed

    return None


def parse_investigation_output(output: dict) -> dict:
    """
    Parse full investigation output into structured components.

    Extracts standard fields from investigator JSON response.

    Args:
        output: Dict with investigation results from Gemini

    Returns:
        {
            "surviving_hypotheses": [...],
            "eliminated_hypotheses": [...],
            "cross_modal_flags": [...],
            "evidence_requests": [...],
            "key_insights": [...],
            "compressed_state": str
        }
    """

    return {
        "surviving_hypotheses": output.get("surviving_hypotheses", []),
        "eliminated_hypotheses": output.get("eliminated_hypotheses", []),
        "cross_modal_flags": output.get("cross_modal_flags", []),
        "evidence_requests": output.get("evidence_requests", []),
        "key_insights": output.get("key_insights", []),
        "compressed_state": output.get("compressed_state", None)
    }


def extract_json_from_markdown(text: str) -> dict:
    """
    Extract JSON from markdown code blocks if Gemini returns it that way.

    Sometimes Gemini returns JSON wrapped in ```json ... ``` blocks
    even when we specify application/json MIME type. This handles that.

    Args:
        text: Text potentially containing ```json ... ``` blocks

    Returns:
        Parsed JSON dict

    Raises:
        json.JSONDecodeError: If text is not valid JSON after extraction
    """

    # Try direct JSON parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code block
    if "```json" in text:
        json_text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        json_text = text.split("```")[1].split("```")[0].strip()
    else:
        json_text = text

    return json.loads(json_text)


def validate_investigation_response(response: dict) -> bool:
    """
    Validate that investigator response has required fields.

    Args:
        response: Parsed JSON response from investigator

    Returns:
        True if valid, False otherwise
    """

    required_fields = [
        "surviving_hypotheses",
        "eliminated_hypotheses",
        "evidence_requests",
        "compressed_state"
    ]

    return all(field in response for field in required_fields)
