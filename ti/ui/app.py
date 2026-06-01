"""Transcript Intelligence — multi-persona dashboard.

Four stakeholder views over one intelligence layer:
  • Customer Success — who's about to churn
  • Support Operations — where customers are stuck
  • Product — what customers ask for and which products lose them
  • Engineering — team load and incident patterns

Every claim ties back to a real utterance in a real meeting. Launch with `make ui`.
"""
from __future__ import annotations

# Streamlit puts ti/ui/ on sys.path but not the repo root, so bootstrap.
import sys
from pathlib import Path
_repo_root = Path(__file__).resolve().parent.parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

import pandas as pd
import plotly.express as px
import streamlit as st

from ti.insights.customer_journey import build_customer_journey, rank_customers_by_risk
from ti.insights.action_lineage import all_owners_summary
from ti.store import duckdb_store


# ─────────────────────────────────────────────────────────────────────────────
# Page setup
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Transcript Intelligence",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      /* Tighten the default spacing */
      .block-container { padding-top: 2rem; padding-bottom: 2rem; }
      /* Health badges */
      .badge {
          display: inline-block; padding: 2px 10px; border-radius: 999px;
          font-size: 0.78rem; font-weight: 600; color: white;
      }
      .badge-red    { background: #dc2626; }
      .badge-amber  { background: #f59e0b; }
      .badge-green  { background: #16a34a; }
      .badge-slate  { background: #475569; }
      /* Section header */
      .lead { font-size: 1.05rem; color: #475569; margin-top: -8px; }
      .quote {
          background: #f8fafc; border-left: 4px solid #0ea5e9;
          padding: 10px 14px; margin: 6px 0; border-radius: 6px;
          font-style: italic; color: #334155;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# Cached data loaders
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_corpus_overview() -> dict:
    with duckdb_store.connect() as con:
        n_calls = con.execute("SELECT COUNT(*) FROM transcripts").fetchone()[0]
        n_customers = con.execute(
            "SELECT COUNT(DISTINCT name) FROM entities WHERE kind='customer'"
        ).fetchone()[0]
        n_signals = con.execute("SELECT COUNT(*) FROM risk_signals").fetchone()[0]
        n_action = con.execute("SELECT COUNT(*) FROM action_items").fetchone()[0]
        by_type = con.execute(
            "SELECT call_type, COUNT(*) AS n FROM transcripts GROUP BY call_type"
        ).fetchall()
    return {
        "n_calls": n_calls,
        "n_customers": n_customers,
        "n_signals": n_signals,
        "n_action": n_action,
        "by_type": dict(by_type),
    }


@st.cache_data(show_spinner=False)
def load_ranked_customers(top_n: int) -> list:
    return rank_customers_by_risk(top_n=top_n)


@st.cache_data(show_spinner=False)
def load_owners_summary() -> list:
    return all_owners_summary(min_items=2)


@st.cache_data(show_spinner=False)
def load_themes() -> pd.DataFrame:
    with duckdb_store.connect() as con:
        df = con.execute(
            """SELECT theme, subtopic,
                      COUNT(*) AS n_classifications,
                      COUNT(DISTINCT meeting_id) AS distinct_meetings,
                      ROUND(AVG(confidence), 2) AS avg_confidence
               FROM topics
               GROUP BY theme, subtopic
               ORDER BY n_classifications DESC"""
        ).df()
    return df


@st.cache_data(show_spinner=False)
def load_product_sentiment() -> pd.DataFrame:
    with duckdb_store.connect() as con:
        df = con.execute(
            """SELECT entity_name AS product,
                      COUNT(*) AS meetings_mentioning,
                      SUM(mention_count) AS total_mentions,
                      ROUND(AVG(avg_sentiment), 2) AS sentiment_when_mentioned
               FROM entity_sentiment
               WHERE entity_kind = 'product'
               GROUP BY entity_name
               ORDER BY total_mentions DESC"""
        ).df()
    return df


@st.cache_data(show_spinner=False)
def load_support_landscape() -> dict:
    with duckdb_store.connect() as con:
        cases = con.execute(
            """SELECT meeting_id, title, sentiment_score, start_time,
                      duration_min, attendees, arc_slope
               FROM transcripts
               WHERE call_type = 'support'
               ORDER BY sentiment_score ASC"""
        ).df()
        # Customers in support most often.
        repeat = con.execute(
            """SELECT e.name AS customer, COUNT(DISTINCT e.meeting_id) AS support_cases
               FROM entities e
               JOIN transcripts t ON t.meeting_id = e.meeting_id
               WHERE e.kind = 'customer' AND t.call_type = 'support'
               GROUP BY e.name
               ORDER BY support_cases DESC
               LIMIT 10"""
        ).df()
        # Risk-signal split for support context.
        signal_breakdown = con.execute(
            """SELECT kind, severity, COUNT(*) AS n
               FROM risk_signals rs
               JOIN transcripts t ON t.meeting_id = rs.meeting_id
               WHERE t.call_type = 'support'
               GROUP BY kind, severity"""
        ).df()
    return {"cases": cases, "repeat_customers": repeat, "signal_breakdown": signal_breakdown}


@st.cache_data(show_spinner=False)
def load_incident_meetings() -> pd.DataFrame:
    with duckdb_store.connect() as con:
        df = con.execute(
            """SELECT meeting_id, title, call_type, start_time,
                      sentiment_score, duration_min
               FROM transcripts
               WHERE lower(title) LIKE '%incident%'
                  OR lower(title) LIKE '%war room%'
                  OR lower(title) LIKE '%outage%'
                  OR lower(title) LIKE '%urgent%'
                  OR lower(title) LIKE '%rca%'
               ORDER BY start_time DESC"""
        ).df()
    return df


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def health_badge(score: float) -> str:
    if score < 0.30:
        return f'<span class="badge badge-red">At risk · {score:.2f}</span>'
    if score < 0.60:
        return f'<span class="badge badge-amber">Watch · {score:.2f}</span>'
    return f'<span class="badge badge-green">Healthy · {score:.2f}</span>'


def severity_badge(severity: str) -> str:
    color = {"high": "badge-red", "medium": "badge-amber", "low": "badge-slate"}.get(
        severity.lower(), "badge-slate"
    )
    return f'<span class="badge {color}">{severity.title()}</span>'


def resolve_utterance(meeting_id: str, utt_index: int) -> tuple[str, str] | None:
    with duckdb_store.connect() as con:
        row = con.execute(
            "SELECT speaker_name, text FROM utterances WHERE meeting_id=? AND utt_index=?",
            [meeting_id, utt_index],
        ).fetchone()
    return (row[0], row[1]) if row else None


def lookup_meeting_title(meeting_id: str) -> str:
    with duckdb_store.connect() as con:
        row = con.execute(
            "SELECT title FROM transcripts WHERE meeting_id=?", [meeting_id]
        ).fetchone()
    return row[0] if row else meeting_id


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────

overview = load_corpus_overview()

with st.sidebar:
    st.markdown("### 🔭 Pick your lens")
    st.caption("One corpus. Four perspectives. Same evidence underneath.")
    persona = st.radio(
        "Choose your role",
        options=["Customer Success", "Support Ops", "Product", "Engineering"],
        captions=[
            "Who's about to leave?",
            "Where are customers stuck?",
            "What do customers want?",
            "What's on my team?",
        ],
        index=2,  # Product as the landing view
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### Corpus at a glance")
    st.write(f"📞 **{overview['n_calls']}** calls analyzed")
    st.write(f"🏢 **{overview['n_customers']}** customers tracked")
    st.write(f"⚠️ **{overview['n_signals']}** risk signals surfaced")
    st.write(f"✅ **{overview['n_action']}** action items captured")

    st.markdown("---")
    with st.expander("About this dashboard", expanded=False):
        st.markdown(
            """
            This tool turns hundreds of call transcripts — support cases, business
            reviews, and internal team meetings — into views built for the leaders
            who actually need them.

            **Every number you see ties back to a real utterance in a real meeting.**
            Click any **Evidence** expander to see the exact quote.

            The four views show the same intelligence through different lenses —
            the right answer depends on who's asking.
            """
        )


# ─────────────────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────────────────

PERSONA_HEROES = {
    "Customer Success": (
        "Customer Success — Renewal Watch",
        "Who's about to churn, what's driving it, and what to do this week.",
    ),
    "Support Ops": (
        "Support Operations — Where Customers Are Stuck",
        "Cases, escalations, and the customers and products costing you the most time.",
    ),
    "Product": (
        "Product — Voice of Customer",
        "What themes show up most, which products win or lose sentiment, and what to put on the roadmap.",
    ),
    "Engineering": (
        "Engineering — Team Load & Incident Pulse",
        "Who owes what, which incidents keep recurring, and where the team is blocked.",
    ),
}

title, lead = PERSONA_HEROES[persona]
st.title(title)
st.markdown(f'<div class="lead">{lead}</div>', unsafe_allow_html=True)
st.markdown("")


# ─────────────────────────────────────────────────────────────────────────────
# Persona renderers
# ─────────────────────────────────────────────────────────────────────────────

def render_customer_success() -> None:
    top_n = st.sidebar.slider("Customers to show", 5, 20, 10)
    ranked = load_ranked_customers(top_n)

    if not ranked:
        st.warning("No customer journeys available. Did `make enrich` and `make build-db` complete?")
        return

    n_red = sum(1 for j in ranked if j.trajectory_score < 0.30)
    n_amber = sum(1 for j in ranked if 0.30 <= j.trajectory_score < 0.60)
    n_green = sum(1 for j in ranked if j.trajectory_score >= 0.60)

    a, b, c, d = st.columns(4)
    a.metric("At risk", n_red, help="Customer Health Score below 0.30")
    b.metric("Watch", n_amber, help="0.30–0.60 — fine today, vulnerable to a bad week")
    c.metric("Healthy", n_green, help="Above 0.60 — proactive ops can convert these to references")
    d.metric("Avg health", f"{sum(j.trajectory_score for j in ranked)/len(ranked):.2f}")

    st.markdown("")
    st.markdown("##### Customer health — lowest first")
    st.caption(
        "Health Score (0 = at risk, 1 = healthy) blends sentiment trend, action follow-through, "
        "escalations, and risk-signal density. **Lower means act this week.**"
    )

    df = pd.DataFrame(
        [
            {
                "Customer": j.customer_name,
                "Health Score": j.trajectory_score,
                "Calls in journey": len(j.nodes),
                "Escalations": j.components.escalation_count,
                "Risk signals / call": round(j.components.churn_signal_density, 2),
            }
            for j in ranked
        ]
    )

    fig = px.bar(
        df.iloc[::-1],
        x="Health Score",
        y="Customer",
        orientation="h",
        color="Health Score",
        color_continuous_scale=[(0, "#dc2626"), (0.5, "#f59e0b"), (1, "#16a34a")],
        range_color=[0, 1],
        height=max(280, 32 * len(df)),
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        coloraxis_showscale=False,
        yaxis_title=None,
        xaxis_title="Health Score (higher = healthier)",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("##### Drill into a customer")
    selected = st.selectbox(
        "Customer",
        options=[j.customer_name for j in ranked],
        label_visibility="collapsed",
    )
    journey = build_customer_journey(selected)
    if journey is None:
        st.error(f"No journey for {selected}")
        return

    header = st.container()
    with header:
        col_score, col_meet, col_first, col_last = st.columns([1, 1, 1, 1])
        col_score.metric("Health Score", f"{journey.trajectory_score:.2f}")
        col_meet.metric("Calls in journey", len(journey.nodes))
        col_first.metric("First touch", journey.nodes[0].date.strftime("%b %d"))
        col_last.metric("Most recent", journey.nodes[-1].date.strftime("%b %d"))

    st.markdown("")
    st.markdown(
        f'<div class="quote">{health_badge(journey.trajectory_score)} '
        f"&nbsp;&nbsp;What's pulling the score: "
        f"sentiment trend {journey.components.sentiment_slope:+.2f} · "
        f"follow-through {journey.components.action_closure_rate:.0%} · "
        f"escalations {journey.components.escalation_count} · "
        f"risk density {journey.components.churn_signal_density:.1f}/call</div>",
        unsafe_allow_html=True,
    )

    st.markdown("##### Their journey across all conversations")
    j_rows = [
        {
            "Date": n.date.strftime("%Y-%m-%d"),
            "Call type": n.call_type.title(),
            "Meeting": n.title,
            "Pre-tagged sentiment (1–5)": n.sentiment_score,
            "Risk signals raised": n.risk_signal_count,
        }
        for n in journey.nodes
    ]
    st.dataframe(j_rows, use_container_width=True, hide_index=True)

    st.markdown("##### What they actually said — evidence")
    if not journey.evidence:
        st.info("No high-severity evidence captured for this customer.")
    for c in journey.evidence:
        utt = resolve_utterance(c.meeting_id, c.utterance_index)
        meeting_title = lookup_meeting_title(c.meeting_id)
        label = f"📅 {meeting_title[:60]}"
        with st.expander(label, expanded=False):
            if utt:
                st.markdown(f'<div class="quote"><b>{utt[0]}:</b> {utt[1]}</div>',
                            unsafe_allow_html=True)
            if c.quote:
                st.caption(f"Why it's flagged: {c.quote}")


def render_support_ops() -> None:
    data = load_support_landscape()

    a, b, c = st.columns(3)
    a.metric("Support cases in corpus", len(data["cases"]))
    b.metric(
        "Avg sentiment (1–5)",
        f"{data['cases']['sentiment_score'].mean():.2f}",
        help="Pre-tagged overall meeting sentiment. Lower = unhappier customer.",
    )
    n_high_sev = data["signal_breakdown"][data["signal_breakdown"]["severity"] == "high"]["n"].sum()
    c.metric("High-severity signals in support calls", int(n_high_sev))

    st.markdown("")
    tab1, tab2, tab3 = st.tabs([
        "🔥 Hottest cases",
        "🔁 Repeat-customer pressure",
        "⚠️ Risk signal mix",
    ])

    with tab1:
        st.markdown("##### Worst-rated support cases — start here")
        st.caption("Lowest pre-tagged sentiment score first. These are the customers who left calls unhappy.")
        worst = data["cases"].head(10)[
            ["title", "sentiment_score", "start_time", "duration_min"]
        ].rename(columns={
            "title": "Case",
            "sentiment_score": "Sentiment (1–5)",
            "start_time": "When",
            "duration_min": "Duration (min)",
        })
        worst["When"] = pd.to_datetime(worst["When"]).dt.strftime("%Y-%m-%d")
        worst["Duration (min)"] = worst["Duration (min)"].round(1)
        st.dataframe(worst, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("##### Customers showing up in support most often")
        st.caption(
            "A customer with 3+ support cases is signalling product friction. "
            "Pair this with the Customer Success view to see if their renewal is in danger."
        )
        fig = px.bar(
            data["repeat_customers"].iloc[::-1],
            x="support_cases", y="customer", orientation="h",
            color="support_cases",
            color_continuous_scale=[(0, "#fef3c7"), (1, "#dc2626")],
            height=max(280, 32 * len(data["repeat_customers"])),
        )
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            coloraxis_showscale=False,
            yaxis_title=None,
            xaxis_title="Support cases in last quarter",
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.markdown("##### Risk signals coming out of support calls")
        st.caption(
            "Three categories surface from support: **escalations** (issue jumped the queue), "
            "**blockers** (something inside Aegis is stuck), and **churn** (the customer is at risk)."
        )
        breakdown = data["signal_breakdown"]
        if not breakdown.empty:
            fig = px.bar(
                breakdown,
                x="kind", y="n", color="severity",
                color_discrete_map={"low": "#94a3b8", "medium": "#f59e0b", "high": "#dc2626"},
                barmode="stack",
                category_orders={"severity": ["high", "medium", "low"]},
            )
            fig.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                yaxis_title="Signal count",
                xaxis_title=None,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No risk-signal breakdown for support calls.")


def render_product() -> None:
    themes_df = load_themes()
    product_df = load_product_sentiment()

    a, b, c = st.columns(3)
    a.metric("Distinct themes covered", themes_df["theme"].nunique())
    a.caption("Themes the LLM derived from your corpus")
    b.metric("Best-loved product", product_df.iloc[product_df["sentiment_when_mentioned"].idxmax()]["product"]
             if not product_df.empty else "—")
    c.metric(
        "Most-discussed product",
        product_df.iloc[product_df["total_mentions"].idxmax()]["product"]
        if not product_df.empty else "—",
        delta=f"{int(product_df['total_mentions'].max())} mentions" if not product_df.empty else None,
    )

    st.markdown("")
    tab1, tab2, tab3 = st.tabs(["🗺️ Theme landscape", "📦 Product reception", "🎯 Where conversations cluster"])

    with tab1:
        st.markdown("##### What customers and your team are actually talking about")
        st.caption(
            "Each bar is a subtopic the LLM clustered from the corpus. Heavy bars indicate"
            " where conversation volume is — that's roadmap pressure or recurring pain."
        )
        top_subtopics = themes_df.head(15)
        fig = px.bar(
            top_subtopics.iloc[::-1],
            x="distinct_meetings",
            y="subtopic",
            color="theme",
            orientation="h",
            hover_data=["n_classifications", "avg_confidence"],
            height=max(360, 26 * len(top_subtopics)),
        )
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            yaxis_title=None,
            xaxis_title="Meetings touching this subtopic",
            legend_title="Theme",
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown("##### Sentiment when each product is mentioned")
        st.caption(
            "Total mentions tells you what gets attention. "
            "Sentiment-when-mentioned tells you whether it's good attention or bad."
        )
        if product_df.empty:
            st.info("No product entities indexed yet.")
        else:
            fig = px.scatter(
                product_df,
                x="total_mentions", y="sentiment_when_mentioned",
                size="meetings_mentioning",
                text="product",
                color="sentiment_when_mentioned",
                color_continuous_scale=[(0, "#dc2626"), (0.5, "#f59e0b"), (1, "#16a34a")],
                size_max=60,
            )
            fig.update_traces(textposition="top center")
            fig.update_layout(
                margin=dict(l=10, r=10, t=20, b=10),
                xaxis_title="Total mentions (= attention)",
                yaxis_title="Avg sentiment when mentioned (-1 to +1)",
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(product_df, use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("##### Theme by call type — where the conversation actually happens")
        st.caption(
            "Themes the LLM clustered, broken out by where they show up. "
            "Themes that show up across **all three** call types are the highest-priority for product."
        )
        with duckdb_store.connect() as con:
            cross = con.execute(
                """SELECT t.theme, tr.call_type, COUNT(DISTINCT tr.meeting_id) AS meetings
                   FROM topics t
                   JOIN transcripts tr ON tr.meeting_id = t.meeting_id
                   GROUP BY t.theme, tr.call_type
                   ORDER BY meetings DESC"""
            ).df()
        if cross.empty:
            st.info("No cross-type theme data.")
        else:
            fig = px.bar(
                cross, x="theme", y="meetings", color="call_type",
                barmode="group",
                color_discrete_map={
                    "internal": "#0ea5e9",
                    "external": "#a855f7",
                    "support":  "#dc2626",
                },
            )
            fig.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_title=None,
                yaxis_title="Meetings",
                legend_title="Call type",
            )
            st.plotly_chart(fig, use_container_width=True)


def render_engineering() -> None:
    owners = load_owners_summary()
    incidents = load_incident_meetings()

    n_open = sum(s.total_items - s.closed_items for s in owners)
    n_owners_loaded = sum(1 for s in owners if s.total_items >= 5)

    a, b, c = st.columns(3)
    a.metric("Open action items", n_open)
    b.metric("Engineers carrying ≥ 5 items", n_owners_loaded)
    c.metric("Incident-flavoured meetings", len(incidents))

    st.markdown("")
    tab1, tab2 = st.tabs(["👥 Who owes what", "🚨 Incident pulse"])

    with tab1:
        st.markdown("##### Action items by owner — sort by total or by what's still open")
        st.caption(
            "Owners are extracted from each meeting's action items. "
            "*Follow-through rate is conservative* — we only mark an item closed when its specific "
            "wording recurs in a later utterance. Use open-count as the primary load signal."
        )
        rows = sorted(owners, key=lambda s: -s.total_items)[:12]
        df = pd.DataFrame(
            [
                {
                    "Owner": s.owner,
                    "Total items": s.total_items,
                    "Open": s.total_items - s.closed_items,
                    "Closed (provable)": s.closed_items,
                    "Follow-through": s.closure_rate,
                }
                for s in rows
            ]
        )
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Follow-through": st.column_config.ProgressColumn(
                    format="%.0f%%", min_value=0, max_value=1
                ),
            },
        )

        st.markdown("##### Drill into one owner's open commitments")
        owner_choice = st.selectbox(
            "Owner",
            options=[s.owner for s in rows],
            label_visibility="collapsed",
        )
        chosen = next(s for s in rows if s.owner == owner_choice)
        st.write(f"**{chosen.owner}** — {len(chosen.open_items)} open items")
        for o in chosen.open_items[:12]:
            mtg_title = lookup_meeting_title(o.source_meeting_id)
            st.markdown(
                f"- _{mtg_title[:60]}_ → {o.description}",
                unsafe_allow_html=True,
            )

    with tab2:
        st.markdown("##### Incident-flavoured meetings — outages, RCAs, war rooms")
        st.caption(
            "These are the meetings that mention incidents, outages, war rooms, or RCAs. "
            "Recurring titles or low sentiment trends are where engineering ownership investments would matter most."
        )
        if incidents.empty:
            st.info("No incident-flavoured meetings indexed.")
        else:
            inc = incidents.copy()
            inc["start_time"] = pd.to_datetime(inc["start_time"]).dt.strftime("%Y-%m-%d")
            inc["duration_min"] = inc["duration_min"].round(1)
            st.dataframe(
                inc[["title", "call_type", "start_time", "sentiment_score", "duration_min"]]
                .rename(columns={
                    "title": "Meeting",
                    "call_type": "Type",
                    "start_time": "When",
                    "sentiment_score": "Sentiment (1–5)",
                    "duration_min": "Duration (min)",
                }),
                use_container_width=True,
                hide_index=True,
            )


# ─────────────────────────────────────────────────────────────────────────────
# Dispatch
# ─────────────────────────────────────────────────────────────────────────────

with st.spinner("Pulling latest signals from the corpus…"):
    if persona == "Customer Success":
        render_customer_success()
    elif persona == "Support Ops":
        render_support_ops()
    elif persona == "Product":
        render_product()
    else:
        render_engineering()

st.markdown("---")
st.caption(
    "Built for the Transcript Intelligence assignment · "
    "All claims trace back to a real utterance in a real meeting · "
    "Made of one taxonomy, one alias map, four lenses."
)
