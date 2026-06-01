"""Canonical transcript representation.

Merges the 6-file raw structure into one validated `TranscriptDoc`.
Field names are kept close to the raw JSON where reasonable so the
loader stays a thin mapping layer.
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


SentimentLabel = Literal["positive", "neutral", "negative"]
# Full set of pre-tagged keyMoment types observed across the 100 transcripts.
# concern / churn_signal / technical_issue / feature_gap are the negative
# anchors; positive_pivot / praise / pricing_offer / action_item are positive
# or neutral. Used by the Risk Detector and Customer Journey Graph.
KeyMomentType = Literal[
    "concern",
    "positive_pivot",
    "churn_signal",
    "technical_issue",
    "feature_gap",
    "action_item",
    "praise",
    "pricing_offer",
]


class Meeting(BaseModel):
    """meeting-info.json"""
    model_config = ConfigDict(extra="ignore")

    meeting_id: str
    title: str
    organizer_email: str | None = None
    host: str | None = None
    start_time: datetime
    end_time: datetime
    duration_min: float
    attendees: list[str] = Field(default_factory=list)


class Speaker(BaseModel):
    """A unique participant in the call."""
    name: str
    speaker_id: int


class SpeakerTurn(BaseModel):
    """speakers.json — one entry per contiguous turn at the mic."""
    speaker_name: str
    start_s: float
    end_s: float


class Utterance(BaseModel):
    """transcript.json[data][*] — one sentence with pre-tagged sentiment."""
    model_config = ConfigDict(extra="ignore")

    index: int
    text: str
    speaker_name: str
    speaker_id: int
    start_s: float
    end_s: float
    sentiment: SentimentLabel
    confidence: float


class JoinLeaveEvent(BaseModel):
    """events.json — Join/Leave participant events."""
    participant: str
    event_type: Literal["Join", "Leave"]
    time_s: float
    timestamp_ms: int


class KeyMoment(BaseModel):
    """summary.json.keyMoments[*] — pre-tagged moments of interest."""
    time_s: float
    text: str
    type: KeyMomentType
    speaker: str


class PreTaggedSummary(BaseModel):
    """summary.json — treat as a comparison baseline, not ground truth.

    See plan §1 (Failure Mode #5) for the framing.
    """
    summary: str
    action_items: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    overall_sentiment: str
    sentiment_score: float
    key_moments: list[KeyMoment] = Field(default_factory=list)


class TranscriptDoc(BaseModel):
    """The merged, validated representation of one transcript."""
    meeting: Meeting
    speakers: list[Speaker]
    speaker_turns: list[SpeakerTurn]
    utterances: list[Utterance]
    events: list[JoinLeaveEvent]
    pre_tagged: PreTaggedSummary

    @property
    def meeting_id(self) -> str:
        return self.meeting.meeting_id

    def utterance_at(self, index: int) -> Utterance:
        """Citation helper — guarantees (meeting_id, utterance_index) resolves.

        Used by the 'no citation, no claim' rule in plan §1 Failure Mode #2.
        """
        return self.utterances[index]
