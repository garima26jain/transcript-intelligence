"""Extract customers / products / owners from one transcript.

This is the raw-mentions pass. Reconciliation across surface forms
("Quantum Edge" vs "QE") happens later in customer_normalize.py.
"""
from __future__ import annotations

from ti.config import settings
from ti.enrich._client import call_with_tool
from ti.enrich._prompts import load as load_prompt
from ti.schema import Entity, TranscriptDoc


def _utterances_block(doc: TranscriptDoc, limit: int = 80) -> str:
    """Numbered utterance list, capped so long calls stay in context."""
    return "\n".join(
        f"[{u.index}] {u.speaker_name}: {u.text}"
        for u in doc.utterances[:limit]
    )


def extract_entities(doc: TranscriptDoc) -> list[Entity]:
    prompt = load_prompt("entity_extract", "v1").format(
        title=doc.meeting.title,
        summary=doc.pre_tagged.summary,
        action_items="\n".join(f"- {a}" for a in doc.pre_tagged.action_items)
        or "(none)",
        utterances=_utterances_block(doc),
    )
    out = call_with_tool(
        agent="entity_extractor",
        prompt_name="entity_extract",
        prompt_version="v1",
        prompt_text=prompt,
        model=settings.model_classify,
        tool_name="extract_entities",
        tool_description="Pull customers, products, and action owners.",
        tool_schema={
            "type": "object",
            "properties": {
                "entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "kind": {
                                "type": "string",
                                "enum": ["customer", "product", "owner"],
                            },
                            "aliases": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "mention_count": {"type": "integer", "minimum": 0},
                        },
                        "required": ["name", "kind"],
                    },
                },
            },
            "required": ["entities"],
        },
        inputs_for_audit={"meeting_id": doc.meeting_id},
        max_tokens=1024,
    )

    seen: dict[tuple[str, str], Entity] = {}
    for e in out["entities"]:
        key = (e["kind"], e["name"].lower())
        ent = Entity(
            name=e["name"],
            kind=e["kind"],
            aliases=e.get("aliases", []) or [],
            mention_count=e.get("mention_count", 0) or 0,
        )
        if key in seen:
            # Dedupe — keep the first, fold counts.
            seen[key].mention_count += ent.mention_count
            seen[key].aliases = sorted(set(seen[key].aliases + ent.aliases))
        else:
            seen[key] = ent
    return list(seen.values())
