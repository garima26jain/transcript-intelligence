"""
Transcript loader: reads raw and synthetic transcripts into a unified schema.

Design choice: A single loader normalises both real and synthetic data into
one dict schema early in the pipeline so all downstream agents see the same
interface regardless of file format or source. See data_card.md.
"""
from pathlib import Path


def load_all(data_dir: Path | None = None) -> list[dict]:
    """Load all transcripts (real + synthetic) from data/raw/ and data/synthetic/.

    Args:
        data_dir: Override default data directory root (defaults to repo data/).

    Returns:
        List of transcript dicts with unified schema.
    """
    pass


def load_one(path: Path) -> dict:
    """Load and parse a single transcript file into the unified schema.

    Args:
        path: Absolute or relative path to a transcript file.

    Returns:
        Single transcript dict.
    """
    pass
