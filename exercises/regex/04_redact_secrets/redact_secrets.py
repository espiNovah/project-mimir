import re


def redact(text: str) -> str:
    """Replace API keys (sk- plus 8+ chars) with [API_KEY] and emails with [EMAIL]."""
    raise NotImplementedError("Write this function")


def count_redactions(text: str) -> dict[str, int]:
    """Return {"api_keys": n, "emails": m}: how many of each redact() would replace."""
    raise NotImplementedError("Write this function")
