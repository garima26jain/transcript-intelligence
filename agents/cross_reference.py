"""
Cross-call pattern detection agent.

Design choice: Individual call analysis misses systemic issues that only
appear when aggregating across call types, time windows, or customer
segments. This agent surfaces recurring themes not visible per-transcript.
See TRADEOFFS.md §3.
"""
import pandas as pd


def find_cross_call_patterns(
    categorized_df: pd.DataFrame,
    sentiment_df: pd.DataFrame,
    window_days: int = 30,
) -> pd.DataFrame:
    """Identify topics and themes recurring across multiple calls and call types.

    Args:
        categorized_df: Output of agents/categorizer.py classify().
        sentiment_df: Output of agents/sentiment.py summarize_sentiment() aggregated.
        window_days: Lookback window for time-based pattern detection.

    Returns:
        DataFrame with [pattern_id, description, supporting_call_ids,
        frequency, severity_score, first_seen, last_seen].
    """
    pass
