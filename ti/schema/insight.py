"""Stakeholder-facing insight types.

These are what agents synthesize and what the UI / deck render.
Every insight carries citations so the 'no citation, no claim' rule
(plan §1 Failure Mode #2) is enforced at the type level.
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ti.schema.enrichment import CallType


class Citation(BaseModel):
    """Pointer to a specific utterance in a specific meeting."""
    meeting_id: str
    utterance_index: int
    quote: str | None = None        # optional verbatim for display


class CustomerJourneyNode(BaseModel):
    """One interaction with a customer on the timeline."""
    meeting_id: str
    call_type: CallType
    date: datetime
    title: str
    sentiment_score: float          # pre-tagged 1..5 (kept for display)
    arc_slope: float | None = None
    risk_signal_count: int = 0


class TrustTrajectoryComponents(BaseModel):
    """The factors that produce a Trust Trajectory Score.

    Score is published WITH its components per plan §1 Failure Mode #3.
    Never publish the score alone.
    """
    sentiment_slope: float          # over the customer's timeline
    action_closure_rate: float      # 0..1
    escalation_count: int
    churn_signal_density: float     # signals per meeting


class CustomerJourney(BaseModel):
    """The headline insight: a customer's full cross-call narrative."""
    customer_name: str
    trajectory_score: float = Field(ge=0.0, le=1.0)
    components: TrustTrajectoryComponents
    nodes: list[CustomerJourneyNode] = Field(default_factory=list)
    evidence: list[Citation] = Field(default_factory=list)


ActionItemStatus = Literal["open", "closed", "unknown"]


class ActionLineageRecord(BaseModel):
    """One action item tracked across meetings."""
    owner: str
    description: str
    source_meeting_id: str
    source_utterance_index: int | None = None
    status: ActionItemStatus
    closed_in_meeting_id: str | None = None
    closure_citation: Citation | None = None


class OwnerLineageSummary(BaseModel):
    """Per-owner action-item closure stats."""
    owner: str
    total_items: int
    closed_items: int
    closure_rate: float = Field(ge=0.0, le=1.0)
    open_items: list[ActionLineageRecord] = Field(default_factory=list)


class Insight(BaseModel):
    """Base type for any synthesized, citation-backed insight.

    Anything an agent emits to a stakeholder uses this shape so the
    audit log can record provenance (prompt + model + citations).
    """
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    text: str
    citations: list[Citation] = Field(min_length=1)   # at least one required
    confidence: float = Field(ge=0.0, le=1.0)
    model_used: str
    prompt_version: str
    produced_at: datetime
