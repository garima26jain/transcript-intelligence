"""Multi-resolution sentiment — purely deterministic.

The raw transcripts already carry per-utterance sentiment labels
(`positive | neutral | negative`). We derive:
  - per-speaker average sentiment
  - per-call sentiment arc (slope + start/end)
  - per-entity sentiment (sentiment when a customer/product is named)

Zero LLM calls. This is what "sentiment as a signal, not a score"
(plan §3 decision 2) actually looks like in code.
"""
from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Iterable

from ti.schema import (
    EntitySentiment,
    SentimentArc,
    SpeakerSentiment,
    TranscriptDoc,
    Utterance,
)
from ti.schema.enrichment import Entity


_SENTIMENT_VALUE = {"negative": -1.0, "neutral": 0.0, "positive": 1.0}


def _to_value(s: str) -> float:
    return _SENTIMENT_VALUE.get(s, 0.0)


def speaker_sentiment(utterances: list[Utterance]) -> list[SpeakerSentiment]:
    """Per-speaker average sentiment within a call."""
    bucket: dict[str, list[float]] = defaultdict(list)
    for u in utterances:
        bucket[u.speaker_name].append(_to_value(u.sentiment))
    return [
        SpeakerSentiment(
            speaker_name=name,
            avg_sentiment=mean(vals),
            utterance_count=len(vals),
        )
        for name, vals in bucket.items()
    ]


def _slope(values: list[float]) -> float:
    """Least-squares slope over utterance index. Robust to length 1–2."""
    n = len(values)
    if n < 2:
        return 0.0
    x_mean = (n - 1) / 2
    y_mean = sum(values) / n
    num = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
    den = sum((i - x_mean) ** 2 for i in range(n))
    return num / den if den else 0.0


def sentiment_arc(utterances: list[Utterance]) -> SentimentArc:
    """Arc trajectory: slope + start/end value (5-utterance windows)."""
    if not utterances:
        return SentimentArc(slope=0.0, start_value=0.0, end_value=0.0)
    values = [_to_value(u.sentiment) for u in utterances]
    window = max(1, min(5, len(values) // 4 or 1))
    start = mean(values[:window])
    end = mean(values[-window:])
    return SentimentArc(
        slope=_slope(values),
        start_value=start,
        end_value=end,
        smoothed=values,
    )


def entity_sentiment(
    utterances: list[Utterance],
    entities: Iterable[Entity],
) -> list[EntitySentiment]:
    """Sentiment of utterances that name a given entity (case-insensitive).

    Used to answer "what's the sentiment when Quantum Edge is mentioned?"
    """
    out: list[EntitySentiment] = []
    for ent in entities:
        # Match any surface form (canonical name + aliases).
        needles = [n.lower() for n in [ent.name, *ent.aliases]]
        vals: list[float] = []
        for u in utterances:
            text_lower = u.text.lower()
            if any(needle in text_lower for needle in needles):
                vals.append(_to_value(u.sentiment))
        if vals:
            out.append(
                EntitySentiment(
                    entity_name=ent.name,
                    entity_kind=ent.kind,
                    avg_sentiment=mean(vals),
                    mention_count=len(vals),
                )
            )
    return out


def compute_sentiment(
    doc: TranscriptDoc,
    entities: Iterable[Entity] = (),
) -> tuple[SentimentArc, list[SpeakerSentiment], list[EntitySentiment]]:
    """One-call helper used by the enrich orchestrator."""
    arc = sentiment_arc(doc.utterances)
    speakers = speaker_sentiment(doc.utterances)
    ents = entity_sentiment(doc.utterances, entities)
    return arc, speakers, ents
