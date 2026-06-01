# Transcript Intelligence

> An agentic platform that turns ~100 call transcripts (support, external, internal) into stakeholder-grade insights for Sales, CS, PM, and Engineering leaders.

---

## What this is (and what it isn't)

**It is**: a small, opinionated platform with the same shape a production system would have — a normalized data layer, an LLM enrichment pipeline, a custom **MCP server**, a **LangGraph multi-agent layer**, governance with versioned prompts + audit log, and two deep cross-call insights (**Customer Journey Graph** + **Action-Item Lineage**).

**It isn't**: production-ready. No PII redaction in code (the dataset is synthetic). No access control. No rate limiting. The "what I'd do with one more week" slide in the deck names these gaps explicitly.

---

## Quick start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Add your Anthropic API key
cp .env.example .env
# then edit .env and set ANTHROPIC_API_KEY=sk-ant-...

# 3. Run the pipeline
make ingest      # normalize raw transcripts
make enrich      # LLM enrichment → data/enriched/
make spotcheck   # methodology table
make mcp         # start the MCP server (stdio)
make demo        # run the LangGraph coordinator over example queries
make ui          # launch the Streamlit CS-lead view
```

---

## Architecture (one screen)

```
  Streamlit / Notebooks
          │
  Coordinator Agent (LangGraph) ── HITL gate (inline)
          │
  Risk Detector + Insight Synthesizer
          │  (tool calls)
  Custom MCP Server  ── 4 tools
          │
  DuckDB + NetworkX
          │
  Enrichment pipeline (call_type → topics → sentiment → entities → normalize → risk)
          │
  data/raw/ (100 transcripts)
```

Cross-cutting: **governance** (versioned prompts in `ti/governance/prompts/`, append-only audit log) and **methodology** (10–15 transcript spot-check vs the pre-tagged labels).

---

## Failure modes the design guards against

| # | Risk | Mitigation |
|---|---|---|
| 1 | Silent entity-resolution failure (Quantum Edge vs Quantum Edge Capital) | Explicit `customer_normalize.py` step + manual alias review |
| 2 | Hallucinated cross-meeting linkage | Every claim must cite `(meeting_id, utterance_index)` — schema enforced |
| 3 | Synthetic-metric overconfidence (Trust Trajectory Score) | Always published with its components + evidence |
| 4 | Sycophantic synthesis | Schema-required citations; HITL gate on churn-signal classification |
| 5 | Pre-tagged label drift | Treated as comparison baseline, not ground truth; disagreement is information |
| 6 | Production gap (PII, access control, rate limits) | Out of scope for take-home; named in deck |

---

## What's original vs. modified

The 100 transcripts in `data/raw/` are used as-is, unmodified. No synthetic data was generated. If any call-type bucket appears underrepresented after auto-classification, it is reported in the deck but not augmented.

---

## Layout

```
ti/                  → main package
  schema/            → Pydantic source of truth
  ingest/            → 6-file folder → TranscriptDoc
  enrich/            → call_type, taxonomy, topics, sentiment, entities, normalize, risk
  store/             → DuckDB + NetworkX
  mcp_server/        → 4 MCP tools
  agents/            → Coordinator + Risk Detector + Insight Synthesizer
  governance/        → versioned prompts + audit log
  insights/          → Customer Journey Graph + Action-Item Lineage
  ui/                → Streamlit (CS-lead persona)
scripts/             → CLI entry points
notebooks/           → 01..05 — exploration, required tasks, bonus insights, methodology
deliverables/        → slide deck + video script
```
