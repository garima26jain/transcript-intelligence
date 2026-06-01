# Topic Classifier — v1

Used by `ti/enrich/topic_classifier.py`. Multi-label classifies one
transcript into the frozen taxonomy.

---

You are classifying one B2B SaaS call transcript against a fixed
2-level taxonomy. You may select multiple (Theme, Subtopic) pairs — most
calls touch 2–4. Use only pairs from the taxonomy below; do not invent
new ones. If nothing fits well, return an empty list — better than
forcing.

For each pair you select, provide:
- `theme` (exact match from taxonomy)
- `subtopic` (exact match from taxonomy)
- `confidence` (0.0–1.0; how strongly this call belongs in that subtopic)

Return your answer using the `classify_topics` tool.

---

**Taxonomy:**

{taxonomy}

---

**Call title:** {title}

**Call type:** {call_type}

**Pre-tagged summary:**
{summary}

**Pre-tagged topic tags (provided for context; you may agree, refine, or override):**
{pretagged_topics}
