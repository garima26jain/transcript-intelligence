"""
Insight lineage tool exposed via MCP.

Design choice: Making lineage queryable via MCP lets both agents and
human reviewers verify insight provenance interactively, without digging
into internal data files. Supports the "show your work" requirement.
See governance/lineage.py and DECISIONS.md ADR-004.
"""
from typing import Any


def get_lineage(insight_id: str) -> dict[str, Any]:
    """Return the full evidence chain for a given insight.

    Args:
        insight_id: Unique identifier for the insight.

    Returns:
        Dict with {insight_id, title, evidence: [{transcript_id, turn_index,
        excerpt, relevance_score}], created_at}.
    """
    pass
