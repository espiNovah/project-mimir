import re

# local part, @, then a domain with at least one ".something" after the first word.
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


def extract_emails(text: str) -> list[str]:
    """Return every email address in text, in order of appearance."""
    return EMAIL_RE.findall(text)
