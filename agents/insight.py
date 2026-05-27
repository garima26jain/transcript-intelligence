"""
Final insight synthesis agent.

Design choice: Raw categorization and sentiment data requires a synthesis
step to convert signal into stakeholder-ready narrative. Sonnet is used
here (vs. Haiku earlier) because the output is executive-facing and
requires reasoning across multiple data sources. See TRADEOFFS.md §3.
"""
import pandas as pd


def synthesize_insights(
    categorized_df: pd.DataFrame,
    sentiment_df: pd.DataFrame,
    patterns_df: pd.DataFrame,
) -> list[dict]:
    """Synthesize cross-signal insights from categorization, sentiment, and patterns.

    Args:
        categorized_df: Output of agents/categorizer.py classify().
        sentiment_df: Aggregated sentiment summaries per transcript.
        patterns_df: Output of agents/cross_reference.py find_cross_call_patterns().

    Returns:
        List of insight dicts: [{insight_id, title, narrative, evidence_ids,
        stakeholder_lens, priority_score}].
    """
    pass
