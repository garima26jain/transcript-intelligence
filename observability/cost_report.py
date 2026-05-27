"""
Cost analysis from Langfuse traces.

Design choice: Pulling cost data from Langfuse traces (rather than
estimating upfront) gives accurate per-agent, per-run attribution and
enables the tiered routing argument to be backed with real numbers.
See TRADEOFFS.md §8.
"""
import pandas as pd


def generate_report(
    start_date: str | None = None,
    end_date: str | None = None,
    group_by: str = "agent",
) -> pd.DataFrame:
    """Query Langfuse traces and produce a cost breakdown report.

    Args:
        start_date: ISO date string for report start (defaults to earliest trace).
        end_date: ISO date string for report end (defaults to latest trace).
        group_by: Dimension to group costs by: "agent", "model", or "run".

    Returns:
        DataFrame with [group, input_tokens, output_tokens, total_cost_usd, call_count].
    """
    pass
