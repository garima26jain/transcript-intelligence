"""Enrichment outputs — what we add on top of the raw transcript."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


CallType = Literal["internal", "external", "support", "unknown"]
EntityKind = Literal["customer", "product", "owner"]
RiskKind = Literal["churn", "escalation", "blocker"]
Severity = Literal["low", "medium", "high"]


class Topic(BaseModel):
    """Multi-label categorization output — 2-level taxonomy."""
    theme: str
    subtopic: str
    confidence: float = Field(ge=0.0, le=1.0)


class Entity(BaseModel):
    """Normalized entity (customer/product/owner)."""
    name: str                       # canonical name post-normalization
    kind: EntityKind
    aliases: list[str] = Field(default_factory=list)
    mention_count: int = 0


class SpeakerSentiment(BaseModel):
    """Per-speaker average sentiment within a single call."""
    speaker_name: str
    avg_sentiment: float            # -1.0 .. +1.0
    utterance_count: int


class EntitySentiment(BaseModel):
    """Sentiment when a specific customer/product is mentioned."""
    entity_name: str
    entity_kind: EntityKind
    avg_sentiment: float
    mention_count: int


class SentimentArc(BaseModel):
    """Trajectory of sentiment within a call."""
    slope: float                    # least-squares slope over utterance index
    start_value: float
    end_value: float
    smoothed: list[float] = Field(default_factory=list)


class StructuredActionItem(BaseModel):
    """An action item parsed into structure.

    `source_utterance_index` ties it to the originating utterance so the
    Action Tracker can enforce the 'no citation, no claim' rule.
    """
    owner: str
    description: str
    due: str | None = None
    source_utterance_index: int | None = None


class RiskSignal(BaseModel):
    """A churn / escalation / blocker signal extracted from the call.

    `source_utterance_index` is required so every published signal can
    be traced back to a real utterance (plan §1 Failure Mode #2).
    """
    kind: RiskKind
    severity: Severity
    customer: str | None = None
    product: str | None = None
    driver: str
    source_utterance_index: int
    surfaced_by_speaker: str


class EnrichmentResult(BaseModel):
    """Everything we add on top of a raw TranscriptDoc."""
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    meeting_id: str
    enriched_at: datetime
    prompt_versions: dict[str, str] = Field(default_factory=dict)
    model_versions: dict[str, str] = Field(default_factory=dict)

    call_type: CallType
    call_type_confidence: float = Field(ge=0.0, le=1.0)

    topics: list[Topic] = Field(default_factory=list)

    speaker_sentiment: list[SpeakerSentiment] = Field(default_factory=list)
    entity_sentiment: list[EntitySentiment] = Field(default_factory=list)
    sentiment_arc: SentimentArc | None = None

    entities: list[Entity] = Field(default_factory=list)
    risk_signals: list[RiskSignal] = Field(default_factory=list)
    structured_action_items: list[StructuredActionItem] = Field(default_factory=list)
