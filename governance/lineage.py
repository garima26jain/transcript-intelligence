"""
Insight evidence chain / lineage tracker.

Design choice: Every insight must be traceable back to the specific
transcript turns that support it. This lineage graph lets reviewers audit
claims and lets agents avoid circular reasoning. See DECISIONS.md ADR-004.
"""
from typing import Any


def record_evidence(
    insight_id: str,
    evidence_items: list[dict[str, Any]],
) -> None:
    """Record which transcript passages support a given insight.

    Args:
        insight_id: Unique identifier for the insight.
        evidence_items: List of dicts: [{transcript_id, turn_index, excerpt, relevance_score}].
    """
    pass


def get_evidence(insight_id: str) -> list[dict[str, Any]]:
    """Retrieve the evidence chain for a given insight.

    Args:
        insight_id: Unique identifier for the insight.

    Returns:
        List of evidence item dicts in descending relevance order.
    """
    pass
