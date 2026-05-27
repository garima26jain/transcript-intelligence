"""
Multi-dimensional sentiment analysis for call transcripts.

Design choice: Vendor sentiment labels collapse nuance (e.g., frustrated
but resolved vs. frustrated and unresolved). Recomputing with structured
LLM output gives per-turn trajectory and separate dimensions.
See TRADEOFFS.md §2 and ADR-005.
"""
import pandas as pd


def extract_sentiment_trajectory(transcript: dict) -> list[dict]:
    """Extract per-turn sentiment across multiple dimensions (frustration, urgency, trust).

    Args:
        transcript: Single transcript dict with turn-by-turn dialogue.

    Returns:
        List of dicts: [{turn_index, speaker, frustration, urgency, trust, valence}].
    """
    pass


def summarize_sentiment(trajectory: list[dict]) -> dict:
    """Collapse a per-turn trajectory into a call-level sentiment summary.

    Args:
        trajectory: Output of extract_sentiment_trajectory().

    Returns:
        Dict with opening_sentiment, closing_sentiment, peak_frustration_turn,
        resolution_indicator, overall_valence.
    """
    pass
