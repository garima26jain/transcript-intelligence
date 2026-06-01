"""Raw file I/O for the 6-file transcript folder structure.

Pure I/O — no schema validation, no field mapping. Field translation
lives in canonicalize.py. Keeping the layers separate makes both testable
and means a malformed JSON file is detected before validation kicks in.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_FILES = (
    "meeting-info.json",
    "summary.json",
    "transcript.json",
    "speakers.json",
    "speaker-meta.json",
    "events.json",
)


class TranscriptFolderError(ValueError):
    """Raised when a folder is missing required files or has invalid JSON."""


def load_raw(folder: Path) -> dict[str, Any]:
    """Read all 6 files from a transcript folder, return as one dict.

    Keys are filenames without the `.json` suffix, with hyphens swapped
    for underscores: `meeting_info`, `summary`, `transcript`, `speakers`,
    `speaker_meta`, `events`.
    """
    if not folder.is_dir():
        raise TranscriptFolderError(f"Not a directory: {folder}")

    missing = [f for f in REQUIRED_FILES if not (folder / f).is_file()]
    if missing:
        raise TranscriptFolderError(
            f"{folder.name}: missing files: {missing}"
        )

    out: dict[str, Any] = {}
    for fname in REQUIRED_FILES:
        path = folder / fname
        key = fname.removesuffix(".json").replace("-", "_")
        try:
            out[key] = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise TranscriptFolderError(
                f"{folder.name}/{fname}: invalid JSON: {e}"
            ) from e
    return out


def iter_transcript_folders(raw_root: Path) -> list[Path]:
    """List transcript subfolders under data/raw, sorted by ULID (chronological).

    Skips hidden files like `.DS_Store` and `.gitkeep`.
    """
    if not raw_root.is_dir():
        raise FileNotFoundError(f"Raw data root missing: {raw_root}")
    folders = [
        p for p in raw_root.iterdir()
        if p.is_dir() and not p.name.startswith(".")
    ]
    return sorted(folders, key=lambda p: p.name)
