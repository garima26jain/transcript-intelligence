# 7-minute video demo script

Screen recording with narration. No professional production — just a
clean walk through the running system, oriented around the headline
insight (Customer Journey Graph) with the live MCP demo as the closer.

---

## 0:00 – 0:30 · Cold open

**Screen:** the architecture diagram from README §3 (or `slides.md`).

**Narration:**
> 100 transcripts. Three call types — support, external, internal — but the same customers recur across all three. That cross-call narrative is what most candidates miss. Here's what I built to surface it.

---

## 0:30 – 2:00 · The pipeline in action

**Screen:** terminal showing `make enrich` already done; open
`data/enriched/01KQD1270E98A7DFC55ADCF8.json` (the Protect Performance
meeting).

**Walk through, while pointing at the JSON:**

- `call_type: internal` (rule + Haiku fallback)
- `topics: [Reliability > Capacity, Engineering > Tech Debt, Customer Health > Churn Risk]`
  — note how ours surfaces "Quantum Edge churn risk" where the pre-tag missed it.
- `risk_signals[3]` → `kind: churn, severity: high, customer: Quantum Edge,
   source_utterance_index: 38`. **Citation enforced at the schema level.**

> "Every risk signal has to cite a real utterance. No citation, no claim."

---

## 2:00 – 3:30 · The headline insight (Customer Journey Graph)

**Screen:** open `notebooks/03_customer_journey.ipynb`. Execute the
`build_customer_journey("Quantum Edge")` cell.

**Walk through:**

- Chronological view across all 3 call types in one timeline.
- Trust Trajectory Score: 0.32 (declining).
- The four component bars: sentiment slope, closure rate, escalations,
  churn-signal density.
- The evidence list — clickable meeting_id + utterance_index pairs.

> "The score is always published with its components and evidence. Never lead with the number alone — that's failure mode #3 in the plan."

---

## 3:30 – 4:30 · Action-Item Lineage

**Screen:** notebook 04. Render the per-owner closure chart.

**Walk through:**

- 5–7 owners ranked by closure rate.
- Click into the highest open-item owner — show their open items list
  with source meetings.

> "Eng leaders want this. Tyler is at 62% — half his open items are cross-functional. Sofia is at 92% — execution velocity on her side. This is what 'AI for ops' actually means in practice."

---

## 4:30 – 5:30 · Streamlit CS-lead view

**Screen:** `make ui` → browser at `localhost:8501`.

**Walk through:**

- Ranked customer-risk list, lowest trajectory first.
- Click Quantum Edge → drill-down → journey timeline + evidence.

> "One persona view today; same intelligence layer drives the other three. Architecture supports adding them without re-plumbing."

---

## 5:30 – 6:30 · **Live MCP demo (THE CLOSER)**

**Screen:** Claude Code with the MCP server attached.

**Type:**
> "Which customers are at highest churn risk and why? Use the transcript MCP tools."

**Walk through:**

- Watch `search_transcripts`, `get_customer_journey`, and
  `sentiment_timeline` fire in sequence.
- Claude returns a ranked list with meeting_id citations.

> "This is the JD line — *'build custom MCP servers, not just consume APIs.'* Same server plugs into our agents, into Claude Code, into Cursor, into a future Slack bot. The tools are the integration surface."

---

## 6:30 – 7:00 · Methodology + close

**Screen:** notebook 05, the spot-check disagreement table.

**Narration:**
> "I didn't build a full eval harness. Pre-tagged labels are LLM-generated — measuring agreement between two LLMs is weak signal. Instead, 10–15 spot-checks with reasoning per disagreement, and one honest sentence:
> *Pre-tagged labels are a comparison baseline, not ground truth.*"

**End on:** the failure-modes table from the deck.

> "That's how I'd ship this in production — and that's the senior judgment about LLM-system quality."

End.
