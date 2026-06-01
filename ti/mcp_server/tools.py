"""The four MCP tools the agents (and Claude Code, when attached) call.

Each tool returns JSON-serializable dicts. Citations are included
wherever cross-meeting reasoning is involved so the 'no citation, no
claim' rule (plan §1 Failure Mode #2) holds across the system boundary.
"""
from __future__ import annotations

from typing import Any

from ti.store import duckdb_store


def search_transcripts(
    query: str | None = None,
    call_type: str | None = None,
    customer: str | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    """Find transcripts matching a free-text query and/or structured filters.

    Args:
        query: case-insensitive substring search over title + summary.
        call_type: one of internal | external | support | unknown.
        customer: customer name (matched against canonical-name entities).
        limit: max results, default 20.
    """
    hits = duckdb_store.search(
        query=query, call_type=call_type, customer=customer, limit=limit
    )
    return {"hits": hits, "n": len(hits)}


def get_customer_journey(customer: str) -> dict[str, Any]:
    """Return every interaction with a customer across all call types, chronologically.

    Output includes per-meeting sentiment, arc slope, and a count of risk
    signals — the raw material for the Customer Journey Graph headline
    insight. Each meeting is a citation: the agent layer should quote
    `meeting_id` when answering.
    """
    journey = duckdb_store.customer_journey_rows(customer)
    if not journey:
        return {"customer": customer, "found": False, "journey": []}

    # Quick aggregates so the agent doesn't have to recompute.
    scores = [m["sentiment_score"] for m in journey if m["sentiment_score"] is not None]
    risk_total = sum(m["risk_signal_count"] for m in journey)
    return {
        "customer": customer,
        "found": True,
        "n_meetings": len(journey),
        "first_seen": journey[0]["date"],
        "last_seen": journey[-1]["date"],
        "avg_sentiment_score": sum(scores) / len(scores) if scores else None,
        "total_risk_signals": risk_total,
        "journey": journey,
    }


def get_action_items_by_owner(
    owner: str, limit: int = 50
) -> dict[str, Any]:
    """All action items assigned to a person, joined with meeting context.

    Used by the Action-Item Lineage insight (notebook 04). Owner match
    is substring + case-insensitive so 'tyler' matches 'Tyler Washington'.
    """
    items = duckdb_store.action_items_by_owner(owner, limit=limit)
    return {"owner": owner, "n": len(items), "items": items}


def sentiment_timeline(entity_name: str) -> dict[str, Any]:
    """Per-meeting sentiment time series for a customer or product.

    Two signals returned per point: `entity_avg_sentiment` (sentiment of
    utterances that mention this entity within the meeting, range -1..+1)
    and `meeting_sentiment_score` (pre-tagged 1..5 overall meeting score).
    """
    points = duckdb_store.sentiment_timeline_rows(entity_name)
    return {"entity": entity_name, "n": len(points), "points": points}


# ---- Registry for the MCP server ----
TOOLS = {
    "search_transcripts": search_transcripts,
    "get_customer_journey": get_customer_journey,
    "get_action_items_by_owner": get_action_items_by_owner,
    "sentiment_timeline": sentiment_timeline,
}
