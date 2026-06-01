"""Customer Journey Graph + Trust Trajectory Score — the headline insight.

Plan §1 Failure Mode #3: the score is ALWAYS published with its
components and evidence. Never lead with the number alone.

Trust Trajectory Score = weighted blend of:
  - sentiment_slope         (over the customer's chronological meetings)
  - action_closure_rate     (action items closed in later meetings)
  - escalation_count        (inverted)
  - churn_signal_density    (signals per meeting; inverted)

All four components are returned alongside the score so the consumer
(deck slide, agent, notebook) can show *why*.
"""
from __future__ import annotations

from datetime import datetime
from statistics import mean
from typing import Any

from ti.schema import (
    Citation,
    CustomerJourney,
    CustomerJourneyNode,
    TrustTrajectoryComponents,
)
from ti.store import duckdb_store


def _meetings_for(customer: str) -> list[dict[str, Any]]:
    return duckdb_store.customer_journey_rows(customer)


def _action_closure_rate(customer_meeting_ids: list[str]) -> float:
    """Crude proxy: fraction of customer-meeting action items whose
    description fuzzy-matches an utterance in a later same-customer meeting.

    A simple heuristic — full implementation lives in `action_lineage.py`.
    Here we just need a single rate for the score.
    """
    if not customer_meeting_ids:
        return 0.0
    with duckdb_store.connect() as con:
        # All action items raised for this customer's meetings.
        items = con.execute(
            f"""SELECT meeting_id, description FROM action_items
                WHERE meeting_id IN ({','.join(['?'] * len(customer_meeting_ids))})""",
            customer_meeting_ids,
        ).fetchall()
    if not items:
        return 0.0
    closed = 0
    with duckdb_store.connect() as con:
        for src_meeting, desc in items:
            # First 5 meaningful words of description as a fingerprint.
            tokens = [w for w in desc.split() if len(w) > 4][:3]
            if not tokens:
                continue
            needle = " ".join(tokens).lower()
            row = con.execute(
                f"""SELECT 1 FROM utterances
                    WHERE meeting_id IN ({','.join(['?'] * len(customer_meeting_ids))})
                      AND meeting_id <> ?
                      AND lower(text) LIKE ?
                    LIMIT 1""",
                [*customer_meeting_ids, src_meeting, f"%{needle}%"],
            ).fetchone()
            if row:
                closed += 1
    return closed / len(items) if items else 0.0


def _escalation_and_signal_density(customer_meeting_ids: list[str]) -> tuple[int, float]:
    if not customer_meeting_ids:
        return 0, 0.0
    with duckdb_store.connect() as con:
        n_escalation = con.execute(
            f"""SELECT COUNT(*) FROM risk_signals
                WHERE kind = 'escalation'
                  AND meeting_id IN ({','.join(['?'] * len(customer_meeting_ids))})""",
            customer_meeting_ids,
        ).fetchone()[0]
        n_signals = con.execute(
            f"""SELECT COUNT(*) FROM risk_signals
                WHERE meeting_id IN ({','.join(['?'] * len(customer_meeting_ids))})""",
            customer_meeting_ids,
        ).fetchone()[0]
    density = n_signals / len(customer_meeting_ids)
    return int(n_escalation), density


def _normalize(value: float, lo: float, hi: float) -> float:
    """Clamp to 0..1 over [lo, hi]."""
    if hi == lo:
        return 0.5
    return max(0.0, min(1.0, (value - lo) / (hi - lo)))


def trust_trajectory_score(components: TrustTrajectoryComponents) -> float:
    """0..1, higher = healthier. Weights chosen so each component pulls ~equally."""
    # Sentiment slope range: -1..+1 → normalize to 0..1 (positive better)
    s_slope = _normalize(components.sentiment_slope, -0.5, 0.5)
    # Closure rate is already 0..1, higher better
    s_close = components.action_closure_rate
    # Escalations: 0 is best, 5+ is worst
    s_esc = 1.0 - _normalize(components.escalation_count, 0, 5)
    # Churn signal density: 0 is best, 3+ signals/meeting is worst
    s_chs = 1.0 - _normalize(components.churn_signal_density, 0, 3)
    return round(0.25 * s_slope + 0.25 * s_close + 0.25 * s_esc + 0.25 * s_chs, 3)


def _churn_density(customer_meeting_ids: list[str]) -> float:
    if not customer_meeting_ids:
        return 0.0
    with duckdb_store.connect() as con:
        n = con.execute(
            f"""SELECT COUNT(*) FROM risk_signals
                WHERE kind = 'churn'
                  AND meeting_id IN ({','.join(['?'] * len(customer_meeting_ids))})""",
            customer_meeting_ids,
        ).fetchone()[0]
    return n / len(customer_meeting_ids)


def build_customer_journey(customer: str) -> CustomerJourney | None:
    meetings = _meetings_for(customer)
    if not meetings:
        return None

    mids = [m["meeting_id"] for m in meetings]

    nodes = [
        CustomerJourneyNode(
            meeting_id=m["meeting_id"],
            call_type=m["call_type"],
            date=datetime.fromisoformat(m["date"]) if m["date"] else datetime.min,
            title=m["title"],
            sentiment_score=m["sentiment_score"] or 0.0,
            arc_slope=m["arc_slope"],
            risk_signal_count=m["risk_signal_count"],
        )
        for m in meetings
    ]

    # Sentiment slope: simple regression of pre-tagged scores against time order.
    scores = [n.sentiment_score for n in nodes]
    slope = 0.0
    if len(scores) >= 2:
        x_mean = (len(scores) - 1) / 2
        y_mean = mean(scores)
        num = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(scores))
        den = sum((i - x_mean) ** 2 for i in range(len(scores)))
        # Pre-tagged scores are 1..5, so scale roughly to per-step delta.
        slope = (num / den) if den else 0.0

    closure = _action_closure_rate(mids)
    n_esc, density = _escalation_and_signal_density(mids)
    churn_density = _churn_density(mids)

    components = TrustTrajectoryComponents(
        sentiment_slope=slope,
        action_closure_rate=closure,
        escalation_count=n_esc,
        churn_signal_density=churn_density,
    )
    score = trust_trajectory_score(components)

    # Evidence: top risk signals as citations.
    with duckdb_store.connect() as con:
        evid_rows = con.execute(
            f"""SELECT meeting_id, source_utterance_index, driver
                FROM risk_signals
                WHERE meeting_id IN ({','.join(['?'] * len(mids))})
                  AND severity IN ('high', 'medium')
                ORDER BY CASE severity WHEN 'high' THEN 0 ELSE 1 END
                LIMIT 5""",
            mids,
        ).fetchall()
    evidence = [
        Citation(meeting_id=r[0], utterance_index=r[1], quote=r[2][:120])
        for r in evid_rows
    ]

    return CustomerJourney(
        customer_name=customer,
        trajectory_score=score,
        components=components,
        nodes=nodes,
        evidence=evidence,
    )


def rank_customers_by_risk(top_n: int = 10) -> list[CustomerJourney]:
    """Build journeys for all customers, return the lowest trajectory scores."""
    with duckdb_store.connect() as con:
        rows = con.execute(
            """SELECT name, COUNT(DISTINCT meeting_id) AS n
               FROM entities
               WHERE kind = 'customer'
               GROUP BY name
               HAVING n >= 2
               ORDER BY n DESC"""
        ).fetchall()
    journeys = []
    for name, _ in rows:
        j = build_customer_journey(name)
        if j is not None:
            journeys.append(j)
    journeys.sort(key=lambda j: j.trajectory_score)
    return journeys[:top_n]
