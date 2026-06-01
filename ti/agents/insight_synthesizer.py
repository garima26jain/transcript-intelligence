"""Insight Synthesizer — produces the final persona-tuned narrative.

Schema-enforced citations: the LLM must return at least one
`(meeting_id, utterance_index)` pair as evidence. This is plan §1
Failure Mode #4 (sycophantic synthesis) turned into code.
"""
from __future__ import annotations

import json
from typing import Any

from ti.agents._state import AgentState
from ti.config import settings
from ti.enrich._client import call_with_tool
from ti.enrich._prompts import load as load_prompt
from ti.mcp_server import tools as mcp_tools


def _gather_action_results(state: AgentState) -> dict[str, Any]:
    """For action_status intent, pull the relevant owner's items."""
    owner = (state.get("extracted") or {}).get("owner")
    if not owner:
        return {}
    return {"action_items": mcp_tools.get_action_items_by_owner(owner)}


def _gather_customer_results(state: AgentState) -> dict[str, Any]:
    """For customer_focus intent, pull both journey and sentiment timeline."""
    customer = (state.get("extracted") or {}).get("customer")
    if not customer:
        return {}
    return {
        "journey": mcp_tools.get_customer_journey(customer),
        "sentiment_timeline": mcp_tools.sentiment_timeline(customer),
    }


def synthesize(state: AgentState) -> dict:
    # Top up tool_results based on intent if specialist hasn't already.
    extra: dict[str, Any] = {}
    if state.get("intent") == "action_status":
        extra.update(_gather_action_results(state))
    elif state.get("intent") == "customer_focus":
        extra.update(_gather_customer_results(state))

    tool_results = {**state.get("tool_results", {}), **extra}

    findings_block = json.dumps(state.get("findings", []), indent=2, default=str) or "[]"
    tool_results_block = json.dumps(tool_results, indent=2, default=str)[:8000]

    prompt = load_prompt("synthesize", "v1").format(
        persona=state.get("persona", "cs_lead"),
        query=state["query"],
        findings_block=findings_block,
        tool_results_block=tool_results_block,
    )
    out = call_with_tool(
        agent="insight_synthesizer",
        prompt_name="synthesize",
        prompt_version="v1",
        prompt_text=prompt,
        model=settings.model_classify,
        tool_name="synthesize_answer",
        tool_description="Produce the final persona-tuned narrative with citations.",
        tool_schema={
            "type": "object",
            "properties": {
                "answer": {"type": "string"},
                "citations": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "properties": {
                            "meeting_id": {"type": "string"},
                            "utterance_index": {"type": "integer"},
                            "quote": {"type": ["string", "null"]},
                        },
                        "required": ["meeting_id", "utterance_index"],
                    },
                },
            },
            "required": ["answer", "citations"],
        },
        inputs_for_audit={
            "persona": state.get("persona", "cs_lead"),
            "intent": state.get("intent"),
        },
        max_tokens=2048,
    )
    return {
        "tool_results": tool_results,
        "answer": out["answer"],
        "citations": out["citations"],
        "trace": [f"synthesize → {len(out['answer'])} chars, {len(out['citations'])} citations"],
    }
