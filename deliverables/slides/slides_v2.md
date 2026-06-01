<!--
Marp deck source — Version 2 (human presentation voice).

Render with:
  npx @marp-team/marp-cli@latest slides_v2.md --pdf -o ../slides_v2.pdf

Speaker notes are in HTML comment blocks after each slide.
They're invisible in the PDF but guide the live talk.
-->

---
marp: true
theme: default
paginate: true
header: 'Transcript Intelligence'
footer: 'Garima Jain · Senior Software Engineer'
---

# Transcript Intelligence

### What 100 call transcripts can tell you — if you ask the right questions

*Senior Software Engineer · Take-home assignment*

<!--
SPEAKER: Open warm, not with a bio slide. Just start talking.
"Thanks for having me. I want to show you something I noticed in your data
that I don't think the assignment brief was expecting."
-->

---

## Let me start with what I didn't do

I didn't write a notebook that runs topic clustering, prints a confusion matrix, and calls it done.

That's the expected answer. I want to show you the *right* answer.

> What you have in those 100 transcripts isn't a classification problem.
> It's a customer story problem — and the plot spans all three call types.

<!--
SPEAKER: Pause here. Let it land.
This reframe is the whole thesis — everything else supports it.
-->

---

## Here's what I actually found in the data

The same customers show up across support calls, external business reviews, and internal war rooms.

Take **Brightpath**:

```
  Support call  →  backup issue reported
  CS review     →  reliability "a concern"
  Internal mtg  →  named as potential churn
  Renewal call  →  tension in every exchange
```

That's a churn story. It played out over weeks. Nobody connected the dots.

**That's what this system does.**

<!--
SPEAKER: Walk through each row slowly. Let the audience feel the slow-motion train wreck.
The silence between lines is the point — a human CSM would have caught this.
This system catches it automatically, at scale.
-->

---

## One more thing about the data before I show you the work

The pre-tagged labels — `topics`, `sentimentScore`, `keyMoments` — are almost certainly LLM-generated.

I didn't throw them away. I used them as a **comparison baseline**.

When my system disagrees with a pre-tag, that disagreement is *information*. I treat it that way.

<!--
SPEAKER: This is a subtle point but important.
Say: "I'm not here to grade myself against another model's output. I'm here to show
you where the interesting signal is — and sometimes it's in the disagreements."
-->

---

## The required work: Topic categorization

I built a **two-level taxonomy** — Theme → Subtopic — derived from the corpus itself, not imposed from outside.

| Theme | Example Subtopics |
|---|---|
| Customer Health | Renewal Risk, Escalation Pattern |
| Product Reliability | Backup Failures, Detect Outage (March) |
| Internal Alignment | Cross-team Drag, Ownership Gaps |

**Why not clustering?** Because `cluster_3` is not something a CS leader can act on. `Customer Health > Renewal Risk` is.

All theme names come from the corpus's own language. No invented jargon.

<!--
SPEAKER: "The taxonomy is frozen at v1 — you can swap it, extend it, lock it.
But the names matter. Your team already uses this language. I just made it structural."
-->

---

## The required work: Sentiment — four ways, not one

The pre-tag gives you a score per utterance. That's a start. Here's what I added:

**Per-speaker** — who is actually driving optimism or tension in a room?

**Arc slope** — does the call *resolve*, or does it stay tense throughout? For a support call, that's everything.

**Per-entity** — how does sentiment shift when a specific customer or product gets named?

**Per-customer trajectory** — the same customer's emotional arc, across all their calls.

That last one is where the churn signal lives.

<!--
SPEAKER: Build to the trajectory point. That's the bridge to the journey graph.
"The score is fine. The arc is interesting. The trajectory is the product."
-->

---

## Bonus insight #1 — The Journey Graph

Every customer's interactions, stitched together in time across all three call types.

*Here's Quantum Edge:*

```
  Apr 2  · support   · Slow backup performance (#4521)
  Apr 8  · external  · Reliability discussion — tone shifts
  Apr 15 · internal  · Named as churn risk in eng war room
  Apr 20 · external  · Renewal call — trust already gone
```

A CS leader looking only at the renewal call sees a difficult customer.

A CS leader with this graph sees a customer they could have saved two weeks earlier.

<!--
SPEAKER: Tap the Apr 15 line. "This is the one that kills you — internal meeting,
customer named, no one looped in CS. With this system, that triggers an alert."
-->

---

## Bonus insight #2 — Trust Trajectory Score

For each customer: a score between 0 and 1.

But here's the thing — **I never show just the number.**

```
  Quantum Edge   → 0.31  ↓
    ├ sentiment slope      : −0.4
    ├ action closure rate  : 38%
    ├ escalation count     : 2
    └ churn signal density : high
```

The score is a signal. The components are the evidence. Both are required output — by design, not convention.

A number without evidence is just a guess. I built the evidence into the schema.

<!--
SPEAKER: "This is an LLM system. The risk is hallucinated confidence.
The schema forces every score to carry its proof. No components, no score."
-->

