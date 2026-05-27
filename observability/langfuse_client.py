"""
Langfuse observability wrapper for all LLM calls.

Design choice: Wrapping every LLM call in a single tracked_llm_call()
function gives one place to add tracing, cost attribution, and latency
without scattering Langfuse SDK calls across agents. See TRADEOFFS.md §8.
"""
from typing import Any, Callable


def tracked_llm_call(
    fn: Callable,
    trace_name: str,
    metadata: dict[str, Any] | None = None,
) -> Callable:
    """Decorator/wrapper that wraps an LLM call function with Langfuse tracing.

    Args:
        fn: The LLM call function to wrap (e.g. client.messages.create).
        trace_name: Human-readable name for this trace in Langfuse.
        metadata: Optional key-value pairs attached to the trace.

    Returns:
        Wrapped function that logs inputs, outputs, latency, and tokens to Langfuse.
    """
    pass
