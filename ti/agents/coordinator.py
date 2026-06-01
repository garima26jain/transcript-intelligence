"""LangGraph Coordinator — assembles router + specialists + HITL + synthesizer.

Graph:

         route
           │
   ┌───────┴────────┐
   ▼                ▼
  risk         synthesize  (action_status / general route directly here)
   │
   ▼
 hitl_gate
   │
   ▼
synthesize  →  END
"""
from __future__ import annotations

from langgraph.graph import END, StateGraph

from ti.agents._state import AgentState
from ti.agents.hitl import hitl_gate
from ti.agents.insight_synthesizer import synthesize
from ti.agents.risk_detector import detect_risk
from ti.agents.router import route


def _after_route(state: AgentState) -> str:
    """Conditional edge dispatcher."""
    intent = state.get("intent", "general")
    if intent in {"risk_assessment", "customer_focus"}:
        return "risk"
    return "synthesize"


def build_coordinator():
    g = StateGraph(AgentState)
    g.add_node("route", route)
    g.add_node("risk", detect_risk)
    g.add_node("hitl_gate", hitl_gate)
    g.add_node("synthesize", synthesize)

    g.set_entry_point("route")
    g.add_conditional_edges("route", _after_route, {
        "risk": "risk",
        "synthesize": "synthesize",
    })
    g.add_edge("risk", "hitl_gate")
    g.add_edge("hitl_gate", "synthesize")
    g.add_edge("synthesize", END)

    return g.compile()
