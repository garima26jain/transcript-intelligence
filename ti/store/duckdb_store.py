"""DuckDB store — SQL-queryable view of the corpus.

Builds a small star-schema-ish DB from `data/processed/transcripts.jsonl`
+ `data/enriched/*.json`. The MCP tools query through this.

We chose DuckDB over Postgres because: (a) zero infra, (b) blazing fast
on a 100-doc corpus, (c) file-based and reproducible, (d) the analytical
query patterns we need (group by call_type, time-series sentiment, joins
across customers + meetings) are exactly what DuckDB is built for.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb

from ti.config import settings
from ti.schema import EnrichmentResult, TranscriptDoc


_DB_PATH = settings.data_enriched / "_corpus.duckdb"

SCHEMA_DDL = """
CREATE TABLE IF NOT EXISTS transcripts (
    meeting_id      VARCHAR PRIMARY KEY,
    title           VARCHAR,
    call_type       VARCHAR,
    call_type_conf  DOUBLE,
    start_time      TIMESTAMP,
    end_time        TIMESTAMP,
    duration_min    DOUBLE,
    attendees       VARCHAR,
    summary         TEXT,
    sentiment_score DOUBLE,
    sentiment_label VARCHAR,
    arc_slope       DOUBLE,
    arc_start       DOUBLE,
    arc_end         DOUBLE
);

CREATE TABLE IF NOT EXISTS utterances (
    meeting_id   VARCHAR,
    utt_index    INTEGER,
    speaker_name VARCHAR,
    text         TEXT,
    sentiment    VARCHAR,
    start_s      DOUBLE,
    PRIMARY KEY (meeting_id, utt_index)
);

CREATE TABLE IF NOT EXISTS topics (
    meeting_id  VARCHAR,
    theme       VARCHAR,
    subtopic    VARCHAR,
    confidence  DOUBLE
);

CREATE TABLE IF NOT EXISTS entities (
    meeting_id     VARCHAR,
    name           VARCHAR,
    kind           VARCHAR,
    mention_count  INTEGER
);

CREATE TABLE IF NOT EXISTS risk_signals (
    meeting_id              VARCHAR,
    kind                    VARCHAR,
    severity                VARCHAR,
    customer                VARCHAR,
    product                 VARCHAR,
    driver                  TEXT,
    source_utterance_index  INTEGER,
    surfaced_by_speaker     VARCHAR
);

CREATE TABLE IF NOT EXISTS action_items (
    meeting_id  VARCHAR,
    owner       VARCHAR,
    description TEXT
);

CREATE TABLE IF NOT EXISTS speaker_sentiment (
    meeting_id      VARCHAR,
    speaker_name    VARCHAR,
    avg_sentiment   DOUBLE,
    utterance_count INTEGER
);

CREATE TABLE IF NOT EXISTS entity_sentiment (
    meeting_id    VARCHAR,
    entity_name   VARCHAR,
    entity_kind   VARCHAR,
    avg_sentiment DOUBLE,
    mention_count INTEGER
);
"""


def db_path() -> Path:
    return _DB_PATH


def connect(read_only: bool = True) -> duckdb.DuckDBPyConnection:
    """Open a connection. Read-only by default for safety."""
    return duckdb.connect(str(_DB_PATH), read_only=read_only)


def build_db() -> Path:
    """Rebuild the DB from processed + enriched JSON. Idempotent (drops + recreates)."""
    if _DB_PATH.exists():
        _DB_PATH.unlink()

    processed = settings.data_processed / "transcripts.jsonl"
    if not processed.exists():
        raise FileNotFoundError(f"Run `make ingest` first: {processed} missing.")

    docs: dict[str, TranscriptDoc] = {}
    for line in processed.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        d = TranscriptDoc.model_validate_json(line)
        docs[d.meeting_id] = d

    con = duckdb.connect(str(_DB_PATH), read_only=False)
    con.execute(SCHEMA_DDL)

    enriched_dir = settings.data_enriched
    n_enriched = 0
    for d in docs.values():
        enriched_path = enriched_dir / f"{d.meeting_id}.json"
        if not enriched_path.exists():
            continue
        r = EnrichmentResult.model_validate_json(enriched_path.read_text())
        n_enriched += 1

        con.execute(
            """INSERT INTO transcripts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            [
                d.meeting_id,
                d.meeting.title,
                r.call_type,
                r.call_type_confidence,
                d.meeting.start_time,
                d.meeting.end_time,
                d.meeting.duration_min,
                "; ".join(d.meeting.attendees),
                d.pre_tagged.summary,
                d.pre_tagged.sentiment_score,
                d.pre_tagged.overall_sentiment,
                r.sentiment_arc.slope if r.sentiment_arc else 0.0,
                r.sentiment_arc.start_value if r.sentiment_arc else 0.0,
                r.sentiment_arc.end_value if r.sentiment_arc else 0.0,
            ],
        )

        for u in d.utterances:
            con.execute(
                "INSERT INTO utterances VALUES (?,?,?,?,?,?)",
                [d.meeting_id, u.index, u.speaker_name, u.text, u.sentiment, u.start_s],
            )

        for t in r.topics:
            con.execute(
                "INSERT INTO topics VALUES (?,?,?,?)",
                [d.meeting_id, t.theme, t.subtopic, t.confidence],
            )

        for e in r.entities:
            con.execute(
                "INSERT INTO entities VALUES (?,?,?,?)",
                [d.meeting_id, e.name, e.kind, e.mention_count],
            )

        for rs in r.risk_signals:
            con.execute(
                "INSERT INTO risk_signals VALUES (?,?,?,?,?,?,?,?)",
                [
                    d.meeting_id, rs.kind, rs.severity, rs.customer, rs.product,
                    rs.driver, rs.source_utterance_index, rs.surfaced_by_speaker,
                ],
            )

        for a in r.structured_action_items:
            con.execute(
                "INSERT INTO action_items VALUES (?,?,?)",
                [d.meeting_id, a.owner, a.description],
            )

        for sp in r.speaker_sentiment:
            con.execute(
                "INSERT INTO speaker_sentiment VALUES (?,?,?,?)",
                [d.meeting_id, sp.speaker_name, sp.avg_sentiment, sp.utterance_count],
            )

        for es in r.entity_sentiment:
            con.execute(
                "INSERT INTO entity_sentiment VALUES (?,?,?,?,?)",
                [d.meeting_id, es.entity_name, es.entity_kind, es.avg_sentiment, es.mention_count],
            )

    print(f"Built {_DB_PATH.name}: {len(docs)} transcripts indexed, {n_enriched} enriched.")
    con.close()
    return _DB_PATH


