"""Bootstrap a 2-level topic taxonomy from a sample of summaries.

Run once per corpus. The taxonomy is then frozen and reused by
`topic_classifier.py` for every transcript. This is the LLM-derived
taxonomy approach from plan §3 decision 1 — named, actionable themes
that beat `cluster_3` for stakeholder consumption.
"""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from ti.config import settings
from ti.enrich._client import call_with_tool
from ti.enrich._prompts import load as load_prompt


class Subtopic(BaseModel):
    name: str
    description: str


class Theme(BaseModel):
    name: str
    description: str
    subtopics: list[Subtopic]


class Taxonomy(BaseModel):
    version: str = "v1"
    themes: list[Theme] = Field(default_factory=list)

    def pairs(self) -> list[tuple[str, str]]:
        return [(t.name, s.name) for t in self.themes for s in t.subtopics]

    def as_prompt_block(self) -> str:
        out: list[str] = []
        for t in self.themes:
            out.append(f"- **{t.name}**: {t.description}")
            for s in t.subtopics:
                out.append(f"  - `{s.name}` — {s.description}")
        return "\n".join(out)


TAXONOMY_TOOL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "themes": {
            "type": "array",
            "minItems": 4,
            "maxItems": 6,
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "subtopics": {
                        "type": "array",
                        "minItems": 3,
                        "maxItems": 6,
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                            },
                            "required": ["name", "description"],
                        },
                    },
                },
                "required": ["name", "description", "subtopics"],
            },
        },
    },
    "required": ["themes"],
}


def bootstrap_taxonomy(
    summaries: list[dict[str, Any]],
    n_samples: int = 25,
    seed: int = 42,
) -> Taxonomy:
    """One LLM call → frozen taxonomy. Samples stratified randomly."""
    rng = random.Random(seed)
    sample = rng.sample(summaries, min(n_samples, len(summaries)))
    sample_block = "\n\n".join(
        f"**{i+1}. {s['title']}**\n{s['summary']}"
        for i, s in enumerate(sample)
    )
    prompt = load_prompt("taxonomy_bootstrap", "v1").format(
        n_samples=len(sample),
        samples=sample_block,
    )
    out = call_with_tool(
        agent="taxonomy_bootstrap",
        prompt_name="taxonomy_bootstrap",
        prompt_version="v1",
        prompt_text=prompt,
        model=settings.model_synthesize,  # Opus — corpus-shaping decision
        tool_name="propose_taxonomy",
        tool_description="Propose a 2-level taxonomy of themes and subtopics.",
        tool_schema=TAXONOMY_TOOL_SCHEMA,
        inputs_for_audit={"n_samples": len(sample)},
        max_tokens=4096,
    )
    return Taxonomy(themes=[Theme(**t) for t in out["themes"]])


def taxonomy_path() -> Path:
    return settings.data_enriched / "_taxonomy_v1.json"


def save(tax: Taxonomy) -> Path:
    p = taxonomy_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(tax.model_dump_json(indent=2), encoding="utf-8")
    return p


def load() -> Taxonomy:
    p = taxonomy_path()
    if not p.exists():
        raise FileNotFoundError(
            f"Taxonomy not bootstrapped yet: {p}. Run enrich first."
        )
    return Taxonomy.model_validate_json(p.read_text(encoding="utf-8"))
