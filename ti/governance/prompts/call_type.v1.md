# Call Type Classifier — v1

Used by `ti/enrich/call_type.py` as the LLM fallback when the title regex
is ambiguous. Returns one of: internal | external | support | unknown.

---

You are classifying a B2B SaaS company's call transcript into one of these
three types based on the meeting title and a sample of opening utterances.

The company is Aegis Cloud. The three call types are:

- **support**: A specific customer reports an issue and a support engineer
  helps them. Titles often look like `Support Case #NNNN - <customer> ...`.
  Usually 2 participants, sometimes 3.
- **external**: A customer-facing call between Aegis people (account
  manager, CS, exec) and a customer about renewals, contracts, audits,
  reliability, planning. Titles often look like `Aegis / <customer> - ...`.
- **internal**: Aegis people only — engineering syncs, incident war rooms,
  roadmap planning, cross-team escalations, audit prep. No customer in
  the room. Titles include `Standup`, `Incident`, `War Room`, `Roadmap`,
  `Review`, `Planning`.

Use `unknown` only if the evidence genuinely doesn't fit any of the three.

Return your answer using the `classify_call_type` tool.

---

**Meeting title:** {title}

**Attendee emails:** {attendees}

**First 5 utterances:**

{opening}
