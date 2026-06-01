"""Shared state for the LangGraph coordinator.

Reducer note: `trace` and `citations` use `operator.add` so each node
can return additive deltas instead of needing to read+rewrite the
whole list. All other fields use the default 'overwrite' reducer.
"""
from __future__ import annotations

import operator
from typing import Annotated, Any, Literal, TypedDict


Persona = Literal["support_lead", "cs_lead", "pm", "eng_lead"]
Intent = Literal[
    "risk_assessment",   # "which customers are at risk?"
    "customer_focus",    # "tell me about Quantum Edge"
    "action_status",     # "what are Tyler's open items?"
    "general",           # anything else — fall back to synthesizer
]


class AgentState(TypedDict, total=False):
    # Inputs
    query: str
    persona: Persona

    # Set by the router
    intent: Intent
    extracted: dict[str, Any]      # {"customer": "...", "owner": "..."}

    # Filled by specialist agents
    tool_results: dict[str, Any]   # raw MCP tool outputs, keyed by tool name
    findings: list[dict[str, Any]] # structured findings with citations

    # HITL — collected, not blocking. In production: a queue.
    hitl_flags: list[dict[str, Any]]

    # Final
    answer: str
    citations: Annotated[list[dict[str, Any]], operator.add]

    # Human-readable step log for the demo video
    trace: Annotated[list[str], operator.add]
