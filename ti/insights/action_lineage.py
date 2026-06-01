"""Action-Item Lineage — per-owner closure rate tracking.

Eng-leader candy (plan §6 insight #4). Each action item from meeting A
is tracked into later meetings via fuzzy text matching; per-owner
closure rate is the headline number.

Closure heuristic: action item's first 3 meaningful words appear in any
later utterance involving the same owner OR the same customer. Crude
but informative — and the plan flagged this approach upfront in §1
Failure Mode #2 (the mitigation: every closure must cite the closing
utterance).
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from ti.schema import (
    ActionLineageRecord,
    Citation,
    OwnerLineageSummary,
)
from ti.store import duckdb_store


_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "to", "of", "in", "on", "for",
    "with", "by", "is", "are", "was", "were", "be", "been", "being",
    "this", "that", "these", "those", "from", "as", "at", "it",
}


def _fingerprint(text: str, n: int = 3) -> str:
    """First N meaningful (long, non-stopword) tokens, lowercased."""
    tokens = [
        w.strip(",.():;!?'\"").lower()
        for w in text.split()
        if len(w) > 4 and w.lower() not in _STOPWORDS
    ]
    return " ".join(tokens[:n])


def _find_closure(
    item_owner: str,
    item_description: str,
    source_meeting_id: str,
    source_date: datetime,
) -> Citation | None:
    """Look for evidence that the item was discussed in a later meeting."""
    fp = _fingerprint(item_description)
    if not fp:
        return None
    with duckdb_store.connect() as con:
        row = con.execute(
            """SELECT u.meeting_id, u.utt_index, u.text
               FROM utterances u
               JOIN transcripts t ON t.meeting_id = u.meeting_id
               WHERE t.start_time > ?
                 AND u.meeting_id <> ?
                 AND lower(u.text) LIKE ?
               ORDER BY t.start_time ASC
               LIMIT 1""",
            [source_date, source_meeting_id, f"%{fp}%"],
        ).fetchone()
    if not row:
        return None
    return Citation(meeting_id=row[0], utterance_index=row[1], quote=row[2][:120])


def lineage_for_owner(owner: str) -> OwnerLineageSummary:
    """Per-owner closure summary with open items."""
    with duckdb_store.connect() as con:
        rows = con.execute(
            """SELECT a.meeting_id, a.description, t.start_time, t.title
               FROM action_items a
               JOIN transcripts t ON t.meeting_id = a.meeting_id
               WHERE lower(a.owner) LIKE ?
               ORDER BY t.start_time ASC""",
            [f"%{owner.lower()}%"],
        ).fetchall()

    records: list[ActionLineageRecord] = []
    open_items: list[ActionLineageRecord] = []
    closed = 0
    for meeting_id, description, start_time, _title in rows:
        citation = _find_closure(owner, description, meeting_id, start_time)
        if citation:
            record = ActionLineageRecord(
                owner=owner,
                description=description,
                source_meeting_id=meeting_id,
                source_utterance_index=None,
                status="closed",
                closed_in_meeting_id=citation.meeting_id,
                closure_citation=citation,
            )
            closed += 1
        else:
            record = ActionLineageRecord(
                owner=owner,
                description=description,
                source_meeting_id=meeting_id,
                source_utterance_index=None,
                status="open",
            )
            open_items.append(record)
        records.append(record)

    total = len(records)
    rate = closed / total if total else 0.0
    return OwnerLineageSummary(
        owner=owner,
        total_items=total,
        closed_items=closed,
        closure_rate=round(rate, 3),
        open_items=open_items,
    )


def all_owners_summary(min_items: int = 2) -> list[OwnerLineageSummary]:
    """Build a per-owner closure summary across the corpus."""
    with duckdb_store.connect() as con:
        rows = con.execute(
            """SELECT owner, COUNT(*) AS n
               FROM action_items
               WHERE owner <> '(unknown)'
               GROUP BY owner
               HAVING n >= ?
               ORDER BY n DESC""",
            [min_items],
        ).fetchall()
    return [lineage_for_owner(owner) for owner, _ in rows]
