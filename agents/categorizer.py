"""
Hybrid categorization pipeline: cluster → name → classify.

Design choice: Pure LLM classification hallucinates categories; pure
clustering gives unnamed clusters. Hybrid grounds the taxonomy in real
data while giving categories semantic names. See TRADEOFFS.md §1.
"""
from typing import Any
import pandas as pd


def cluster_transcripts(transcripts: list[dict]) -> pd.DataFrame:
    """Step 1: Embed summaries, run HDBSCAN to find natural clusters.

    Returns DataFrame with [transcript_id, cluster_id, embedding].
    """
    pass


def name_clusters(clustered_df: pd.DataFrame) -> dict[int, dict]:
    """Step 2: For each cluster, ask Sonnet for a 2-3 word name + definition.

    Returns mapping of cluster_id -> {name, definition}.
    """
    pass


def classify(transcripts: list[dict], taxonomy: dict) -> pd.DataFrame:
    """Step 3: For each transcript, use Haiku to assign category + confidence.

    Returns DataFrame with [transcript_id, category, confidence, reasoning].
    """
    pass
