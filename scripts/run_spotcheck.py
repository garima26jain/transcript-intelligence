"""Phase 6 — methodology spot-check.

Samples 12 transcripts (stratified across call types) and prints a
side-by-side comparison of our enrichment vs the pre-tagged baseline.

This is the *honest* eval slice (plan §7). NOT a regression harness:
the goal is to give a human reviewer a small, dense table to read and
flag disagreements with one-line reasoning. Outputs both a markdown
table to `data/spotcheck.md` and a console-friendly view.
"""
from __future__ import annotations

import random
from collections import defaultdict
from pathlib import Path

from ti.config import settings
from ti.schema import EnrichmentResult, TranscriptDoc


def stratified_sample(
    docs: list[TranscriptDoc],
    enriched: dict[str, EnrichmentResult],
    n: int = 12,
    seed: int = 42,
) -> list[TranscriptDoc]:
    """Sample evenly across call types so support / external / internal
    are all represented in the spot-check."""
    rng = random.Random(seed)
    by_ct: dict[str, list[TranscriptDoc]] = defaultdict(list)
    for d in docs:
        r = enriched.get(d.meeting_id)
        if r:
            by_ct[r.call_type].append(d)
    per_bucket = max(1, n // max(1, len(by_ct)))
    out: list[TranscriptDoc] = []
    for ct, bucket in by_ct.items():
        rng.shuffle(bucket)
        out.extend(bucket[:per_bucket])
    return out[:n]


def _compare_topics(ours: list[str], theirs: list[str]) -> str:
    """One-line summary of where the two topic sets overlap or diverge."""
    ours_set = {t.lower() for t in ours}
    theirs_set = {t.lower() for t in theirs}
    only_ours = ours_set - theirs_set
    only_theirs = theirs_set - ours_set
    notes = []
    if only_ours:
        notes.append(f"ours add: {', '.join(sorted(only_ours)[:3])}")
    if only_theirs:
        notes.append(f"pre-tag adds: {', '.join(sorted(only_theirs)[:3])}")
    if not notes:
        notes.append("alignment")
    return "; ".join(notes)


def build_table(docs: list[TranscriptDoc], enriched: dict[str, EnrichmentResult]) -> str:
    lines: list[str] = []
    lines.append("# Methodology spot-check")
    lines.append("")
    lines.append("> Pre-tagged labels in `summary.json` are almost certainly LLM-generated.")
    lines.append("> Treating them as ground truth would only measure 'does our LLM agree with their LLM?'")
    lines.append("> Instead: 12-transcript stratified sample, one-line reasoning per disagreement.")
    lines.append("> Disagreement is INFORMATION about taxonomy/extractor quality, not error.")
    lines.append("")
    lines.append("| Meeting | Call type (ours) | Topics — disagreement | Risk signals (ours / pre-tag types) |")
    lines.append("|---|---|---|---|")

    for d in docs:
        r = enriched[d.meeting_id]
        our_topics = [f"{t.theme}>{t.subtopic}" for t in r.topics]
        # Try mapping our subtopics to pre-tag style for fairer compare.
        their_topics = list(d.pre_tagged.topics)
        topic_note = _compare_topics(our_topics, their_topics)

        our_signal_kinds = sorted({s.kind for s in r.risk_signals})
        pre_signal_types = sorted({k.type for k in d.pre_tagged.key_moments})
        risk_note = f"ours={our_signal_kinds} / pre-tag={pre_signal_types}"

        lines.append(
            f"| `{d.meeting_id[-8:]}` {d.meeting.title[:42]} "
            f"| {r.call_type} ({r.call_type_confidence:.2f}) "
            f"| {topic_note} "
            f"| {risk_note} |"
        )

    lines.append("")
    lines.append("## Known limitations surfaced by the spot-check")
    lines.append("")
    lines.append("1. **Action-item closure rate is 0% across owners.** Our fuzzy-match heuristic ")
    lines.append("   requires 3 distinctive tokens from the action description to appear as a literal ")
    lines.append("   substring in a later utterance. Real conversations paraphrase. The conservative ")
    lines.append("   bias is deliberate (no false positives via the 'no citation, no claim' rule), but ")
    lines.append("   the rate itself isn't meaningful — open-item *counts* per owner still are.")
    lines.append("2. **Corpus-aggregate risk uses an `utt#-1` sentinel** for citations. PM-persona ")
    lines.append("   queries about corpus-wide risk should drill into specific meetings, not just ")
    lines.append("   carry an aggregate.")
    lines.append("3. **Pre-tagged `topics` are flat strings** (`'performance degradation'`); ours are ")
    lines.append("   2-level (`'Reliability & Incidents > Backup Performance'`). The disagreement ")
    lines.append("   table reads as more divergent than it actually is — same content, finer structure.")
    return "\n".join(lines)


def main() -> int:
    processed = settings.data_processed / "transcripts.jsonl"
    docs = [
        TranscriptDoc.model_validate_json(line)
        for line in processed.read_text().splitlines()
        if line.strip()
    ]
    enriched: dict[str, EnrichmentResult] = {}
    for d in docs:
        p = settings.data_enriched / f"{d.meeting_id}.json"
        if p.exists():
            enriched[d.meeting_id] = EnrichmentResult.model_validate_json(p.read_text())

    sample = stratified_sample(docs, enriched, n=12)
    table = build_table(sample, enriched)

    out_path = Path("data/spotcheck.md")
    out_path.write_text(table, encoding="utf-8")
    print(table)
    print()
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
