"""Risk Detector specialist agent.

Given a customer (or "the corpus"), pull their full journey via MCP
tools, then one Sonnet call to synthesize ranked, citation-backed risk
findings. HITL flags are collected for any `high`-severity churn.
"""
from __future__ import annotations

import json
from typing import Any

from ti.agents._state import AgentState
from ti.config import settings
from ti.enrich._client import call_with_tool
from ti.enrich._prompts import load as load_prompt
from ti.mcp_server import tools as mcp_tools


def _format_journey(journey: list[dict[str, Any]]) -> str:
    if not journey:
        return "(no meetings found)"
    return "\n".join(
        f"  • {m['date'][:10]}  [{m['call_type']:8s}]  "
        f"score={m['sentiment_score']:.1f}  risks={m['risk_signal_count']}  "
        f"— {m['title'][:60]}"
        for m in journey
    )


def _signals_for_customer(customer: str) -> list[dict[str, Any]]:
    """Cross-meeting view of every risk signal naming this customer."""
    from ti.store import duckdb_store

    with duckdb_store.connect() as con:
        rows = con.execute(
            """SELECT rs.meeting_id, rs.kind, rs.severity, rs.driver,
                      rs.source_utterance_index, rs.surfaced_by_speaker,
                      t.title, t.start_time
               FROM risk_signals rs
               JOIN transcripts t ON t.meeting_id = rs.meeting_id
               WHERE lower(rs.customer) = lower(?)
               ORDER BY t.start_time ASC""",
            [customer],
        ).fetchall()
    return [
        {
            "meeting_id": r[0],
            "kind": r[1],
            "severity": r[2],
            "driver": r[3],
            "source_utterance_index": r[4],
            "surfaced_by_speaker": r[5],
            "title": r[6],
            "date": r[7].isoformat() if r[7] else None,
        }
        for r in rows
    ]


def detect_risk(state: AgentState) -> dict:
    customer = (state.get("extracted") or {}).get("customer")
    if not customer:
        # No specific customer — produce a corpus-wide top-N by signal density.
        return _corpus_wide_risk(state)

    journey = mcp_tools.get_customer_journey(customer)
    signals = _signals_for_customer(customer)

    if not journey.get("found"):
        return {
            "findings": [],
            "trace": [f"risk_detect → customer '{customer}' not found in corpus"],
        }

    journey_block = _format_journey(journey["journey"])
    signals_block = "\n".join(
        f"  • {s['date'][:10] if s['date'] else '?'}  "
        f"[{s['kind']}/{s['severity']}]  utt#{s['source_utterance_index']}  "
        f"— {s['driver'][:80]}"
        for s in signals
    ) or "(none)"

    prompt = load_prompt("risk_assess", "v1").format(
        customer=customer,
        n_meetings=journey["n_meetings"],
        first_seen=journey["first_seen"],
        last_seen=journey["last_seen"],
        avg_sentiment=f"{journey['avg_sentiment_score']:.2f}"
        if journey["avg_sentiment_score"] is not None else "n/a",
        total_risk=journey["total_risk_signals"],
        journey_block=journey_block,
        signals_block=signals_block,
    )
    out = call_with_tool(
        agent="risk_detector",
        prompt_name="risk_assess",
        prompt_version="v1",
        prompt_text=prompt,
        model=settings.model_classify,
        tool_name="assess_risk",
        tool_description="Produce ranked, citation-backed risk findings.",
        tool_schema={
            "type": "object",
            "properties": {
                "findings": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "headline": {"type": "string"},
                            "severity": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                            },
                            "evidence_meeting_id": {"type": "string"},
                            "evidence_utterance_index": {"type": "integer"},
                            "recommendation": {"type": "string"},
                        },
                        "required": [
                            "headline", "severity",
                            "evidence_meeting_id",
                            "evidence_utterance_index",
                            "recommendation",
                        ],
                    },
                },
            },
            "required": ["findings"],
        },
        inputs_for_audit={"customer": customer, "n_meetings": journey["n_meetings"]},
        max_tokens=2048,
    )
    findings = out["findings"]
    hitl_flags = [
        {"customer": customer, "headline": f["headline"], "severity": f["severity"]}
        for f in findings
        if f["severity"] == "high"
    ]
    return {
        "tool_results": {"journey": journey, "signals": signals},
        "findings": findings,
        "hitl_flags": hitl_flags,
        "trace": [
            f"risk_detect → customer={customer} signals={len(signals)} findings={len(findings)} hitl={len(hitl_flags)}"
        ],
    }


def _corpus_wide_risk(state: AgentState) -> dict:
    """Corpus-wide: top-5 customers by risk-signal density across recent meetings."""
    from ti.store import duckdb_store

    with duckdb_store.connect() as con:
        rows = con.execute(
            """SELECT rs.customer, COUNT(*) AS n_signals,
                      SUM(CASE WHEN rs.severity = 'high' THEN 1 ELSE 0 END) AS n_high,
                      SUM(CASE WHEN rs.kind = 'churn' THEN 1 ELSE 0 END) AS n_churn
               FROM risk_signals rs
               WHERE rs.customer IS NOT NULL AND rs.customer <> ''
               GROUP BY rs.customer
               ORDER BY n_high DESC, n_signals DESC
               LIMIT 5""",
        ).fetchall()
    findings = [
        {
            "headline": f"{r[0]} carries {r[1]} risk signals across the corpus ({r[2]} high-severity, {r[3]} churn).",
            "severity": "high" if r[2] > 0 else "medium",
            "evidence_meeting_id": "(corpus-aggregate)",
            "evidence_utterance_index": -1,
            "recommendation": f"Drill into {r[0]}'s journey for specific drivers.",
        }
        for r in rows
    ]
    hitl_flags = [
        {"customer": r[0], "severity": "high", "n_high": r[2]}
        for r in rows if r[2] > 0
    ]
    return {
        "tool_results": {"corpus_top_n": rows},
        "findings": findings,
        "hitl_flags": hitl_flags,
        "trace": [f"risk_detect (corpus-wide) → top {len(findings)} customers"],
    }
