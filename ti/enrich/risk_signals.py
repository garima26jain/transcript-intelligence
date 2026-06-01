"""Extract structured risk signals (churn / escalation / blocker).

Every signal MUST cite a source utterance — schema-enforced via the
`source_utterance_index: int` required field on RiskSignal. This is
plan §1 Failure Mode #2 turned into code: 'no citation, no claim.'
"""
from __future__ import annotations

from ti.config import settings
from ti.enrich._client import call_with_tool
from ti.enrich._prompts import load as load_prompt
from ti.schema import RiskSignal, TranscriptDoc


def _utterances_block(doc: TranscriptDoc, limit: int = 80) -> str:
    return "\n".join(
        f"[{u.index}] {u.speaker_name}: {u.text}"
        for u in doc.utterances[:limit]
    )


def _key_moments_block(doc: TranscriptDoc) -> str:
    if not doc.pre_tagged.key_moments:
        return "(none)"
    return "\n".join(
        f"- t={k.time_s:.0f}s [{k.type}] {k.speaker}: {k.text}"
        for k in doc.pre_tagged.key_moments
    )


def extract_risk_signals(doc: TranscriptDoc) -> list[RiskSignal]:
    prompt = load_prompt("risk_signals", "v1").format(
        title=doc.meeting.title,
        key_moments=_key_moments_block(doc),
        utterances=_utterances_block(doc),
    )
    out = call_with_tool(
        agent="risk_detector",
        prompt_name="risk_signals",
        prompt_version="v1",
        prompt_text=prompt,
        model=settings.model_classify,
        tool_name="extract_risk_signals",
        tool_description="Extract structured churn / escalation / blocker signals.",
        tool_schema={
            "type": "object",
            "properties": {
                "signals": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "kind": {
                                "type": "string",
                                "enum": ["churn", "escalation", "blocker"],
                            },
                            "severity": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                            },
                            "customer": {"type": ["string", "null"]},
                            "product": {"type": ["string", "null"]},
                            "driver": {"type": "string"},
                            "source_utterance_index": {"type": "integer"},
                            "surfaced_by_speaker": {"type": "string"},
                        },
                        "required": [
                            "kind",
                            "severity",
                            "driver",
                            "source_utterance_index",
                            "surfaced_by_speaker",
                        ],
                    },
                },
            },
            "required": ["signals"],
        },
        inputs_for_audit={"meeting_id": doc.meeting_id},
        max_tokens=1536,
    )

    # Enforce 'no citation, no claim': drop any signal whose
    # source_utterance_index doesn't actually exist in the doc.
    valid: list[RiskSignal] = []
    max_idx = len(doc.utterances) - 1
    for s in out["signals"]:
        if 0 <= s["source_utterance_index"] <= max_idx:
            valid.append(RiskSignal(**s))
    return valid
