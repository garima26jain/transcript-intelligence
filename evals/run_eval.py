"""
Evaluation runner: F1, bootstrap confidence intervals, baseline comparison.

Design choice: At N=15, standard F1 confidence intervals are unreliable.
Bootstrap CI (n=10 000 resamples) gives honest uncertainty estimates.
A majority-class baseline is included so lift is meaningful.
See evals/results.md and TRADEOFFS.md §6.
"""
from pathlib import Path
from typing import Any
import pandas as pd


def load_golden_set(path: Path | None = None) -> list[dict]:
    """Load hand-labeled golden examples from evals/golden_set.jsonl.

    Args:
        path: Override default path to golden_set.jsonl.

    Returns:
        List of dicts: [{transcript_id, true_category, notes}].
    """
    pass


def evaluate(
    predictions: pd.DataFrame,
    golden: list[dict],
) -> dict[str, float]:
    """Compare model predictions against the golden set and compute metrics.

    Args:
        predictions: DataFrame with [transcript_id, category, confidence].
        golden: Output of load_golden_set().

    Returns:
        Dict with macro_f1, per_class_f1, accuracy, majority_baseline_f1.
    """
    pass


def bootstrap_ci(
    predictions: pd.DataFrame,
    golden: list[dict],
    n_resamples: int = 10_000,
    confidence: float = 0.95,
) -> dict[str, tuple[float, float]]:
    """Compute bootstrap confidence intervals for each metric.

    Args:
        predictions: DataFrame with [transcript_id, category, confidence].
        golden: Output of load_golden_set().
        n_resamples: Number of bootstrap resamples (default 10 000).
        confidence: Confidence level (default 0.95).

    Returns:
        Dict mapping metric name -> (lower_bound, upper_bound).
    """
    pass


def main() -> None:
    """CLI entry point: load golden set, run eval, print metrics + CI, save results."""
    pass
