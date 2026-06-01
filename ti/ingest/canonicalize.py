"""Field mapping from raw JSON dicts → validated TranscriptDoc.

This is where the camelCase → snake_case translation lives, and where
all the Pydantic validation kicks in. If a raw file violates assumptions
we'll see it immediately as a ValidationError tagged with the meeting_id.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from ti.schema import (
    JoinLeaveEvent,
    KeyMoment,
    Meeting,
    PreTaggedSummary,
    Speaker,
    SpeakerTurn,
    TranscriptDoc,
    Utterance,
)


class CanonicalizationError(ValueError):
    """Raised when raw data can't be mapped into the canonical shape."""


def _parse_dt(s: str) -> datetime:
    """Accept both `Z`-suffixed and offset-style ISO timestamps."""
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _meeting(raw: dict[str, Any]) -> Meeting:
    return Meeting(
        meeting_id=raw["meetingId"],
        title=raw["title"],
        organizer_email=raw.get("organizerEmail"),
        host=raw.get("host"),
        start_time=_parse_dt(raw["startTime"]),
        end_time=_parse_dt(raw["endTime"]),
        duration_min=float(raw["duration"]),
        attendees=raw.get("allEmails", []),
    )


def _speakers(raw_meta: dict[str, str]) -> list[Speaker]:
    """`speaker-meta.json` is `{speaker_id_str: name}`."""
    return [
        Speaker(name=name, speaker_id=int(sid))
        for sid, name in raw_meta.items()
    ]


def _speaker_turns(raw_turns: list[dict[str, Any]]) -> list[SpeakerTurn]:
    return [
        SpeakerTurn(
            speaker_name=t["speakerName"],
            start_s=float(t["timestamp"]),
            end_s=float(t["endTimeTs"]),
        )
        for t in raw_turns
    ]


def _utterances(raw_transcript: dict[str, Any]) -> list[Utterance]:
    data = raw_transcript.get("data", [])
    return [
        Utterance(
            index=u["index"],
            text=u["sentence"],
            speaker_name=u["speaker_name"],
            speaker_id=u["speaker_id"],
            start_s=float(u["time"]),
            end_s=float(u["endTime"]),
            sentiment=u["sentimentType"],
            confidence=float(u.get("averageConfidence", 0.0)),
        )
        for u in data
    ]


def _events(raw_events: list[dict[str, Any]]) -> list[JoinLeaveEvent]:
    return [
        JoinLeaveEvent(
            participant=e["participantName"],
            event_type=e["type"],
            time_s=float(e["time"]),
            timestamp_ms=int(e["timestamp"]),
        )
        for e in raw_events
    ]


def _pre_tagged(raw_summary: dict[str, Any]) -> PreTaggedSummary:
    return PreTaggedSummary(
        summary=raw_summary["summary"],
        action_items=raw_summary.get("actionItems", []),
        topics=raw_summary.get("topics", []),
        overall_sentiment=raw_summary.get("overallSentiment", "unknown"),
        sentiment_score=float(raw_summary.get("sentimentScore", 0.0)),
        key_moments=[
            KeyMoment(
                time_s=float(k["time"]),
                text=k["text"],
                type=k["type"],
                speaker=k["speaker"],
            )
            for k in raw_summary.get("keyMoments", [])
        ],
    )


def to_transcript_doc(raw: dict[str, Any]) -> TranscriptDoc:
    """Canonicalize a `load_raw()` payload into a validated TranscriptDoc.

    Errors are re-raised with the meeting_id prefixed so the failing
    folder is identifiable in the ingest script's output.
    """
    meeting_id = raw["meeting_info"].get("meetingId", "<unknown>")
    try:
        return TranscriptDoc(
            meeting=_meeting(raw["meeting_info"]),
            speakers=_speakers(raw["speaker_meta"]),
            speaker_turns=_speaker_turns(raw["speakers"]),
            utterances=_utterances(raw["transcript"]),
            events=_events(raw["events"]),
            pre_tagged=_pre_tagged(raw["summary"]),
        )
    except Exception as e:
        raise CanonicalizationError(f"{meeting_id}: {e}") from e