---

## Bonus insight #3 — Who's actually closing their action items?

Across every meeting with action items, I track who owned what and whether it showed up closed in a later call.

```
  Tyler Washington  :  5 / 8  closed  (62%)
  Sofia Petrov      : 11 / 12 closed  (92%)   ← reliable
  Chris Lee         :  2 / 6  closed  (33%)   ← worth a conversation
```

This isn't a performance report. It's a blocker detector.

When the same items don't close across multiple calls, there's usually a systemic reason — cross-team dependency, unclear ownership, or the wrong person on the hook.

<!--
SPEAKER: "Engineering leaders love this one. CSMs love this one.
It's the insight you could build from memory if you were in every meeting.
Most people aren't."
-->

---

## Two more I designed but didn't fully build

**Voice-of-Customer Gap Detector** — when external sentiment for a customer drops but internal eng/PM meetings stop mentioning them, that's a warning sign. Customer pain isn't reaching the org.

**Escalation Predictor** — the support → external review → war room pattern in the corpus is a natural training signal. With enough history, you can flag tickets before they escalate.

Both are in the architecture. Both are a week of focused work from shippable.

<!--
SPEAKER: "I'm not padding the list. These are real features I scoped, designed the data
pipeline for, and chose not to half-implement. I'd rather show you something honest
than something broken."
-->

---

## How it's all wired together

```
  Streamlit UI + Notebooks
          │
  Coordinator Agent (LangGraph) ── human-in-the-loop gate
          │
  Risk Detector         Insight Synthesizer
          │  (tool calls)
  Custom MCP Server  ── 4 tools
          │
  DuckDB  ·  NetworkX (journey graph)
          │
  Enrichment pipeline
  (classify → sentiment → entities → normalize → risk score)
          │
  data/raw/  (100 transcripts)
```

Every prompt is versioned. Every insight is logged with full lineage.

<!--
SPEAKER: "The LangGraph coordinator is the part I'd want to walk through in more detail
if we have time. The HITL gate is where a human reviewer can intercept a risky
synthesis before it surfaces to a stakeholder."
-->

---

## Six things that could go wrong — and how I'm handling them

| Risk | What I did about it |
|---|---|
| Same customer, different spellings | `customer_normalize.py` + alias map |
| LLM invents a cross-call link | Every link needs a `(meeting_id, utterance_index)` citation |
| Score sounds confident, isn't | Score always ships with four components + evidence |
| Synthesis flatters instead of informs | `Insight.citations` is schema-required — `min_length=1` |
| My tags drift from pre-tags | Disagreements are logged and spot-checked |
| PII, access control in prod | Scoped out — named explicitly, not hidden |

I'd rather tell you what I left out than pretend I covered everything.

<!--
SPEAKER: Linger on the last row. "PII redaction and per-stakeholder ACLs are
a week of real work. I named them in the architecture so you know where they go.
Pretending they're done would be the wrong trade-off for a take-home."
-->

---

## A word on how I evaluated this

I didn't build a regression harness against the pre-tagged labels. Here's why: those labels are probably LLM-generated. Measuring my LLM output against another LLM's output isn't evaluation — it's circular.

**What I did instead:** 10–15 transcript spot-checks, comparing my system's output to the pre-tags, with written reasoning for every disagreement.

The honest version of evaluation for free-form insights is human review on a small, carefully chosen sample. That's what I built toward.

The senior signal here isn't a high F1 score on a synthetic benchmark. It's knowing why that benchmark would be misleading.

<!--
SPEAKER: This is the meta-point of the whole presentation.
"If you want to hire someone who'll build the right thing, not just the
thing that looks good on a metric — this is the moment I'm gesturing at."
-->

---

## What I'd do with one more week

**Honest priority order:**

1. Human-labeled eval subset — the spot-checks showed me exactly where to focus
2. Production HITL queue — a real reviewer dashboard, not an inline gate
3. Salesforce / Zendesk connector — same MCP shape, different tool implementations
4. Agent handoffs — Risk Detector surfacing directly to the Action Tracker
5. PII redaction + per-stakeholder access control

The architecture supports all of these without a redesign. That was intentional.

<!--
SPEAKER: "I didn't build a throwaway notebook. I built a foundation.
Everything on this list slots in — you're not re-architecting, you're extending."
-->

---

## What I want you to take away

Three things:

**The insight is in the journey, not the transcript.** Individual call analysis is a commodity. Cross-call narrative is the product.

**Evidence is not optional.** Every score, every tag, every insight needs a citation. That's not overhead — it's what makes it trustworthy.

**Honest evaluation beats impressive metrics.** I'll always tell you what I didn't build and why.

*The code, notebooks, and architecture writeup are all in `/deliverables/` — happy to walk through any layer.*

---

## Questions?

What would you like to dig into?

- The journey graph and entity resolution
- The LangGraph agent design
- The evaluation methodology
- What production would actually take

<!--
SPEAKER: Don't summarize again. Just open the floor.
The deck has said everything — now have a conversation.
-->