# ---- Query helpers used by MCP tools ----

def search(
    *,
    query: str | None = None,
    call_type: str | None = None,
    customer: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Free-text search over title/summary + structured filters."""
    where: list[str] = []
    params: list[Any] = []
    if query:
        where.append("(lower(t.title) LIKE ? OR lower(t.summary) LIKE ?)")
        params.extend([f"%{query.lower()}%", f"%{query.lower()}%"])
    if call_type:
        where.append("t.call_type = ?")
        params.append(call_type)
    if customer:
        where.append("EXISTS (SELECT 1 FROM entities e WHERE e.meeting_id = t.meeting_id AND e.kind = 'customer' AND lower(e.name) LIKE ?)")
        params.append(f"%{customer.lower()}%")

    sql = "SELECT meeting_id, title, call_type, start_time, sentiment_score FROM transcripts t"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY start_time DESC LIMIT ?"
    params.append(limit)

    with connect() as con:
        rows = con.execute(sql, params).fetchall()
    return [
        {
            "meeting_id": r[0],
            "title": r[1],
            "call_type": r[2],
            "date": r[3].isoformat() if r[3] else None,
            "sentiment_score": r[4],
        }
        for r in rows
    ]


def customer_journey_rows(customer: str) -> list[dict[str, Any]]:
    """Chronological list of every meeting that mentions a customer."""
    sql = """
        SELECT DISTINCT t.meeting_id, t.title, t.call_type, t.start_time,
               t.sentiment_score, t.arc_slope,
               (SELECT COUNT(*) FROM risk_signals rs WHERE rs.meeting_id = t.meeting_id) AS risk_count
        FROM transcripts t
        JOIN entities e ON e.meeting_id = t.meeting_id
        WHERE e.kind = 'customer' AND lower(e.name) = lower(?)
        ORDER BY t.start_time ASC
    """
    with connect() as con:
        rows = con.execute(sql, [customer]).fetchall()
    return [
        {
            "meeting_id": r[0],
            "title": r[1],
            "call_type": r[2],
            "date": r[3].isoformat() if r[3] else None,
            "sentiment_score": r[4],
            "arc_slope": r[5],
            "risk_signal_count": r[6],
        }
        for r in rows
    ]


def action_items_by_owner(owner: str, limit: int = 50) -> list[dict[str, Any]]:
    """Per-owner action items, joined with meeting context."""
    sql = """
        SELECT a.meeting_id, t.title, t.start_time, a.description
        FROM action_items a
        JOIN transcripts t ON t.meeting_id = a.meeting_id
        WHERE lower(a.owner) LIKE ?
        ORDER BY t.start_time DESC
        LIMIT ?
    """
    with connect() as con:
        rows = con.execute(sql, [f"%{owner.lower()}%", limit]).fetchall()
    return [
        {
            "meeting_id": r[0],
            "meeting_title": r[1],
            "date": r[2].isoformat() if r[2] else None,
            "description": r[3],
        }
        for r in rows
    ]


def sentiment_timeline_rows(entity_name: str) -> list[dict[str, Any]]:
    """Per-meeting sentiment for a named customer/product, chronological."""
    sql = """
        SELECT t.meeting_id, t.title, t.start_time, t.call_type,
               es.avg_sentiment, es.mention_count, t.sentiment_score
        FROM entity_sentiment es
        JOIN transcripts t ON t.meeting_id = es.meeting_id
        WHERE lower(es.entity_name) = lower(?)
        ORDER BY t.start_time ASC
    """
    with connect() as con:
        rows = con.execute(sql, [entity_name]).fetchall()
    return [
        {
            "meeting_id": r[0],
            "title": r[1],
            "date": r[2].isoformat() if r[2] else None,
            "call_type": r[3],
            "entity_avg_sentiment": r[4],
            "mention_count": r[5],
            "meeting_sentiment_score": r[6],
        }
        for r in rows
    ]
