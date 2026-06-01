"""Custom MCP server (FastMCP, stdio transport).

Exposes the 4 tools from `ti.mcp_server.tools` over MCP so:
  - our LangGraph agents (Phase 4) can call them via standard MCP plumbing,
  - Claude Code (or any MCP host) can attach and ask questions live —
    this is the live-demo closer in the video script (plan §9, 5:30–6:30).

Start with `make mcp` or `python -m scripts.start_mcp`.
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ti.mcp_server import tools


mcp = FastMCP("transcript-intelligence")


@mcp.tool()
def search_transcripts(
    query: str | None = None,
    call_type: str | None = None,
    customer: str | None = None,
    limit: int = 20,
) -> dict:
    """Find transcripts matching a free-text query and/or structured filters.

    Args:
        query: case-insensitive substring search over title + summary.
        call_type: one of internal | external | support | unknown.
        customer: customer name (canonical).
        limit: max results, default 20.
    """
    return tools.search_transcripts(
        query=query, call_type=call_type, customer=customer, limit=limit
    )


@mcp.tool()
def get_customer_journey(customer: str) -> dict:
    """Every interaction with a customer across all call types, chronologically.

    Returns per-meeting sentiment, arc slope, risk-signal count, and
    aggregate stats. Each meeting in the journey is citable via its meeting_id.
    """
    return tools.get_customer_journey(customer)


@mcp.tool()
def get_action_items_by_owner(owner: str, limit: int = 50) -> dict:
    """All action items assigned to a person, joined with meeting context.

    Owner match is substring + case-insensitive.
    """
    return tools.get_action_items_by_owner(owner, limit=limit)


@mcp.tool()
def sentiment_timeline(entity_name: str) -> dict:
    """Per-meeting sentiment time series for a customer or product.

    Returns two signals per point: entity-scoped sentiment (-1..+1) and
    the pre-tagged overall meeting score (1..5).
    """
    return tools.sentiment_timeline(entity_name)


def run() -> None:
    mcp.run()


if __name__ == "__main__":
    run()
