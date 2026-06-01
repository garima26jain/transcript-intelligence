"""Classify each transcript as internal | external | support | unknown.

Hybrid by design: title regex handles ~90% of cases at zero cost, LLM
fallback handles the ambiguous remainder (see plan §3 decision 6 on
cost-aware routing).
"""
from __future__ import annotations

import re

from ti.config import settings
from ti.enrich._client import call_with_tool
from ti.enrich._prompts import load as load_prompt
from ti.schema import TranscriptDoc
from ti.schema.enrichment import CallType


_SUPPORT_RE = re.compile(r"\bSupport Case #\d+", re.IGNORECASE)
_EXTERNAL_RE = re.compile(r"\bAegis\s*/\s*\w", re.IGNORECASE)
_INTERNAL_RE = re.compile(
    r"\b(standup|sync|war room|incident|roadmap|planning|review|retro|readiness|audit prep|threat assessment)\b",
    re.IGNORECASE,
)


def classify_by_rule(title: str) -> tuple[CallType | None, float]:
    """Return (call_type, confidence) if a rule matches, else (None, 0)."""
    if _SUPPORT_RE.search(title):
        return "support", 0.98
    if _EXTERNAL_RE.search(title):
        return "external", 0.95
    if _INTERNAL_RE.search(title):
        return "internal", 0.85
    return None, 0.0


def _classify_by_llm(doc: TranscriptDoc) -> tuple[CallType, float]:
    """LLM fallback for ambiguous titles. Uses Haiku — cheapest model."""
    opening = "\n".join(
        f"  {u.speaker_name}: {u.text}"
        for u in doc.utterances[:5]
    )
    prompt = load_prompt("call_type", "v1").format(
        title=doc.meeting.title,
        attendees=", ".join(doc.meeting.attendees),
        opening=opening,
    )
    out = call_with_tool(
        agent="call_type",
        prompt_name="call_type",
        prompt_version="v1",
        prompt_text=prompt,
        model=settings.model_screen,
        tool_name="classify_call_type",
        tool_description="Classify the call into one of the four types.",
        tool_schema={
            "type": "object",
            "properties": {
                "call_type": {
                    "type": "string",
                    "enum": ["internal", "external", "support", "unknown"],
                },
                "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "reasoning": {"type": "string"},
            },
            "required": ["call_type", "confidence"],
        },
        inputs_for_audit={"meeting_id": doc.meeting_id, "title": doc.meeting.title},
        max_tokens=256,
    )
    return out["call_type"], float(out["confidence"])


def classify_call_type(doc: TranscriptDoc) -> tuple[CallType, float]:
    """Rule-first, LLM-fallback classification."""
    by_rule, conf = classify_by_rule(doc.meeting.title)
    if by_rule is not None:
        return by_rule, conf
    return _classify_by_llm(doc)
