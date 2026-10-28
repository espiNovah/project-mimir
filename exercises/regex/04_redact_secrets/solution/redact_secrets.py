import re

API_KEY_RE = re.compile(r"sk-[A-Za-z0-9_-]{8,}")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


def _redact(text: str) -> tuple[str, int, int]:
    text, n_keys = API_KEY_RE.subn("[API_KEY]", text)
    text, n_emails = EMAIL_RE.subn("[EMAIL]", text)
    return text, n_keys, n_emails


def redact(text: str) -> str:
    """Replace API keys (sk- plus 8+ chars) with [API_KEY] and emails with [EMAIL]."""
    return _redact(text)[0]


def count_redactions(text: str) -> dict[str, int]:
    """Return {"api_keys": n, "emails": m}: how many of each redact() would replace."""
    _, n_keys, n_emails = _redact(text)
    return {"api_keys": n_keys, "emails": n_emails}
