"""Phase 4 demo: run the LangGraph coordinator over three persona queries.

Each query exercises a different code path:
  1. CS-lead risk assessment for one customer → router → risk → hitl → synth
  2. Eng-lead action-item status by owner    → router → synth (direct)
  3. PM-level corpus-wide risk question      → router → risk (no customer) → hitl → synth
"""
from __future__ import annotations

import sys

from ti.agents.coordinator import build_coordinator


EXAMPLES = [
    {
        "persona": "cs_lead",
        "query": "What's the status of Quantum Edge — are we at risk of losing them?",
    },
    {
        "persona": "eng_lead",
        "query": "What are Tyler Washington's open action items?",
    },
    {
        "persona": "pm",
        "query": "Which customers are the biggest churn risk this quarter?",
    },
]


def _print_section(title: str) -> None:
    print()
    print("=" * 80)
    print(f"  {title}")
    print("=" * 80)


def main() -> int:
    coord = build_coordinator()
    for i, ex in enumerate(EXAMPLES, 1):
        _print_section(f"Example {i} — persona={ex['persona']}")
        print(f"Query: {ex['query']}")
        result = coord.invoke({"query": ex["query"], "persona": ex["persona"]})

        print("\n--- Trace ---")
        for step in result.get("trace", []):
            print(f"  • {step}")

        print("\n--- HITL flags ---")
        flags = result.get("hitl_flags", [])
        if flags:
            for f in flags:
                print(f"  ⚠ {f}")
        else:
            print("  (none)")

        print("\n--- Answer ---")
        print(result.get("answer", "(no answer produced)"))

        print("\n--- Citations ---")
        for c in result.get("citations", []):
            print(f"  · {c['meeting_id']} utt#{c['utterance_index']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
