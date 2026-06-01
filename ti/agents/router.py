"""Intent router — one Haiku call → intent + extracted entities.

Cheapest model in the routing pattern (plan §3 decision 6). Sets two
state fields the downstream agents read: `intent` and `extracted`.
"""
from __future__ import annotations

from ti.agents._state import AgentState
from ti.config import settings
from ti.enrich._client import call_with_tool
from ti.enrich._prompts import load as load_prompt


def route(state: AgentState) -> dict:
    prompt = load_prompt("route", "v1").format(query=state["query"])
    out = call_with_tool(
        agent="coordinator.router",
        prompt_name="route",
        prompt_version="v1",
        prompt_text=prompt,
        model=settings.model_screen,
        tool_name="classify_query",
        tool_description="Classify the query and pull out named entities.",
        tool_schema={
            "type": "object",
            "properties": {
                "intent": {
                    "type": "string",
                    "enum": [
                        "risk_assessment",
                        "customer_focus",
                        "action_status",
                        "general",
                    ],
                },
                "customer": {"type": ["string", "null"]},
                "owner": {"type": ["string", "null"]},
                "product": {"type": ["string", "null"]},
                "reasoning": {"type": "string"},
            },
            "required": ["intent"],
        },
        inputs_for_audit={"query": state["query"][:200]},
        max_tokens=256,
    )
    extracted = {
        k: out.get(k) for k in ("customer", "owner", "product") if out.get(k)
    }
    return {
        "intent": out["intent"],
        "extracted": extracted,
        "trace": [f"route → intent={out['intent']} extracted={extracted}"],
    }
