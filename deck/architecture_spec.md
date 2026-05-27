# Architecture Diagram Spec

## Diagram structure

Two clearly labeled subgraphs:

### Subgraph A: "What I Built"
- Transcripts (input)
- PII Redaction
- Embedding + Storage
- MCP Server (3 tools)
- Categorizer Agent
- Insight Agent
- Evidence + Lineage + Audit Log
- Insights Output
- Cross-cutting: Langfuse (traces, cost), PII redactor

### Subgraph B: "What I'd Add at Scale"
- Go ingestion service
- Vector DB with reranker
- HITL review queue
- Critic agent (offline only)
- Distilled small classifier
- Multi-tenant routing
- K8s autoscaling
- Real-time streaming

## Render as
Mermaid (.mmd) → PNG. Generate the .mmd file on Day 5.
