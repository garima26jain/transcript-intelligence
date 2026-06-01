"""Customer-journey graph using NetworkX.

Nodes:
  - customer (canonical name)
  - meeting (meeting_id)
  - risk_signal (composite)

Edges:
  - customer → meeting           ("mentioned_in")
  - meeting  → risk_signal       ("contains")
  - risk_signal → customer       ("targets") when the signal names a customer

The graph is built from the DuckDB store and persisted as GraphML so
notebook 03 can render the headline insight without re-querying.
"""
from __future__ import annotations

from pathlib import Path

import networkx as nx

from ti.config import settings
from ti.store import duckdb_store


_GRAPH_PATH = settings.data_graph / "customer_journey.graphml"


def graph_path() -> Path:
    return _GRAPH_PATH


def build_graph() -> nx.MultiDiGraph:
    g = nx.MultiDiGraph()

    with duckdb_store.connect() as con:
        meetings = con.execute(
            "SELECT meeting_id, title, call_type, start_time, sentiment_score, arc_slope FROM transcripts"
        ).fetchall()
        for m in meetings:
            g.add_node(
                f"meeting:{m[0]}",
                kind="meeting",
                title=m[1],
                call_type=m[2],
                date=m[3].isoformat() if m[3] else "",
                sentiment_score=float(m[4] or 0),
                arc_slope=float(m[5] or 0),
            )

        customers = con.execute(
            "SELECT DISTINCT name FROM entities WHERE kind = 'customer'"
        ).fetchall()
        for c in customers:
            g.add_node(f"customer:{c[0]}", kind="customer", name=c[0])

        mentions = con.execute(
            "SELECT meeting_id, name FROM entities WHERE kind = 'customer'"
        ).fetchall()
        for meeting_id, customer in mentions:
            g.add_edge(
                f"customer:{customer}",
                f"meeting:{meeting_id}",
                kind="mentioned_in",
            )

        risk_rows = con.execute(
            """SELECT meeting_id, kind, severity, customer, driver,
                      source_utterance_index, surfaced_by_speaker
               FROM risk_signals"""
        ).fetchall()
        for i, r in enumerate(risk_rows):
            sid = f"signal:{r[0]}:{i}"
            g.add_node(
                sid,
                kind="risk_signal",
                signal_kind=r[1],
                severity=r[2],
                customer=r[3] or "",
                driver=r[4],
                source_utterance_index=int(r[5]),
                surfaced_by=r[6],
            )
            g.add_edge(f"meeting:{r[0]}", sid, kind="contains")
            if r[3]:
                g.add_edge(sid, f"customer:{r[3]}", kind="targets")

    return g


def save(g: nx.MultiDiGraph) -> Path:
    _GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)
    nx.write_graphml(g, _GRAPH_PATH)
    return _GRAPH_PATH


def load() -> nx.MultiDiGraph:
    return nx.read_graphml(_GRAPH_PATH)
