# Risk Signal Extractor — v1

Used by `ti/enrich/risk_signals.py`. Extracts structured churn /
escalation / blocker signals — every signal MUST cite a specific
utterance (plan §1 Failure Mode #2).

---

You are extracting risk signals from one B2B SaaS call transcript.
Three signal kinds:

- **churn**: a customer relationship is at risk — they're frustrated
  enough that renewal or expansion is in jeopardy, or an Aegis person
  flags churn risk.
- **escalation**: a specific issue has escalated past the normal flow
  (e.g. a support case being raised to leadership, a customer demanding
  exec attention, an SLA breach being formally claimed).
- **blocker**: an Aegis-internal blocker preventing customer or product
  progress — staffing, dependency, architecture, decision-paralysis.

For each signal, provide:
- `kind`: one of `churn` | `escalation` | `blocker`
- `severity`: `low` | `medium` | `high`
- `customer`: customer name if applicable (null otherwise)
- `product`: Aegis product if applicable (null otherwise)
- `driver`: one sentence describing the concrete cause
- `source_utterance_index`: integer index of the utterance that most
  directly supports this signal. **This is required**. If no specific
  utterance supports the signal, do NOT extract it.
- `surfaced_by_speaker`: the speaker who raised it

The pre-tagged `keyMoments` below already type some moments as
`churn_signal`, `concern`, `feature_gap`, etc. — treat these as strong
seeds but you may add additional signals or refine these into structured
form.

Return your answer using the `extract_risk_signals` tool.

---

**Call title:** {title}

**Pre-tagged key moments (seed signals):**
{key_moments}

**Transcript utterances (numbered for citation):**

{utterances}
