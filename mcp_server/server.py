"""
FastMCP server entry point for the Transcript Intelligence tool layer.

Design choice: Exposing the tool layer as an MCP server decouples it from
any specific agent framework. The same three tools work in LangGraph,
Claude Desktop, or any future runtime without code changes.
See DECISIONS.md ADR-004 and mcp_server/README.md.
"""
from typing import Any


def main() -> None:
    """Initialise and serve the FastMCP server with all registered tools.

    Registers: search_transcripts, cross_reference_calls, get_lineage.
    Reads port and host from environment; defaults to stdio transport.
    """
    pass


if __name__ == "__main__":
    main()
