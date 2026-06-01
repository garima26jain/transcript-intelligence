"""Phase 1: normalize raw transcripts → data/processed/transcripts.jsonl.

One line per transcript. Run via `make ingest` or `python -m scripts.run_ingest`.
"""
from __future__ import annotations

import sys

from ti.config import settings
from ti.ingest.canonicalize import CanonicalizationError, to_transcript_doc
from ti.ingest.loader import (
    TranscriptFolderError,
    iter_transcript_folders,
    load_raw,
)


def main() -> int:
    raw_root = settings.data_raw
    out_dir = settings.data_processed
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "transcripts.jsonl"

    folders = iter_transcript_folders(raw_root)
    print(f"Found {len(folders)} transcript folders under {raw_root}")

    ok = 0
    failed: list[tuple[str, str]] = []
    durations: list[float] = []
    utterance_counts: list[int] = []

    with out_path.open("w", encoding="utf-8") as f:
        for folder in folders:
            try:
                raw = load_raw(folder)
                doc = to_transcript_doc(raw)
            except (TranscriptFolderError, CanonicalizationError) as e:
                failed.append((folder.name, str(e)))
                continue

            f.write(doc.model_dump_json() + "\n")
            ok += 1
            durations.append(doc.meeting.duration_min)
            utterance_counts.append(len(doc.utterances))

    print(f"\nProcessed: {ok}/{len(folders)}")
    if failed:
        print(f"Failed:    {len(failed)}")
        for name, err in failed[:5]:
            print(f"  - {name}: {err}")
        if len(failed) > 5:
            print(f"  (+{len(failed) - 5} more)")

    if ok:
        avg_dur = sum(durations) / len(durations)
        avg_utt = sum(utterance_counts) / len(utterance_counts)
        print(
            f"\nStats: avg duration = {avg_dur:.1f} min, "
            f"avg utterances = {avg_utt:.0f}, "
            f"output size = {out_path.stat().st_size:,} bytes"
        )
    print(f"Output: {out_path}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
