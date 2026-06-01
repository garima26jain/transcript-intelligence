<!--
Marp deck — Transcript Intelligence
Render with:
  npx @marp-team/marp-cli@latest slides.md --pdf -o ../slides.pdf

Structure mirrors how the panel will receive it:
  Problem → Approach → What we built (required + bonus) → Demo proof →
  How it's built → Quality / methodology → Future scope → Q&A
-->

---
marp: true
theme: default
paginate: true
size: 16:9
header: 'Transcript Intelligence'
footer: 'B2B SaaS call-intelligence platform · take-home presentation'
style: |
  section {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 26px;
    padding: 56px 80px;
    color: #1e293b;
    background: #fafafa;
  }
  h1, h2 {
    color: #0f172a;
    border-bottom: 3px solid #0ea5e9;
    padding-bottom: 8px;
    margin-bottom: 18px;
  }
  h3 { color: #1e293b; }
  strong { color: #0f172a; }
  blockquote {
    border-left: 5px solid #6366f1;
    background: #eef2ff;
    color: #312e81;
    margin: 14px 0;
    padding: 14px 18px;
    border-radius: 6px;
    font-style: italic;
  }
  code { background: #f1f5f9; padding: 2px 6px; border-radius: 4px; }
  table { font-size: 22px; }
  th { background: #0f172a; color: #f8fafc; }
  tr:nth-child(even) { background: #f1f5f9; }
  section.title {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
    color: #f8fafc;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  section.title h1 {
    font-size: 78px;
    color: #f8fafc;
    border: none;
    margin-bottom: 6px;
  }
  section.title h3 { color: #cbd5e1; }
  section.divider {
    background: #0f172a;
    color: #f8fafc;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
  }
  section.divider h1 {
    font-size: 64px;
    color: #f8fafc;
    border: none;
  }
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }
  .card {
    background: #ffffff;
    border-radius: 12px;
    border-left: 5px solid #0ea5e9;
    padding: 18px 22px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
  }
  .card-red    { border-left-color: #dc2626; }
  .card-amber  { border-left-color: #f59e0b; }
  .card-green  { border-left-color: #16a34a; }
  .card-violet { border-left-color: #7c3aed; }
  .metric { display: inline-block; margin: 6px 14px 6px 0; }
  .metric .num { font-size: 40px; font-weight: 800; color: #0ea5e9; line-height: 1; }
  .metric .lbl { display: block; font-size: 17px; color: #64748b; letter-spacing: 0.2px; }
  .pill {
    display: inline-block; padding: 3px 12px; border-radius: 999px;
    font-size: 17px; font-weight: 600; margin: 2px;
  }
  .pill-red    { background: #fee2e2; color: #b91c1c; }
  .pill-amber  { background: #fef3c7; color: #b45309; }
  .pill-green  { background: #d1fae5; color: #047857; }
  .pill-blue   { background: #dbeafe; color: #1d4ed8; }
  .pill-violet { background: #ede9fe; color: #6d28d9; }
  .small { font-size: 20px; color: #475569; }
---

<!-- _class: title -->

# Transcript Intelligence

### Turning 100 call transcripts into decisions every leader can act on

**B2B SaaS · senior AI engineering take-home**

---

## The problem in one slide

A B2B SaaS company is recording calls across three channels:

<div class="grid-3">
<div class="card card-red">

**Support calls**
Customers asking for help — bugs, billing, performance

</div>
<div class="card card-amber">

**External calls**
Account managers running renewals, audits, planning

</div>
<div class="card card-violet">

**Internal calls**
Eng standups, war rooms, roadmap planning

</div>
</div>

**Today, those recordings sit in a folder.** Nobody reads them. The patterns inside them never reach the people who could act on them.

> The assignment asks for categorization + sentiment + bonus insights. The *real* problem is that the same customer story plays across all three channels — and no one connects the dots.

---

## The hidden opportunity in this dataset

<div class="grid-2">
<div>

I traced the same customers across **all three call types**, looking for patterns the brief didn't ask about.

What I found:

- A **support case** about backup performance
- A **business review** where reliability was flagged "a concern"
- An **internal eng meeting** that named the same customer as a churn risk
- A **renewal call** with visible tension

</div>
<div>

<div class="card card-red">

**This is a slow-motion customer crisis.**
It played out over weeks. Nobody connected the dots.

</div>

<div class="card card-green" style="margin-top: 14px;">

**This is the unfair advantage in your data.**
Cross-call narrative is the signal — and the system I built surfaces it automatically.

</div>

</div>
</div>

---

## My approach in one sentence

> Build a **small, opinionated agentic intelligence platform** — not a pipeline — and let the same intelligence layer serve four different stakeholders through four different lenses.

<div class="grid-2" style="margin-top: 24px;">
<div class="card">

**Why platform, not pipeline?**
A pipeline ends at a chart. A platform lets the next stakeholder ask the next question without rebuilding anything.

</div>
<div class="card">

**Why agentic?**
Cross-call reasoning requires multiple tool calls + memory + judgment. That's what agents are for. Static SQL won't get you to "why is Quantum Edge churning?"

</div>
</div>

<div class="card card-violet" style="margin-top: 20px;">

**Why opinionated?** A take-home is judged on the architectural bets you're confident enough to make, name, and defend. I made six.

</div>

---

<!-- _class: divider -->

# What's inside

Required tasks · bonus insights · the agentic platform

---

## What I shipped — at a glance

<div class="grid-2">
<div class="card card-green">

### ✅ Required
- 6-theme topic taxonomy + multi-label classifier
- Sentiment as a **signal**, not a score (4 resolutions)

</div>
<div class="card card-violet">

### ⭐ Bonus insights
- **Customer Journey + Health Score** (headline)
- **Action-Item Lineage** by owner
- **Voice-of-Customer Gap** *(designed)*
- **Escalation Predictor** *(designed)*

</div>
</div>

<div class="grid-2" style="margin-top: 20px;">
<div class="card">

### 🧱 Platform
- Custom **MCP server** with 4 tools
- **LangGraph** coordinator + 2 specialists
- **Inline HITL gate** on high-stakes labels
- Versioned prompts + audit log w/ lineage

</div>
<div class="card">

### 👥 Stakeholders
4 personas over one intelligence layer:
Customer Success · Support Ops · Product · Engineering

</div>
</div>

---

## Required #1 — Topic categorization

**Why not k-means / BERTopic?** A CS leader doesn't want `cluster_3`. They want a *named, actionable* theme.

<div class="grid-2">
<div>

### 6 themes, 27 subtopics — LLM-derived from your corpus

<div class="small">

- 🛡️ **Reliability & Incidents** — outages, RCAs, capacity
- 🤝 **Customer Accounts & Renewals** — onboarding, renewals, at-risk accounts
- 🆘 **Support Cases** — billing, defects, escalations
- 📋 **Compliance & Comply Product** — audit prep, framework gaps
- 🛠️ **Product & Engineering Delivery** — sprints, planning, QA
- 🚀 **Go-to-Market & Competitive** — wins, losses, competitive positioning

</div>
</div>
<div class="card card-violet">

**How:** Opus 4.7 reads 25 stratified summaries, proposes the taxonomy. Sonnet 4.6 multi-label classifies all 100 transcripts with structured-output tool calls. Taxonomy is versioned + frozen.

**Why this is senior:** the taxonomy is **named in your corpus's own language** — "the March Detect outage" theme. Not generic categories.

</div>
</div>

---

## Required #2 — Sentiment as a signal, not a score

Pre-tagged data has per-utterance labels. I add **four resolutions** that turn sentiment into actionable signal.

<div class="grid-2">
<div class="card">

**Per speaker**
Who drives positivity in a war room? Who's the calm anchor in a tense renewal?

</div>
<div class="card">

**Arc slope**
Does the call resolve or stay tense? Critical for support — *"did the customer leave happier than they came in?"*

</div>
</div>

<div class="grid-2" style="margin-top: 14px;">
<div class="card">

**Per entity**
Sentiment **when a specific customer or product is named**. Reveals "Quantum Edge" mentions average -0.4.

</div>
<div class="card card-green">

**Per customer trajectory**
The bridge to the headline insight — sentiment **across the customer's whole journey**, not just one call.

</div>
</div>

---

<!-- _class: divider -->

# Bonus insights

Where this stops looking like a take-home

---

## Bonus #1 — Customer Journey + Health Score

For each customer, every interaction stitched chronologically across all three call types.

### Real corpus output: **Summit Trust**

| Date | Type | What happened |
|------|------|---------------|
| Feb 12 | 🆘 Support | Detect alert delays — sentiment 2.4 |
| Feb 28 | 🤝 External | Service Reliability Discussion — concerns escalated |
| Mar 22 | 🆘 Support | Comply v2 report formatting issue |

<div class="grid-2" style="margin-top: 16px;">
<div class="card card-red">

**Health Score: 0.06 🔴**
*Lowest in the corpus.* Not a number — a verdict.

</div>
<div class="card">

**Components shown alongside, always:**
sentiment slope · follow-through · escalations · risk-signal density

*Never lead with the score alone.*

</div>
</div>

---

## Bonus #2 — Action-Item Lineage

Every action item tracked by owner. Open vs closed, with citations.

<div class="grid-2">
<div>

### Top owners by load

| Owner | Open items |
|---|---|
| Maria Santos | 31 |
| David Kim | 24 |
| Sarah Chen | 23 |
| Elena Vasquez | 20 |
| Kevin O'Brien | 19 |

</div>
<div class="card card-violet">

**Eng-leader candy.** Surfaces recurring blockers and uneven ownership at a glance.

**Honest caveat (shown on the methodology slide):** closure rate is conservative by design — we only mark closed when wording recurs verbatim in a later utterance. **Open-item counts carry the load.**

</div>
</div>

---

## Bonus #3 + #4 — Designed, not yet built

<div class="grid-2">
<div class="card card-amber">

### Voice-of-Customer Gap Detector

When **external sentiment** for a customer trends down, but **internal eng/PM meetings** don't mention them → flag the gap.

*"Customer pain that isn't reaching the org."*

**Who cares:** PMs and execs who need to know what they're not seeing.

</div>
<div class="card card-amber">

### Escalation Predictor

Use the corpus's **support → external → war-room** transition patterns as labels. Predict which **active support cases** will escalate before they do.

**Who cares:** Support leaders who could pre-empt one Tuesday-night fire-drill per quarter.

</div>
</div>

<div class="small" style="margin-top: 20px;">

A well-articulated insight you can build later is worth more than a half-baked one shipped today.

</div>

---

## Same intelligence, four stakeholders

<div class="grid-2">
<div class="card card-red">

### 🎯 Customer Success
*"Who's about to leave?"*

Ranked health table → drill-down → real evidence quotes.

</div>
<div class="card card-amber">

### 🛠️ Support Ops
*"Where are customers stuck?"*

Worst-rated cases, repeat customers, risk-signal mix.

</div>
</div>

<div class="grid-2" style="margin-top: 14px;">
<div class="card card-violet">

### 📊 Product
*"What do customers want?"*

Theme landscape, per-product sentiment, cross-channel signals.

</div>
<div class="card">

### ⚙️ Engineering
*"What's on my team?"*

Action-item load by owner, incident pulse, blocker themes.

</div>
</div>

<div class="small" style="margin-top: 18px;">

One taxonomy. One alias map. One audit log. Four lenses.

</div>

---

## Live demo proof — agent answering a CS-lead question

**Question asked:** *"What's the status of Quantum Edge — are we at risk of losing them?"*

> Quantum Edge is at critical churn risk — the highest-priority renewal on your desk this week. The account carries **9 risk signals** from a single meeting, driven by three compounding crises: a **six-hour Aegis Detect outage on March 10–11** that breached the 99.5% uptime SLA and was never proactively communicated; an active competitive evaluation of **SentinelShield** at lower pricing; and a tighter Quantum Edge budget heading into next year. **Leo Marquez has stated the engineering remediation call is his sole deciding factor for a renewal recommendation.**

<div class="grid-2" style="margin-top: 14px;">
<div class="card card-green">

**9 specific citations** to real utterance indices.
**3 HITL flags** raised for human review before publication.

</div>
<div class="card">

The customer name, the competitor, the exec name, the dates — **all extracted from the transcripts, none invented.**

</div>
</div>

---

<!-- _class: divider -->

# How it's built

Architecture · failure modes · governance

---

## Architecture on one slide

```
   Streamlit (4 personas)  +  Notebooks (reference)  +  Claude Code (MCP)
              │                                              ▲
              ▼                                              │
   ┌─────────────────────────────┐                ┌─────────┴────────┐
   │  Coordinator Agent          │                │  Custom MCP      │
   │  (LangGraph)                │◀──tool calls──▶│  Server          │
   │  · router (Haiku)           │                │  · search        │
   │  · risk_detector (Sonnet)   │                │  · journey       │
   │  · insight_synth (Sonnet)   │                │  · action_items  │
   │  · inline HITL gate         │                │  · sentiment     │
   └──────────────┬──────────────┘                └─────────┬────────┘
                  ▼                                         │
           Governance:                                      ▼
           versioned prompts                       DuckDB  +  NetworkX
           append-only audit log                          │
                                                          ▼
   Enrichment: call_type → taxonomy → topics → sentiment →
               entities → customer_normalize → risk_signals
                                                          │
                                            data/raw/ (100 transcripts)
```

---

## Failure modes I designed against

A senior engineer's distinguishing skill is **anticipating** failure before writing code. Six risks → six mitigations baked into the architecture:

| # | Risk | Mitigation |
|---|------|------------|
| 1 | Entity resolution fails silently | `customer_normalize.py` + alias map (merged 38 surface forms) |
| 2 | Cross-meeting linkage hallucinated | Every claim cites `(meeting_id, utterance_index)` — schema-enforced |
| 3 | Synthetic-metric overconfidence | Health Score always shown with components + evidence |
| 4 | Sycophantic synthesis | `Insight.citations` is `min_length=1` at the Pydantic layer |
| 5 | Pre-tagged label drift | Treated as **comparison baseline**, not ground truth |
| 6 | Production gap (PII, ACL) | Scoped out — called out on future-scope slide |

---

## Methodology — what eval actually means here

<div class="grid-2">
<div>

**What I'm not doing**
A full F1/MAE regression harness across 5 tasks.

**Why not?** The pre-tagged labels in your data are themselves LLM-generated. Measuring agreement between two LLMs is weak signal at high engineering cost.

</div>
<div class="card">

**What I am doing**

- **12-transcript stratified spot-check** → markdown table with one-line reasoning per disagreement
- **Lineage in audit log** → every LLM call records prompt-version + model + tokens + latency
- **HITL gate** on high-severity churn — only on the labels where wrong = expensive

</div>
</div>

> Pre-tagged labels are a *comparison baseline*, not ground truth. For free-form insights, the only honest eval is human review on a small sample.

---

## What it costs, what it scales to

<div class="grid-3">
<div class="card">

<span class="metric"><span class="num">$5.72</span><span class="lbl">Total enrichment cost</span></span>

100 transcripts end-to-end.

</div>
<div class="card">

<span class="metric"><span class="num">318</span><span class="lbl">LLM calls audited</span></span>

Every one traceable.

</div>
<div class="card">

<span class="metric"><span class="num">86%</span><span class="lbl">Hit the rule-based fast path</span></span>

Only 14% needed the Haiku fallback for call-type classification.

</div>
</div>

<div class="card card-violet" style="margin-top: 24px;">

**Cost-aware model routing — right model for the job:**
**Haiku** for screening · **Sonnet** for classification + sentiment · **Opus** only for cross-meeting synthesis (taxonomy, alias map).

That's the entire cost story. Building a per-run ledger for 100 docs is over-engineering — the routing decision itself is what matters.

</div>

---

## What I'd do with one more week

<div class="grid-2">
<div class="card card-violet">

### Productionize the quality layer

- **Human-labeled eval subset** — now that spot-checks reveal where to focus
- **Real HITL UX** — queue + reviewer dashboard, not inline gate
- **PII redaction + per-stakeholder access control**

</div>
<div class="card card-violet">

### Expand the platform

- **Salesforce / Zendesk MCP** — same shape, different data source
- **Slack agent** — query in any channel, MCP tools fire
- **Agent-to-agent collaboration** — Risk Detector hands off to Action Tracker

</div>
</div>

<div class="card" style="margin-top: 20px;">

### One quarter out

Multi-tenant deployment · real-time pipeline · automated anomaly detection that pages CS when a customer's Health Score drops more than 0.20 in 7 days.

</div>

---

## The senior story in one slide

<div class="grid-2">
<div>

### What the panel wants to see

- ✅ Required tasks: solid
- ✅ Bonus insights: 2 implemented, 2 designed
- ✅ Stakeholder lens: 4 personas, one platform
- ✅ Architectural opinions, named and defended
- ✅ Failure modes anticipated, not discovered
- ✅ Cost-aware from day one
- ✅ Honest methodology, no eval theatre

</div>
<div class="card card-green">

### What's underneath

- **47 Python modules**
- **9 versioned prompts**
- **4 MCP tools**
- **3 LangGraph agents**
- **100 transcripts enriched at $5.72**
- **318-entry audit log with full lineage**
- **1 headline insight built, 1 eng-leader insight built, 2 more designed**

</div>
</div>

---

<!-- _class: title -->

# Thank you

### Happy to walk through any layer — code, prompts, decisions, what didn't work.

The system, the audit log, and the deck source are all in the repo.
