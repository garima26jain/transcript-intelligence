# Transcript Intelligence

> Analyzing 150 customer-service call transcripts to surface
> cross-stakeholder insights.

## Overview
*One paragraph: what this is, who it's for, what it produces.*

## How to Read This Repo

If you have 5 minutes, read in this order:
1. `field_notes.md` — what I saw in the data
2. `TRADEOFFS.md` — the choices I considered and why
3. `DECISIONS.md` — five ADRs on irreversible calls
4. `evals/results.md` — honest write-up of what worked and what didn't
5. The 7-min video in `demo/`

If you have 30 minutes, also read:
- `mcp_server/README.md` — why MCP, what's exposed
- `data_card.md` — provenance, biases, synthetic data strategy
- `notebooks/analysis.ipynb` — the end-to-end run


## Key Results
*Three bullet placeholders for headline metrics — to fill after Day 4.*

## Architecture
*One sentence + link to deck/architecture_spec.md*

## How to Run
*Three commands: setup, analyze, eval. Filled in once Makefile works.*

## Repo Map
*Tree view of top-level folders with one-line descriptions.*

## Trade-offs
*See [TRADEOFFS.md](./TRADEOFFS.md)*

## Limits & Future Work
*See "Limits" section in TRADEOFFS.md and evals/results.md*

## Tech Stack
- Python 3.12, environment managed with `uv`
- Anthropic Claude (Sonnet + Haiku, tiered routing)
- OpenAI text-embedding-3-small (embeddings only)
- Langfuse (observability)
- Microsoft Presidio (PII)
- FastMCP (MCP server)
- LangGraph (agent orchestration)
