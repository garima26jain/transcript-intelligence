"""Multi-label classify one transcript against the frozen taxonomy."""
from __future__ import annotations

from ti.config import settings
from ti.enrich._client import call_with_tool
from ti.enrich._prompts import load as load_prompt
from ti.enrich.taxonomy import Taxonomy
from ti.schema import TranscriptDoc
from ti.schema.enrichment import CallType, Topic


def classify_topics(
    doc: TranscriptDoc,
    taxonomy: Taxonomy,
    call_type: CallType,
) -> list[Topic]:
    valid_pairs = set(taxonomy.pairs())
    valid_themes = sorted({t for t, _ in valid_pairs})

    prompt = load_prompt("topic_classify", "v1").format(
        taxonomy=taxonomy.as_prompt_block(),
        title=doc.meeting.title,
        call_type=call_type,
        summary=doc.pre_tagged.summary,
        pretagged_topics=", ".join(doc.pre_tagged.topics) or "(none)",
    )
    out = call_with_tool(
        agent="topic_classifier",
        prompt_name="topic_classify",
        prompt_version="v1",
        prompt_text=prompt,
        model=settings.model_classify,
        tool_name="classify_topics",
        tool_description="Multi-label classify into the provided taxonomy.",
        tool_schema={
            "type": "object",
            "properties": {
                "topics": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "theme": {"type": "string", "enum": valid_themes},
                            "subtopic": {"type": "string"},
                            "confidence": {
                                "type": "number",
                                "minimum": 0.0,
                                "maximum": 1.0,
                            },
                        },
                        "required": ["theme", "subtopic", "confidence"],
                    },
                },
            },
            "required": ["topics"],
        },
        inputs_for_audit={"meeting_id": doc.meeting_id},
        max_tokens=1024,
    )

    # Drop any (theme, subtopic) pairs the model invented despite our schema.
    valid_topics: list[Topic] = []
    for t in out["topics"]:
        if (t["theme"], t["subtopic"]) in valid_pairs:
            valid_topics.append(Topic(**t))
    return valid_topics
