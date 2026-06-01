"""Phase 2: enrich every transcript.

Per transcript: call_type → topics → entities → risk_signals → sentiment.
Corpus-level: bootstrap taxonomy (once at start); build customer alias map
(once at end) → re-normalize per-transcript entity names.

Idempotent: an already-enriched meeting_id is skipped unless --force.
Smoke-test friendly: --limit N runs on the first N transcripts only.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from ti.config import settings
from ti.enrich import (
    call_type as ct_mod,
    customer_normalize as norm_mod,
    entity_extractor,
    risk_signals,
    sentiment as sent_mod,
    taxonomy as tax_mod,
    topic_classifier,
)
from ti.schema import (
    EnrichmentResult,
    Entity,
    StructuredActionItem,
    TranscriptDoc,
)


_ACTION_ITEM_RE = re.compile(r"^\s*([\w\s.\-']+?):\s+(.+)$")


def parse_action_items(pretagged: list[str]) -> list[StructuredActionItem]:
    """Cheap deterministic parse: '<Owner>: <Description>' → struct."""
    out: list[StructuredActionItem] = []
    for raw in pretagged:
        m = _ACTION_ITEM_RE.match(raw)
        if m:
            out.append(
                StructuredActionItem(
                    owner=m.group(1).strip(),
                    description=m.group(2).strip(),
                )
            )
        else:
            out.append(StructuredActionItem(owner="(unknown)", description=raw.strip()))
    return out


def load_processed() -> list[TranscriptDoc]:
    path = settings.data_processed / "transcripts.jsonl"
    if not path.exists():
        print(f"❌ {path} not found. Run `make ingest` first.")
        sys.exit(1)
    return [
        TranscriptDoc.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def enriched_path(meeting_id: str) -> Path:
    return settings.data_enriched / f"{meeting_id}.json"


def enrich_one(
    doc: TranscriptDoc,
    taxonomy: tax_mod.Taxonomy,
) -> EnrichmentResult:
    """Run all enrichers for one transcript. Returns the EnrichmentResult."""
    # 1. call_type (rule first, Haiku fallback)
    ct, ct_conf = ct_mod.classify_call_type(doc)

    # 2. topics (Sonnet, multi-label, taxonomy-bounded)
    topics = topic_classifier.classify_topics(doc, taxonomy, ct)

    # 3. entities (Sonnet, raw mentions — aliases reconciled in pass 2)
    entities = entity_extractor.extract_entities(doc)

    # 4. risk signals (Sonnet, citation-enforced)
    signals = risk_signals.extract_risk_signals(doc)

    # 5. sentiment (deterministic, no LLM call)
    arc, speaker_sent, entity_sent = sent_mod.compute_sentiment(doc, entities)

    # 6. action items (deterministic regex)
    action_items = parse_action_items(doc.pre_tagged.action_items)

    return EnrichmentResult(
        meeting_id=doc.meeting_id,
        enriched_at=datetime.now(timezone.utc),
        prompt_versions={
            "call_type": "v1",
            "topic_classify": "v1",
            "entity_extract": "v1",
            "risk_signals": "v1",
        },
        model_versions={
            "screen": settings.model_screen,
            "classify": settings.model_classify,
        },
        call_type=ct,
        call_type_confidence=ct_conf,
        topics=topics,
        speaker_sentiment=speaker_sent,
        entity_sentiment=entity_sent,
        sentiment_arc=arc,
        entities=entities,
        risk_signals=signals,
        structured_action_items=action_items,
    )


def write_enriched(result: EnrichmentResult) -> None:
    p = enriched_path(result.meeting_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(result.model_dump_json(indent=2), encoding="utf-8")


def apply_alias_normalization(alias_map: norm_mod.AliasMap, docs: list[TranscriptDoc]) -> int:
    """Second pass: rewrite customer entity names in enriched files."""
    updated = 0
    for doc in docs:
        p = enriched_path(doc.meeting_id)
        if not p.exists():
            continue
        result = EnrichmentResult.model_validate_json(p.read_text())
        changed = False
        for ent in result.entities:
            if ent.kind == "customer":
                canonical = alias_map.canonical_for(ent.name)
                if canonical != ent.name:
                    ent.aliases = sorted(set([ent.name, *ent.aliases]))
                    ent.name = canonical
                    changed = True
        # Re-compute entity sentiment so it indexes against canonical names.
        if changed:
            _, _, ent_sent = sent_mod.compute_sentiment(doc, result.entities)
            result.entity_sentiment = ent_sent
            write_enriched(result)
            updated += 1
    return updated


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase 2 enrichment runner.")
    ap.add_argument("--limit", type=int, default=None, help="Smoke-test on first N transcripts.")
    ap.add_argument("--force", action="store_true", help="Re-enrich even if file exists.")
    ap.add_argument(
        "--skip-taxonomy",
        action="store_true",
        help="Reuse existing taxonomy without re-bootstrapping.",
    )
    ap.add_argument(
        "--skip-aliases",
        action="store_true",
        help="Skip the corpus-level customer alias normalization pass.",
    )
    args = ap.parse_args()

    all_docs = load_processed()
    docs = all_docs[: args.limit] if args.limit else all_docs
    print(f"Loaded {len(all_docs)} canonical transcripts; enriching {len(docs)}.")

    # --- Corpus-level: bootstrap taxonomy ---
    # Always sample from the full corpus — taxonomy quality depends on
    # coverage, not on which subset we're enriching this run.
    if args.skip_taxonomy and tax_mod.taxonomy_path().exists():
        taxonomy = tax_mod.load()
        print(f"Loaded existing taxonomy: {len(taxonomy.themes)} themes.")
    else:
        summaries = [
            {"title": d.meeting.title, "summary": d.pre_tagged.summary}
            for d in all_docs
        ]
        print(f"Bootstrapping taxonomy from {len(all_docs)} summaries (1 Opus call)...")
        taxonomy = tax_mod.bootstrap_taxonomy(summaries)
        tax_mod.save(taxonomy)
        print(
            f"  → {len(taxonomy.themes)} themes, "
            f"{sum(len(t.subtopics) for t in taxonomy.themes)} subtopics"
        )

    # --- Per-transcript enrichment ---
    ok, skipped, failed = 0, 0, []
    for i, doc in enumerate(docs, 1):
        if not args.force and enriched_path(doc.meeting_id).exists():
            skipped += 1
            continue
        try:
            print(f"[{i:3d}/{len(docs)}] {doc.meeting_id} — {doc.meeting.title[:60]}")
            result = enrich_one(doc, taxonomy)
            write_enriched(result)
            ok += 1
        except Exception as e:
            failed.append((doc.meeting_id, str(e)))
            print(f"     ❌ FAILED: {type(e).__name__}: {e}")

    print(f"\nEnriched: {ok} new, {skipped} skipped (already enriched), {len(failed)} failed.")
    if failed:
        for mid, err in failed[:5]:
            print(f"  - {mid}: {err}")
        if len(failed) > 5:
            print(f"  (+{len(failed) - 5} more)")

    # --- Corpus-level: customer alias map ---
    if args.skip_aliases:
        print("Skipping customer alias normalization (--skip-aliases).")
        return 0 if not failed else 1

    print("\nBuilding customer alias map (1 Opus call)...")
    all_customer_entities: list[tuple[str, list[str], int]] = []
    for doc in docs:
        p = enriched_path(doc.meeting_id)
        if not p.exists():
            continue
        result = EnrichmentResult.model_validate_json(p.read_text())
        for ent in result.entities:
            if ent.kind == "customer":
                all_customer_entities.append((ent.name, ent.aliases, ent.mention_count))

    alias_map = norm_mod.build_alias_map(all_customer_entities)
    norm_mod.save(alias_map)
    print(f"  → {len(alias_map.clusters)} canonical customers from {len(all_customer_entities)} raw mentions")

    print("Applying alias normalization to enriched files...")
    updated = apply_alias_normalization(alias_map, docs)
    print(f"  → {updated} enriched files updated with canonical customer names")

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
