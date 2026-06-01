"""Append-only audit log for every LLM call.

Every entry carries enough lineage that any insight in the deck can be
traced back to its production path: prompt version + hash, model, inputs,
output, latency. This is the *single* governance feature we keep — see
plan §3 decision 6 on why we don't ship a separate cost ledger.
"""
from __future__ import annotations

import hashlib
import json
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from ti.config import settings


def prompt_hash(text: str) -> str:
    """First 12 chars of sha256 — enough to disambiguate prompt versions."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def append(entry: dict[str, Any]) -> None:
    """Append one structured entry to the audit log."""
    settings.audit_log.parent.mkdir(parents=True, exist_ok=True)
    with settings.audit_log.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, default=str) + "\n")


@contextmanager
def record(
    *,
    agent: str,
    prompt_name: str,
    prompt_version: str,
    prompt_text: str,
    model: str,
    inputs: dict[str, Any] | None = None,
) -> Iterator[dict[str, Any]]:
    """Context manager that records one LLM call.

    Usage:
        with record(agent="topic_classifier", prompt_name="topic.v1",
                    prompt_version="v1", prompt_text=PROMPT,
                    model=settings.model_classify,
                    inputs={"meeting_id": doc.meeting_id}) as ctx:
            response = client.messages.create(...)
            ctx["output"] = response.content[0].text
            ctx["usage"] = {"in": response.usage.input_tokens,
                            "out": response.usage.output_tokens}

    Latency and timestamps are populated automatically.
    """
    started = time.monotonic()
    entry: dict[str, Any] = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "agent": agent,
        "prompt_name": prompt_name,
        "prompt_version": prompt_version,
        "prompt_hash": prompt_hash(prompt_text),
        "model": model,
        "inputs": inputs or {},
        "status": "ok",
    }
    try:
        yield entry
    except Exception as e:
        entry["status"] = "error"
        entry["error"] = f"{type(e).__name__}: {e}"
        raise
    finally:
        entry["latency_ms"] = round((time.monotonic() - started) * 1000, 1)
        append(entry)


def reset() -> None:
    """Delete the audit log. Useful for clean test runs."""
    if settings.audit_log.exists():
        settings.audit_log.unlink()


def read_all() -> list[dict[str, Any]]:
    """Read every entry. Used by the spot-check notebook for lineage demos."""
    if not settings.audit_log.exists():
        return []
    return [
        json.loads(line)
        for line in settings.audit_log.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
