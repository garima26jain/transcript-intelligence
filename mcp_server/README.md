# MCP Server

## Why MCP
The job description calls out custom MCP servers as a Day-1 critical
skill. MCP makes the tool layer reusable across agent frameworks and
Claude Desktop, where APIs would lock us to a specific runtime.

## Tools exposed
1. `search_transcripts(query, call_type?, top_k=5)` — hybrid BM25 + embedding
2. `cross_reference_calls(topic, since_days=30)` — finds topic across call types
3. `get_lineage(insight_id)` — evidence chain for an insight

## How to run
```bash
python mcp_server/server.py
```

## Claude Desktop integration
Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "transcript-intelligence": {
      "command": "python",
      "args": ["/absolute/path/to/mcp_server/server.py"]
    }
  }
}
```

Restart Claude Desktop. The 3 tools should appear in the tool picker.
