"""
Synthetic transcript generator.

Design choice: Generating synthetic data from real call patterns ensures
synthetic transcripts share the same distribution as real ones, avoiding
the common failure mode of "plausible but wrong" synthetic data.
See TRADEOFFS.md §5 and data_card.md.
"""
from typing import Any


def generate_batch(
    real_transcripts: list[dict],
    n: int,
    seed_patterns: list[str] | None = None,
) -> list[dict]:
    """Generate a batch of synthetic transcripts conditioned on real patterns.

    Args:
        real_transcripts: Sample of real transcripts used to infer style/schema.
        n: Number of synthetic transcripts to produce.
        seed_patterns: Optional list of pattern strings to plant deliberately.

    Returns:
        List of synthetic transcript dicts matching the real transcript schema.
    """
    pass


def main() -> None:
    """CLI entry point: load real transcripts, generate synthetic batch, save to data/synthetic/."""
    pass
