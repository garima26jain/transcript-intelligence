"""Reconcile customer surface forms across the corpus.

Plan §1 Failure Mode #1: "Quantum Edge" vs "Quantum Edge Capital" vs
"QE" silently break the Customer Journey Graph if not normalized.
This module runs once at the end of enrichment as a corpus-level step.

Strategy: collect every (name + aliases) tuple emitted by
entity_extractor across all 100 transcripts → one Opus call to cluster
into canonical names → write alias map → re-apply to per-transcript
enrichments.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Iterable

from pydantic import BaseModel, Field

from ti.config import settings
from ti.enrich._client import call_with_tool
from ti.enrich._prompts import load as load_prompt


class CustomerCluster(BaseModel):
    canonical: str
    aliases: list[str] = Field(default_factory=list)
    total_mentions: int = 0


class AliasMap(BaseModel):
    version: str = "v1"
    clusters: list[CustomerCluster] = Field(default_factory=list)

    def canonical_for(self, raw: str) -> str:
        """Look up a raw mention → canonical form. Returns input if unmapped."""
        key = raw.strip().lower()
        for c in self.clusters:
            if key == c.canonical.lower():
                return c.canonical
            if any(key == a.lower() for a in c.aliases):
                return c.canonical
        return raw


def alias_map_path() -> Path:
    return settings.data_enriched / "_customer_aliases_v1.json"


def save(am: AliasMap) -> Path:
    p = alias_map_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(am.model_dump_json(indent=2), encoding="utf-8")
    return p


def load() -> AliasMap:
    p = alias_map_path()
    if not p.exists():
        return AliasMap()
    return AliasMap.model_validate_json(p.read_text(encoding="utf-8"))


def _collect_mentions(
    customer_entities: Iterable[tuple[str, list[str], int]],
) -> dict[str, int]:
    """Flatten (name, aliases, count) tuples into mention → total_count."""
    counter: Counter[str] = Counter()
    for name, aliases, count in customer_entities:
        for form in [name, *aliases]:
            form = form.strip()
            if form:
                counter[form] += max(count, 1)
    return dict(counter)


def build_alias_map(
    customer_entities: Iterable[tuple[str, list[str], int]],
) -> AliasMap:
    """One LLM call clusters surface forms into canonical customers."""
    mentions = _collect_mentions(customer_entities)
    if not mentions:
        return AliasMap()

    mentions_block = "\n".join(
        f"- {name!r}: mentioned {count}x"
        for name, count in sorted(mentions.items(), key=lambda x: -x[1])
    )
    prompt = load_prompt("customer_normalize", "v1").format(mentions=mentions_block)

    out = call_with_tool(
        agent="customer_normalize",
        prompt_name="customer_normalize",
        prompt_version="v1",
        prompt_text=prompt,
        model=settings.model_synthesize,  # Opus — corpus-shaping decision
        tool_name="normalize_customers",
        tool_description="Cluster customer surface forms into canonical names.",
        tool_schema={
            "type": "object",
            "properties": {
                "clusters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "canonical": {"type": "string"},
                            "aliases": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["canonical", "aliases"],
                    },
                },
            },
            "required": ["clusters"],
        },
        inputs_for_audit={"unique_mentions": len(mentions)},
        max_tokens=4096,
    )

    clusters: list[CustomerCluster] = []
    if "clusters" not in out:
        # Output got truncated — Opus didn't finish the JSON. Better than
        # crashing: persist an empty map and continue. The spot-check will
        # flag the gap.
        return AliasMap()
    for c in out["clusters"]:
        aliases = list(c.get("aliases", []))
        total = sum(mentions.get(a, 0) for a in aliases) + mentions.get(c["canonical"], 0)
        clusters.append(
            CustomerCluster(
                canonical=c["canonical"],
                aliases=aliases,
                total_mentions=total,
            )
        )
    return AliasMap(clusters=clusters)
