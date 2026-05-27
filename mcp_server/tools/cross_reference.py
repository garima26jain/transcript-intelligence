"""
Cross-call topic reference tool exposed via MCP.

Design choice: Providing cross-reference as an MCP tool (rather than
a batch step) allows interactive exploration — an agent or human can
query "which call types mentioned X in the last 30 days" on demand.
See DECISIONS.md ADR-004.
"""
from typing import Any


def cross_reference_calls(
    topic: str,
    since_days: int = 30,
) -> list[dict[str, Any]]:
    """Find transcripts mentioning a topic, grouped by call type.

    Args:
        topic: Topic string to search across all call types.
        since_days: Lookback window in days (default 30).

    Returns:
        List of dicts: [{call_type, count, representative_transcript_ids, sample_excerpts}].
    """
    pass
