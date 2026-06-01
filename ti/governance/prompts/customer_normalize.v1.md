# Customer Name Normalizer — v1

Used by `ti/enrich/customer_normalize.py`. Reconciles surface-form
mentions of customer names into canonical aliases — plan §1 Failure
Mode #1: "Graph quality ≤ entity-resolution quality."

---

You are reconciling customer name mentions from a B2B SaaS company's
call transcripts. Multiple surface forms may refer to the same customer
("Quantum Edge", "Quantum Edge Capital", "QE Capital", "QE"). Your job
is to group them.

Rules:
- Pick the **most complete reasonable form** as the canonical name
  (usually the longest plausible one — "Quantum Edge Capital" over "QE").
- Each cluster's `aliases` list should include every observed surface
  form (including the canonical one).
- Only group together when you're confident they refer to the same
  customer. If unsure, keep them separate.
- Do NOT invent customers that weren't in the input list.

Return your answer using the `normalize_customers` tool.

---

**Observed customer mentions (each with its mention count):**

{mentions}
