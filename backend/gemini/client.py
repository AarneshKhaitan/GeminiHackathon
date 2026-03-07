"""
Gemini API wrapper with retry logic, fallback, and token tracking.

All Gemini calls in the system go through this client. Features:
- LangChain ChatGoogleGenerativeAI integration (better LangGraph compatibility)
- JSON response format enforcement with structured output
- Exponential backoff retry (3 attempts)
- Token usage tracking (input + output)
- Fallback to cached JSON on total failure
- Async/await support

ARCHITECTURAL NOTE: Every agent (Investigator, Orchestrator, Evidence Packager)
uses this client via call_gemini() convenience function.
"""

import json
import asyncio
from typing import Any
from pathlib import Path

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser

import config


class GeminiClient:
    """Wrapper for all Gemini API calls with retry and fallback using LangChain."""

    def __init__(self):
        """Initialize LangChain Gemini client with JSON response format."""
        self.llm = ChatGoogleGenerativeAI(
            model=config.GEMINI_MODEL,
            temperature=config.GEMINI_TEMPERATURE,
            google_api_key=config.GEMINI_API_KEY,
            convert_system_message_to_human=True  # Gemini doesn't support system messages
        )

        # JSON output parser for structured responses
        self.json_parser = JsonOutputParser()

    async def call(
        self,
        prompt: str,
        schema: dict | None = None,
        fallback_path: str | None = None,
        max_retries: int = 3
    ) -> dict:
        """
        Make Gemini API call with retry logic and fallback using LangChain.

        Args:
            prompt: The prompt to send to Gemini
            schema: Optional JSON schema for validation (not enforced yet)
            fallback_path: Path to cached JSON if all API attempts fail
            max_retries: Number of retry attempts (default: 3)

        Returns:
            {
                "response": <parsed JSON response>,
                "token_usage": {
                    "input_tokens": int,
                    "output_tokens": int,
                    "total_tokens": int
                },
                "from_cache": bool (optional, only if fallback used)
            }

        Raises:
            Exception: If all retries fail and no fallback is provided
        """

        # Add JSON formatting instruction to prompt
        json_prompt = f"{prompt}\n\nYou MUST respond with valid JSON only. Do not include any markdown formatting or code blocks."

        for attempt in range(max_retries):
            try:
                # Make async LangChain API call
                message = HumanMessage(content=json_prompt)
                response = await self.llm.ainvoke([message])

                # Get response content (handle LangChain's content structure)
                content = response.content

                if isinstance(content, list):
                    # LangChain returns list of content blocks
                    # Extract text from blocks
                    if content and isinstance(content[0], dict) and 'text' in content[0]:
                        content = content[0]['text']
                    elif content:
                        content = str(content[0])
                    else:
                        content = ""
                elif isinstance(content, dict) and 'text' in content:
                    # Single content block with text key
                    content = content['text']
                elif not isinstance(content, str):
                    # Handle other types by converting to string
                    content = str(content)

                # Parse JSON response
                try:
                    parsed = json.loads(content)
                except json.JSONDecodeError as json_err:
                    # Try to extract JSON from markdown code blocks
                    text = content
                    if "```json" in text:
                        text = text.split("```json")[1].split("```")[0].strip()
                    elif "```" in text:
                        text = text.split("```")[1].split("```")[0].strip()

                    # Try parsing again
                    try:
                        parsed = json.loads(text)
                    except json.JSONDecodeError:
                        # If still failing, it might be control characters
                        # Try with strict=False to allow control characters
                        import re
                        # Remove invalid control characters but keep newlines/tabs we want
                        cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', text)
                        try:
                            parsed = json.loads(cleaned, strict=False)
                        except json.JSONDecodeError:
                            # Last resort: try original content with strict=False
                            parsed = json.loads(content, strict=False)

                # Validate against schema if provided (basic check)
                if schema:
                    self._validate_schema(parsed, schema)

                # Extract token usage from response
                # Try response.usage_metadata attribute first (newer LangChain versions)
                usage_metadata = {}
                if hasattr(response, 'usage_metadata') and response.usage_metadata:
                    usage_metadata = response.usage_metadata
                else:
                    # Fallback to response_metadata
                    usage_metadata = response.response_metadata.get("usage_metadata", {})

                # Extract standard token counts
                input_tokens = usage_metadata.get("input_tokens", 0)
                output_tokens = usage_metadata.get("output_tokens", 0)
                total_tokens = usage_metadata.get("total_tokens", 0)

                # Extract reasoning tokens from output_token_details (Gemini thinking tokens)
                output_details = usage_metadata.get("output_token_details", {})
                reasoning_tokens = output_details.get("reasoning", 0)

                token_usage = {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens or (input_tokens + output_tokens),
                    "reasoning_tokens": reasoning_tokens  # Gemini's thinking token count
                }

                # If we got valid token counts, return them
                if token_usage["input_tokens"] > 0 and token_usage["output_tokens"] > 0:
                    return {
                        "response": parsed,
                        "token_usage": token_usage
                    }

                # Estimate if no metadata available
                print(f"⚠️  No token usage metadata found, estimating from content length")
                token_usage["input_tokens"] = len(json_prompt) // 4  # Rough estimate: 4 chars per token
                token_usage["output_tokens"] = len(content) // 4
                token_usage["total_tokens"] = token_usage["input_tokens"] + token_usage["output_tokens"]

                return {
                    "response": parsed,
                    "token_usage": token_usage
                }

            except Exception as e:
                print(f"⚠️  Gemini API attempt {attempt + 1}/{max_retries} failed: {e}")

                if attempt < max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    print(f"⏱️  Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    # All retries exhausted - try fallback
                    if fallback_path:
                        print(f"🔄 All retries failed, using fallback: {fallback_path}")
                        return self._load_fallback(fallback_path)
                    else:
                        raise Exception(f"Gemini API failed after {max_retries} attempts: {e}")

    def _validate_schema(self, data: dict, schema: dict):
        """
        Basic schema validation (can be expanded).

        Currently just checks top-level keys exist.
        For full JSON Schema validation, integrate jsonschema library.
        """
        # TODO: Implement proper JSON schema validation if needed
        if "required" in schema:
            for key in schema["required"]:
                if key not in data:
                    raise ValueError(f"Missing required key in response: {key}")

    def _load_fallback(self, fallback_path: str) -> dict:
        """
        Load pre-cached response from file.

        Used when all API retries fail. Returns cached JSON with
        zero token usage and from_cache flag.
        """
        with open(fallback_path, 'r') as f:
            cached = json.load(f)

        return {
            "response": cached,
            "token_usage": {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0
            },
            "from_cache": True
        }


# Singleton instance (one client for entire application)
_client: GeminiClient | None = None


def get_client() -> GeminiClient:
    """Get or create GeminiClient singleton."""
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client


async def call_gemini(
    prompt: str,
    schema: dict | None = None,
    fallback_path: str | None = None
) -> dict:
    """
    Convenience function for making Gemini calls.

    This is the PRIMARY function used by all agents.

    Usage:
        result = await call_gemini(prompt)
        response_data = result["response"]
        tokens = result["token_usage"]

    Args:
        prompt: Prompt to send to Gemini
        schema: Optional JSON schema for validation
        fallback_path: Optional path to cached fallback

    Returns:
        Dict with "response" and "token_usage" keys
    """
    client = get_client()
    return await client.call(prompt, schema, fallback_path)
