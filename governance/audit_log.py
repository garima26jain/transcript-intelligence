"""
LLM call audit trail.

Design choice: Every LLM call is logged with its inputs, outputs, model,
latency, and token counts before any post-processing. This enables cost
attribution, debugging, and compliance review without relying solely on
Langfuse (which may be unavailable offline). See TRADEOFFS.md §7.
"""
from typing import Any


def log_call(
    call_id: str,
    model: str,
    prompt: str,
    response: str,
    latency_ms: float,
    token_counts: dict[str, int],
    metadata: dict[str, Any] | None = None,
) -> None:
    """Append a single LLM call record to the audit log.

    Args:
        call_id: Unique identifier for this call (UUID).
        model: Model name used (e.g. "claude-haiku-4-5").
        prompt: Full prompt string sent to the model.
        response: Full response string returned by the model.
        latency_ms: Wall-clock latency in milliseconds.
        token_counts: Dict with keys input_tokens, output_tokens.
        metadata: Optional extra context (agent name, transcript_id, etc.).
    """
    pass


def get_log(since_call_id: str | None = None) -> list[dict]:
    """Retrieve audit log entries, optionally starting after a given call_id.

    Args:
        since_call_id: If provided, return only entries after this call.

    Returns:
        List of audit log entry dicts in chronological order.
    """
    pass
