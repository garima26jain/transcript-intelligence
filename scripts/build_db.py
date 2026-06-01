"""Build (or rebuild) the DuckDB corpus from processed + enriched data."""
from __future__ import annotations

from ti.store import duckdb_store, graph_store


def main() -> int:
    duckdb_store.build_db()
    g = graph_store.build_graph()
    p = graph_store.save(g)
    print(
        f"Graph: {g.number_of_nodes()} nodes, {g.number_of_edges()} edges → {p}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
