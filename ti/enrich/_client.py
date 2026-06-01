"""Anthropic client wrapper with structured output + audit logging.

Every LLM call goes through `call_with_tool()` which:
  1. Forces the model to use a single named tool (gives us strict schema).
  2. Wraps the call in `governance.audit.record()` for lineage.
  3. Returns the parsed tool input as a dict.

Why tool-use instead of "respond in JSON"?
  - The model is guaranteed to emit valid JSON matching the schema.
  - Pydantic validation gives one clean error path on schema drift.
  - Same pattern works across all enrichers — one helper, one mental model.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from anthropic import Anthropic

from ti.config import settings
from ti.governance import audit


@lru_cache(maxsize=1)
def _client() -> Anthropic:
    if not settings.anthropic_api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set. Copy .env.example to .env and fill it in."
        )
    return Anthropic(api_key=settings.anthropic_api_key)


def call_with_tool(
    *,
    agent: str,
    prompt_name: str,
    prompt_version: str,
    prompt_text: str,
    model: str,
    tool_name: str,
    tool_description: str,
    tool_schema: dict[str, Any],
    inputs_for_audit: dict[str, Any] | None = None,
    max_tokens: int = 2048,
    temperature: float | None = 0.0,
) -> dict[str, Any]:
    """One LLM call → strict structured output via forced tool use.

    Returns the parsed tool input dict. Logs the full call to the audit
    log so any insight downstream is traceable.
    """
    tools = [
        {
            "name": tool_name,
            "description": tool_description,
            "input_schema": tool_schema,
        }
    ]
    tool_choice = {"type": "tool", "name": tool_name}

    with audit.record(
        agent=agent,
        prompt_name=prompt_name,
        prompt_version=prompt_version,
        prompt_text=prompt_text,
        model=model,
        inputs=inputs_for_audit,
    ) as ctx:
        # Opus 4.7 rejects `temperature` — newer reasoning models don't take it.
        # Older models (Sonnet 4.6, Haiku 4.5) still accept it.
        create_kwargs: dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "tools": tools,
            "tool_choice": tool_choice,
            "messages": [{"role": "user", "content": prompt_text}],
        }
        if temperature is not None and "opus-4-7" not in model:
            create_kwargs["temperature"] = temperature
        resp = _client().messages.create(**create_kwargs)
        ctx["usage"] = {
            "input_tokens": resp.usage.input_tokens,
            "output_tokens": resp.usage.output_tokens,
        }
        ctx["stop_reason"] = resp.stop_reason

        # Forced tool use: the first content block is always a tool_use.
        for block in resp.content:
            if block.type == "tool_use" and block.name == tool_name:
                ctx["output_summary"] = {
                    "tool": tool_name,
                    "keys": list(block.input.keys()) if isinstance(block.input, dict) else None,
                }
                return dict(block.input)

        raise RuntimeError(
            f"Expected tool_use block for {tool_name}, got: "
            f"{[b.type for b in resp.content]}"
        )
