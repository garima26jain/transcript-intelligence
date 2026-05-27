"""
PII redaction and restoration using Microsoft Presidio.

Design choice: Presidio is chosen over regex because it handles contextual
entity recognition (e.g., distinguishing account numbers from phone numbers)
and supports reversible pseudonymisation via a token map so evidence chains
can reference real transcript IDs internally. See DECISIONS.md ADR-005.
"""


def redact(transcript: dict) -> tuple[dict, dict]:
    """Redact PII from a transcript using Presidio analyzer + anonymizer.

    Args:
        transcript: Raw transcript dict with potentially PII-containing text.

    Returns:
        Tuple of (redacted_transcript, token_map) where token_map maps
        placeholder tokens back to original values.
    """
    pass


def restore(redacted_transcript: dict, token_map: dict) -> dict:
    """Restore original PII values from a redacted transcript and its token map.

    Args:
        redacted_transcript: Transcript with placeholder tokens.
        token_map: Mapping of placeholder tokens to original PII values.

    Returns:
        Transcript with original PII values restored.
    """
    pass
