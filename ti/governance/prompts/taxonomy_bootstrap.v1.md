# Topic Taxonomy Bootstrap — v1

Used by `ti/enrich/taxonomy.py` once at the start of the run to derive a
2-level taxonomy (Theme → Subtopic) from a sample of call summaries.

---

You are designing a topic taxonomy for a B2B SaaS company's internal
"call intelligence" tool. The company sells three products:

- **Protect** — backup / data protection
- **Detect** — security / threat detection
- **Comply** — compliance / audit

Stakeholders who'll consume this taxonomy: Support Leads, Customer Success
Leads, Product Managers, Engineering Leads. They each want to filter,
search, and trend.

Below are {n_samples} call summaries sampled across support, external,
and internal calls. Read them all, then propose a 2-level taxonomy
(Theme → Subtopic) that is:

1. **Actionable**: a stakeholder can ask "show me all `Reliability >
   Backup Performance` calls last month" and get useful results.
2. **Named, not numbered**: subtopics should be 1–3 words a human reads
   directly, never `cluster_3`.
3. **Mutually distinct at the subtopic level**: each subtopic should
   have a clear discriminator from its siblings.
4. **Cover the corpus**: every summary should fit at least one
   (Theme, Subtopic) pair without forcing.
5. **Compact**: 4–6 themes, each with 3–6 subtopics.

Return your answer using the `propose_taxonomy` tool.

---

**Sample summaries:**

{samples}
