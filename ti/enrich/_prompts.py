"""Versioned prompt loader.

Prompts live in `ti/governance/prompts/<name>.<version>.md`. Loading is
cached so repeated enrich runs don't re-read disk per call.
"""
from __future__ import annotations

from functools import lru_cache

from ti.config import settings


@lru_cache(maxsize=64)
def load(name: str, version: str = "v1") -> str:
    """Load a versioned prompt file as raw text.

    Args:
        name: e.g. "call_type", "topic_classify"
        version: e.g. "v1"
    """
    path = settings.prompts_dir / f"{name}.{version}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {path}")
    return path.read_text(encoding="utf-8")
