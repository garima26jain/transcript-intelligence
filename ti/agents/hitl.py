"""Human-in-the-loop gate.

In production this is a queue + UI. For the take-home it's an inline
collector: any high-severity churn flag gets recorded in state and
echoed to the trace so the demo video can show the gate firing.

The deliberate choice (plan §3 decision 5) is to gate ONLY on
high-stakes labels (churn, escalation), not every label. Gating
everything is annoying; gating nothing is unsafe.
"""
from __future__ import annotations

from ti.agents._state import AgentState


def hitl_gate(state: AgentState) -> dict:
    flags = state.get("hitl_flags", [])
    if not flags:
        return {"trace": ["hitl_gate → no high-stakes flags, passing through"]}
    msg = (
        f"hitl_gate → {len(flags)} high-severity flag(s) recorded for review "
        f"(would block external publication in production)"
    )
    return {"trace": [msg]}
