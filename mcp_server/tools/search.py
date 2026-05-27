"""
Hybrid BM25 + embedding search over transcript corpus.

Design choice: Pure embedding search misses exact-match keywords (product
names, error codes); pure BM25 misses semantic similarity. Hybrid with
reciprocal rank fusion gives the best of both at this corpus size.
See TRADEOFFS.md §4.
"""
from typing import Any


def search_transcripts(
    query: str,
    call_type: str | None = None,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Search transcripts using hybrid BM25 + embedding retrieval.

    Args:
        query: Natural-language search query.
        call_type: Optional filter to restrict results to a specific call category.
        top_k: Number of results to return (default 5).

    Returns:
        List of result dicts: [{transcript_id, score, excerpt, call_type, metadata}].
    """
    pass
