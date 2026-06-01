# Entity Extractor — v1

Used by `ti/enrich/entity_extractor.py`. Pulls out the named entities
that matter for cross-call insights.

---

You are extracting named entities from one B2B SaaS call transcript.
Three entity kinds matter:

- **customer**: external companies Aegis Cloud sells to (e.g. "Quantum
  Edge", "Brightpath Commerce", "Blackridge Investments"). Do NOT
  extract Aegis Cloud itself.
- **product**: Aegis Cloud's own products: "Protect", "Detect", "Comply"
  (and versioned variants like "Comply v2"). Only these.
- **owner**: Aegis-internal people referenced as owners of action items
  or decisions (e.g. "Tyler Washington"). Skip greetings and incidental
  mentions — only include people tied to an action or decision.

For each entity, capture every surface form you saw it as (e.g.
"Quantum Edge", "Quantum Edge Capital", "QE"). These aliases will be
reconciled later — your job is to be comprehensive on what was said.

Return your answer using the `extract_entities` tool.

---

**Call title:** {title}

**Pre-tagged summary:**
{summary}

**Pre-tagged action items (for owner extraction):**
{action_items}

**Transcript utterances (numbered for citation):**

{utterances}
